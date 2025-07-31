import asyncpg
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class QueryRecord:
    id: int
    user_id: Optional[str]
    question: str
    response: str
    sources: List[Dict]
    processing_time: float
    created_at: datetime
    feedback_rating: Optional[int] = None

@dataclass
class FeedbackRecord:
    id: int
    query_id: str
    user_id: str
    rating: int
    feedback_text: Optional[str]
    created_at: datetime

class DatabaseManager:
    def __init__(self):
        self.pool = None
        self.db_url = os.getenv(
            "DATABASE_URL", 
            "postgresql://user:password@localhost:5432/ai_system"
        )
    
    async def connect(self):
        """데이터베이스 연결 풀 생성"""
        try:
            self.pool = await asyncpg.create_pool(
                self.db_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            # 테이블 초기화
            await self.init_tables()
            logger.info("데이터베이스 연결 성공")
            
        except Exception as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            raise
    
    async def disconnect(self):
        """연결 풀 종료"""
        if self.pool:
            await self.pool.close()
    
    async def init_tables(self):
        """테이블 생성"""
        async with self.pool.acquire() as conn:
            # 사용자 쿼리 테이블
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS queries (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255),
                    question TEXT NOT NULL,
                    response TEXT NOT NULL,
                    sources JSONB,
                    processing_time FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 피드백 테이블
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    query_id INTEGER REFERENCES queries(id),
                    user_id VARCHAR(255) NOT NULL,
                    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                    feedback_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 인덱스 생성
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_queries_user_id ON queries(user_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_queries_created_at ON queries(created_at)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_query_id ON feedback(query_id)")
            
            logger.info("데이터베이스 테이블 초기화 완료")
    
    async def save_query(
        self, 
        user_id: Optional[str], 
        question: str, 
        response: str, 
        sources: List[Dict], 
        processing_time: float = 0.0
    ) -> QueryRecord:
        """쿼리 기록 저장"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO queries (user_id, question, response, sources, processing_time)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id, created_at
            """, user_id, question, response, json.dumps(sources), processing_time)
            
            return QueryRecord(
                id=row['id'],
                user_id=user_id,
                question=question,
                response=response,
                sources=sources,
                processing_time=processing_time,
                created_at=row['created_at']
            )
    
    async def save_feedback(
        self, 
        query_id: str, 
        user_id: str, 
        rating: int, 
        feedback_text: Optional[str] = None
    ) -> FeedbackRecord:
        """피드백 저장"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO feedback (query_id, user_id, rating, feedback_text)
                VALUES ($1, $2, $3, $4)
                RETURNING id, created_at
            """, int(query_id), user_id, rating, feedback_text)
            
            return FeedbackRecord(
                id=row['id'],
                query_id=query_id,
                user_id=user_id,
                rating=rating,
                feedback_text=feedback_text,
                created_at=row['created_at']
            )
    
    async def get_user_history(self, user_id: str, limit: int = 10) -> List[QueryRecord]:
        """사용자 쿼리 히스토리 조회"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT q.*, f.rating as feedback_rating
                FROM queries q
                LEFT JOIN feedback f ON q.id = f.query_id
                WHERE q.user_id = $1
                ORDER BY q.created_at DESC
                LIMIT $2
            """, user_id, limit)
            
            return [
                QueryRecord(
                    id=row['id'],
                    user_id=row['user_id'],
                    question=row['question'],
                    response=row['response'],
                    sources=json.loads(row['sources']) if row['sources'] else [],
                    processing_time=row['processing_time'],
                    created_at=row['created_at'],
                    feedback_rating=row['feedback_rating']
                )
                for row in rows
            ]
    
    async def get_popular_queries(self, limit: int = 5, days: int = 7) -> List[Dict]:
        """인기 질문 조회"""
        async with self.pool.acquire() as conn:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            rows = await conn.fetch("""
                SELECT question, COUNT(*) as query_count,
                       AVG(f.rating) as avg_rating
                FROM queries q
                LEFT JOIN feedback f ON q.id = f.query_id
                WHERE q.created_at >= $1
                GROUP BY question
                HAVING COUNT(*) > 1
                ORDER BY query_count DESC, avg_rating DESC NULLS LAST
                LIMIT $2
            """, cutoff_date, limit)
            
            return [
                {
                    "question": row['question'],
                    "count": row['query_count'],
                    "avg_rating": float(row['avg_rating']) if row['avg_rating'] else None
                }
                for row in rows
            ]
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """시스템 통계 조회"""
        async with self.pool.acquire() as conn:
            # 기본 통계
            stats_row = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_queries,
                    COUNT(DISTINCT user_id) as unique_users,
                    AVG(processing_time) as avg_processing_time
                FROM queries
                WHERE created_at >= NOW() - INTERVAL '30 days'
            """)
            
            # 피드백 통계
            feedback_row = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_feedback,
                    AVG(rating) as avg_rating
                FROM feedback
                WHERE created_at >= NOW() - INTERVAL '30 days'
            """)
            
            # 일별 쿼리 수
            daily_queries = await conn.fetch("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as query_count
                FROM queries
                WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY DATE(created_at)
                ORDER BY date
            """)
            
            return {
                "total_queries": stats_row['total_queries'],
                "unique_users": stats_row['unique_users'],
                "avg_processing_time": float(stats_row['avg_processing_time']) if stats_row['avg_processing_time'] else 0,
                "total_feedback": feedback_row['total_feedback'],
                "avg_rating": float(feedback_row['avg_rating']) if feedback_row['avg_rating'] else 0,
                "daily_queries": [
                    {
                        "date": row['date'].isoformat(),
                        "count": row['query_count']
                    }
                    for row in daily_queries
                ]
            }
    
    async def get_feedback_count_since_last_train(self) -> int:
        """마지막 학습 이후 피드백 수 조회"""
        async with self.pool.acquire() as conn:
            # 실제로는 별도 테이블에서 마지막 학습 시간을 관리해야 함
            # 여기서는 임시로 7일 전부터 계산
            cutoff_date = datetime.now() - timedelta(days=7)
            
            row = await conn.fetchrow("""
                SELECT COUNT(*) as feedback_count
                FROM feedback
                WHERE created_at >= $1
            """, cutoff_date)
            
            return row['feedback_count']
    
    @staticmethod
    async def check_connection() -> bool:
        """연결 상태 확인"""
        try:
            db = DatabaseManager()
            await db.connect()
            await db.disconnect()
            return True
        except:
            return False

# Dependency injection을 위한 함수
async def get_db() -> DatabaseManager:
    """FastAPI dependency로 사용할 DB 인스턴스"""
    db = DatabaseManager()
    await db.connect()
    try:
        yield db
    finally:
        await db.disconnect()