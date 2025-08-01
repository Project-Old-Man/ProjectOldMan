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
    
    logger.info(f"🤖 Generating response for page: {page}")
    
    responses = {
        "health": [
            "건강을 위해서는 규칙적인 운동과 균형 잡힌 식단이 중요합니다. 하루 30분 이상의 유산소 운동을 권장드리며, 충분한 수분 섭취도 잊지 마세요.",
            "충분한 수면(7-8시간)과 스트레스 관리가 건강의 핵심입니다. 명상이나 요가 같은 활동도 도움이 됩니다.",
            "정기적인 건강검진을 통해 질병을 예방하세요. 특히 중장년층은 혈압, 혈당, 콜레스테롤 수치를 주기적으로 확인하는 것이 중요합니다."
        ],
        "travel": [
            "경주는 역사와 문화가 살아있는 멋진 여행지입니다. 불국사, 석굴암, 첨성대 등을 방문해보세요. 현지 음식도 꼭 맛보시길 추천드립니다.",
            "제주도는 자연 경관이 아름다워 가족 여행지로 추천드립니다. 한라산, 성산일출봉, 우도 등이 인기 명소입니다.",
            "부산 해운대는 바다와 도시의 매력을 동시에 느낄 수 있는 곳입니다. 해변을 따라 산책하며 신선한 해산물도 즐겨보세요."
        ],
        "investment": [
            "투자는 분산투자를 통해 리스크를 줄이는 것이 중요합니다. 한 곳에 모든 자금을 투자하지 마시고, 여러 자산에 나누어 투자하세요.",
            "ETF는 초보 투자자에게 적합한 투자 상품입니다. 적은 비용으로 다양한 자산에 분산투자할 수 있어 안정적입니다.",
            "장기 투자 관점에서 접근하시는 것을 추천드립니다. 단기 변동에 흔들리지 말고 꾸준히 투자하는 것이 성공의 열쇠입니다."
        ],
        "legal": [
            "법률 문제는 전문가의 상담을 받으시는 것이 좋습니다. 대한법률구조공단이나 법무부 법률홈페이지를 활용해보세요.",
            "계약서 작성 시 세부 조건을 꼼꼼히 확인하세요. 특히 계약 기간, 해지 조건, 위약금 등을 명확히 해야 합니다.",
            "분쟁 발생 시 조기에 해결하는 것이 바람직합니다. 소액심판이나 조정 제도를 먼저 이용해보시는 것을 추천드립니다."
        ]
    }
    
    import random
    page_responses = responses.get(page, [
        "궁금한 점을 더 구체적으로 알려주시면 더 자세한 답변을 드릴 수 있습니다.",
        "추가 정보가 필요하시면 언제든 말씀해주세요.",
        "더 도움이 되는 정보를 원하시면 구체적인 상황을 설명해주시면 좋겠습니다."
    ])
    selected_response = random.choice(page_responses)
    
    logger.info(f"📝 Selected response from {page} category")
    return selected_response

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
        logger.info(f"📥 Query received: {request.question[:50]}...")
        logger.info(f"📋 User ID: {request.user_id}")
        logger.info(f"🔧 Context: {request.context}")
        
        # 컨텍스트에서 페이지 정보 추출
        page = ""
        if request.context:
            page = request.context.get("page", "")
            logger.info(f"📄 Page: {page}")
        
        # 간단한 응답 생성
        response = generate_simple_response(request.question, page)
        logger.info(f"✅ Response generated: {response[:50]}...")
        
        processing_time = time.time() - start_time
        logger.info(f"⏱️ Processing time: {processing_time:.2f}s")
        
        result = QueryResponse(
            response=response,
            processing_time=processing_time,
            sources=[]
        )
        
        logger.info(f"📤 Sending response: {len(result.response)} characters")
        return result
        
    except Exception as e:
        logger.error(f"❌ Query processing failed: {e}")
        logger.error(f"🔍 Error details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"처리 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )