# AI 놀이터 - 중장년층 커뮤니티

AI 기술을 쉽고 재미있게 배울 수 있는 중장년층을 위한 웹 애플리케이션입니다.

## 🚀 주요 기능

- **카테고리별 AI 상담**: 건강, 여행, 투자, 법률 분야 전문 AI 챗봇
- **추천 질문 시스템**: 각 카테고리별 맞춤 질문 제공
- **대화 히스토리**: 이전 대화 내용 확인 및 재사용
- **컴포넌트 기반 구조**: 모듈화된 프론트엔드 아키텍처
- **반응형 디자인**: 중장년층 친화적 큰 글씨와 직관적 UI
- **RAG 시스템**: 카테고리별 벡터 검색과 LLM 응답 생성

## 🏗️ 기술 스택

### 프론트엔드
- **순수 HTML/CSS/JavaScript**: 컴포넌트 기반 구조
- **Tailwind CSS**: 유틸리티 우선 CSS 프레임워크
- **커스텀 폰트**: Noto Sans KR, Gaegu 폰트 적용
- **노리 캐릭터**: 각 카테고리별 맞춤 캐릭터 이미지

### 백엔드
- **FastAPI**: Python 웹 프레임워크 (포트 9000)
- **RAG 파이프라인**: 카테고리별 전문 AI 응답 시스템
- **sentence-transformers**: MiniLM-L6-v2 임베딩 모델
- **FAISS**: 카테고리별 벡터 데이터베이스
- **llama-cpp**: 로컬 LLM 모델 (TinyLlama, GGUF)
- **RESTful API**: 표준 HTTP API 구조

## 📁 전체 파일 구조

```
ProjectOldMan/
├── frontend/                    # 프론트엔드 애플리케이션
│   ├── index.html              # 메인 HTML 파일 (레이아웃 구조)
│   ├── app.js                  # 메인 JavaScript 로직
│   ├── styles.css              # 전체 스타일 정의
│   ├── nginx.conf              # Nginx 설정 파일
│   ├── components/             # 컴포넌트 HTML 파일들
│   │   ├── header.html         # 상단 헤더 컴포넌트
│   │   ├── sidebar.html        # 왼쪽 사이드바 컴포넌트
│   │   ├── chat.html           # 채팅 영역 컴포넌트
│   │   ├── portfolio-overview.tsx  # 투자 포트폴리오 대시보드
│   │   └── ai-playground.tsx   # AI 실험실 컴포넌트
│   └── images/                 # 노리 캐릭터 이미지들
│       ├── nori.png           # 기본 노리 이미지
│       ├── nori-health.png    # 건강 상담 노리
│       ├── nori-travel.png    # 여행 상담 노리
│       ├── nori-investment.png # 투자 상담 노리
│       └── nori-legal.png     # 법률 상담 노리
├── backend/                     # FastAPI 백엔드
│   ├── main.py                 # FastAPI 애플리케이션 진입점
│   ├── requirements.txt        # Python 의존성 패키지
│   ├── routers/               # API 엔드포인트 라우팅
│   │   ├── __init__.py
│   │   └── chat.py            # /api/chat 엔드포인트
│   ├── services/              # 비즈니스 로직 서비스
│   │   ├── __init__.py
│   │   ├── rag_pipeline.py    # 전체 RAG 워크플로우
│   │   ├── category_router.py # 카테고리 분류 로직
│   │   ├── embedding.py       # 텍스트 임베딩 처리
│   │   └── llm_manager.py     # LLM 호출 및 응답 생성
│   ├── vector_db/             # FAISS 벡터 데이터베이스
│   │   ├── __init__.py
│   │   ├── health.py          # 건강 분야 벡터 검색
│   │   ├── travel.py          # 여행 분야 벡터 검색
│   │   ├── finance.py         # 투자 분야 벡터 검색
│   │   └── legal.py           # 법률 분야 벡터 검색
│   ├── prompts/               # 카테고리별 시스템 프롬프트
│   │   ├── health.txt         # 건강 프롬프트 템플릿
│   │   ├── travel.txt         # 여행 프롬프트 템플릿
│   │   ├── finance.txt        # 투자 프롬프트 템플릿
│   │   └── legal.txt          # 법률 프롬프트 템플릿
│   └── models/                # 로컬 LLM 모델 파일
│       └── tinyllama.gguf     # 로컬 LLM 모델 파일
├── prometheus.yml              # 모니터링 설정
├── test_compatibility.py       # 시스템 호환성 테스트 스크립트
├── Dockerfile                  # 백엔드 Docker 설정
└── README.md                   # 프로젝트 문서 (현재 파일)
```

