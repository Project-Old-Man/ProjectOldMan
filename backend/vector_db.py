import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any, Optional
import os
import logging
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    text: str
    score: float
    metadata: Dict[str, Any]

class VectorDBManager:
    def __init__(self):
        self.embedding_model = None
        self.index = None
        self.documents = []  # List[Dict[str, Any]]
        self.vectors = None  # np.ndarray
        self.id_map = []     # List[int] (index to doc)
        self.next_id = 0
        self.embedding_model_name = os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

    async def connect(self):
        """FAISS 인덱스 및 임베딩 모델 초기화"""
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        self.index = None
        self.documents = []
        self.vectors = None
        self.id_map = []
        self.next_id = 0
        logger.info("FAISS 인덱스 및 임베딩 모델 초기화 완료")

    async def disconnect(self):
        self.embedding_model = None
        self.index = None
        self.documents = []
        self.vectors = None
        self.id_map = []
        logger.info("FAISS 인덱스 연결 종료")

    async def add_document(
        self,
        content: str,
        title: str = "",
        category: str = "general",
        source: str = "",
        metadata: Dict[str, Any] = None
    ) -> str:
        """문서 추가"""
        embedding = self.embedding_model.encode(content)
        doc = {
            "id": self.next_id,
            "content": content,
            "title": title,
            "category": category,
            "source": source,
            "metadata": metadata or {},
        }
        self.documents.append(doc)
        if self.vectors is None:
            self.vectors = np.array([embedding], dtype=np.float32)
        else:
            self.vectors = np.vstack([self.vectors, embedding])
        self.id_map.append(self.next_id)
        self.next_id += 1
        self._rebuild_index()
        logger.info(f"문서 추가 완료: {doc['id']}")
        return str(doc["id"])

    async def bulk_add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """문서 일괄 추가"""
        contents = [doc["content"] for doc in documents]
        embeddings = self.embedding_model.encode(contents)
        ids = []
        for i, doc in enumerate(documents):
            doc_id = self.next_id
            meta = doc.get("metadata", {})
            new_doc = {
                "id": doc_id,
                "content": doc["content"],
                "title": doc.get("title", ""),
                "category": doc.get("category", "general"),
                "source": doc.get("source", ""),
                "metadata": meta,
            }
            self.documents.append(new_doc)
            ids.append(str(doc_id))
            self.id_map.append(doc_id)
            self.next_id += 1
        if self.vectors is None:
            self.vectors = np.array(embeddings, dtype=np.float32)
        else:
            self.vectors = np.vstack([self.vectors, embeddings])
        self._rebuild_index()
        logger.info(f"{len(documents)}개 문서 일괄 추가 완료")
        return ids

    async def search(
        self,
        query: str,
        limit: int = 5,
        category: Optional[str] = None
    ) -> List[SearchResult]:
        """벡터 검색"""
        if self.index is None or self.vectors is None or len(self.documents) == 0:
            return []
        query_embedding = self.embedding_model.encode(query).astype(np.float32)
        D, I = self.index.search(np.expand_dims(query_embedding, 0), limit * 2)
        results = []
        for idx, dist in zip(I[0], D[0]):
            if idx == -1:
                continue
            doc = self.documents[idx]
            if category and doc["category"] != category:
                continue
            results.append(SearchResult(
                text=doc["content"],
                score=float(-dist),  # FAISS는 L2 거리(작을수록 유사), 음수로 변환
                metadata={
                    "title": doc.get("title", ""),
                    "category": doc.get("category", ""),
                    "source": doc.get("source", ""),
                    "metadata": doc.get("metadata", {})
                }
            ))
            if len(results) >= limit:
                break
        return results

    async def search_by_vector(
        self,
        vector: List[float],
        limit: int = 5
    ) -> List[SearchResult]:
        if self.index is None or self.vectors is None or len(self.documents) == 0:
            return []
        query_embedding = np.array(vector, dtype=np.float32)
        D, I = self.index.search(np.expand_dims(query_embedding, 0), limit * 2)
        results = []
        for idx, dist in zip(I[0], D[0]):
            if idx == -1:
                continue
            doc = self.documents[idx]
            results.append(SearchResult(
                text=doc["content"],
                score=float(-dist),
                metadata={
                    "title": doc.get("title", ""),
                    "category": doc.get("category", ""),
                    "source": doc.get("source", ""),
                    "metadata": doc.get("metadata", {})
                }
            ))
            if len(results) >= limit:
                break
        return results

    async def get_average_embedding(self, texts: List[str]) -> List[float]:
        embeddings = self.embedding_model.encode(texts)
        avg_embedding = np.mean(embeddings, axis=0)
        return avg_embedding.tolist()

    async def delete_document(self, doc_id: str) -> bool:
        try:
            doc_id = int(doc_id)
            idx = next(i for i, doc in enumerate(self.documents) if doc["id"] == doc_id)
            self.documents.pop(idx)
            self.vectors = np.delete(self.vectors, idx, axis=0)
            self.id_map.pop(idx)
            self._rebuild_index()
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
        try:
            doc_id = int(doc_id)
            idx = next(i for i, doc in enumerate(self.documents) if doc["id"] == doc_id)
            if content:
                self.documents[idx]["content"] = content
                embedding = self.embedding_model.encode(content)
                self.vectors[idx] = embedding
            if metadata:
                self.documents[idx]["metadata"].update(metadata)
            self._rebuild_index()
            logger.info(f"문서 업데이트 완료: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"문서 업데이트 실패: {e}")
            return False

    async def get_collection_stats(self) -> Dict[str, Any]:
        total_docs = len(self.documents)
        categories = {}
        for doc in self.documents:
            cat = doc.get("category", "general")
            categories[cat] = categories.get(cat, 0) + 1
        return {
            "total_documents": total_docs,
            "categories": categories,
            "embedding_model": self.embedding_model_name
        }

    async def health_check(self) -> bool:
        # 인메모리이므로 항상 True
        return True

    async def rebuild_index(self) -> bool:
        self._rebuild_index()
        return True

    def _rebuild_index(self):
        if self.vectors is not None and len(self.vectors) > 0:
            dim = self.vectors.shape[1]
            self.index = faiss.IndexFlatL2(dim)
            self.index.add(self.vectors)
        else:
            self.index = None