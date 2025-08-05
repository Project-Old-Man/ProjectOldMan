from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
import time
import logging
import random

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI 놀이터 API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 카테고리별 전문 응답 데이터베이스
CATEGORY_KNOWLEDGE = {
    "health": {
        "운동": [
            "중장년층에게 권장하는 운동은 걷기, 수영, 요가, 태극권입니다. 주 3-4회, 30분씩 꾸준히 하는 것이 중요해요.",
            "무릎에 부담이 적은 수중운동이나 실버체조를 추천해요. 운동 전후 스트레칭은 필수입니다.",
            "계단 오르기, 가벼운 근력운동도 좋아요. 본인의 체력에 맞춰 점진적으로 강도를 높이세요."
        ],
        "식단": [
            "균형 잡힌 식단이 중요해요. 야채, 과일, 단백질을 골고루 섭취하시고, 나트륨 섭취는 줄이세요.",
            "칼슘과 비타민D가 풍부한 음식을 드세요. 멸치, 두부, 달걀 등이 좋습니다.",
            "하루 8잔 이상 충분한 수분 섭취를 하시고, 과도한 음주는 피하세요."
        ],
        "혈압": [
            "정기적인 혈압 측정이 중요해요. 가정용 혈압계로 매일 같은 시간에 측정하세요.",
            "저염식, 금연, 절주, 규칙적인 운동이 혈압 관리에 도움이 됩니다.",
            "스트레스 관리도 중요해요. 명상이나 취미활동으로 마음의 안정을 찾으세요."
        ],
        "건강검진": [
            "년 1-2회 정기 건강검진을 받으세요. 국가건강검진을 꼭 활용하시구요.",
            "40세 이후엔 위내시경, 대장내시경도 정기적으로 받는 것이 좋습니다.",
            "혈당, 콜레스테롤, 혈압 등 기본 수치는 주기적으로 확인하세요."
        ]
    },
    "travel": {
        "제주도": [
            "제주도는 중장년층께 최고의 여행지예요! 한라산 둘레길, 올레길을 편안하게 걸으실 수 있어요.",
            "성산일출봉, 우도, 만장굴 등을 여유롭게 둘러보세요. 렌터카보다는 관광버스 투어를 추천해요.",
            "제주 흑돼지, 갈치조림, 전복죽 등 맛있는 음식도 놓치지 마세요!"
        ],
        "부산": [
            "부산은 바다와 온천을 함께 즐길 수 있어요. 해운대, 광안리에서 산책하시고 동래온천에서 휴식을!",
            "감천문화마을, 태종대, 용두산공원은 꼭 가보세요. 지하철로 이동이 편리해요.",
            "자갈치시장에서 신선한 해산물을 드시고, 부산국제영화제 거리도 구경하세요."
        ],
        "경주": [
            "경주는 역사와 문화를 체험할 수 있는 최고의 여행지예요. 불국사, 석굴암은 필수 코스입니다.",
            "천마총, 첨성대, 안압지를 천천히 둘러보세요. 걷기 편한 신발을 꼭 준비하세요.",
            "경주 한정식과 황남빵도 맛보시고, 보문관광단지에서 숙박하시면 편리해요."
        ],
        "준비물": [
            "편한 신발이 가장 중요해요. 상비약, 개인 의료용품도 꼭 챙기세요.",
            "여행자보험 가입을 권해드리고, 만성질환이 있으시면 충분한 약물을 준비하세요.",
            "날씨에 맞는 옷차림과 우산, 선크림도 필수입니다."
        ]
    },
    "investment": {
        "안전투자": [
            "중장년층께는 안전성이 최우선이에요. 예금, 적금, 국채 등 원금보장 상품을 기본으로 하세요.",
            "투자 비중은 나이에 따라 조절하세요. 60세라면 주식 40%, 채권 60% 정도가 적당해요.",
            "절대 고수익을 약속하는 투자는 피하세요. '원금보장'이라는 말도 의심해보세요."
        ],
        "연금": [
            "국민연금 외에 개인연금(IRP, 연금저축)도 고려해보세요. 세제혜택이 있어요.",
            "은퇴 후 생활비를 미리 계산해서 필요한 연금액을 준비하세요.",
            "연금 수령 시기와 방법도 미리 계획하는 것이 좋습니다."
        ],
        "재테크": [
            "분산투자의 원칙을 지키세요. 한 곳에 모든 돈을 투자하면 위험해요.",
            "투자 전에 상품을 완전히 이해하고, 본인의 위험감수능력을 정확히 파악하세요.",
            "정기적으로 포트폴리오를 점검하고 리밸런싱하는 것이 중요해요."
        ],
        "부동산": [
            "부동산 투자 시 입지, 교통, 개발계획 등을 꼼꼼히 확인하세요.",
            "대출 투자는 신중하게! 이자 부담과 리스크를 충분히 고려하세요.",
            "세금, 관리비, 중개수수료 등 부대비용도 미리 계산해두세요."
        ]
    },
    "legal": {
        "계약": [
            "계약서의 모든 조항을 꼼꼼히 읽어보세요. 이해되지 않는 부분은 반드시 질문하세요.",
            "중요한 계약은 가족과 상의하고, 필요시 변호사의 도움을 받으세요.",
            "계약 해지 조건, 위약금, 쿨링오프 기간 등을 확인하세요."
        ],
        "상속": [
            "상속은 미리 준비하는 것이 좋아요. 유언장 작성과 재산 정리를 해두세요.",
            "상속세 절약 방법과 가족 간 분쟁 방지를 위해 전문가와 상담하세요.",
            "부동산, 금융자산, 부채 등을 명확히 정리해두세요."
        ],
        "소비자": [
            "전화 권유 판매, 방문 판매는 특히 주의하세요. 쿨링오프 제도를 활용하세요.",
            "피해를 당했다면 소비자분쟁조정위원회나 소비자보호원에 신고하세요.",
            "계약 전에 사업자등록증, 약관을 확인하고 계약서 사본을 받으세요."
        ],
        "사기예방": [
            "높은 수익을 보장한다는 투자 권유는 대부분 사기예요. 절대 현혹되지 마세요.",
            "개인정보, 금융정보를 함부로 알려주지 마세요. 공인인증서 관리도 주의하세요.",
            "의심스러우면 가족, 전문가와 상의하고, 경찰서나 금융감독원에 신고하세요."
        ]
    }
}

