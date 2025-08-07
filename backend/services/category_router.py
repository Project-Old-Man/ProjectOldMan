import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class CategoryRouter:
    def __init__(self):
        self.keywords = {
            "health": [
                "건강", "병원", "의사", "치료", "약", "증상", "아픔", "아프", "진료", "검진",
                "혈압", "당뇨", "콜레스테롤", "운동", "다이어트", "영양", "비타민", "감기",
                "두통", "복통", "발열", "기침", "몸살", "피로", "스트레스", "수면", "불면증"
            ],
            "travel": [
                "여행", "관광", "휴가", "여행지", "숙박", "호텔", "펜션", "항공", "기차", "버스",
                "제주도", "부산", "경주", "강릉", "전주", "해외여행", "국내여행", "패키지", 
                "자유여행", "맛집", "카페", "박물관", "놀이공원", "해변", "산", "등산"
            ],
            "investment": [
                "투자", "주식", "펀드", "적금", "예금", "부동산", "재테크", "금융", "은행",
                "수익", "손실", "배당", "이자", "대출", "보험", "연금", "퇴직", "노후",
                "세금", "절세", "ISA", "IRP", "연말정산", "cryptocurrency", "비트코인"
            ],
            "legal": [
                "법률", "변호사", "소송", "계약", "상속", "유언", "이혼", "재산분할", "양육비",
                "임대차", "전세", "월세", "부동산계약", "매매", "사기", "피해", "손해배상",
                "교통사고", "의료사고", "노동", "해고", "퇴직금", "임금", "근로계약"
            ]
        }
        
        logger.info("🏷️ Category Router 초기화 완료")
        logger.info(f"📝 카테고리별 키워드 수: {[(cat, len(keywords)) for cat, keywords in self.keywords.items()]}")
    
    async def classify_category(self, text: str) -> str:
        """텍스트 카테고리 분류"""
        text_lower = text.lower()
        scores = {}
        
        # 각 카테고리별 점수 계산
        for category, keywords in self.keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            scores[category] = score
        
        # 가장 높은 점수의 카테고리 반환
        if scores:
            best_category = max(scores, key=scores.get)
            if scores[best_category] > 0:
                logger.info(f"🎯 카테고리 분류: '{text[:30]}...' → {best_category} (점수: {scores[best_category]})")
                return best_category
        
        # 기본값
        logger.info(f"🎯 카테고리 분류: '{text[:30]}...' → health (기본값)")
        return "health"
