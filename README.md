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
├── frontend/                    # 프론트엔드 (Nginx 정적 서버)
│   ├── index.html              # 메인 HTML
│   ├── app.js                  # 주요 JS 로직 (카테고리, 채팅, API 통신 등)
│   ├── styles.css              # 스타일
│   ├── nginx.conf              # Nginx 설정
│   ├── components/             # UI 컴포넌트 HTML
│   └── images/                 # 노리 캐릭터 등 이미지
│   └── Dockerfile              # 프론트엔드용 Dockerfile
├── backend/                     # 백엔드 (FastAPI)
│   ├── main.py                 # FastAPI 진입점
│   ├── requirements.txt        # Python 패키지 목록
│   ├── routers/                # API 라우터
│   │   └── chat.py             # /api/chat 엔드포인트
│   ├── services/               # 핵심 서비스 로직
│   │   ├── rag_pipeline.py     # 전체 RAG 파이프라인
│   │   ├── category_router.py  # 카테고리 분류
│   │   ├── embedding.py        # 임베딩 처리
│   │   └── llm_manager.py      # LLM 관리 및 응답 생성
│   ├── vector_db/              # 카테고리별 FAISS 벡터 DB
│   ├── prompts/                # 카테고리별 프롬프트 템플릿
│   └── models/                 # GGUF LLM 모델 파일
├── Dockerfile                  # 백엔드용 Dockerfile
├── prometheus.yml              # 모니터링 설정
├── test_compatibility.py       # 환경 호환성 테스트
└── README.md                   # 문서
```

---

## 2. 작동 방식 (End-to-End)

### 프론트엔드 (frontend/)
- **index.html**: SPA 구조, 주요 UI 영역 분할
- **app.js**:  
  - 컴포넌트 동적 로딩 (header/sidebar/chat)
  - 카테고리/탭 전환, 추천 질문, 채팅 내역 관리
  - 백엔드 API(`/api/chat`, `/api/model-info`, `/health`)와 통신
  - 채팅 입력 → 백엔드로 POST → 응답 표시
- **Nginx**: 정적 파일 서빙, Docker로 배포

### 백엔드 (backend/)
- **main.py**: FastAPI 앱, 라우터 등록, CORS 등 설정
- **routers/chat.py**:  
  - `/api/chat` POST 요청 처리
  - 입력: {message, category, user_id}
  - 출력: {response, category}
- **services/rag_pipeline.py**:  
  - 카테고리 분류 → 임베딩 → 벡터 검색 → 프롬프트 조합 → LLM 호출
- **services/embedding.py**:  
  - sentence-transformers로 텍스트 임베딩
  - FAISS 벡터 DB와 연동
- **services/llm_manager.py**:  
  - llama-cpp-python으로 GGUF LLM 로딩 및 응답 생성
  - Mock 모드 지원 (모델 미로딩 시)
- **vector_db/**:  
  - 카테고리별 FAISS 인덱스 관리
- **prompts/**:  
  - 카테고리별 시스템 프롬프트 템플릿

### Docker
- **Dockerfile (백엔드)**:  
  - Python 3.10, numpy 1.x, faiss, llama-cpp-python(소스 빌드), 기타 의존성 고정
  - 모델 파일은 `/backend/models/`에 위치
- **Dockerfile (프론트엔드)**:  
  - nginx:alpine 기반, 정적 파일 복사, curl/헬스체크 추가

---

## 3. 현재 상태 및 동작 확인

- **모든 주요 패키지(NumPy, FAISS, tokenizers 등) 호환성 문제 해결됨**
- **임베딩, 벡터스토어, LLM 모두 정상 로딩 및 동작**
- **프론트엔드/백엔드 Docker 컨테이너 정상 기동**
- **/health, /api/chat 등 API 정상 응답**
- **프론트엔드에서 채팅, 추천질문, 카테고리 전환 등 UI 정상 동작**

---

## 4. 추가로 수정/개선해야 할 점

### (1) 모델/임베딩/FAISS 등 버전 호환성
- Dockerfile에서 numpy/scipy/faiss 등 버전 고정은 잘 되어 있음
- 추후 sentence-transformers, transformers, tokenizers 등 업그레이드시 호환성 재확인 필요

### (2) LLM 모델 교체/추가
- `backend/services/llm_manager.py`의 MODEL_PATH/MODEL_NAME을 바꿔서 다른 GGUF 모델 사용 가능
- 여러 모델 지원하려면 모델 선택 API/로직 추가 가능

### (3) 프론트엔드 개선
- 모바일 최적화, 접근성(키보드 네비, 고대비 등) 추가 개발 필요
- 사용자 인증/대화 저장 등 기능 추가 예정

### (4) 데이터/프롬프트 확장
- prompts/ 및 vector_db/에 실제 데이터/프롬프트 추가 필요
- 카테고리별 샘플 데이터 확장

### (5) 운영/배포
- HTTPS, 도메인, 프록시 등 운영환경 배포시 추가 설정 필요
- prometheus.yml 등 모니터링 연동 필요시 설정

### (6) 기타
- 테스트 코드(test_compatibility.py) 확장
- 에러 핸들링/로깅 강화
- API 문서 자동화(Swagger 등) 활용

---

## 5. 결론

- **현재 구조는 RAG+LLM 기반 챗봇 서비스로 잘 설계되어 있음**
- **실제 서비스/운영을 위해서는 데이터, 프롬프트, UI/UX, 인증, 배포 등 추가 개발 필요**
- **패키지 버전 호환성(특히 numpy, faiss, tokenizers 등)은 계속 주의 필요**

**특정 기능 추가/수정이 필요하면 구체적으로 요청해 주세요!**