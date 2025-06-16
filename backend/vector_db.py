import weaviate
import weaviate.classes as wvc
from weaviate.classes.config import Property, DataType
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any, Optional
import os
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    text: str
    score: float
    metadata: Dict[str, Any]

class VectorDBManager:
    def __init__(self):
        self.client = None
        self.embedding_model = None
        self.collection_name = "KnowledgeBase"
        
        # Weaviate 연결 설정
        self.weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self.weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        
        # 임베딩 모델 설정
        self.embedding_model_name = os.getenv(
            "EMBEDDING_MODEL", 
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    
    async def connect(self):
        """Weaviate 클라이언트 연결"""
        try:
            # Weaviate 클라이언트 설정
            auth_config = None
            if self.weaviate_api_key:
                auth_config = weaviate.auth.AuthApiKey(api_key=self.weaviate_api_key)
            
            self.client = weaviate.Client(
                url=self.weaviate_url,
                auth_client_secret=auth_config,
                timeout_config=(5, 15)
            )
            
            # 임베딩 모델 로드
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            
            # 스키마 초기화
            await self.init_schema()
            
            logger.info("Weaviate 연결 성공")
            
        except Exception as e:
            logger.error(f"Weaviate 연결 실패: {e}")
            raise
    
    async def disconnect(self):
        """연결 종료"""
        if self.client:
            self.client = None
    
    async def init_schema(self):
        """Weaviate 스키마 초기화"""
        try:
            # 기존 컬렉션 확인
            if self.client.schema.exists(self.collection_name):
                logger.info(f"컬렉션 '{self.collection_name}' 이미 존재")
                return
            
            # 스키마 정의
            schema = {
                "class": self.collection_name,
                "description": "AI 시스템 지식 베이스",
                "properties": [
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "텍스트 내용"
                    },
                    {
                        "name": "title",
                        "dataType": ["string"],
                        "description": "제목"
                    },
                    {
                        "name": "category",
                        "dataType": ["string"],
                        "description": "카테고리"
                    },
                    {
                        "name": "source",
                        "dataType": ["string"],
                        "description": "출처"
                    },
                    {
                        "name": "metadata",
                        "dataType": ["object"],
                        "description": "메타데이터"
                    },
                    {
                        "name": "created_at",
                        "dataType": ["date"],
                        "description": "생성일시"
                    }
                ],
                "vectorizer": "none"  # 수동으로 벡터 제공
            }
            
            # 스키마 생성
            self.client.schema.create_class(schema)
            logger.info(f"스키마 '{self.collection_name}' 생성 완료")
            
        except Exception as e:
            logger.error(f"스키마 초기화 실패: {e}")
            raise
    
    async def add_document(
        self, 
        content: str, 
        title: str = "", 
        category: str = "general", 
        source: str = "", 
        metadata: Dict[str, Any] = None
    ) -> str:
        """문서 추가"""
        try:
            # 임베딩 생성
            embedding = self.embedding_model.encode(content)
            
            # 문서 데이터 준비
            doc_data = {
                "content": content,
                "title": title,
                "category": category,
                "source": source,
                "metadata": metadata or {},
                "created_at": "2024-01-01T00:00:00Z"  # 실제로는 현재 시간
            }
            
            # Weaviate에 추가
            doc_id = self.client.data_object.create(
                data_object=doc_data,
                class_name=self.collection_name,
                vector=embedding.tolist()
            )
            
            logger.info(f"문서 추가 완료: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"문서 추가 실패: {e}")
            raise
    
    async def search(
        self, 
        query: str, 
        limit: int = 5, 
        category: Optional[str] = None
    ) -> List[SearchResult]:
        """벡터 검색"""
        try:
            # 쿼리 임베딩 생성
            query_embedding = self.embedding_model.encode(query)
            
            # 검색 쿼리 구성
            near_vector = {"vector": query_embedding.tolist()}
            
            # 카테고리 필터링
            where_filter = None
            if category:
                where_filter = {
                    "path": ["category"],
                    "operator": "Equal",
                    "valueString": category
                }
            
            # Weaviate 검색
            result = (
                self.client.query
                .get(self.collection_name, ["content", "title", "category", "source", "metadata"])
                .with_near_vector(near_vector)
                .with_limit(limit)
                .with_additional(["certainty", "distance"])
            )
            
            if where_filter:
                result = result.with_where(where_filter)
            
            response = result.do()
            
            # 결과 파싱
            search_results = []
            if "data" in response and "Get" in response["data"]:
                for item in response["data"]["Get"][self.collection_name]:
                    search_results.append(SearchResult(
                        text=item["content"],
                        score=item["_additional"]["certainty"],
                        metadata={
                            "title": item.get("title", ""),
                            "category": item.get("category", ""),
                            "source": item.get("source", ""),
                            "metadata": item.get("metadata", {})
                        }
                    ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"벡터 검색 실패: {e}")
            return []
    
    async def search_by_vector(
        self, 
        vector: List[float], 
        limit: int = 5
    ) -> List[SearchResult]:
        """벡터로 직접 검색"""
        try:
            near_vector = {"vector": vector}
            
            result = (
                self.client.query
                .get(self.collection_name, ["content", "title", "category", "source", "metadata"])
                .with_near_vector(near_vector)
                .with_limit(limit)
                .with_additional(["certainty"])
                .do()
            )
            
            search_results = []
            if "data" in result and "Get" in result["data"]:
                for item in result["data"]["Get"][self.collection_name]:
                    search_results.append(SearchResult(
                        text=item["content"],
                        score=item["_additional"]["certainty"],
                        metadata={
                            "title": item.get("title", ""),
                            "category": item.get("category", ""),
                            "source": item.get("source", ""),
                            "metadata": item.get("metadata", {})
                        }
                    ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"벡터 검색 실패: {e}")
            return []
    
    async def get_average_embedding(self, texts: List[str]) -> List[float]:
        """여러 텍스트의 평균 임베딩 계산"""
        try:
            embeddings = self.embedding_model.encode(texts)
            avg_embedding = np.mean(embeddings, axis=0)
            return avg_embedding.tolist()
            
        except Exception as e:
            logger.error(f"평균 임베딩 계산 실패: {e}")
            return []
    
    async def bulk_add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """문서 일괄 추가"""
        try:
            doc_ids = []
            
            # 배치로 임베딩 생성
            contents = [doc["content"] for doc in documents]
            embeddings = self.embedding_model.encode(contents)
            
            # Weaviate에 일괄 추가
            with self.client.batch(batch_size=100) as batch:
                for i, doc in enumerate(documents):
                    doc_data = {
                        "content": doc["content"],
                        "title": doc.get("title", ""),
                        "category": doc.get("category", "general"),
                        "source": doc.get("source", ""),
                        "metadata": doc.get("metadata", {}),
                        "created_at": "2024-01-01T00:00:00Z"
                    }
                    
                    doc_id = batch.add_data_object(
                        data_object=doc_data,
                        class_name=self.collection_name,
                        vector=embeddings[i].tolist()
                    )
                    doc_ids.append(doc_id)
            
            logger.info(f"{len(documents)}개 문서 일괄 추가 완료")
            return doc_ids
            
        except Exception as e:
            logger.error(f"문서 일괄 추가 실패: {e}")
            raise
    
    async def delete_document(self, doc_id: str) -> bool:
        """문서 삭제"""
        try:
            self.client.data_object.delete(
                uuid=doc_id,
                class_name=self.collection_name
            )
            logger.info(f"문서 삭제 완료: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"문서 삭제 실패: {e}")
            return False
    
    async def update_document(
        self, 
        doc_id: str, 
        content: str = None, 
        metadata: Dict[str, Any] = None
    ) -> bool:
        """문서 업데이트"""
        try:
            update_data = {}
            
            if content:
                # 새로운 임베딩 생성
                embedding = self.embedding_model.encode(content)
                update_data["content"] = content
                
                # 벡터도 함께 업데이트
                self.client.data_object.update(
                    uuid=doc_id,
                    class_name=self.collection_name,
                    data_object=update_data,
                    vector=embedding.tolist()
                )
            elif metadata:
                update_data.update(metadata)
                self.client.data_object.update(
                    uuid=doc_id,
                    class_name=self.collection_name,
                    data_object=update_data
                )
            
            logger.info(f"문서 업데이트 완료: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"문서 업데이트 실패: {e}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """컬렉션 통계 조회"""
        try:
            # 총 문서 수
            count_result = (
                self.client.query
                .aggregate(self.collection_name)
                .with_meta_count()
                .do()
            )
            
            total_docs = 0
            if "data" in count_result and "Aggregate" in count_result["data"]:
                total_docs = count_result["data"]["Aggregate"][self.collection_name][0]["meta"]["count"]
            
            # 카테고리별 분포
            category_result = (
                self.client.query
                .aggregate(self.collection_name)
                .with_group_by(["category"])
                .with_meta_count()
                .do()
            )
            
            categories = {}
            if "data" in category_result and "Aggregate" in category_result["data"]:
                for group in category_result["data"]["Aggregate"][self.collection_name]:
                    category = group["groupedBy"]["value"]
                    count = group["meta"]["count"]
                    categories[category] = count
            
            return {
                "total_documents": total_docs,
                "categories": categories,
                "embedding_model": self.embedding_model_name
            }
            
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")
            return {"total_documents": 0, "categories": {}, "embedding_model": self.embedding_model_name}
    
    async def health_check(self) -> bool:
        """Weaviate 연결 상태 확인"""
        try:
            if not self.client:
                return False
            
            # 간단한 쿼리로 연결 확인
            result = self.client.query.aggregate(self.collection_name).with_meta_count().do()
            return "data" in result
            
        except Exception as e:
            logger.error(f"Health check 실패: {e}")
            return False
    
    async def rebuild_index(self) -> bool:
        """인덱스 재구성 (필요시)"""
        try:
            # Weaviate는 자동으로 인덱스를 관리하므로
            # 특별한 재구성이 필요하지 않음
            logger.info("인덱스 상태 양호")
            return True
            
        except Exception as e:
            logger.error(f"인덱스 재구성 실패: {e}")
            return False