from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import time
from datetime import datetime
import logging
import os
from contextlib import asynccontextmanager

# 로컬 imports
from database import DatabaseManager, get_db
from vector_db import VectorDBManager
from llm_service import LLMService
from prompt_manager import PromptManager
from model_manager import ModelManager

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic 모델들
class QueryRequest(BaseModel):
    question: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class RecommendRequest(BaseModel):
    user_id: str
    limit: Optional[int] = 5

class FeedbackRequest(BaseModel):
    query_id: str
    user_id: str
    rating: int  # 1-5
    feedback_text: Optional[str] = None

class QueryResponse(BaseModel):
    query_id: str
    response: str
    sources: List[Dict[str, Any]]
    processing_time: float

class ModelSwitchRequest(BaseModel):
    model_id: str

class ModelAddRequest(BaseModel):
    model_id: str
    model_config: Dict[str, Any]

# 전역 서비스 인스턴스들
llm_service = None
vector_db = None
prompt_manager = None
model_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 초기화
    global llm_service, vector_db, prompt_manager, model_manager
    
    logger.info("AI 백엔드 서버 초기화 중...")
    
    # 서비스 초기화
    model_manager = ModelManager()
    llm_service = LLMService()
    vector_db = VectorDBManager()
    prompt_manager = PromptManager()
    
    # vLLM 모델 로드
    await llm_service.initialize()
    
    # 벡터DB 연결
    await vector_db.connect()
    
    logger.info("초기화 완료!")
    
    yield
    
    # 종료 시 정리
    logger.info("서버 종료 중...")
    if llm_service:
        await llm_service.shutdown()
    if vector_db:
        await vector_db.disconnect()

