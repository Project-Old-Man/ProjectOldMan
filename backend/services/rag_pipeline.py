from typing import Dict, Any, Optional
from services.category_router import CategoryRouter
from services.embedding import EmbeddingService
from services.vector_store import VectorStore
from services.llm_manager import get_llm_manager
import logging

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        logger.info("🚀 RAG Pipeline 초기화 시작...")
        
        try:
            self.category_router = CategoryRouter()
            logger.info("✅ Category Router 초기화 완료")
        except Exception as e:
            logger.error(f"❌ Category Router 초기화 실패: {e}")
            self.category_router = None
        
        try:
            self.embedding_service = EmbeddingService()
            logger.info("✅ Embedding Service 초기화 완료")
        except Exception as e:
            logger.error(f"❌ Embedding Service 초기화 실패: {e}")
            self.embedding_service = None
        
        try:
            self.vector_store = VectorStore(self.embedding_service)
            self._initialize_sample_data()
            logger.info("✅ Vector Store 초기화 완료")
        except Exception as e:
            logger.error(f"❌ Vector Store 초기화 실패: {e}")
            self.vector_store = None
        
        try:
            self.llm_manager = get_llm_manager()
            logger.info("✅ LLM Manager 초기화 완료")
        except Exception as e:
            logger.error(f"❌ LLM Manager 초기화 실패: {e}")
            self.llm_manager = None
        
        logger.info("🚀 RAG Pipeline 초기화 완료")
    
    def _initialize_sample_data(self):
        """샘플 데이터로 벡터 데이터베이스 초기화"""
        sample_docs = [
            {
                "text": "고혈압 관리를 위해서는 저염식 식단을 유지하고 규칙적인 운동을 하는 것이 중요합니다.",
                "category": "health",
                "topic": "혈압관리"
            },
            {
                "text": "당뇨병 예방을 위해 당분 섭취를 줄이고 식이섬유가 풍부한 음식을 섭취하세요.",
                "category": "health", 
                "topic": "당뇨예방"
            },
            {
                "text": "제주도 여행 시 성산일출봉과 한라산, 우도 등을 방문하는 것을 추천합니다.",
                "category": "travel",
                "topic": "제주도여행"
            },
            {
                "text": "부산 여행에서는 해운대, 광안리, 감천문화마을을 꼭 방문해보세요.",
                "category": "travel",
                "topic": "부산여행"
            },
            {
                "text": "안전한 투자를 위해서는 분산투자와 장기투자 원칙을 지키는 것이 중요합니다.",
                "category": "investment",
                "topic": "투자원칙"
            },
            {
                "text": "계약서 작성 시에는 조건과 책임을 명확히 하고 전문가의 검토를 받으세요.",
                "category": "legal",
                "topic": "계약법"
            }
        ]
        
        texts = [doc["text"] for doc in sample_docs]
        metadata = [{"category": doc["category"], "topic": doc["topic"]} for doc in sample_docs]
        
        self.vector_store.add_documents(texts, metadata)
        logger.info(f"📚 샘플 데이터 {len(sample_docs)}개 추가 완료")

    async def process_query(
        self, 
        query: str, 
        category: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """전체 RAG 파이프라인 처리"""
        try:
            logger.info(f"📝 쿼리 처리 시작: {query[:50]}...")
            
            # 1. 카테고리 분류
            if not category:
                category = await self.category_router.classify_category(query)
                logger.info(f"🏷️ 자동 분류된 카테고리: {category}")
            
            # 2. 벡터 검색으로 관련 문서 찾기
            relevant_docs = []
            if self.vector_store:
                relevant_docs = self.vector_store.search(query, top_k=3)
                logger.info(f"🔍 관련 문서 {len(relevant_docs)}개 찾음")
            
            # 3. 카테고리별 프롬프트 구성
            system_prompt = self._get_system_prompt(category)
            
            # 4. 컨텍스트 구성 (관련 문서 포함)
            context = ""
            if relevant_docs:
                context = "\n참고 정보:\n"
                for i, doc in enumerate(relevant_docs[:2]):  # 상위 2개만 사용
                    context += f"{i+1}. {doc['text']}\n"
                context += "\n"
            
            # 5. 최종 프롬프트 생성
            final_prompt = f"""{system_prompt}

{context}사용자 질문: {query}

답변:"""
            
            # 6. LLM 응답 생성
            response = await self.llm_manager.generate_response(
                final_prompt, 
                max_tokens=256
            )
            
            logger.info(f"✅ 응답 생성 완료 (카테고리: {category})")
            
            return {
                "response": response,
                "category": category,
                "relevant_docs_count": len(relevant_docs),
                "using_real_embeddings": self.embedding_service.is_using_real_model() if self.embedding_service else False
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
