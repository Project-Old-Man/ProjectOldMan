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

    # 백엔드 URL 설정
    backend_url: str = os.environ.get("BACKEND_URL", "http://localhost:8000")

    class Config:
        env_file = ".env"
        case_sensitive = False

# 전역 설정 인스턴스
settings = Settings()