# FastAPI 앱 생성
app = FastAPI(
    title="AI 추천 시스템 API",
    description="AI 기반 질의응답 및 추천 시스템",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "AI 추천 시스템 API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """서버 상태 체크"""
    try:
        # DB 연결 확인
        db_status = await DatabaseManager.check_connection()
        vector_status = await vector_db.health_check() if vector_db else False
        llm_status = llm_service.is_ready() if llm_service else False
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": db_status,
                "vector_db": vector_status,
                "llm": llm_status
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, db: DatabaseManager = Depends(get_db)):
    """메인 질의응답 API"""
    start_time = time.time()
    
    try:
        logger.info(f"Query received: {request.question[:50]}...")
        
        # 1. 벡터 검색으로 관련 컨텍스트 찾기
        search_results = await vector_db.search(
            query=request.question,
            limit=5
        )
        
        # 2. 프롬프트 생성
        prompt = prompt_manager.create_query_prompt(
            question=request.question,
            context=search_results,
            user_context=request.context
        )
        
        # 3. LLM 추론
        response = await llm_service.generate_response(prompt)
        
        # 4. DB에 쿼리 기록 저장
        query_record = await db.save_query(
            user_id=request.user_id,
            question=request.question,
            response=response,
            sources=[r["metadata"] for r in search_results],
            processing_time=time.time() - start_time
        )
        
        return QueryResponse(
            query_id=str(query_record.id),
            response=response,
            sources=[r["metadata"] for r in search_results],
            processing_time=time.time() - start_time
        )
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"처리 중 오류가 발생했습니다: {str(e)}")

@app.post("/query/stream")
async def stream_query(request: QueryRequest, db: DatabaseManager = Depends(get_db)):
    """스트리밍 질의응답 API"""
    
    async def generate_stream():
        try:
            # 벡터 검색
            search_results = await vector_db.search(request.question, limit=3)
            
            # 프롬프트 생성
            prompt = prompt_manager.create_query_prompt(
                question=request.question,
                context=search_results,
                user_context=request.context
            )
            
            # 스트리밍 응답 생성
            full_response = ""
            async for chunk in llm_service.stream_response(prompt):
                full_response += chunk
                yield f"data: {json.dumps({'chunk': chunk, 'type': 'content'})}\n\n"
            
            # 완료 후 DB 저장
            await db.save_query(
                user_id=request.user_id,
                question=request.question,
                response=full_response,
                sources=[r["metadata"] for r in search_results]
            )
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            yield f"data: {json.dumps({'error': str(e), 'type': 'error'})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache"}
    )

@app.post("/recommend")
async def get_recommendations(request: RecommendRequest, db: DatabaseManager = Depends(get_db)):
    """개인화된 추천 API"""
    try:
        # 사용자 히스토리 기반 추천
        user_history = await db.get_user_history(request.user_id, limit=10)
        
        if not user_history:
            # 히스토리가 없으면 인기 질문 추천
            popular_queries = await db.get_popular_queries(limit=request.limit)
            return {"recommendations": popular_queries, "type": "popular"}
        
        # 사용자 관심사 기반 벡터 검색
        recent_queries = [h.question for h in user_history]
        interest_vector = await vector_db.get_average_embedding(recent_queries)
        
        similar_content = await vector_db.search_by_vector(
            vector=interest_vector,
            limit=request.limit * 2  # 더 많이 가져와서 필터링
        )
        
        # 이미 본 내용 제외하고 추천
        seen_questions = set(recent_queries)
        recommendations = []
        
        for content in similar_content:
            if content["text"] not in seen_questions:
                recommendations.append({
                    "question": content["text"],
                    "similarity": content["score"],
                    "category": content["metadata"].get("category", "general")
                })
                
                if len(recommendations) >= request.limit:
                    break
        
        return {"recommendations": recommendations, "type": "personalized"}
        
    except Exception as e:
        logger.error(f"Recommendation failed: {e}")
        raise HTTPException(status_code=500, detail="추천 생성 중 오류가 발생했습니다")

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest, db: DatabaseManager = Depends(get_db)):
    """사용자 피드백 수집 API"""
    try:
        feedback_record = await db.save_feedback(
            query_id=request.query_id,
            user_id=request.user_id,
            rating=request.rating,
            feedback_text=request.feedback_text
        )
        
        logger.info(f"Feedback saved: {request.rating}/5 for query {request.query_id}")
        
        return {
            "message": "피드백이 저장되었습니다",
            "feedback_id": str(feedback_record.id)
        }
        
    except Exception as e:
        logger.error(f"Feedback save failed: {e}")
        raise HTTPException(status_code=500, detail="피드백 저장 중 오류가 발생했습니다")

@app.get("/analytics/stats")
async def get_analytics(db: DatabaseManager = Depends(get_db)):
    """시스템 통계 API"""
    try:
        stats = await db.get_system_stats()
        return stats
    except Exception as e:
        logger.error(f"Analytics failed: {e}")
        raise HTTPException(status_code=500, detail="통계 조회 중 오류가 발생했습니다")

@app.post("/admin/retrain")
async def trigger_retrain():
    """모델 재학습 트리거 (관리자용)"""
    try:
        # 재학습 조건 체크
        db = DatabaseManager()
        feedback_count = await db.get_feedback_count_since_last_train()
        
        if feedback_count < 100:  # 최소 피드백 수
            return {"message": "재학습 조건 미충족", "feedback_count": feedback_count}
        
        # 백그라운드 태스크로 재학습 시작
        asyncio.create_task(start_retraining())
        
        return {"message": "재학습이 시작되었습니다", "feedback_count": feedback_count}
        
    except Exception as e:
        logger.error(f"Retrain trigger failed: {e}")
        raise HTTPException(status_code=500, detail="재학습 트리거 실패")

async def start_retraining():
    """백그라운드 재학습 프로세스"""
    try:
        logger.info("재학습 프로세스 시작...")
        
        # 1. 새로운 학습 데이터 준비
        # 2. 파인튜닝 실행 (외부 스크립트 호출)
        # 3. 새 모델 검증
        # 4. 모델 핫스와프
        
        # 실제 구현에서는 별도의 학습 파이프라인을 호출
        await asyncio.sleep(5)  # 임시 지연
        
        logger.info("재학습 완료")
        
    except Exception as e:
        logger.error(f"재학습 실패: {e}")

# 모델 관리 API 엔드포인트들
@app.get("/admin/models")
async def get_models():
    """사용 가능한 모델 목록 조회"""
    try:
        if not model_manager:
            raise HTTPException(status_code=503, detail="모델 매니저가 초기화되지 않았습니다")
        
        models = model_manager.get_available_models()
        return {"models": models}
        
    except Exception as e:
        logger.error(f"모델 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="모델 목록 조회 중 오류가 발생했습니다")

@app.get("/admin/model-info")
async def get_model_info():
    """현재 활성 모델 정보 조회"""
    try:
        if not model_manager:
            raise HTTPException(status_code=503, detail="모델 매니저가 초기화되지 않았습니다")
        
        model_info = model_manager.get_model_info()
        return model_info
        
    except Exception as e:
        logger.error(f"모델 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="모델 정보 조회 중 오류가 발생했습니다")

@app.post("/admin/switch-model")
async def switch_model(request: ModelSwitchRequest):
    """모델 전환"""
    try:
        if not model_manager:
            raise HTTPException(status_code=503, detail="모델 매니저가 초기화되지 않았습니다")
        
        success = model_manager.switch_model(request.model_id)
        if not success:
            raise HTTPException(status_code=400, detail="모델 전환에 실패했습니다")
        
        # LLM 서비스 재초기화 (새 모델 로드)
        if llm_service:
            await llm_service.shutdown()
            await llm_service.initialize()
        
        return {"message": f"모델이 {request.model_id}로 전환되었습니다"}
        
    except Exception as e:
        logger.error(f"모델 전환 실패: {e}")
        raise HTTPException(status_code=500, detail="모델 전환 중 오류가 발생했습니다")

@app.post("/admin/add-model")
async def add_model(request: ModelAddRequest):
    """새 모델 추가"""
    try:
        if not model_manager:
            raise HTTPException(status_code=503, detail="모델 매니저가 초기화되지 않았습니다")
        
        # 모델 경로 유효성 검사
        model_path = request.model_config.get("name", "")
        if not model_manager.validate_model_path(model_path):
            raise HTTPException(status_code=400, detail="유효하지 않은 모델 경로입니다")
        
        success = model_manager.add_model(request.model_id, request.model_config)
        if not success:
            raise HTTPException(status_code=400, detail="모델 추가에 실패했습니다")
        
        return {"message": f"모델 {request.model_id}이 추가되었습니다"}
        
    except Exception as e:
        logger.error(f"모델 추가 실패: {e}")
        raise HTTPException(status_code=500, detail="모델 추가 중 오류가 발생했습니다")

@app.delete("/admin/remove-model/{model_id}")
async def remove_model(model_id: str):
    """모델 제거"""
    try:
        if not model_manager:
            raise HTTPException(status_code=503, detail="모델 매니저가 초기화되지 않았습니다")
        
        success = model_manager.remove_model(model_id)
        if not success:
            raise HTTPException(status_code=400, detail="모델 제거에 실패했습니다")
        
        return {"message": f"모델 {model_id}이 제거되었습니다"}
        
    except Exception as e:
        logger.error(f"모델 제거 실패: {e}")
        raise HTTPException(status_code=500, detail="모델 제거 중 오류가 발생했습니다")

@app.get("/analytics/model-stats")
async def get_model_stats():
    """모델 사용 통계"""
    try:
        if not model_manager:
            raise HTTPException(status_code=503, detail="모델 매니저가 초기화되지 않았습니다")
        
        # 실제 구현에서는 데이터베이스에서 모델 사용 통계를 조회
        model_info = model_manager.get_model_info()
        
        stats = {
            "active_model": model_info["active_model"],
            "total_models": model_info["available_models"],
            "auto_switch_enabled": model_info["auto_switch_enabled"],
            "usage_stats": {
                "total_queries": 0,  # 실제로는 DB에서 조회
                "success_rate": 0.95,
                "average_response_time": 1.2
            }
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"모델 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="모델 통계 조회 중 오류가 발생했습니다")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )