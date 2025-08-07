FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# pip 업그레이드
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 모든 NumPy 관련 패키지 제거 후 1.x 강제 설치
RUN pip uninstall -y numpy scipy scikit-learn || true
RUN pip cache purge

# NumPy 1.24.4 강제 설치 (절대 2.x 방지)
RUN pip install --no-cache-dir --force-reinstall numpy==1.24.4
RUN pip install --no-cache-dir --force-reinstall scipy==1.10.1

# PyTorch 설치 (NumPy 1.x와 호환되는 버전)
RUN pip install --no-cache-dir torch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 --index-url https://download.pytorch.org/whl/cpu

# FastAPI 기본 패키지 설치
RUN pip install --no-cache-dir \
    fastapi==0.110.0 \
    uvicorn[standard]==0.27.0 \
    pydantic==2.6.0 \
    python-multipart==0.0.9

# LLM 관련 패키지 설치
RUN pip install --no-cache-dir llama-cpp-python==0.2.56

# Transformers와 Sentence-Transformers 설치 (NumPy 버전 고정 유지)
RUN pip install --no-cache-dir --no-deps \
    transformers==4.21.3 \
    sentence-transformers==2.2.2 \
    scikit-learn==1.3.2

# 의존성 수동 설치 (NumPy 충돌 방지)
RUN pip install --no-cache-dir \
    tokenizers==0.13.3 \
    huggingface-hub==0.16.4 \
    tqdm \
    regex \
    requests \
    packaging \
    filelock

# FAISS 설치 시도 (실패해도 계속)
RUN pip install --no-cache-dir faiss-cpu==1.7.3 || echo "FAISS 설치 실패 - 간단 벡터 저장소 사용"

# 유틸리티 패키지 설치
RUN pip install --no-cache-dir \
    python-dotenv==1.0.1 \
    typing-extensions>=4.8.0 \
    httpx>=0.25.0

# NumPy 버전 확인 및 고정
RUN python -c "import numpy; assert numpy.__version__.startswith('1.'), f'NumPy 2.x detected: {numpy.__version__}'; print(f'✅ NumPy version verified: {numpy.__version__}')"

# 백엔드 코드 복사
COPY backend/ ./backend/
WORKDIR /app/backend

# 모델 디렉토리 생성
RUN mkdir -p models

# 포트 노출
EXPOSE 9000

# 환경 변수 설정
ENV PYTHONPATH=/app/backend
ENV MODEL_PATH=models/tinyllama.gguf
ENV USE_MOCK_EMBEDDING=false
ENV PYTHONUNBUFFERED=1
ENV NUMPY_EXPERIMENTAL_ARRAY_FUNCTION=0
ENV PIP_NO_DEPS=false

# 서버 시작 전 최종 NumPy 확인
RUN python -c "import numpy; print(f'Final NumPy check: {numpy.__version__}')"

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:9000/health || exit 1

# 서버 실행
CMD ["python", "main.py"]