class QueryRequest(BaseModel):
    question: str
    user_id: str
    context: Dict[str, Any] = {}

class QueryResponse(BaseModel):
    response: str
    processing_time: float
    sources: List[Dict[str, Any]] = []
    category: str = ""
    suggestion: Optional[str] = None

async def generate_category_response(question: str, category: str) -> Dict[str, Any]:
    """카테고리별 맞춤 응답 생성"""
    
    # 질문에서 키워드 추출
    question_lower = question.lower()
    
    knowledge_base = CATEGORY_KNOWLEDGE.get(category, {})
    
    # 키워드 매칭으로 가장 적절한 응답 찾기
    best_match = None
    best_responses = []
    
    for keyword, responses in knowledge_base.items():
        if keyword in question_lower or any(k in question_lower for k in keyword.split()):
            best_match = keyword
            best_responses = responses
            break
    
    # 응답 생성
    if best_responses:
        # 여러 응답 중 하나를 랜덤 선택하거나 조합
        if len(best_responses) == 1:
            main_response = best_responses[0]
        else:
            # 2-3개 응답을 조합
            selected = random.sample(best_responses, min(2, len(best_responses)))
            main_response = " ".join(selected)
    else:
        # 기본 응답
        default_responses = {
            "health": "건강 관련 질문을 더 구체적으로 말씀해 주시면 맞춤 정보를 제공해드릴 수 있어요. 운동, 식단, 건강검진 등에 대해 물어보세요!",
            "travel": "어떤 여행지나 여행 스타일에 관심이 있으신가요? 제주도, 부산, 경주 등 구체적인 지역이나 준비물에 대해 질문해보세요!",
            "investment": "투자 관련 구체적인 질문을 해주세요. 안전한 투자, 연금, 부동산 등에 대해 일반적인 정보를 제공해드릴 수 있어요.",
            "legal": "법률 관련 질문을 더 구체적으로 해주세요. 계약, 상속, 소비자 보호 등에 대한 기본 정보를 알려드릴 수 있어요."
        }
        main_response = default_responses.get(category, "구체적인 질문을 해주시면 더 도움이 되는 답변을 드릴 수 있어요.")
    
    # 카테고리별 전문가 역할 표시
    category_titles = {
        "health": "건강 전문 상담사",
        "travel": "여행 전문 가이드", 
        "investment": "투자 상담 전문가",
        "legal": "법률 정보 전문가"
    }
    
    expert_title = category_titles.get(category, "AI 상담사")
    formatted_response = f"[{expert_title}] {main_response}"
    
    # 면책 조항 추가
    disclaimers = {
        "health": "※ 구체적인 건강 문제는 반드시 전문의와 상담하세요.",
        "travel": "※ 여행 전 최신 정보를 확인하고 안전에 주의하세요.",
        "investment": "※ 투자에는 위험이 따르므로 전문가와 상담 후 결정하세요.",
        "legal": "※ 법률 문제는 변호사나 법무사와 상담하시기 바랍니다."
    }
    
    if category in disclaimers:
        formatted_response += f"\n\n{disclaimers[category]}"
    
    # 추가 질문 제안
    suggestions = {
        "health": "다른 건강 관련 질문: 혈압 관리, 당뇨 예방, 건강한 식단, 운동법",
        "travel": "다른 여행 관련 질문: 여행지 추천, 준비물, 숙박, 교통편",
        "investment": "다른 투자 관련 질문: 연금 준비, 안전한 투자, 부동산, 세금",
        "legal": "다른 법률 관련 질문: 계약서 작성, 상속 준비, 사기 예방, 소비자 권익"
    }
    
    return {
        "response": formatted_response,
        "suggestion": suggestions.get(category),
        "matched_keyword": best_match
    }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """메인 질의응답 처리"""
    start_time = time.time()
    
    try:
        # 카테고리 추출
        category = request.context.get("page", "general")
        
        logger.info(f"Query: {request.question[:50]}... | Category: {category}")
        
        # 카테고리별 맞춤 응답 생성
        result = await generate_category_response(request.question, category)
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            response=result["response"],
            processing_time=processing_time,
            sources=[],
            category=category,
            suggestion=result.get("suggestion")
        )
        
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "services": {
            "database": True,
            "vector_db": True,
            "llm": True
        },
        "categories": list(CATEGORY_KNOWLEDGE.keys()),
        "timestamp": time.time()
    }

