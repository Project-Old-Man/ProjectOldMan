from typing import Dict, Any, Optional
from services.category_router import CategoryRouter  # 절대 임포트
from services.embedding import EmbeddingService      # 절대 임포트
from services.llm_manager import get_llm_manager     # 절대 임포트
import logging

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        self.category_router = CategoryRouter()
        self.embedding_service = EmbeddingService()
        self.llm_manager = get_llm_manager()  # 싱글톤 인스턴스 사용
        
        logger.info("🚀 RAG Pipeline 초기화 완료")
    
    async def process_query(
        self, 
        query: str, 
        category: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """전체 RAG 파이프라인 처리"""
        try:
            logger.info(f"📝 쿼리 처리 시작: {query[:50]}...")
            
            # 1. 카테고리 분류 (제공되지 않은 경우)
            if not category:
                category = await self.category_router.classify_category(query)
                logger.info(f"🏷️ 자동 분류된 카테고리: {category}")
            
            # 2. 카테고리별 프롬프트 구성
            system_prompt = self._get_system_prompt(category)
            
            # 3. 최종 프롬프트 생성
            final_prompt = f"""{system_prompt}

사용자 질문: {query}

답변:"""
            
            # 4. LLM 응답 생성
            response = await self.llm_manager.generate_response(
                final_prompt, 
                max_tokens=256
            )
            
            logger.info(f"✅ 응답 생성 완료 (카테고리: {category})")
            
            return {
                "response": response,
                "category": category
            }
            
        except Exception as e:
            logger.error(f"❌ RAG 파이프라인 오류: {e}")
            return {
                "response": f"죄송합니다. 처리 중 오류가 발생했습니다: {str(e)}",
                "category": category or "general"
            }
    
    def _get_system_prompt(self, category: str) -> str:
        """카테고리별 시스템 프롬프트 반환"""
        prompts = {
            "health": """당신은 중장년층을 위한 건강 상담 전문 AI입니다. 
안전하고 신뢰할 수 있는 건강 정보를 제공하되, 의학적 진단은 하지 마세요. 
항상 전문의 상담을 권하고, 이해하기 쉽게 설명해주세요.""",
            
            "travel": """당신은 중장년층을 위한 여행 상담 전문 AI입니다. 
안전하고 편안한 여행을 위한 실용적인 조언을 제공해주세요. 
국내외 여행지 정보와 준비사항을 친절하게 안내해주세요.""",
            
            "investment": """당신은 중장년층을 위한 투자 상담 전문 AI입니다. 
안전하고 보수적인 투자 방법을 우선으로 조언하고, 
리스크를 충분히 설명하며 전문가 상담을 권해주세요.""",
            
            "legal": """당신은 중장년층을 위한 법률 상담 전문 AI입니다. 
일반적인 법률 정보를 제공하되, 구체적인 법적 조언은 하지 마세요. 
항상 변호사 상담을 권하고, 이해하기 쉽게 설명해주세요."""
        }
        
        return prompts.get(category, prompts["health"])  # 기본값은 건강
