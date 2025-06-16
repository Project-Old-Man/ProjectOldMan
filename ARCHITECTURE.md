# 🏗️ AI 놀이터 시스템 아키텍처

## 🎯 **전체 시스템 개요**

AI 놀이터는 **완전한 AI 웹 애플리케이션**으로, 사용자 질문을 받아 AI 모델이 실시간으로 답변하는 시스템입니다.

```
👤 사용자 → 🎨 프론트엔드 → 🖥️ 백엔드 → 🤖 AI 모델
                ↓              ↓              ↓
            📱 웹 브라우저   🔍 벡터 검색   💾 데이터 저장
```

---

## 🔄 **데이터 흐름 (완전한 파이프라인)**

### **1단계: 사용자 입력**
```
사용자가 "건강에 대해 궁금해요" 입력
    ↓
프론트엔드에서 API 호출
```

### **2단계: 백엔드 처리**
```
백엔드에서 4단계 처리:
1. 🔍 벡터 검색 → 관련 정보 찾기
2. 📝 프롬프트 생성 → AI용 질문 만들기
3. 🤖 AI 추론 → 모델에서 답변 생성
4. 💾 데이터 저장 → 대화 기록 저장
```

### **3단계: 응답 반환**
```
AI 답변 → 백엔드 → 프론트엔드 → 사용자 화면
```

---

## 🎨 **프론트엔드 (Frontend)**

### **기술 스택**
- **HTML5/CSS3/JavaScript**: 순수 웹 기술
- **반응형 디자인**: 모바일 친화적
- **실시간 통신**: Fetch API 사용

### **주요 기능**
```javascript
// 사용자 입력 처리
async function sendMessage() {
    const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            question: message,        // 사용자 질문
            user_id: 'user_' + Date.now(),
            context: { page: getCurrentPage() }
        })
    });
    
    const data = await response.json();
    addMessage(data.response, 'bot'); // AI 답변 표시
}
```

### **페이지 구조**
- 🏠 **메인 페이지**: AI 놀이터 홈
- 💊 **건강 페이지**: 건강 정보 및 챗봇
- ✈️ **여행 페이지**: 여행 정보 및 챗봇
- 💰 **투자 페이지**: 투자 정보 및 챗봇
- ⚖️ **법률 페이지**: 법률 정보 및 챗봇
- 💬 **챗봇 모달**: 실시간 AI 대화

---

## 🖥️ **백엔드 (Backend)**

### **기술 스택**
- **FastAPI**: Python 웹 프레임워크
- **vLLM**: 대규모 언어 모델 추론
- **Weaviate**: 벡터 데이터베이스
- **PostgreSQL**: 관계형 데이터베이스

### **핵심 컴포넌트**

#### **1. 메인 API 서버 (`main.py`)**
```python
@app.post("/query")
async def process_query(request: QueryRequest):
    # 1. 벡터 검색
    search_results = await vector_db.search(request.question)
    
    # 2. 프롬프트 생성
    prompt = prompt_manager.create_query_prompt(
        question=request.question,
        context=search_results
    )
    
    # 3. AI 모델 추론
    response = await llm_service.generate_response(prompt)
    
    # 4. 데이터베이스 저장
    await db.save_query(request.question, response)
    
    return QueryResponse(response=response)
```

#### **2. AI 모델 서비스 (`llm_service.py`)**
```python
class LLMService:
    async def generate_response(self, prompt: str) -> str:
        if self.engine:  # vLLM 로컬 모델
            return await self._generate_with_vllm(prompt)
        elif self.openai_api_key:  # OpenAI API
            return await self._generate_with_openai(prompt)
        elif self.hf_api_key:  # HuggingFace API
            return await self._generate_with_huggingface(prompt)
```

#### **3. 벡터 검색 (`vector_db.py`)**
```python
class VectorDBManager:
    async def search(self, query: str) -> List[SearchResult]:
        # 쿼리를 벡터로 변환
        query_embedding = self.embedding_model.encode(query)
        
        # Weaviate에서 유사한 문서 검색
        results = self.client.query.get("KnowledgeBase")
            .with_near_vector({"vector": query_embedding})
            .with_limit(5)
            .do()
        
        return results
```

#### **4. 데이터베이스 관리 (`database.py`)**
```python
class DatabaseManager:
    async def save_query(self, question: str, response: str):
        # PostgreSQL에 대화 기록 저장
        await self.pool.execute("""
            INSERT INTO queries (question, response, created_at)
            VALUES ($1, $2, NOW())
        """, question, response)
```

#### **5. 모델 관리 (`model_manager.py`)**
```python
class ModelManager:
    def switch_model(self, model_id: str) -> bool:
        # 도메인별 모델 전환
        if model_id == "health-expert":
            return self._load_health_model()
        elif model_id == "travel-expert":
            return self._load_travel_model()
        # ...
```

