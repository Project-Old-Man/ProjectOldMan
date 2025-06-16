# 모델 디렉토리

이 디렉토리는 AI 모델 파일들을 저장하는 곳입니다.

## 📁 디렉토리 구조

```
model/
├── README.md                    # 이 파일
├── .gitkeep                     # 빈 디렉토리 유지용
├── models.json                  # 모델 설정 파일
├── local/                       # 로컬 모델 파일들
│   ├── korean-llm/             # 한국어 LLM 모델
│   ├── health-expert/          # 건강 전문 모델
│   ├── travel-expert/          # 여행 전문 모델
│   └── legal-expert/           # 법률 전문 모델
└── configs/                    # 모델 설정 파일들
    ├── korean-llm.json
    ├── health-expert.json
    └── travel-expert.json
```

## 🚀 모델 추가 방법

### 1. 로컬 모델 파일 추가

```bash
# 모델 파일을 model/local/ 디렉토리에 복사
cp -r /path/to/your/model model/local/your-model-name
```

### 2. 모델 설정 파일 생성

`model/configs/your-model-name.json` 파일을 생성:

```json
{
  "name": "your-model-name",
  "type": "local",
  "path": "./model/local/your-model-name",
  "description": "모델 설명",
  "parameters": {
    "max_tokens": 512,
    "temperature": 0.7,
    "top_p": 0.9
  },
  "supported_tasks": ["text-generation", "chat"],
  "language": "ko",
  "domain": "general"
}
```

### 3. 환경 변수 설정

`.env` 파일에서 모델 경로 설정:

```bash
# 로컬 모델 사용시
LLM_MODEL=./model/local/your-model-name

# 또는 절대 경로
LLM_MODEL=/app/model/local/your-model-name
```

## 📋 지원하는 모델 형식

### vLLM 지원 형식
- **HuggingFace Transformers**: `.bin`, `.safetensors`
- **GGUF**: `.gguf` (vLLM 0.3.0+)
- **AWQ**: `.awq`
- **GPTQ**: `.gptq`

### 모델 파일 예시
```
model/local/korean-llm/
├── config.json
├── tokenizer.json
├── tokenizer_config.json
├── model.safetensors
└── generation_config.json
```

## 🔧 모델 전환 방법

### 1. 환경 변수로 전환
```bash
# 한국어 모델
export LLM_MODEL=./model/local/korean-llm

# 건강 전문 모델
export LLM_MODEL=./model/local/health-expert

# 서버 재시작
docker-compose restart backend
```

### 2. API로 모델 전환
```bash
curl -X POST "http://localhost:8000/admin/switch-model" \
     -H "Content-Type: application/json" \
     -d '{"model_path": "./model/local/korean-llm"}'
```

## 📊 모델 성능 모니터링

모델 사용 통계는 다음 API로 확인할 수 있습니다:

```bash
# 모델 정보 조회
curl http://localhost:8000/admin/model-info

# 성능 통계
curl http://localhost:8000/analytics/model-stats
```

## ⚠️ 주의사항

1. **모델 크기**: 대용량 모델은 충분한 디스크 공간 필요
2. **메모리**: GPU 메모리 사용량 확인
3. **라이선스**: 모델 사용 라이선스 준수
4. **백업**: 중요한 모델 파일은 백업 보관

## 🆘 문제 해결

### 모델 로딩 실패
```bash
# 로그 확인
docker-compose logs backend

# 모델 경로 확인
ls -la model/local/your-model-name/
```

### 메모리 부족
```bash
# GPU 메모리 사용량 확인
nvidia-smi

# 환경 변수 조정
export GPU_MEMORY_UTILIZATION=0.7
``` 