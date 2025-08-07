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
            },
             {"text": "관절염에는 관절에 무리를 주지 않는 걷기 운동이 도움이 됩니다. 무리한 등산은 피하세요.", "category": "health", "topic": "관절염"},
            {"text": "고지혈증은 콜레스테롤 수치 관리가 중요하며, 식단 조절과 유산소 운동이 필요합니다.", "category": "health", "topic": "고지혈증"},
            {"text": "눈 건강을 위해 자외선을 피하고, 비타민 A가 풍부한 음식을 섭취하세요.", "category": "health", "topic": "눈건강"},

            # travel
            {"text": "전주 한옥마을은 전통 문화와 한식 체험이 가능한 중장년층 여행지입니다.", "category": "travel", "topic": "전주"},
            {"text": "통영은 미륵산 케이블카와 동피랑 벽화마을로 유명한 남해안 관광지입니다.", "category": "travel", "topic": "통영"},
            {"text": "설악산 국립공원은 가을 단풍철에 특히 아름다우며, 무리 없는 등산 코스도 마련되어 있습니다.", "category": "travel", "topic": "설악산"},

            # investment
            {"text": "국공채는 안정성이 높아 은퇴 후 자산 보호용 투자로 적합합니다.", "category": "investment", "topic": "국공채"},
            {"text": "배당주 투자는 주기적인 수익을 원하는 투자자에게 적합하며, 기업 실적을 잘 분석해야 합니다.", "category": "investment", "topic": "배당주"},
            {"text": "분산 투자는 개별 리스크를 줄이고 장기적으로 안정적인 수익을 도모할 수 있는 방법입니다.", "category": "investment", "topic": "포트폴리오"},

            # legal
            {"text": "상속 분쟁을 줄이려면 유언장을 미리 작성하고 법적으로 인증받는 것이 중요합니다.", "category": "legal", "topic": "상속"},
            {"text": "임대차 계약 시 계약 기간과 보증금 반환 조건을 명확히 문서화해야 합니다.", "category": "legal", "topic": "임대차"},
            {"text": "근로 계약서에는 근무 시간, 급여, 휴가, 퇴직 조건이 명시되어 있어야 분쟁을 예방할 수 있습니다.", "category": "legal", "topic": "근로계약"},
             {
    "category": "health",
    "topic": "고혈압",
    "text": "고혈압 관리를 위해서는 나트륨 섭취를 줄이고, 규칙적인 유산소 운동과 스트레스 관리를 병행하는 것이 중요합니다."
  },
  {
    "category": "health",
    "topic": "당뇨병",
    "text": "당뇨병 예방에는 혈당 관리가 핵심이며, 저탄수화물 식단과 함께 꾸준한 혈당 체크가 필요합니다."
  },
  {
    "category": "health",
    "topic": "관절염",
    "text": "관절염 환자는 관절에 무리를 주지 않는 수영, 걷기 등의 운동이 도움이 되며, 체중 관리도 중요합니다."
  },
  {
    "category": "health",
    "topic": "골다공증",
    "text": "골다공증 예방을 위해서는 칼슘과 비타민 D 섭취, 체중 부하 운동이 필수적입니다."
  },
  {
    "category": "health",
    "topic": "우울증",
    "text": "중장년층의 우울증은 조기 발견이 중요하며, 가족 및 지역사회와의 소통이 예방에 도움이 됩니다."
  },
  {
    "category": "health",
    "topic": "치매",
    "text": "치매 예방에는 규칙적인 운동, 두뇌 활동, 사회적 교류 유지가 효과적이라는 연구 결과가 있습니다."
  },
  {
    "category": "health",
    "topic": "복부비만",
    "text": "복부비만은 심혈관질환과 밀접한 관련이 있으므로, 식이조절과 운동이 필수입니다."
  },
  {
    "category": "health",
    "topic": "불면증",
    "text": "불면증 개선에는 규칙적인 수면 습관과 빛, 카페인, 전자기기 노출 최소화가 필요합니다."
  },
  {
    "category": "health",
    "topic": "심근경색",
    "text": "심근경색은 흉통, 호흡곤란, 식은땀 등의 증상이 있으며, 발생 시 즉시 응급실로 가야 합니다."
  },
  {
    "category": "health",
    "topic": "간 건강",
    "text": "지방간과 간염 예방을 위해 과음은 피하고 정기적인 혈액검사를 받는 것이 좋습니다."
  },
  {
    "category": "travel",
    "topic": "경주 여행",
    "text": "경주는 불국사, 석굴암, 첨성대 등 유네스코 문화유산이 많아 역사 여행지로 추천됩니다."
  },
  {
    "category": "travel",
    "topic": "전주 한옥마을",
    "text": "전주 한옥마을은 전통 한옥과 한식 체험이 가능하여 중장년층 관광객에게 인기 있는 장소입니다."
  },
  {
    "category": "travel",
    "topic": "통영",
    "text": "통영은 미륵산 케이블카, 동피랑 벽화마을, 신선한 해산물로 유명한 남해안 여행지입니다."
  },
  {
    "category": "travel",
    "topic": "제주도",
    "text": "제주도는 성산일출봉, 우도, 한라산 등 자연경관과 관광 인프라가 잘 갖춰진 대표 여행지입니다."
  },
  {
    "category": "travel",
    "topic": "설악산",
    "text": "설악산은 단풍철에 아름다운 풍경을 자랑하며, 케이블카나 완만한 탐방로도 있어 부담 없이 즐길 수 있습니다."
  },
  {
    "category": "travel",
    "topic": "부산",
    "text": "부산은 해운대, 광안리, 감천문화마을, 자갈치 시장 등 다양한 해양·도심 관광이 가능한 도시입니다."
  },
  {
    "category": "travel",
    "topic": "남이섬",
    "text": "남이섬은 산책로와 자전거길, 수목이 잘 정비되어 있어 중장년층이 여유롭게 즐길 수 있는 여행지입니다."
  },
  {
    "category": "travel",
    "topic": "강릉",
    "text": "강릉은 정동진 해돋이와 안목 커피거리 등 자연과 휴식이 공존하는 여행지입니다."
  },
  {
    "category": "travel",
    "topic": "안동",
    "text": "안동 하회마을은 전통문화 체험과 고택 숙박이 가능해 전통을 체험할 수 있는 여행지입니다."
  },
  {
    "category": "travel",
    "topic": "대전 유성온천",
    "text": "유성온천은 피로 회복과 관절 건강에 좋다고 알려진 온천으로, 중장년층에게 인기가 높습니다."
  },
  {
    "category": "investment",
    "topic": "국공채",
    "text": "국공채는 국가가 발행한 채권으로, 안정적인 수익을 추구하는 중장년층에게 적합한 투자 수단입니다."
  },
  {
    "category": "investment",
    "topic": "ETF",
    "text": "ETF는 다양한 자산에 분산 투자할 수 있어 초보자나 리스크를 줄이고 싶은 투자자에게 유리합니다."
  },
  {
    "category": "investment",
    "topic": "배당주",
    "text": "배당주는 정기적으로 수익을 받을 수 있는 주식으로, 은퇴자나 안정적 수익을 원하는 사람에게 적합합니다."
  },
  {
    "category": "investment",
    "topic": "REITs",
    "text": "REITs는 부동산 투자신탁으로, 소액으로도 부동산 시장에 간접 투자할 수 있는 방법입니다."
  },
  {
    "category": "investment",
    "topic": "개인연금",
    "text": "개인연금은 노후를 위한 자산 준비 수단으로, 세액공제 혜택과 안정적 수익을 기대할 수 있습니다."
  },
  {
    "category": "investment",
    "topic": "적립식펀드",
    "text": "적립식 펀드는 일정 금액을 정기적으로 투자하여 리스크를 분산시키는 장기 투자 방법입니다."
  },
  {
    "category": "investment",
    "topic": "금 투자",
    "text": "금은 인플레이션 헤지 수단으로, 장기적인 자산 보존 목적에 적합한 실물 자산입니다."
  },
  {
    "category": "investment",
    "topic": "환율",
    "text": "환율 변동성은 해외투자에 영향을 미치므로, 분산 포트폴리오 구성 시 중요 요소입니다."
  },
  {
    "category": "investment",
    "topic": "채권형펀드",
    "text": "채권형펀드는 안정적인 이자 수익을 목표로 하며, 원금 손실 가능성은 낮은 편입니다."
  },
  {
    "category": "investment",
    "topic": "TDF",
    "text": "TDF(타깃데이트펀드)는 은퇴 시점에 맞춰 자산 배분이 조정되어 자동화된 포트폴리오 관리가 가능합니다."
  },
  {
    "category": "legal",
    "topic": "상속",
    "text": "상속 분쟁을 줄이기 위해서는 유언장을 미리 작성하고, 공증을 받는 것이 법적 효력을 높이는 방법입니다."
  },
  {
    "category": "legal",
    "topic": "임대차보호법",
    "text": "주택임대차보호법은 세입자의 권리를 보호하기 위한 법률로, 전입신고와 확정일자는 필수입니다."
  },
  {
    "category": "legal",
    "topic": "근로계약서",
    "text": "근로계약서는 근무조건, 급여, 휴가 등을 명확히 하여 향후 분쟁 예방에 중요한 역할을 합니다."
  },
  {
    "category": "legal",
    "topic": "이혼",
    "text": "이혼 시 재산분할과 양육권, 위자료 등에 대한 법률 상담을 받는 것이 중요합니다."
  },
  {
    "category": "legal",
    "topic": "소액재판",
    "text": "소액재판은 3천만원 이하의 민사분쟁을 신속하게 처리하는 절차로, 법률 대리인 없이도 진행할 수 있습니다."
  },
  {
    "category": "legal",
    "topic": "형사고소",
    "text": "형사고소는 범죄 피해자가 경찰 또는 검찰에 가해자를 처벌해 달라고 요구하는 법적 절차입니다."
  },
  {
    "category": "legal",
    "topic": "교통사고 합의",
    "text": "교통사고 발생 시 형사적 책임과 별개로 민사적 합의도 필요하며, 보험사의 조력도 중요합니다."
  },
  {
    "category": "legal",
    "topic": "계약서 작성",
    "text": "계약서는 반드시 서면으로 작성하고, 주요 조항(기간, 책임, 분쟁 해결 방법 등)을 명확히 해야 합니다."
  },
  {
    "category": "legal",
    "topic": "부동산 등기",
    "text": "부동산 등기를 통해 소유권을 공식화할 수 있으며, 매매 후 즉시 등기를 완료하는 것이 안전합니다."
  },
  {
    "category": "legal",
    "topic": "명의신탁",
    "text": "명의신탁은 부동산 실소유자와 등기명의자가 다른 상태로, 법적으로 금지되어 있는 경우가 많습니다."
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
            if relevant_docs and len(relevant_docs) > 0:
                context = "\n참고 정보:\n"
                for i, doc in enumerate(relevant_docs[:3]):  # 상위 3개 모두 사용
                    context += f"{i+1}. {doc['text']}\n"
                context += "\n"
            else:
                context = "\n참고 정보: 검색된 정보가 없으니 일반적인 조언을 드립니다.\n\n"
            
            # 5. 최종 프롬프트 생성
            final_prompt = f"""{system_prompt}

{context}사용자 질문: {query}

답변은 반드시 [요약], [상세 설명], [실천 조언] 형식의 3개 섹션으로 나누어 작성하고, 전체 길이가 300자 이상이 되도록 상세하게 작성해주세요.

답변:"""
            
            # 6. LLM 응답 생성
            response = await self.llm_manager.generate_response(
                final_prompt, 
                max_tokens=768
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
            "health": (
                "당신은 중장년층을 위한 건강 상담 전문 AI입니다.\n"
                "항상 친절하고 명확하게 설명하세요.\n\n"
                "아래 형식을 따르세요:\n"
                "1. 요약 (한 문단)\n"
                "2. 상세 설명 (증상, 원인, 관리법 중심)\n"
                "3. 실천 조언 (일상에서 적용할 수 있는 조치들)\n\n"
                "의학적 진단은 하지 말고, 필요한 경우 병원 방문을 권유하세요.\n"
                "모든 응답은 300자 이상으로 작성하세요."
            ),
            "travel": (
                "당신은 중장년층을 위한 여행 상담 전문 AI입니다.\n"
                "안전하고 편안한 여행을 위해 다음 구조로 응답하세요:\n\n"
                "1. 요약 (여행지 핵심 특징)\n"
                "2. 상세 설명 (날씨, 활동, 식사, 이동 난이도 등)\n"
                "3. 실천 조언 (짐 챙기는 팁, 주의사항 등)\n\n"
                "모든 응답은 중장년층이 이해하기 쉬운 표현으로 300자 이상 작성하세요."
            ),
            "investment": (
                "당신은 중장년층을 위한 보수적 투자 상담 AI입니다.\n"
                "절대 무리한 투자를 권하지 말고, 아래 구조로 응답하세요:\n\n"
                "1. 요약 (핵심 요점)\n"
                "2. 상세 설명 (관련 자산 특성, 리스크 설명 포함)\n"
                "3. 실천 조언 (어떻게 시작할지, 어떤 자료를 참고할지 등)\n\n"
                "전문가 상담을 권유하며, 모든 응답은 300자 이상이어야 합니다."
            ),
            "legal": (
                "당신은 중장년층을 위한 생활 법률 정보 제공 AI입니다.\n"
                "절대 법적 조언이나 해석을 하지 말고, 다음 형식으로 응답하세요:\n\n"
                "1. 요약 (핵심 쟁점 요약)\n"
                "2. 상세 설명 (일반적 정보, 관련 법률)\n"
                "3. 실천 조언 (문서 준비, 상담 권유 등)\n\n"
                "모든 답변은 300자 이상이어야 하며, 변호사 상담을 권유하세요."
            )
        }
        return prompts.get(category, prompts["health"])  # 기본값은 건강
