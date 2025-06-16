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
- **Weaviate**: 벡터 데이터베이스
- **vLLM**: 대규모 언어 모델 추론
- **Sentence Transformers**: 텍스트 임베딩

### 프론트엔드
- **HTML5/CSS3/JavaScript**: 순수 웹 기술
- **Nginx**: 정적 파일 서빙

## 📦 설치 및 실행

### 1. Docker Compose로 전체 시스템 실행 (권장)

```bash
# 저장소 클론
git clone <repository-url>
cd ProjectOldMan

# 환경 변수 설정 (선택사항)
cp env.example .env
# .env 파일을 편집하여 필요한 설정 추가

# Docker Compose로 실행
docker-compose up -d

# 서비스 상태 확인
docker-compose ps
```

### 2. 개별 서비스 실행

#### 백엔드 실행
```bash
cd backend

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export DATABASE_URL="postgresql://username:password@localhost:5432/database_name"
export WEAVIATE_URL="http://localhost:8080"

# 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 프론트엔드 실행
```bash
cd frontend

# Nginx로 서빙 (Docker 사용)
docker build -t ai-playground-frontend .
docker run -p 80:80 ai-playground-frontend

# 또는 Python HTTP 서버 사용
python -m http.server 80
```

## 🌐 접속 방법

- **프론트엔드**: http://localhost
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Weaviate**: http://localhost:8080

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
├── backend/                 # FastAPI 백엔드
│   ├── main.py             # 메인 애플리케이션
│   ├── database.py         # 데이터베이스 관리
│   ├── vector_db.py        # 벡터 데이터베이스
│   ├── llm_service.py      # LLM 서비스
│   ├── prompt_manager.py   # 프롬프트 관리
│   ├── requirements.txt    # Python 의존성
│   └── Dockerfile         # 백엔드 Docker 설정
├── frontend/               # 웹 프론트엔드
│   ├── index.html         # 메인 HTML 파일
│   └── Dockerfile         # 프론트엔드 Docker 설정
├── model/                  # AI 모델 파일들
├── docker-compose.yml     # 전체 시스템 Docker 설정
├── env.example            # 환경 변수 예시
└── README.md              # 프로젝트 문서
```

## 🔄 최근 업데이트

### 수정된 주요 사항:
1. **의존성 파일명 수정**: `requirements_txt.txt` → `requirements.txt`
2. **백엔드 Dockerfile 추가**: Python 3.11 기반 컨테이너
3. **Docker Compose 설정**: 전체 시스템 통합 실행
4. **프론트엔드-백엔드 연결**: API 호출 기능 구현
5. **환경 변수 설정**: `.env` 파일 지원

## 🐛 문제 해결

### 일반적인 문제들:

1. **포트 충돌**
   ```bash
   # 사용 중인 포트 확인
   lsof -i :8000
   lsof -i :80
   ```

2. **데이터베이스 연결 실패**
   ```bash
   # PostgreSQL 상태 확인
   docker-compose logs postgres
   ```

3. **Weaviate 연결 실패**
   ```bash
   # Weaviate 상태 확인
   curl http://localhost:8080/v1/.well-known/ready
   ```

4. **CORS 오류**
   - 백엔드 CORS 설정이 올바른지 확인
   - 프론트엔드에서 올바른 백엔드 URL 사용

## 📝 개발 가이드

### 새로운 기능 추가:
1. 백엔드 API 엔드포인트 추가 (`backend/main.py`)
2. 프론트엔드 UI 수정 (`frontend/index.html`)
3. 필요한 경우 데이터베이스 스키마 업데이트

### 테스트:
```bash
# 백엔드 테스트
cd backend
pytest

# API 테스트
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "안녕하세요"}'
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해주세요.