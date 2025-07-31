# 🤖 AI 모델 설정 가이드

## 🎯 **모델 연결 방법 2가지**

### **방법 1: 로컬 모델 파일 사용**
### **방법 2: Colab Pro API 연결**

---

## 📁 **방법 1: 로컬 모델 파일 사용**

### **1단계: 모델 파일 준비**

#### **지원하는 모델 형식**
- ✅ **HuggingFace Transformers**: `.bin`, `.safetensors`
- ✅ **GGUF**: `.gguf` (vLLM 0.3.0+)
- ✅ **AWQ**: `.awq`
- ✅ **GPTQ**: `.gptq`

#### **모델 파일 구조**
```
model/local/my-korean-model/
├── config.json              # 모델 설정
├── tokenizer.json           # 토크나이저
├── tokenizer_config.json    # 토크나이저 설정
├── model.safetensors        # 모델 가중치 (대용량)
├── generation_config.json   # 생성 설정
└── README.md               # 모델 설명
```

### **2단계: 모델 파일 복사**
```bash
# 모델 파일을 model/local/ 디렉토리에 복사
cp -r /path/to/your/model model/local/my-korean-model

# 예시: 한국어 모델
cp -r ~/Downloads/korean-llama-2-7b model/local/korean-llama
```

### **3단계: 모델 설정 추가**
```bash
# model/models.json 파일에 모델 정보 추가
{
  "models": {
    "my-korean-model": {
      "name": "./model/local/my-korean-model",
      "type": "local",
      "description": "내가 만든 한국어 모델",
      "parameters": {
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 0.9
      },
      "supported_tasks": ["text-generation", "chat"],
      "language": "ko",
      "domain": "general"
    }
  }
}
```

### **4단계: 환경 변수 설정**
```bash
# .env 파일에서
LLM_MODEL=./model/local/my-korean-model
```

### **5단계: 서버 재시작**
```bash
# 백엔드 재시작
cd backend
python3 -m uvicorn main:app --reload
```

---

## ☁️ **방법 2: Colab Pro API 연결**

### **1단계: Colab Pro에서 모델 서빙**

#### **Colab 노트북에서 FastAPI 서버 실행**
```python
# Colab 노트북에 다음 코드 작성
!pip install fastapi uvicorn transformers torch

from fastapi import FastAPI
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = FastAPI()

# 모델 로드
model_name = "your-model-name"  # 예: "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

@app.post("/generate")
async def generate_text(request: dict):
    prompt = request["prompt"]
    temperature = request.get("temperature", 0.7)
    max_tokens = request.get("max_tokens", 512)
    
    # 토큰화
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    
    # 생성
    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_length=inputs.shape[1] + max_tokens,
            temperature=temperature,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # 디코딩
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = response[len(prompt):]  # 프롬프트 제거
    
    return {"response": response}

# 서버 실행
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### **ngrok으로 외부 접속 가능하게 만들기**
```python
# Colab에서 ngrok 설치 및 실행
!pip install pyngrok
from pyngrok import ngrok

# 터널 생성
public_url = ngrok.connect(8000)
print(f"Public URL: {public_url}")
```

### **2단계: 백엔드에서 Colab API 연결**

#### **환경 변수 설정**
```bash
# .env 파일에 추가
COLAB_API_URL=https://your-ngrok-url.ngrok.io
```

#### **모델 설정 추가**
```json
{
  "models": {
    "colab-model": {
      "name": "colab-api",
      "type": "colab",
      "description": "Colab Pro에서 실행하는 모델",
      "parameters": {
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 0.9
      },
      "supported_tasks": ["text-generation", "chat"],
      "language": "ko",
      "domain": "general"
    }
  }
}
```

### **3단계: API 연결 테스트**
```bash
# Colab API 테스트
curl -X POST "https://your-ngrok-url.ngrok.io/generate" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "안녕하세요", "max_tokens": 100}'
```

---

## 🔧 **모델 전환 방법**

### **API로 모델 전환**
```bash
# 로컬 모델로 전환
curl -X POST "http://localhost:8000/admin/switch-model" \
     -H "Content-Type: application/json" \
     -d '{"model_id": "my-korean-model"}'

# Colab 모델로 전환
curl -X POST "http://localhost:8000/admin/switch-model" \
     -H "Content-Type: application/json" \
     -d '{"model_id": "colab-model"}'
```

### **환경 변수로 전환**
```bash
# 로컬 모델
export LLM_MODEL=./model/local/my-korean-model

