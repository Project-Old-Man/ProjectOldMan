from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat  # 절대 임포트
import uvicorn
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ProjectOldMan RAG Chat API",
    description="중장년층을 위한 카테고리별 RAG 챗봇 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 오리진 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/")
async def root():
    return {
        "message": "ProjectOldMan RAG Chat API",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """전체 시스템 헬스체크"""
    try:
        # RAG Pipeline 초기화 테스트
        from services.rag_pipeline import RAGPipeline
        rag_pipeline = RAGPipeline()
        model_info = rag_pipeline.llm_manager.get_model_info()
        
        return {
            "status": "healthy",
            "message": "All systems operational",
            "model": model_info["name"],
            "model_status": model_info["status"]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "message": f"System error: {str(e)}",
            "model": "Unknown",
            "model_status": "error"
        }

if __name__ == "__main__":
    logger.info("🚀 Starting ProjectOldMan RAG Chat API server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9000,
        reload=True,
        log_level="info"
    )
