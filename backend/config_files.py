# config.py
import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    # 기본 애플리케이션 설정
    app_name: str = "AI 추천 시스템"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 서버 설정
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # 데이터베이스 설정
    database_url: str = "postgresql://postgres:password@localhost:5432/ai_system"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    
    # Weaviate 설정
    weaviate_url: str = "http://localhost:8080"
    weaviate_api_key: Optional[str] = None
    
    # LLM 설정
    llm_model: str = "microsoft/DialoGPT-medium"
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    tensor_parallel_size: int = 1
    gpu_memory_utilization: float = 0.9
    
    # 임베딩 모델
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    
    # 외부 API 키
    openai_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    
    # Redis 설정
    redis_url: str = "redis://localhost:6379"
    
    # 로깅 설정
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # 보안 설정
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30
    
    # CORS 설정
    cors_origins: list = ["*"]
    
    # 파일 업로드 설정
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_dir: str = "uploads"
    
    # 캐시 설정
    cache_ttl: int = 3600  # 1시간
    
    # 모니터링 설정
    enable_metrics: bool = True
    metrics_port: int = 9000
    
    # 재학습 설정
    min_feedback_for_retrain: int = 100
    retrain_schedule: str = "0 2 * * 0"  # 매주 일요일 2시
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 전역 설정 인스턴스
settings = Settings()

---

# .env (환경 변수 예시)
# 애플리케이션 설정
APP_NAME="AI 추천 시스템"
DEBUG=false

# 데이터베이스
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_system

# Weaviate
WEAVIATE_URL=http://localhost:8080
# WEAVIATE_API_KEY=your-weaviate-api-key

# LLM 설정
LLM_MODEL=microsoft/DialoGPT-medium
MAX_TOKENS=512
TEMPERATURE=0.7

# 외부 API (선택사항)
# OPENAI_API_KEY=your-openai-api-key
# HUGGINGFACE_API_KEY=your-huggingface-api-key

# Redis
REDIS_URL=redis://localhost:6379

# 보안
SECRET_KEY=your-super-secret-key-change-this-in-production

# 로깅
LOG_LEVEL=INFO

---

# logging_config.py
import logging
import logging.config
from pathlib import Path

def setup_logging():
    """로깅 설정"""
    
    # 로그 디렉토리 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(module)s %(funcName)s %(lineno)d %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "logs/error.log",
                "maxBytes": 10485760,
                "backupCount": 5
            }
        },
        "loggers": {
            "": {  # 루트 로거
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            },
            "fastapi": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            },
            "sqlalchemy.engine": {
                "handlers": ["file"],
                "level": "WARNING",
                "propagate": False
            }
        }
    }
    
    logging.config.dictConfig(logging_config)
    return logging.getLogger(__name__)

---

# init.sql (PostgreSQL 초기화 스크립트)
-- 데이터베이스 생성
CREATE DATABASE ai_system;

-- 사용자 생성
CREATE USER ai_user WITH PASSWORD 'ai_password';
GRANT ALL PRIVILEGES ON DATABASE ai_system TO ai_user;

-- 확장 설치
\c ai_system;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 테이블 생성 (애플리케이션에서 자동 생성되지만 참고용)
/*
CREATE TABLE IF NOT EXISTS queries (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    question TEXT NOT NULL,
    response TEXT NOT NULL,
    sources JSONB,
    processing_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    query_id INTEGER REFERENCES queries(id),
    user_id VARCHAR(255) NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_queries_user_id ON queries(user_id);
CREATE INDEX IF NOT EXISTS idx_queries_created_at ON queries(created_at);
CREATE INDEX IF NOT EXISTS idx_feedback_query_id ON feedback(query_id);
CREATE INDEX IF NOT EXISTS idx_feedback_rating ON feedback(rating);

-- 텍스트 검색용 인덱스
CREATE INDEX IF NOT EXISTS idx_queries_question_gin ON queries USING GIN (to_tsvector('korean', question));
CREATE INDEX IF NOT EXISTS idx_queries_response_gin ON queries USING GIN (to_tsvector('korean', response));
*/

---

# prometheus.yml (모니터링 설정)
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'ai-backend'
    static_configs:
      - targets: ['ai-backend:9000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'weaviate'
    static_configs:
      - targets: ['weaviate:8080']
    metrics_path: '/metrics'