## 🔄 End-to-End 데이터 플로우

### 1. 프론트엔드에서 백엔드로 요청
```javascript
// app.js에서 메시지 전송
const response = await fetch('http://localhost:9000/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: "혈압 관리 방법 알려주세요",
        category: "health",
        user_id: "user_123"
    })
});
```

### 2. 백엔드 RAG 파이프라인 처리
```
사용자 메시지 → FastAPI (/api/chat)
    ↓
1. category_router.py (카테고리 분류: health/travel/finance/legal)
    ↓
2. embedding.py (MiniLM-L6-v2로 텍스트 벡터화)
    ↓
3. vector_db/{category}.py (FAISS에서 관련 문서 검색)
    ↓
4. prompts/{category}.txt (시스템 프롬프트 로드)
    ↓
5. llm_manager.py (TinyLlama로 응답 생성)
    ↓
프론트엔드로 응답 반환
```

### 3. 응답 데이터 구조
```json
{
    "response": "혈압 관리를 위해서는...",
    "category": "health"
}
```

## 🎯 각 폴더/파일 상세 설명

### 🖥️ **프론트엔드 (frontend/)**

#### 📄 **메인 파일들**
- **`index.html`**: 기본 채팅 인터페이스, 백엔드 API 호출 기능
- **`app.js`**: 
  - 컴포넌트 동적 로딩 시스템
  - 카테고리 전환 및 상태 관리
  - `/api/chat` 엔드포인트 통신
  - 추천 질문 시스템 구현
- **`styles.css`**: 중장년층 친화적 디자인 (18px+ 큰 글씨, 노리 아이콘)

#### 📂 **컴포넌트들**
- **`header.html`**: 로고, 배너 버튼, 검색, 프로필
- **`sidebar.html`**: 3개 탭(카테고리/히스토리/추천), 4개 카테고리, 하단 메뉴
- **`chat.html`**: 채팅 헤더, 메시지 컨테이너, 입력 영역

### ⚙️ **백엔드 (backend/)**

#### 🚀 **메인 애플리케이션**
- **`main.py`**: FastAPI 앱, CORS 설정, 라우터 등록 (포트 9000)

#### 🛣️ **API 라우팅**
- **`routers/chat.py`**: 
  - `POST /api/chat` 엔드포인트
  - 요청: `{message, category?, user_id?}`
  - 응답: `{response, category}`

#### ⚙️ **핵심 서비스들**
- **`services/rag_pipeline.py`**: 
  - 전체 RAG 워크플로우 조합
  - 카테고리 분류 → 임베딩 → 벡터 검색 → 프롬프트 조합 → LLM 호출

- **`services/category_router.py`**: 
  - 키워드 기반 텍스트 분류
  - 4개 카테고리 (health/travel/finance/legal) 중 선택

- **`services/embedding.py`**: 
  - sentence-transformers (MiniLM-L6-v2)
  - Mock 모드 지원 (테스트용)

- **`services/llm_manager.py`**: 
  - llama-cpp 기반 GGUF 모델 로딩
  - 비동기 텍스트 생성

