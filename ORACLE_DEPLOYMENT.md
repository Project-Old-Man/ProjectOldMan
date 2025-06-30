# Oracle Cloud Free Tier 배포 가이드

## 🚀 Oracle Cloud Free Tier 설정

### 1. Oracle Cloud 인스턴스 생성

1. **Oracle Cloud Console** 접속
2. **Compute** → **Instances** → **Create Instance**
3. **VM.Standard.A1.Flex** 선택
4. **메모리 설정**: 24GB RAM, 4 OCPU
5. **Ubuntu 22.04** 이미지 선택
6. **Public IP** 할당

### 2. 시스템 요구사항

- **RAM**: 24GB (최대)
- **CPU**: 4 OCPU (ARM 기반)
- **스토리지**: 200GB
- **OS**: Ubuntu 22.04

### 3. 배포 단계

```bash
# 1. 서버에 SSH 연결
ssh ubuntu@YOUR_SERVER_IP

# 2. 배포 스크립트 실행
chmod +x oracle_deploy.sh
./oracle_deploy.sh

# 3. 프로젝트 파일 업로드
# (로컬에서) scp -r . ubuntu@YOUR_SERVER_IP:~/projectoldman/

# 4. 서버에서 실행
cd ~/projectoldman
docker-compose up --build
```

## ⚙️ 최적화 설정

### 메모리 할당
- **PostgreSQL**: 512MB
- **Weaviate**: 1GB
- **Backend (vLLM)**: 8GB
- **Frontend**: 128MB
- **여유분**: ~2GB

### vLLM CPU 최적화
```python
# llm_service.py 설정
GPU_MEMORY_UTILIZATION=0.0  # CPU 모드
MAX_MODEL_LEN=2048          # 메모리 절약
MAX_NUM_BATCHED_TOKENS=4096 # 배치 크기 제한
```

## 📊 성능 예상

### 병렬 처리
- **동시 요청**: 4-8개
- **응답 시간**: 2-5초 (CPU 모드)
- **처리량**: 분당 10-20 요청

### 메모리 사용량
- **모델 로드**: ~6GB
- **운영 중**: ~12GB
- **최대 사용**: ~18GB

## 🔧 모니터링

### 시스템 모니터링
```bash
# 메모리 사용량 확인
free -h

# Docker 컨테이너 상태
docker stats

# 로그 확인
docker-compose logs -f backend
```

### 성능 최적화 팁

1. **모델 캐싱**: HuggingFace 모델 캐시 활용
2. **배치 처리**: 여러 요청을 배치로 처리
3. **메모리 관리**: 사용하지 않는 모델 언로드
4. **스왑 파일**: 2GB 스왑 파일 활용

## 🚨 주의사항

1. **첫 실행**: 모델 다운로드로 인한 긴 시작 시간
2. **메모리 부족**: 24GB RAM 초과 시 스왑 사용
3. **CPU 성능**: ARM 기반으로 GPU보다 느림
4. **네트워크**: 무료 티어 대역폭 제한

## 📝 배포 후 확인

1. **헬스 체크**: `http://YOUR_SERVER_IP/health`
2. **프론트엔드**: `http://YOUR_SERVER_IP`
3. **API 문서**: `http://YOUR_SERVER_IP:8000/docs`
4. **모델 상태**: 로그에서 vLLM 초기화 확인

## 🔄 업데이트

```bash
# 코드 업데이트
git pull origin main

# 컨테이너 재빌드
docker-compose down
docker-compose up --build

# 모델 업데이트 (필요시)
docker-compose exec backend python -c "from llm_service import LLMService; import asyncio; asyncio.run(LLMService().initialize())"
```

## 📞 문제 해결

### 일반적인 문제
1. **메모리 부족**: 스왑 파일 확인, 컨테이너 메모리 제한 조정
2. **모델 로드 실패**: 인터넷 연결 확인, 캐시 삭제
3. **느린 응답**: 배치 크기 조정, 모델 최적화

### 로그 확인
```bash
# 백엔드 로그
docker-compose logs backend

# 전체 로그
docker-compose logs

# 실시간 로그
docker-compose logs -f
``` 