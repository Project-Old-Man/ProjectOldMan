FROM python:3.11-slim

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# requirements.txt 복사 및 설치 (루트 기준)
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# faiss, sentence-transformers 명시적 설치
RUN pip install --no-cache-dir faiss-cpu sentence-transformers

# backend 전체 복사
COPY backend /app

# model 폴더 복사
COPY model /app/model

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]