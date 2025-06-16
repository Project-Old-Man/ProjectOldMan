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