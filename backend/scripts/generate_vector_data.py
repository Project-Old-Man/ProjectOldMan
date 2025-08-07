#!/usr/bin/env python3
"""
카테고리별 벡터 데이터 생성 스크립트
"""

import os
import sys
import yaml
import json
import logging
from pathlib import Path

# 백엔드 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from services.embedding import EmbeddingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 카테고리별 샘플 데이터
SAMPLE_DATA = {
    "health": [
        {"text": "혈압 관리를 위해서는 규칙적인 운동과 저염식 식단이 중요합니다.", "category": "health", "tags": ["혈압", "운동", "식단"]},
        {"text": "당뇨병 예방을 위해 체중 관리와 정기적인 검진이 필요합니다.", "category": "health", "tags": ["당뇨", "체중", "검진"]},
        {"text": "골다공증 예방을 위해 칼슘과 비타민D 섭취가 중요합니다.", "category": "health", "tags": ["골다공증", "칼슘", "비타민D"]},
        {"text": "콜레스테롤 관리를 위해 포화지방 섭취를 줄이고 오메가3를 섭취하세요.", "category": "health", "tags": ["콜레스테롤", "포화지방", "오메가3"]},
        {"text": "스트레스 관리를 위해 명상과 적절한 휴식이 필요합니다.", "category": "health", "tags": ["스트레스", "명상", "휴식"]},
    ],
    "travel": [
        {"text": "제주도 여행 시 한라산 등반과 성산일출봉 관람을 추천합니다.", "category": "travel", "tags": ["제주도", "한라산", "성산일출봉"]},
        {"text": "부산 여행에서는 해운대 해수욕장과 감천문화마을을 방문하세요.", "category": "travel", "tags": ["부산", "해운대", "감천문화마을"]},
        {"text": "경주 여행에서는 불국사와 석굴암 등 역사 유적지를 탐방하세요.", "category": "travel", "tags": ["경주", "불국사", "석굴암"]},
        {"text": "여행 시 여행자 보험 가입과 응급약품 준비가 필요합니다.", "category": "travel", "tags": ["여행자보험", "응급약품", "준비"]},
        {"text": "온천 여행지로는 부곡온천과 유성온천이 유명합니다.", "category": "travel", "tags": ["온천", "부곡온천", "유성온천"]},
    ],
    "investment": [
        {"text": "안전한 투자를 위해 국채와 예금을 기본으로 하세요.", "category": "investment", "tags": ["안전투자", "국채", "예금"]},
        {"text": "연금 준비를 위해 개인연금과 퇴직연금을 활용하세요.", "category": "investment", "tags": ["연금", "개인연금", "퇴직연금"]},
        {"text": "부동산 투자 시 입지와 시설, 교통편을 종합적으로 고려하세요.", "category": "investment", "tags": ["부동산", "입지", "교통"]},
        {"text": "펀드 투자 시 위험도와 수수료를 반드시 확인하세요.", "category": "investment", "tags": ["펀드", "위험도", "수수료"]},
        {"text": "ISA 계좌를 활용하면 세제 혜택을 받을 수 있습니다.", "category": "investment", "tags": ["ISA", "세제혜택", "계좌"]},
    ],
    "legal": [
        {"text": "계약서 작성 시 조건과 책임 사항을 명확히 기재하세요.", "category": "legal", "tags": ["계약서", "조건", "책임"]},
        {"text": "상속 준비를 위해 유언장과 재산 목록을 작성하세요.", "category": "legal", "tags": ["상속", "유언장", "재산목록"]},
        {"text": "사기 예방을 위해 의심스러운 투자 제안을 피하세요.", "category": "legal", "tags": ["사기예방", "투자제안", "주의"]},
        {"text": "임대차 계약 시 보증금과 월세, 계약 기간을 명확히 하세요.", "category": "legal", "tags": ["임대차", "보증금", "월세"]},
        {"text": "소비자 분쟁 발생 시 소비자분쟁조정위원회에 신청하세요.", "category": "legal", "tags": ["소비자분쟁", "조정위원회", "신청"]},
    ]
}

def main():
    """벡터 데이터 생성 메인 함수"""
    logger.info("🚀 벡터 데이터 생성 시작")
    
    # 임베딩 서비스 초기화
    try:
        embedding_service = EmbeddingService()
        status = embedding_service.get_status()
        logger.info(f"📊 임베딩 서비스 상태: {status}")
    except Exception as e:
        logger.error(f"❌ 임베딩 서비스 초기화 실패: {e}")
        return
    
    # 벡터 데이터 디렉토리 생성
    vector_data_dir = Path(__file__).parent.parent / "vector_data"
    vector_data_dir.mkdir(exist_ok=True)
    
    # 카테고리별 벡터 데이터 생성
    for category, documents in SAMPLE_DATA.items():
        logger.info(f"📂 {category} 카테고리 처리 중...")
        
        # 텍스트 추출
        texts = [doc["text"] for doc in documents]
        
        # 임베딩 생성
        try:
            embeddings = embedding_service.encode(texts)
            logger.info(f"✅ {category}: {len(embeddings)}개 임베딩 생성 완료")
        except Exception as e:
            logger.error(f"❌ {category} 임베딩 생성 실패: {e}")
            continue
        
        # 데이터 저장
        category_data = []
        for i, doc in enumerate(documents):
            category_data.append({
                "id": f"{category}_{i+1:03d}",
                "text": doc["text"],
                "category": doc["category"],
                "tags": doc["tags"],
                "embedding": embeddings[i],
                "embedding_dim": len(embeddings[i])
            })
        
        # JSON 파일로 저장
        output_file = vector_data_dir / f"{category}_vectors.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(category_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 {category} 데이터 저장: {output_file}")
        
        # YAML 메타데이터 저장
        metadata = {
            "category": category,
            "document_count": len(documents),
            "embedding_model": embedding_service.model_name,
            "embedding_dim": embedding_service.get_embedding_dim(),
            "using_real_model": embedding_service.is_using_real_model(),
            "tags": list(set(tag for doc in documents for tag in doc["tags"]))
        }
        
        meta_file = vector_data_dir / f"{category}_metadata.yaml"
        with open(meta_file, 'w', encoding='utf-8') as f:
            yaml.dump(metadata, f, allow_unicode=True, default_flow_style=False)
        
        logger.info(f"📋 {category} 메타데이터 저장: {meta_file}")
    
    logger.info("🎉 벡터 데이터 생성 완료!")
    logger.info(f"📁 저장 위치: {vector_data_dir}")

if __name__ == "__main__":
    main()
