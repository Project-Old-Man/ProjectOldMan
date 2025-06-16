import asyncio
import json
import csv
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import aiofiles
from vector_db import VectorDBManager
from database import DatabaseManager

logger = logging.getLogger(__name__)

class DataProcessor:
    """데이터 처리 및 초기 로딩을 위한 유틸리티 클래스"""
    
    def __init__(self):
        self.vector_db = VectorDBManager()
        self.database = DatabaseManager()
    
    async def initialize(self):
        """데이터 처리기 초기화"""
        await self.vector_db.connect()
        await self.database.connect()
        logger.info("데이터 처리기 초기화 완료")
    
    async def load_documents_from_csv(self, csv_path: str) -> int:
        """CSV 파일에서 문서 로드"""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"CSV 파일 로드: {len(df)}개 행")
            
            documents = []
            for _, row in df.iterrows():
                doc = {
                    "content": str(row.get("content", "")),
                    "title": str(row.get("title", "")),
                    "category": str(row.get("category", "general")),
                    "source": str(row.get("source", "")),
                    "metadata": {
                        "author": row.get("author", ""),
                        "tags": str(row.get("tags", "")).split(",") if row.get("tags") else [],
                        "created_date": row.get("created_date", "")
                    }
                }
                documents.append(doc)
            
            # 벡터DB에 일괄 추가
            doc_ids = await self.vector_db.bulk_add_documents(documents)
            logger.info(f"{len(doc_ids)}개 문서를 벡터DB에 추가")
            
            return len(doc_ids)
            
        except Exception as e:
            logger.error(f"CSV 로드 실패: {e}")
            return 0
    
    async def load_documents_from_json(self, json_path: str) -> int:
        """JSON 파일에서 문서 로드"""
        try:
            async with aiofiles.open(json_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
            
            if isinstance(data, dict):
                data = [data]  # 단일 객체를 리스트로 변환
            
            documents = []
            for item in data:
                doc = {
                    "content": item.get("content", ""),
                    "title": item.get("title", ""),
                    "category": item.get("category", "general"),
                    "source": item.get("source", ""),
                    "metadata": item.get("metadata", {})
                }
                documents.append(doc)
            
            doc_ids = await self.vector_db.bulk_add_documents(documents)
            logger.info(f"{len(doc_ids)}개 문서를 JSON에서 로드")
            
            return len(doc_ids)
            
        except Exception as e:
            logger.error(f"JSON 로드 실패: {e}")
            return 0
    
    async def load_sample_data(self) -> int:
        """샘플 데이터 로드"""
        sample_documents = [
            {
                "content": "파이썬은 간단하고 배우기 쉬운 프로그래밍 언어입니다. 데이터 분석, 웹 개발, 인공지능 등 다양한 분야에서 사용됩니다.",
                "title": "파이썬 소개",
                "category": "programming",
                "source": "tutorial",
                "metadata": {"difficulty": "beginner", "language": "python"}
            },
            {
                "content": "머신러닝은 데이터로부터 패턴을 학습하여 예측이나 분류를 수행하는 인공지능 기법입니다. 지도학습, 비지도학습, 강화학습으로 분류됩니다.",
                "title": "머신러닝 기초",
                "category": "ai",
                "source": "guide",
                "metadata": {"difficulty": "intermediate", "topics": ["ml", "ai"]}
            },
            {
                "content": "FastAPI는 Python으로 API를 빠르게 구축할 수 있는 웹 프레임워크입니다. 자동 문서 생성과 타입 힌트를 지원합니다.",
                "title": "FastAPI 개요",
                "category": "web",
                "source": "documentation",
                "metadata": {"framework": "fastapi", "type": "api"}
            },
            {
                "content": "벡터 데이터베이스는 고차원 벡터 데이터를 효율적으로 저장하고 검색할 수 있는 데이터베이스입니다. 유사도 검색에 특화되어 있습니다.",
                "title": "벡터 데이터베이스",
                "category": "database",
                "source": "reference",
                "metadata": {"type": "vector", "use_case": "similarity_search"}
            },
            {
                "content": "Kubernetes는 컨테이너화된 애플리케이션을 자동으로 배포, 확장, 관리하는 오픈소스 플랫폼입니다.",
                "title": "Kubernetes 소개",
                "category": "devops",
                "source": "manual",
                "metadata": {"type": "orchestration", "platform": "kubernetes"}
            }
        ]
        
        try:
            doc_ids = await self.vector_db.bulk_add_documents(sample_documents)
            logger.info(f"{len(doc_ids)}개 샘플 문서 로드 완료")
            return len(doc_ids)
        except Exception as e:
            logger.error(f"샘플 데이터 로드 실패: {e}")
            return 0
    
    async def export_query_data(self, output_path: str, days: int = 30) -> bool:
        """쿼리 데이터를 CSV로 내보내기"""
        try:
            # 최근 N일간의 쿼리 데이터 조회
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            async with self.database.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        q.question,
                        q.response,
                        q.processing_time,
                        q.created_at,
                        f.rating,
                        f.feedback_text
                    FROM queries q
                    LEFT JOIN feedback f ON q.id = f.query_id
                    WHERE q.created_at >= $1
                    ORDER BY q.created_at DESC
                """, cutoff_date)
            
            # CSV로 저장
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['question', 'response', 'processing_time', 'created_at', 'rating', 'feedback_text'])
                
                for row in rows:
                    writer.writerow([
                        row['question'],
                        row['response'],
                        row['processing_time'],
                        row['created_at'].isoformat(),
                        row['rating'],
                        row['feedback_text']
                    ])
            
            logger.info(f"쿼리 데이터 내보내기 완료: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"데이터 내보내기 실패: {e}")
            return False
    
    async def create_training_dataset(self, output_path: str, min_rating: int = 4) -> bool:
        """파인튜닝용 학습 데이터셋 생성"""
        try:
            async with self.database.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        q.question,
                        q.response
                    FROM queries q
                    JOIN feedback f ON q.id = f.query_id
                    WHERE f.rating >= $1
                    ORDER BY f.rating DESC, q.created_at DESC
                """, min_rating)
            
            # JSONL 형식으로 저장 (파인튜닝용)
            training_data = []
            for row in rows:
                training_data.append({
                    "instruction": "다음 질문에 도움이 되는 답변을 제공하세요.",
                    "input": row['question'],
                    "output": row['response']
                })
            
            async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
                for item in training_data:
                    await f.write(json.dumps(item, ensure_ascii=False) + '\n')
            
            logger.info(f"학습 데이터셋 생성 완료: {len(training_data)}개 샘플")
            return True
            
        except Exception as e:
            logger.error(f"학습 데이터셋 생성 실패: {e}")
            return False
    
    async def backup_vector_db(self, backup_path: str) -> bool:
        """벡터 데이터베이스 백업"""
        try:
            # Weaviate에서 모든 객체 추출
            result = (
                self.vector_db.client.query
                .get(self.vector_db.collection_name, ["content", "title", "category", "source", "metadata"])
                .with_additional(["vector"])
                .with_limit(10000)  # 제한 설정
                .do()
            )
            
            backup_data = []
            if "data" in result and "Get" in result["data"]:
                for item in result["data"]["Get"][self.vector_db.collection_name]:
                    backup_data.append({
                        "content": item["content"],
                        "title": item.get("title", ""),
                        "category": item.get("category", ""),
                        "source": item.get("source", ""),
                        "metadata": item.get("metadata", {}),
                        "vector": item["_additional"]["vector"]
                    })
            
            # JSON 파일로 저장
            async with aiofiles.open(backup_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(backup_data, ensure_ascii=False, indent=2))
            
            logger.info(f"벡터DB 백업 완료: {len(backup_data)}개 문서")
            return True
            
        except Exception as e:
            logger.error(f"벡터DB 백업 실패: {e}")
            return False
    
    async def restore_vector_db(self, backup_path: str) -> bool:
        """벡터 데이터베이스 복원"""
        try:
            async with aiofiles.open(backup_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                backup_data = json.loads(content)
            
            # 기존 데이터 삭제 (옵션)
            # await self.vector_db.client.schema.delete_class(self.vector_db.collection_name)
            # await self.vector_db.init_schema()
            
            # 배치로 복원
            with self.vector_db.client.batch(batch_size=100) as batch:
                for item in backup_data:
                    doc_data = {
                        "content": item["content"],
                        "title": item.get("title", ""),
                        "category": item.get("category", ""),
                        "source": item.get("source", ""),
                        "metadata": item.get("metadata", {})
                    }
                    
                    batch.add_data_object(
                        data_object=doc_data,
                        class_name=self.vector_db.collection_name,
                        vector=item["vector"]
                    )
            
            logger.info(f"벡터DB 복원 완료: {len(backup_data)}개 문서")
            return True
            
        except Exception as e:
            logger.error(f"벡터DB 복원 실패: {e}")
            return False
    
    async def cleanup_old_data(self, days: int = 90) -> Dict[str, int]:
        """오래된 데이터 정리"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            async with self.database.pool.acquire() as conn:
                # 오래된 쿼리 삭제
                query_result = await conn.execute("""
                    DELETE FROM queries 
                    WHERE created_at < $1 
                    AND id NOT IN (
                        SELECT DISTINCT query_id 
                        FROM feedback 
                        WHERE rating >= 4
                    )
                """, cutoff_date)
                
                # 고아 피드백 삭제
                feedback_result = await conn.execute("""
                    DELETE FROM feedback 
                    WHERE query_id NOT IN (SELECT id FROM queries)
                """)
            
            deleted_queries = int(query_result.split()[-1]) if query_result else 0
            deleted_feedback = int(feedback_result.split()[-1]) if feedback_result else 0
            
            logger.info(f"데이터 정리 완료 - 쿼리: {deleted_queries}개, 피드백: {deleted_feedback}개")
            
            return {
                "deleted_queries": deleted_queries,
                "deleted_feedback": deleted_feedback
            }
            
        except Exception as e:
            logger.error(f"데이터 정리 실패: {e}")
            return {"deleted_queries": 0, "deleted_feedback": 0}
    
    async def analyze_data_quality(self) -> Dict[str, Any]:
        """데이터 품질 분석"""
        try:
            async with self.database.pool.acquire() as conn:
                # 기본 통계
                basic_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_queries,
                        COUNT(DISTINCT user_id) as unique_users,
                        AVG(LENGTH(question)) as avg_question_length,
                        AVG(LENGTH(response)) as avg_response_length,
                        AVG(processing_time) as avg_processing_time
                    FROM queries
                """)
                
                # 피드백 통계
                feedback_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_feedback,
                        AVG(rating) as avg_rating,
                        COUNT(*) FILTER (WHERE rating >= 4) as positive_feedback,
                        COUNT(*) FILTER (WHERE rating <= 2) as negative_feedback
                    FROM feedback
                """)
                
                # 카테고리별 분포
                category_stats = await conn.fetch("""
                    SELECT 
                        category,
                        COUNT(*) as count
                    FROM (
                        SELECT jsonb_array_elements_text(sources::jsonb) ->> 'category' as category
                        FROM queries
                        WHERE sources IS NOT NULL
                    ) AS t
                    WHERE category IS NOT NULL
                    GROUP BY category
                    ORDER BY count DESC
                """)
            
            # 벡터DB 통계
            vector_stats = await self.vector_db.get_collection_stats()
            
            return {
                "database_stats": {
                    "total_queries": basic_stats['total_queries'],
                    "unique_users": basic_stats['unique_users'],
                    "avg_question_length": float(basic_stats['avg_question_length'] or 0),
                    "avg_response_length": float(basic_stats['avg_response_length'] or 0),
                    "avg_processing_time": float(basic_stats['avg_processing_time'] or 0)
                },
                "feedback_stats": {
                    "total_feedback": feedback_stats['total_feedback'],
                    "avg_rating": float(feedback_stats['avg_rating'] or 0),
                    "positive_feedback": feedback_stats['positive_feedback'],
                    "negative_feedback": feedback_stats['negative_feedback'],
                    "feedback_rate": feedback_stats['total_feedback'] / max(basic_stats['total_queries'], 1)
                },
                "category_distribution": [
                    {"category": row['category'], "count": row['count']}
                    for row in category_stats
                ],
                "vector_db_stats": vector_stats
            }
            
        except Exception as e:
            logger.error(f"데이터 품질 분석 실패: {e}")
            return {}
    
    async def close(self):
        """리소스 정리"""
        await self.vector_db.disconnect()
        await self.database.disconnect()

# CLI 스크립트를 위한 메인 함수
async def main():
    """데이터 처리 CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="데이터 처리 유틸리티")
    parser.add_argument("command", choices=["load_csv", "load_json", "load_sample", "export", "backup", "restore", "cleanup", "analyze"])
    parser.add_argument("--file", help="입력/출력 파일 경로")
    parser.add_argument("--days", type=int, default=30, help="일수 (export, cleanup용)")
    parser.add_argument("--rating", type=int, default=4, help="최소 평점 (export용)")
    
    args = parser.parse_args()
    
    processor = DataProcessor()
    await processor.initialize()
    
    try:
        if args.command == "load_csv":
            if not args.file:
                print("--file 옵션이 필요합니다")
                return
            count = await processor.load_documents_from_csv(args.file)
            print(f"{count}개 문서 로드 완료")
            
        elif args.command == "load_json":
            if not args.file:
                print("--file 옵션이 필요합니다")
                return
            count = await processor.load_documents_from_json(args.file)
            print(f"{count}개 문서 로드 완료")
            
        elif args.command == "load_sample":
            count = await processor.load_sample_data()
            print(f"{count}개 샘플 문서 로드 완료")
            
        elif args.command == "export":
            if not args.file:
                print("--file 옵션이 필요합니다")
                return
            success = await processor.export_query_data(args.file, args.days)
            print("데이터 내보내기 완료" if success else "데이터 내보내기 실패")
            
        elif args.command == "backup":
            if not args.file:
                print("--file 옵션이 필요합니다")
                return
            success = await processor.backup_vector_db(args.file)
            print("백업 완료" if success else "백업 실패")
            
        elif args.command == "restore":
            if not args.file:
                print("--file 옵션이 필요합니다")
                return
            success = await processor.restore_vector_db(args.file)
            print("복원 완료" if success else "복원 실패")
            
        elif args.command == "cleanup":
            result = await processor.cleanup_old_data(args.days)
            print(f"정리 완료 - 쿼리: {result['deleted_queries']}개, 피드백: {result['deleted_feedback']}개")
            
        elif args.command == "analyze":
            stats = await processor.analyze_data_quality()
            print(json.dumps(stats, indent=2, ensure_ascii=False))
            
    finally:
        await processor.close()

if __name__ == "__main__":
    asyncio.run(main())