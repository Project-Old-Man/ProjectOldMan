import re
from typing import Dict

class CategoryRouter:
    def __init__(self):
        self.category_keywords = {
            "health": [
                "건강", "병원", "의사", "약", "치료", "진료", "질병", "증상", "혈압", "당뇨", 
                "운동", "다이어트", "식단", "영양", "건강검진", "콜레스테롤", "스트레스"
            ],
            "travel": [
                "여행", "관광", "휴가", "호텔", "숙박", "항공", "기차", "버스", "맛집", 
                "관광지", "여행지", "코스", "일정", "예약", "패키지"
            ],
            "investment": [
                "투자", "주식", "펀드", "부동산", "적금", "예금", "금융", "은행", "연금", 
                "재테크", "자산", "수익", "손실", "리스크", "포트폴리오", "ETF"
            ],
            "legal": [
                "법률", "변호사", "소송", "계약", "상속", "이혼", "사기", "법적", "권리", 
                "의무", "법원", "판결", "상담", "법무", "계약서", "유언장"
            ]
        }
    
    def classify(self, text: str) -> str:
        """Classify text into categories based on keywords"""
        text_lower = text.lower()
        scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            scores[category] = score
        
        # Return category with highest score, default to health
        if max(scores.values()) == 0:
            return "health"
        
        return max(scores, key=scores.get)
