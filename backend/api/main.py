from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
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
import uvicorn
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic 모델들
class QueryRequest(BaseModel):
    question: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    response: str
    processing_time: float
    sources: List[Dict[str, Any]] = []

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, bool]

# 간단한 응답 생성기 (AI 모델 대신 사용)
def generate_simple_response(question: str, page: str = "general") -> str:
    """간단한 응답 생성 (실제 환경에서는 AI 모델 사용)"""
    
    responses = {
        "health": [
            "건강을 위해서는 규칙적인 운동과 균형 잡힌 식단이 중요합니다.",
            "충분한 수면과 스트레스 관리가 건강의 핵심입니다.",
            "정기적인 건강검진을 통해 질병을 예방하세요."
        ],
        "travel": [
            "경주는 역사와 문화가 살아있는 멋진 여행지입니다.",
            "제주도는 자연 경관이 아름다워 가족 여행지로 추천드립니다.",
            "부산 해운대는 바다와 도시의 매력을 동시에 느낄 수 있는 곳입니다."
        ],
        "investment": [
            "투자는 분산투자를 통해 리스크를 줄이는 것이 중요합니다.",
            "ETF는 초보 투자자에게 적합한 투자 상품입니다.",
            "장기 투자 관점에서 접근하시는 것을 추천드립니다."
        ],
        "legal": [
            "법률 문제는 전문가의 상담을 받으시는 것이 좋습니다.",
            "계약서 작성 시 세부 조건을 꼼꼼히 확인하세요.",
            "분쟁 발생 시 조기에 해결하는 것이 바람직합니다."
        ]
    }
    
    import random
    page_responses = responses.get(page, ["질문에 대한 답변을 준비 중입니다."])
    return random.choice(page_responses)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    logger.info("Starting application...")
    yield
    logger.info("Shutting down application...")

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
    allow_origins=["*"],
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

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """서버 상태 체크"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        services={
            "api": True,
            "database": True,  # 실제로는 DB 연결 확인
            "vector_db": True,  # 실제로는 벡터DB 연결 확인
        }
    )

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """질의응답 처리"""
    start_time = time.time()
    
    try:
        logger.info(f"Query received: {request.question[:50]}...")
        
        # 컨텍스트에서 페이지 정보 추출
        page = ""
        if request.context:
            page = request.context.get("page", "")
        
        # 간단한 응답 생성
        response = generate_simple_response(request.question, page)
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            response=response,
            processing_time=processing_time,
            sources=[]
        )
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"처리 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )