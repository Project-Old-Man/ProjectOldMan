# ☁️ 클라우드 배포 가이드

## 🎯 **배포 전략**

```
🌐 Frontend (Vercel) → ☁️ Backend (Cloud) → 🤖 Model (Colab Pro)
```

---

## 🎨 **1단계: Frontend Vercel 배포**

### **1-1. Vercel 프로젝트 준비**

#### **프로젝트 구조 수정**
```bash
# frontend 디렉토리를 루트로 이동
mv frontend/* .
rmdir frontend

# vercel.json 설정 파일 생성
```

#### **vercel.json 생성**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "index.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "BACKEND_URL": "https://your-backend-url.com"
  }
}
```

#### **환경별 백엔드 URL 설정**
```javascript
// index.html에서 백엔드 URL 동적 설정
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

// API 호출 부분 수정
const response = await fetch(`${BACKEND_URL}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: message })
});
```

### **1-2. Vercel 배포**

#### **GitHub 연동 배포 (권장)**
```bash
# 1. GitHub에 코드 푸시
git add .
git commit -m "Add Vercel deployment config"
git push origin main

# 2. Vercel에서 GitHub 저장소 연결
# - vercel.com 접속
# - "New Project" 클릭
# - GitHub 저장소 선택
# - 환경 변수 설정: BACKEND_URL=https://your-backend-url.com
```

#### **CLI 배포**
```bash
# 1. Vercel CLI 설치
npm i -g vercel

# 2. 로그인
vercel login

# 3. 배포
vercel --prod
```

### **1-3. 환경 변수 설정**
```bash
# Vercel 대시보드에서 환경 변수 설정
BACKEND_URL=https://your-backend-url.com
```

---

## ☁️ **2단계: Backend 클라우드 배포**

### **2-1. 옵션 A: Railway (권장 - 간단)**

#### **Railway 배포**
```bash
# 1. Railway CLI 설치
npm install -g @railway/cli

# 2. 로그인
railway login

# 3. 프로젝트 초기화
cd backend
railway init

# 4. 환경 변수 설정
railway variables set DATABASE_URL="postgresql://..."
railway variables set WEAVIATE_URL="https://your-weaviate-url"
railway variables set COLAB_API_URL="https://your-colab-url.ngrok.io"

# 5. 배포
railway up
```

#### **Railway 설정 파일**
```json
// railway.json
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### **2-2. 옵션 B: Render**

#### **Render 배포**
```bash
# 1. render.yaml 생성
services:
  - type: web
    name: ai-playground-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        value: postgresql://...
      - key: WEAVIATE_URL
        value: https://your-weaviate-url
      - key: COLAB_API_URL
        value: https://your-colab-url.ngrok.io
```

### **2-3. 옵션 C: Heroku**

#### **Heroku 배포**
```bash
# 1. Heroku CLI 설치 및 로그인
heroku login

# 2. 앱 생성
heroku create ai-playground-backend

# 3. PostgreSQL 추가
heroku addons:create heroku-postgresql:hobby-dev

# 4. 환경 변수 설정
heroku config:set DATABASE_URL="postgresql://..."
heroku config:set WEAVIATE_URL="https://your-weaviate-url"
heroku config:set COLAB_API_URL="https://your-colab-url.ngrok.io"

# 5. 배포
git push heroku main
```

### **2-4. 옵션 D: Google Cloud Run**

#### **Cloud Run 배포**
```bash
# 1. Dockerfile 최적화
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

# 2. 빌드 및 배포
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-backend
gcloud run deploy ai-backend --image gcr.io/PROJECT_ID/ai-backend --platform managed
```

---

## 🤖 **3단계: Colab Pro 모델 서빙**

### **3-1. Colab Pro에서 서버 실행**

#### **Colab 노트북 코드**
```python
# 필요한 패키지 설치
!pip install fastapi uvicorn transformers torch pyngrok

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from pyngrok import ngrok
import json

app = FastAPI()

# CORS 설정 (프론트엔드에서 접근 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 모델 로드
print("🔄 모델 로딩 중...")
model_name = "microsoft/DialoGPT-medium"  # 원하는 모델로 변경
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("✅ 모델 로딩 완료!")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": model_name}

@app.post("/generate")
async def generate_text(request: dict):
    try:
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
                pad_token_id=tokenizer.eos_token_id,
                top_p=0.9
            )
        
        # 디코딩
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response[len(prompt):]  # 프롬프트 제거
        
        return {"response": response, "model": model_name}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stream")