# Colab API
export LLM_MODEL=colab-api
```

---

## 📊 **모델 성능 비교**

### **로컬 모델**
- ✅ **장점**: 빠른 응답, 오프라인 작동, 비용 없음
- ❌ **단점**: GPU 메모리 필요, 모델 크기 제한

### **Colab Pro API**
- ✅ **장점**: 강력한 GPU, 대용량 모델, 쉬운 설정
- ❌ **단점**: 인터넷 필요, 비용 발생, 연결 불안정

---

## 🎯 **추천 설정**

### **개발/테스트용**
```bash
# 작은 모델로 빠른 테스트
LLM_MODEL=microsoft/DialoGPT-medium
```

### **프로덕션용**
```bash
# 로컬 대용량 모델
LLM_MODEL=./model/local/korean-llama-2-7b
```

### **고성능 필요시**
```bash
# Colab Pro + 대용량 모델
COLAB_API_URL=https://your-colab-url.ngrok.io
LLM_MODEL=colab-api
```

---

## 🔍 **모델 상태 확인**

### **현재 활성 모델 확인**
```bash
curl http://localhost:8000/admin/model-info
```

### **사용 가능한 모델 목록**
```bash
curl http://localhost:8000/admin/models
```

### **모델 성능 통계**
```bash
curl http://localhost:8000/analytics/model-stats
```

---

## ⚠️ **주의사항**

### **로컬 모델**
- **GPU 메모리**: 모델 크기에 따라 8GB~24GB 필요
- **디스크 공간**: 모델 파일 크기 확인
- **라이선스**: 모델 사용 라이선스 준수

### **Colab Pro**
- **세션 시간**: 12시간 제한
- **연결 안정성**: ngrok 재연결 필요할 수 있음
- **비용**: Colab Pro 구독료

---

## 🚀 **실제 사용 예시**

### **1. 한국어 모델 추가**
```bash
# 1. 모델 다운로드
git clone https://huggingface.co/beomi/KoAlpaca-Polyglot-12.8B model/local/korean-alpaca

# 2. 설정 추가
echo '{
  "models": {
    "korean-alpaca": {
      "name": "./model/local/korean-alpaca",
      "type": "local",
      "description": "한국어 Alpaca 모델",
      "language": "ko"
    }
  }
}' >> model/models.json

# 3. 모델 전환
curl -X POST "http://localhost:8000/admin/switch-model" \
     -d '{"model_id": "korean-alpaca"}'
```

### **2. Colab Pro 연결**
```bash
# 1. Colab에서 ngrok URL 확인
# 2. 환경 변수 설정
export COLAB_API_URL=https://abc123.ngrok.io

# 3. 연결 테스트
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "안녕하세요"}'
```

**이제 원하는 모델을 자유롭게 연결할 수 있습니다! 🎉** 

# 🤖 외부 모델 연결 가이드

## �� **개요**

AI 백엔드는 **페이지별 고정 모델 시스템**을 지원합니다:

- **채팅 페이지** → `my_colab_chat` 모델
- **코딩 페이지** → `my_colab_code` 모델  
- **건강 페이지** → `health-expert` 모델
- **여행 페이지** → `travel-expert` 모델
- **법률 페이지** → `legal-expert` 모델

---

## 🎯 **페이지별 고정 모델 시스템**

### **작동 원리**
```
사용자가 health 페이지에서 질문 → health-expert 모델 자동 선택
사용자가 travel 페이지에서 질문 → travel-expert 모델 자동 선택
사용자가 chat 페이지에서 질문 → my_colab_chat 모델 자동 선택
```

### **설정 방법**
```json
// model/models.json
{
  "page_mapping": {
    "chat": "my_colab_chat",
    "code": "my_colab_code",
    "health": "health-expert", 
    "travel": "travel-expert",
    "legal": "legal-expert",
    "investment": "korean-llm"
  }
}
```

### **프론트엔드에서 페이지 정보 전송**
```javascript
// health 페이지에서 질문할 때
const response = await fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        question: "건강한 운동 방법이 궁금해요",
        user_id: 'user_123',
        context: { page: 'health' }  // ← 이게 중요!
    })
});

// chat 페이지에서 질문할 때  
const response = await fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        question: "안녕하세요",
        user_id: 'user_123',
        context: { page: 'chat' }  // ← 이게 중요!
    })
});
```

---

## 🔧 **방법 1: 환경변수로 설정 (간단)**

### **1단계: .env 파일 설정**
```bash
# .env 파일에 추가
CUSTOM_API_URL=https://your-model-api.com
CUSTOM_API_KEY=your_api_key_here
```

### **2단계: API 서버 준비**
당신의 API 서버는 다음 형식으로 응답해야 합니다:

```python
# Flask/FastAPI 예시
@app.post("/generate")
def generate_response():
    data = request.json
    prompt = data["prompt"]
    max_tokens = data.get("max_tokens", 512)
    temperature = data.get("temperature", 0.7)
    
    # 여기서 모델 추론
    response = your_model.generate(prompt)
    
    return {
        "response": response,
        "status": "success"
    }
