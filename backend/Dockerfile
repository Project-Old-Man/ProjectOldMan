FROM python:3.11-slim

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# pip 업그레이드 및 타임아웃 설정
RUN pip install --upgrade pip
ENV PIP_DEFAULT_TIMEOUT=1000
ENV PIP_RETRIES=5

# Python 의존성 설치 (단계별 설치)
COPY requirements.txt .

# 가장 중요한 패키지부터 설치
RUN pip install --no-cache-dir fastapi uvicorn pydantic python-dotenv

# 데이터베이스 관련 패키지
RUN pip install --no-cache-dir sqlalchemy asyncpg psycopg2-binary

# 나머지 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV MODEL_PATH=/app/model/models.json

# 포트 노출
EXPOSE 8000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 애플리케이션 실행
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]