async def generate_stream(request: dict):
    # 스트리밍 응답 (Server-Sent Events)
    from fastapi.responses import StreamingResponse
    import asyncio
    
    async def generate():
        try:
            prompt = request["prompt"]
            temperature = request.get("temperature", 0.7)
            max_tokens = request.get("max_tokens", 512)
            
            inputs = tokenizer.encode(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=inputs.shape[1] + max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    top_p=0.9,
                    return_dict_in_generate=True,
                    output_scores=True
                )
            
            response = tokenizer.decode(outputs.sequences[0], skip_special_tokens=True)
            response = response[len(prompt):]
            
            # 단어별로 스트리밍
            words = response.split()
            for i, word in enumerate(words):
                yield f"data: {json.dumps({'chunk': word + (' ' if i < len(words) - 1 else '')})}\n\n"
                await asyncio.sleep(0.05)
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")

# ngrok 터널 생성
print("🌐 ngrok 터널 생성 중...")
public_url = ngrok.connect(8000)
print(f"✅ Public URL: {public_url}")

# 서버 실행
print("🚀 서버 시작...")
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
```

### **3-2. 백엔드에서 Colab API 연결**

#### **환경 변수 설정**
```bash
# 백엔드 클라우드 환경에서
COLAB_API_URL=https://your-ngrok-url.ngrok.io
```

#### **모델 설정 업데이트**
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

---

## 🔧 **4단계: 데이터베이스 설정**

### **4-1. PostgreSQL 클라우드 설정**

#### **Railway PostgreSQL**
```bash
# Railway에서 PostgreSQL 추가
railway add postgresql

# 연결 정보 확인
railway variables
```

#### **Supabase (무료 대안)**
```bash
# 1. supabase.com에서 프로젝트 생성
# 2. 연결 정보 복사
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres
```

### **4-2. Weaviate 클라우드 설정**

#### **Weaviate Cloud Services**
```bash
# 1. weaviate.io에서 클러스터 생성
# 2. 연결 정보 설정
WEAVIATE_URL=https://your-cluster.weaviate.network
WEAVIATE_API_KEY=your-api-key
```

---

## 🔗 **5단계: 전체 연결 테스트**

### **5-1. 연결 확인**
```bash
# 1. Frontend 확인
curl https://your-vercel-app.vercel.app

# 2. Backend 확인
curl https://your-backend-url.com/health

# 3. Colab API 확인
curl -X POST "https://your-colab-url.ngrok.io/health"

# 4. 전체 파이프라인 테스트
curl -X POST "https://your-backend-url.com/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "안녕하세요"}'
```

### **5-2. 환경 변수 최종 설정**

#### **Vercel (Frontend)**
```bash
BACKEND_URL=https://your-backend-url.com
```

#### **Railway/Heroku (Backend)**
```bash
DATABASE_URL=postgresql://...
WEAVIATE_URL=https://your-weaviate-url
COLAB_API_URL=https://your-colab-url.ngrok.io
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

---

## 📊 **비용 비교**

| 서비스 | 월 비용 | 특징 |
|--------|---------|------|
| **Vercel** | $0 (Hobby) | 프론트엔드 무료 |
| **Railway** | $5 (Starter) | 백엔드 간단 배포 |
| **Render** | $7 (Starter) | 백엔드 안정적 |
| **Heroku** | $7 (Basic) | 백엔드 전통적 |
| **Colab Pro** | $10 | GPU 모델 서빙 |
| **Supabase** | $0 (Free) | PostgreSQL 무료 |
| **Weaviate Cloud** | $25 (Starter) | 벡터 DB |

**총 월 비용: $15-40**

---

## 🚀 **추천 배포 순서**

### **1단계: Colab Pro 설정**
```bash
# Colab에서 모델 서버 실행
# ngrok URL 복사
```

### **2단계: Backend 배포**
```bash
# Railway 선택 (가장 간단)
railway up
# 환경 변수 설정
```

### **3단계: Frontend 배포**
```bash
# Vercel 배포
vercel --prod
# BACKEND_URL 환경 변수 설정
```

### **4단계: 연결 테스트**
```bash
# 전체 파이프라인 테스트
```

---

## ⚠️ **주의사항**

### **Colab Pro**
- **세션 시간**: 12시간 제한
- **재연결**: ngrok URL 변경 시 백엔드 환경 변수 업데이트 필요
- **비용**: 월 $10

### **클라우드 서비스**
- **무료 티어**: 사용량 제한 확인
- **스케일링**: 트래픽 증가 시 자동 스케일링 설정
- **모니터링**: 로그 및 성능 모니터링 설정

---

## 🎉 **완성된 아키텍처**

```
🌐 Frontend (Vercel)
    ↓
☁️ Backend (Railway/Heroku)
    ↓
🤖 Model (Colab Pro)
    ↓
💾 Database (Supabase/Weaviate)
```

**이제 완전한 클라우드 기반 AI 웹 애플리케이션이 완성됩니다! 🚀** 