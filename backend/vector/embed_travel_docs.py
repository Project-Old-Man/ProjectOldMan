from vector_db import VectorDBManager

docs = [
    {"content": "경주는 신라의 고도이며 불국사, 석굴암 등 유적지가 많다.", "title": "경주 여행", "category": "travel"},
    {"content": "제주도는 자연 경관이 아름답고 부모님과 함께 여행하기 좋다.", "title": "제주도 여행", "category": "travel"},
    {"content": "부산 해운대는 바다와 도심이 어우러진 대표 여행지입니다.", "title": "부산 해운대", "category": "travel"},
    {"content": "설악산은 등산과 단풍으로 유명하며 가을 여행지로 추천된다.", "title": "설악산", "category": "travel"},
    {"content": "전주 한옥마을은 전통과 현대가 공존하는 인기 여행지입니다.", "title": "전주 한옥마을", "category": "travel"},
    {"content": "서울은 한국의 수도로, 경복궁과 같은 역사적인 장소가 많다.", "title": "서울 여행", "category": "travel"},
    {"content": "강릉은 해변과 커피 거리로 유명하며 여름 여행지로 추천된다.", "title": "강릉 여행", "category": "travel"},
    {"content": "건강한 식단은 신선한 채소와 과일을 포함해야 한다.", "title": "건강한 식단", "category": "health"},
    {"content": "운동은 매일 30분 이상 걷기부터 시작하는 것이 좋다.", "title": "운동 추천", "category": "health"},
    {"content": "ETF는 분산 투자에 적합하며 초보 투자자에게 추천된다.", "title": "ETF 투자", "category": "investment"},
    # ...필요시 더 추가...
]

if __name__ == "__main__":
    db = VectorDBManager()
    db.bulk_add_documents(docs)
    print("여행 문서 임베딩 및 저장 완료")
