import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
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
    def __init__(self, db_url: str, dim=None, index_path="faiss.index", meta_path="faiss_meta.json"):
        """Initialize the VectorDBManager with a database URL."""
        self.db_url = db_url
        self.embedding_model_name = os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        # 임베딩 차원 자동 감지
        if dim is None:
            test_vec = self.embedding_model.encode("임베딩 차원 확인용")
            self.dim = test_vec.shape[-1]
        else:
            self.dim = dim
        self.index_path = index_path
        self.meta_path = meta_path
        self.index = faiss.IndexFlatL2(self.dim)
        self.vectors = []
        self.metadatas = []
        self._load()

    def _load(self):
        # 임베딩 모델 로드
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        # 인덱스 및 메타데이터 로드
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            logger.info(f"FAISS 인덱스 로드: {self.index_path}")
        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.metadatas = data.get("metadatas", [])
                self.vectors = [np.array(vec, dtype=np.float32) for vec in data.get("vectors", [])]
            logger.info(f"FAISS 메타데이터 로드: {self.meta_path}")
        else:
            self.metadatas = []
            self.vectors = []

    def _save(self):
        # 인덱스 및 메타데이터 저장
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "metadatas": self.metadatas,
                "vectors": [vec.tolist() for vec in self.vectors]
            }, f, ensure_ascii=False)
        logger.info("FAISS 인덱스/메타데이터 저장 완료")

    def add(self, content: str, title: str = "", category: str = "general", source: str = "", metadata: Dict[str, Any] = None) -> str:
        embedding = self.embedding_model.encode(content)
        self.index.add(np.array([embedding]).astype('float32'))
        doc = {
            "id": len(self.metadatas),
            "content": content,
            "title": title,
            "category": category,
            "source": source,
            "metadata": metadata or {},
        }
        self.vectors.append(embedding)
        self.metadatas.append(doc)
        self._save()
        logger.info(f"문서 추가: {doc['id']}")
        return str(doc["id"])

    def bulk_add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        contents = [doc["content"] for doc in documents]
        embeddings = self.embedding_model.encode(contents)
        ids = []
        for i, doc in enumerate(documents):
            doc_id = len(self.metadatas)
            meta = doc.get("metadata", {})
            new_doc = {
                "id": doc_id,
                "content": doc["content"],
                "title": doc.get("title", ""),
                "category": doc.get("category", "general"),
                "source": doc.get("source", ""),
                "metadata": meta,
            }
            self.index.add(np.array([embeddings[i]]).astype('float32'))
            self.vectors.append(embeddings[i])
            self.metadatas.append(new_doc)
            ids.append(str(doc_id))
        self._save()
        logger.info(f"{len(documents)}개 문서 일괄 추가 완료")
        return ids

    def search(self, query: str, limit: int = 5, category: Optional[str] = None) -> List[SearchResult]:
        if self.index.ntotal == 0 or not self.vectors:
            return []
        query_embedding = self.embedding_model.encode(query).astype(np.float32)
        D, I = self.index.search(np.array([query_embedding]).astype('float32'), limit * 2)
        results = []
        for idx, dist in zip(I[0], D[0]):
            if idx == -1 or idx >= len(self.metadatas):
                continue
            doc = self.metadatas[idx]
            if category and doc.get("category") != category:
                continue
            results.append(SearchResult(
                text=doc["content"],
                score=float(-dist),  # L2 거리(작을수록 유사), 음수로 변환
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

    def search_by_vector(self, vector: List[float], limit: int = 5) -> List[SearchResult]:
        if self.index.ntotal == 0 or not self.vectors:
            return []
        query_embedding = np.array(vector, dtype=np.float32)
        D, I = self.index.search(np.array([query_embedding]).astype('float32'), limit * 2)
        results = []
        for idx, dist in zip(I[0], D[0]):
            if idx == -1 or idx >= len(self.metadatas):
                continue
            doc = self.metadatas[idx]
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

    def get_average_embedding(self, texts: List[str]) -> List[float]:
        embeddings = self.embedding_model.encode(texts)
        avg_embedding = np.mean(embeddings, axis=0)
        return avg_embedding.tolist()

    def delete_document(self, doc_id: str) -> bool:
        try:
            doc_id = int(doc_id)
            idx = next(i for i, doc in enumerate(self.metadatas) if doc["id"] == doc_id)
            self.metadatas.pop(idx)
            self.vectors.pop(idx)
            # 인덱스 재구성
            self.index = faiss.IndexFlatL2(self.dim)
            if self.vectors:
                self.index.add(np.array(self.vectors).astype('float32'))
            self._save()
            logger.info(f"문서 삭제: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"문서 삭제 실패: {e}")
            return False

    def update_document(self, doc_id: str, content: str = None, metadata: Dict[str, Any] = None) -> bool:
        try:
            doc_id = int(doc_id)
            idx = next(i for i, doc in enumerate(self.metadatas) if doc["id"] == doc_id)
            if content:
                self.metadatas[idx]["content"] = content
                embedding = self.embedding_model.encode(content)
                self.vectors[idx] = embedding
            if metadata:
                self.metadatas[idx]["metadata"].update(metadata)
            # 인덱스 재구성
            self.index = faiss.IndexFlatL2(self.dim)
            if self.vectors:
                self.index.add(np.array(self.vectors).astype('float32'))
            self._save()
            logger.info(f"문서 업데이트: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"문서 업데이트 실패: {e}")
            return False

    def get_collection_stats(self) -> Dict[str, Any]:
        total_docs = len(self.metadatas)
        categories = {}
        for doc in self.metadatas:
            cat = doc.get("category", "general")
            categories[cat] = categories.get(cat, 0) + 1
        return {
            "total_documents": total_docs,
            "categories": categories,
            "embedding_model": self.embedding_model_name
        }

    def health_check(self) -> bool:
        return True

    def rebuild_index(self) -> bool:
        self.index = faiss.IndexFlatL2(self.dim)
        if self.vectors:
            self.index.add(np.array(self.vectors).astype('float32'))
        self._save()
        return True

    async def connect(self):
        """Establish a connection to the vector database."""
        try:
            # Check if the FAISS index file exists
            if os.path.exists(self.index_path):
                self.client = faiss.read_index(self.index_path)
                print(f"VectorDB connected successfully. Loaded index from {self.index_path}.")
            else:
                # Initialize a new FAISS index if the file does not exist
                self.client = faiss.IndexFlatL2(self.dim)
                print(f"VectorDB initialized with a new index (dim={self.dim}).")
        except Exception as e:
            print(f"Error connecting to VectorDB: {e}")
            raise

    async def disconnect(self):
        """Close the connection to the vector database."""
        try:
            if self.client:
                # FAISS does not require explicit disconnection
                self.client = None
                print("VectorDB disconnected successfully.")
        except Exception as e:
            print(f"Error disconnecting from VectorDB: {e}")
            raise