---

## 🤖 **AI 모델 시스템**

### **지원하는 모델 타입**

#### **1. 로컬 모델 (vLLM)**
```
model/local/korean-llm/
├── config.json
├── tokenizer.json
├── model.safetensors
└── generation_config.json
```

#### **2. 외부 API**
- **OpenAI**: GPT-3.5, GPT-4
- **HuggingFace**: 다양한 오픈소스 모델

### **도메인별 모델 전환**
```python
# 자동 모델 선택
def get_model_by_domain(domain: str):
    if domain == "health":
        return "health-expert"
    elif domain == "travel":
        return "travel-expert"
    elif domain == "legal":
        return "legal-expert"
    else:
        return "korean-llm"
```

---

## 🔍 **벡터 검색 (RAG 시스템)**

### **검색 과정**
```
사용자 질문: "건강한 운동 방법이 궁금해요"
    ↓
텍스트 임베딩 생성
    ↓
Weaviate에서 유사한 문서 검색
    ↓
관련 컨텍스트 추출
    ↓
AI 모델에 컨텍스트와 함께 전달
    ↓
정확한 답변 생성
```

### **지식 베이스 구조**
```json
{
  "content": "건강한 운동 방법...",
  "title": "운동 가이드",
  "category": "health",
  "source": "health_database",
  "metadata": {
    "author": "의료진",
    "date": "2024-01-01"
  }
}
```

---

## 💾 **데이터 저장 시스템**

### **PostgreSQL 테이블 구조**

#### **1. 쿼리 테이블**
```sql
CREATE TABLE queries (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    question TEXT NOT NULL,
    response TEXT NOT NULL,
    sources JSONB,
    processing_time FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### **2. 피드백 테이블**
```sql
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    query_id INTEGER REFERENCES queries(id),
    user_id VARCHAR(255),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔧 **API 엔드포인트**

### **사용자 API**
- `POST /query` - 질의응답 처리
- `POST /query/stream` - 스트리밍 응답
- `POST /recommend` - 개인화 추천
- `POST /feedback` - 피드백 제출

### **관리자 API**
- `GET /admin/models` - 모델 목록
- `POST /admin/switch-model` - 모델 전환
- `POST /admin/add-model` - 모델 추가
- `DELETE /admin/remove-model/{id}` - 모델 제거

### **분석 API**
- `GET /analytics/stats` - 시스템 통계
- `GET /analytics/model-stats` - 모델 사용 통계

---

## 🚀 **실행 환경**

### **개발 환경**
```bash
# 백엔드
cd backend
python3 -m uvicorn main:app --reload

# 프론트엔드
cd frontend
python3 -m http.server 8080
```

### **Docker 환경**
```bash
# 전체 시스템
docker-compose up -d

# 개별 서비스
docker-compose up backend
docker-compose up frontend
```

---

## 🔄 **실시간 데이터 흐름 예시**

### **시나리오: "여행 추천해주세요"**

```
1. 👤 사용자 입력
   "여행 추천해주세요"
   
2. 🎨 프론트엔드
   fetch('http://localhost:8000/query', {
     question: "여행 추천해주세요",
     context: { page: "travel" }
   })
   
3. 🖥️ 백엔드 처리
   ├── 벡터 검색: 여행 관련 정보 5개 검색
   ├── 프롬프트 생성: "여행 전문가로서 추천해주세요..."
   ├── 모델 전환: travel-expert 모델 선택
   └── AI 추론: 여행 추천 답변 생성
   
4. 💾 데이터 저장
   ├── PostgreSQL: 대화 기록 저장
   └── Weaviate: 새로운 여행 정보 추가
   
5. 🎨 프론트엔드 표시
   "경주 여행을 추천드립니다. 불국사, 석굴암..."
   
6. 👤 사용자 피드백
   "좋은 추천이었어요!" (5점)
```

---

## 🎯 **시스템 특징**

### ✅ **완전한 AI 파이프라인**
- 사용자 입력 → AI 처리 → 응답 생성 → 저장

### ✅ **실시간 처리**
- 스트리밍 응답으로 자연스러운 대화

### ✅ **도메인별 최적화**
- 건강, 여행, 투자, 법률 전문 모델

### ✅ **확장 가능한 구조**
- 새로운 모델과 도메인 쉽게 추가

### ✅ **데이터 기반 학습**
- 사용자 피드백으로 모델 개선

---

## 🔮 **향후 확장 계획**

- **음성 인식**: 음성으로 질문하기
- **이미지 분석**: 사진 기반 질문
- **다국어 지원**: 영어, 일본어 등
- **개인화**: 사용자별 맞춤 답변
- **모바일 앱**: 네이티브 앱 개발

**이 구조로 완전한 AI 웹 애플리케이션이 구축되어 있습니다! 🚀** 