#### 🗄️ **벡터 데이터베이스**
- **`vector_db/`**: 각 카테고리별 FAISS 인덱스
  - 384차원 벡터 (MiniLM-L6-v2 호환)
  - 유사도 검색 (top_k=3)
  - 인덱스 파일 없어도 graceful 처리

#### 📝 **프롬프트 템플릿**
- **`prompts/`**: 카테고리별 시스템 프롬프트
  - 각 분야 전문가 페르소나 정의
  - 안전한 정보 제공 가이드라인

## 📋 설치 및 실행

### 백엔드 실행
```bash
# 백엔드 디렉토리로 이동
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python main.py
# 또는
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

### 프론트엔드 실행
```bash
# 프론트엔드 디렉토리로 이동
cd frontend

# Python 정적 서버로 실행
python -m http.server 3000

# 또는 다른 정적 서버 사용
npx serve . -p 3000

# 또는 Nginx 사용
nginx -c $(pwd)/nginx.conf
```

### Docker 실행
```bash
# 백엔드 Docker 빌드 및 실행
docker build -t projectoldman-backend .
docker run -p 9000:9000 projectoldman-backend
```

## 🌐 접속 방법

- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:9000
- **API 문서**: http://localhost:9000/docs
- **헬스체크**: http://localhost:9000/health

## 🔧 API 사용 예시

### 채팅 요청
```bash
curl -X POST "http://localhost:9000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "혈압 관리 방법 알려주세요"
  }'
```

### 응답 예시
```json
{
  "response": "혈압 관리를 위해서는 규칙적인 운동, 저염식 식단, 스트레스 관리가 중요합니다...",
  "category": "health"
}
```

## 🎨 UI/UX 특징

### 중장년층 친화적 디자인
- **큰 글씨**: 18px 기본 폰트 크기
- **명확한 버튼**: 패딩과 간격 충분히 확보
- **직관적 아이콘**: 노리 캐릭터로 친근감 조성
- **부드러운 색상**: 황금색 계열 메인 컬러

### 접근성 고려사항
- 고대비 색상 조합
- 큰 클릭 영역
- 명확한 시각적 피드백
- 키보드 네비게이션 지원

## 🔄 개발 현황

### ✅ 완료된 기능
- 기본 레이아웃 구조
- 컴포넌트 시스템
- 카테고리 전환
- 추천 질문 시스템
- 반응형 디자인
- 노리 캐릭터 시스템
- **FastAPI 백엔드 구조**
- **RAG 파이프라인**
- **카테고리별 벡터 검색**
- **LLM 통합**
- **End-to-End API 통신**

### 🔲 개발 예정 기능
- 벡터 데이터베이스 데이터 채우기
- 실제 LLM 모델 배포
- 사용자 인증
- 대화 내역 저장
- 모바일 최적화
- 성능 최적화

## 🧪 테스트

### 호환성 테스트
```bash
python test_compatibility.py
```

### API 테스트
```bash
# 헬스체크
curl http://localhost:9000/health

# 채팅 테스트
curl -X POST http://localhost:9000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요"}'
```

## 🤝 기여하기

1. 이슈 생성 또는 기능 요청
2. Fork & Clone
3. 기능 개발 & 테스트
4. Pull Request 생성

## 📞 지원

문의사항이나 버그 리포트는 GitHub Issues를 이용해주세요.

## 🔧 트러블슈팅

### 백엔드 연결 오류
- 백엔드 서버가 포트 9000에서 실행 중인지 확인
- CORS 설정이 올바른지 확인
- 방화벽 설정 확인

### 의존성 설치 오류
- Python 3.8+ 버전 사용 확인
- 가상환경 활성화 확인
- requirements.txt 파일 존재 확인

### LLM 모델 로딩 오류
- models/ 디렉토리에 tinyllama.gguf 파일 존재 확인
- 충분한 메모리 (4GB+) 확인
- Mock 모드로 테스트 가능