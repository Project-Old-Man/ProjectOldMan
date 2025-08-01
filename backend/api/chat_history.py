from fastapi import APIRouter
from typing import List

router = APIRouter()

@router.get("/chat-history", response_model=List[dict])
async def get_chat_history():
    # 예제 데이터
    return [
        {"title": "운동 추천", "content": "운동 자세를 추천받았습니다.", "timestamp": "2024-01-01 10:00:00"},
        {"title": "여행 계획", "content": "서울 근교 여행지를 추천받았습니다.", "timestamp": "2024-01-02 14:30:00"},
        {"title": "투자 상담", "content": "ETF 투자에 대한 조언을 받았습니다.", "timestamp": "2024-01-03 09:15:00"},
    ]
