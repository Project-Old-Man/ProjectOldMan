# AI 놀이터 - 중장년층 커뮤니티

AI 기술을 쉽고 재미있게 배울 수 있는 중장년층을 위한 웹 애플리케이션입니다.

## 🚀 주요 기능

- **AI 챗봇**: 질문에 대한 실시간 답변
- **카테고리별 정보**: 건강, 여행, 투자, 법률 정보 제공
- **커뮤니티**: 사용자 간 소통 공간
- **반응형 디자인**: 모바일 친화적 인터페이스

## 🏗️ 기술 스택

### 백엔드
- **FastAPI**: Python 웹 프레임워크
- **PostgreSQL**: 메인 데이터베이스
- **FAISS**: 벡터 데이터베이스 (로컬)
- **HuggingFace Transformers**: LLM 및 임베딩 모델
- **Sentence Transformers**: 텍스트 임베딩

### 프론트엔드
- **HTML5/CSS3/JavaScript**: 순수 웹 기술
- **Nginx**: 정적 파일 서빙

## 📦 설치 및 실행

### 1. Docker Compose로 전체 시스템 실행 (권장)

```bash
git clone <repository-url>
cd ProjectOldMan

cp env.example .env
# .env 파일을 편집하여 필요한 설정 추가

# (최초 1회) 여행 문서 임베딩
cd backend/vector
python embed_travel_docs.py
cd ../..

docker-compose up -d --build
docker-compose ps
```

### 2. 개별 서비스 실행

#### 백엔드 실행
```bash
cd backend

pip install -r requirements.txt

# (최초 1회) 여행 문서 임베딩
python vector/embed_travel_docs.py

uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 프론트엔드 실행
```bash
cd frontend
python -m http.server 8080
```

## 🌐 접속 방법

- **프론트엔드**: http://localhost:3000 (또는 8080)
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

## 🔧 주요 API 엔드포인트

- `POST /query`: 질의응답 처리
- `POST /query/stream`: 스트리밍 질의응답
- `POST /recommend`: 추천 시스템
- `POST /feedback`: 피드백 제출
- `GET /analytics/stats`: 시스템 통계
- `GET /health`: 서버 상태 확인

## 📁 프로젝트 구조

```
ProjectOldMan/
├── backend/
│   ├── api/                # FastAPI 엔드포인트
│   │   └── main.py
│   ├── db/                 # 데이터베이스 관련
│   │   ├── database.py
│   │   └── data_utils.py
│   ├── llm/                # LLM 및 프롬프트
│   │   ├── llm_service.py
│   │   ├── model_manager.py
│   │   └── prompt_manager.py
│   ├── vector/             # 벡터DB 및 임베딩
│   │   ├── vector_db.py
│   │   └── embed_travel_docs.py
│   ├── scripts/            # 배포/유틸리티 스크립트
│   │   └── deployment_scripts.sh
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   └── Dockerfile
├── model/
│   ├── models.json
│   ├── README.md
│   └── .gitkeep
├── doc/
│   ├── QUICK_START.md
│   └── ... (기타 문서)
├── test_compatibility.py
├── docker-compose.yml
├── env.example
├── .gitignore
└── README.md
```

## 🔄 최근 업데이트

- 추천 시스템 개선: 사용자 히스토리를 기반으로 개인화된 추천 제공
- 프론트엔드 UI 개선: 추천 결과 표시 기능 추가
- 모델 관리 기능 강화: 로드된 모델 및 사용 가능한 모델 목록 조회

## 🐛 문제 해결

- 포트 충돌, DB 연결, 모델 다운로드, CORS 등은 doc/QUICK_START.md 참고

## 📝 개발 가이드

- 새로운 기능은 backend/api, backend/llm, backend/vector 등에서 구현
- 프론트엔드 UI는 frontend/index.html에서 수정
- 문서 임베딩은 backend/vector/embed_travel_docs.py로 관리

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

MIT License

## 📞 지원

이슈를 생성해 문의해주세요.