```

### **3단계: 서버 재시작**
```bash
cd backend
python main.py
```

---

## 🎛️ **방법 2: 모델 설정 파일 방식 (권장)**

### **1단계: models.json 수정**
```json
{
  "models": {
    "my_colab_chat": {
      "name": "my-chat-model",
      "type": "remote_api",
      "description": "내 Colab 채팅 모델",
      "api_url": "https://abc123.ngrok.io",
      "api_key": "",
      "parameters": {
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9
      },
      "supported_tasks": ["text-generation", "chat"],
      "language": "ko",
      "domain": "general"
    },
    "my_colab_code": {
      "name": "my-code-model",
      "type": "remote_api",
      "description": "내 Colab 코드 생성 모델",
      "api_url": "https://def456.ngrok.io",
      "api_key": "",
      "parameters": {
        "max_tokens": 1024,
        "temperature": 0.1,
        "top_p": 0.9
      },
      "supported_tasks": ["text-generation", "code-generation"],
      "language": "ko",
      "domain": "coding"
    }
  },
  "active_model": "my_colab_chat",
  "page_mapping": {
    "chat": "my_colab_chat",
    "code": "my_colab_code"
  }
}
```

### **2단계: API 엔드포인트 구현**

#### **기본 형식**
```python
@app.post("/generate")
def generate():
    data = request.json
    prompt = data["prompt"]
    
    # 모델 추론
    response = your_model.generate(prompt)
    
    return {"response": response}
```

#### **OpenAI 호환 형식**
```python
@app.post("/v1/chat/completions")
def chat_completions():
    data = request.json
    messages = data["messages"]
    prompt = messages[-1]["content"]
    
    # 모델 추론
    response = your_model.generate(prompt)
    
    return {
        "choices": [{
            "message": {
                "content": response
            }
        }]
    }
```

### **3단계: 모델 전환**
```bash
# API로 모델 전환
curl -X POST "http://localhost:8000/admin/switch-model" \
  -H "Content-Type: application/json" \
  -d '{"model_id": "my_colab_chat"}'
```

---

## 🌐 **방법 3: Colab + ngrok 설정**

### **1단계: Colab에서 모델 서버 실행**
```python
# Colab 노트북
!pip install flask flask-cors

from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

app = Flask(__name__)
CORS(app)

# 모델 로드
model_name = "your-model-name"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

@app.post("/generate")
def generate():
    data = request.json
    prompt = data["prompt"]
    max_tokens = data.get("max_tokens", 512)
    temperature = data.get("temperature", 0.7)
    
    # 토크나이징
    inputs = tokenizer(prompt, return_tensors="pt")
    
    # 생성
    with torch.no_grad():
        outputs = model.generate(
            inputs["input_ids"],
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # 디코딩
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = response[len(prompt):]  # 프롬프트 제거
    
    return {"response": response}

# ngrok으로 터널링
!pip install pyngrok
from pyngrok import ngrok

# ngrok 터널 생성
public_url = ngrok.connect(5000)
print(f"Public URL: {public_url}")

# 서버 실행
app.run(host="0.0.0.0", port=5000)
```

### **2단계: models.json에 URL 추가**
```json
{
  "models": {
    "colab_model": {
      "name": "colab-model",
      "type": "remote_api",
      "api_url": "https://abc123.ngrok.io",
      "parameters": {
        "max_tokens": 512,
        "temperature": 0.7
      },
      "domain": "general"
    }
  },
  "active_model": "colab_model"
}
```

---

## 🔍 **API 응답 형식 지원**

백엔드는 **다양한 응답 형식**을 지원합니다:

### **1. 기본 형식**
```json
{
  "response": "모델이 생성한 텍스트"
}
```

### **2. OpenAI 형식**
```json
{
  "choices": [{
    "message": {
      "content": "모델이 생성한 텍스트"
    }
  }]
}
```

### **3. 단순 텍스트 형식**
```json
{
  "text": "모델이 생성한 텍스트"
}
```

---

## 🧪 **테스트 방법**

### **1. API 직접 테스트**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "안녕하세요",
    "user_id": "test_user",
    "context": {"domain": "general"}
  }'
```

### **2. 모델 정보 확인**
```bash
curl "http://localhost:8000/admin/model-info"
```

### **3. 사용 가능한 모델 목록**
```bash
curl "http://localhost:8000/admin/models"
```

---

## ⚠️ **주의사항**

### **1. API 키 보안**
- API 키는 환경변수나 설정 파일에 저장
- Git에 커밋하지 않도록 주의
- 프로덕션에서는 더 강력한 보안 적용

### **2. 응답 시간**
- 원격 API는 네트워크 지연 발생
- 타임아웃 설정 권장 (30초)
- 에러 처리 구현 필수

### **3. 비용 관리**
- API 호출 횟수 모니터링
- 사용량 제한 설정
- 비용 알림 설정

---

## 🚀 **고급 설정**

### **도메인별 자동 모델 전환**
```json
{
  "model_switching": {
    "enabled": true,
    "auto_switch_by_domain": true
  },
  "page_mapping": {
    "health": "health-expert",
    "travel": "travel-expert",
    "legal": "legal-expert",
    "coding": "my_colab_code"
  }
}
```

### **배치 처리**
```python
# 여러 질문을 한 번에 처리
responses = await llm_service.batch_generate([
    "질문 1",
    "질문 2", 
    "질문 3"
])
```

이제 당신의 모델을 쉽게 연결할 수 있습니다! 🎉 