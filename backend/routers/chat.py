from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.rag_pipeline import RAGPipeline  # 상대 임포트 → 절대 임포트

router = APIRouter()
rag_pipeline = RAGPipeline()

class ChatRequest(BaseModel):
    message: str
    category: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    category: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint with RAG pipeline"""
    try:
        response = await rag_pipeline.process_query(
            query=request.message,
            category=request.category,
            user_id=request.user_id
        )
        return ChatResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-info")
async def get_model_info():
    """현재 사용 중인 LLM 모델 정보 조회"""
    try:
        model_info = rag_pipeline.llm_manager.get_model_info()
        return {
            "success": True,
            "model_info": model_info,
            "message": "모델 정보를 성공적으로 조회했습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"모델 정보 조회 실패: {str(e)}")

@router.post("/reload-model")
async def reload_model():
    """모델 재로딩"""
    try:
        success = rag_pipeline.llm_manager.reload_model()
        if success:
            return {
                "success": True,
                "message": "모델이 성공적으로 재로딩되었습니다.",
                "model_info": rag_pipeline.llm_manager.get_model_info()
            }
        else:
            return {
                "success": False,
                "message": "모델 재로딩에 실패했습니다. Mock 모드로 동작합니다.",
                "model_info": rag_pipeline.llm_manager.get_model_info()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"모델 재로딩 실패: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        model_info = rag_pipeline.llm_manager.get_model_info()
        return {
            "status": "healthy",
            "message": "RAG Chat API is running",
            "model": model_info["name"],
            "model_status": model_info["status"]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "model": "Unknown",
            "model_status": "error"
        }