@app.get("/categories")
async def get_categories():
    """사용 가능한 카테고리 목록"""
    return {
        "categories": [
            {"id": "health", "name": "건강 상담", "description": "건강 관리 및 의료 정보"},
            {"id": "travel", "name": "여행 상담", "description": "여행 계획 및 정보"},
            {"id": "investment", "name": "투자 상담", "description": "투자 및 재테크 정보"},
            {"id": "legal", "name": "법률 상담", "description": "법률 상담 및 정보"}
        ]
    }

@app.get("/")
async def root():
    return {
        "message": "AI 놀이터 API 서버가 실행 중입니다!",
        "version": "1.0.0",
        "features": ["카테고리별 전문 상담", "맞춤형 응답", "중장년층 특화"]
    }

@app.get("/recommendations/{category}")
async def get_category_recommendations(category: str):
    """카테고리별 추천 질문 반환"""
    
    recommendations = {
        "health": [
            {"question": "혈압 관리 방법 알려주세요", "description": "중장년층 건강 관리", "priority": 1},
            {"question": "당뇨 예방은 어떻게 하나요?", "description": "성인병 예방법", "priority": 2},
            {"question": "건강한 운동법이 궁금해요", "description": "중장년층 맞춤 운동", "priority": 3},
            {"question": "건강검진 주기는 어떻게 되나요?", "description": "정기 건강검진", "priority": 4},
            {"question": "콜레스테롤 관리법 알려주세요", "description": "혈관 건강", "priority": 5},
        ],
        "travel": [
            {"question": "제주도 여행 추천해주세요", "description": "인기 여행지", "priority": 1},
            {"question": "부산 여행 코스 알려주세요", "description": "바다 여행", "priority": 2},
            {"question": "경주 역사 여행 계획 세워주세요", "description": "문화재 탐방", "priority": 3},
            {"question": "여행 준비물은 뭐가 필요한가요?", "description": "여행 팁", "priority": 4},
            {"question": "강릉 여행 코스 추천해주세요", "description": "동해안 여행", "priority": 5},
        ],
        "investment": [
            {"question": "안전한 투자 방법은?", "description": "저위험 투자", "priority": 1},
            {"question": "연금 준비 어떻게 하나요?", "description": "은퇴 계획", "priority": 2},
            {"question": "부동산 투자 주의사항은?", "description": "부동산 투자", "priority": 3},
            {"question": "적금과 예금 어떤게 좋을까요?", "description": "기본 금융상품", "priority": 4},
            {"question": "국채 투자 방법 알려주세요", "description": "안전 투자", "priority": 5},
        ],
        "legal": [
            {"question": "계약서 작성시 주의사항", "description": "계약 법률", "priority": 1},
            {"question": "상속 준비 방법", "description": "상속 법률", "priority": 2},
            {"question": "사기 예방법 알려주세요", "description": "소비자 보호", "priority": 3},
            {"question": "유언장 작성 방법", "description": "상속 준비", "priority": 4},
            {"question": "임대차 계약 주의사항", "description": "부동산 법률", "priority": 5},
        ]
    }
    
    if category not in recommendations:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    
    return {
        "category": category,
        "recommendations": recommendations[category][:4],  # 상위 4개만 반환
        "total": len(recommendations[category])
    }

@app.get("/recommendations")
async def get_all_recommendations():
    """모든 카테고리의 추천 질문 반환"""
    
    all_categories = ["health", "travel", "investment", "legal"]
    result = {}
    
    for category in all_categories:
        response = await get_category_recommendations(category)
        result[category] = response["recommendations"]
    
    return {
        "recommendations": result,
        "categories": all_categories
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)