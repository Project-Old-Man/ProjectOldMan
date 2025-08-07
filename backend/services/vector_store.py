import logging
from typing import List, Dict, Any
import os

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, embedding_service):
        self.embedding_service = embedding_service
        self.use_faiss = False
        self.index = None
        self.documents = []
        self.document_metadata = []
        
        # 실제 FAISS 초기화 시도
        logger.info("🔄 FAISS 벡터 데이터베이스 초기화 시도...")
        self._init_faiss()
    
    def _init_faiss(self):
        """FAISS 초기화 (실패 시 간단 저장소 사용)"""
        try:
            import faiss
            import numpy as np
            logger.info("📚 FAISS 라이브러리 확인됨")
            
            # FAISS 인덱스 생성 (768차원으로 설정)
            dimension = self.embedding_service.get_embedding_dim()
            self.index = faiss.IndexFlatIP(dimension)  # Inner Product (코사인 유사도)
            self.use_faiss = True
            
            logger.info(f"✅ FAISS 벡터 데이터베이스 초기화 완료 (차원: {dimension})")
            
        except Exception as e:
            logger.warning(f"⚠️ FAISS 초기화 실패, 간단 벡터 저장소 사용: {e}")
            self.use_faiss = False
    
    def add_documents(self, texts: List[str], metadata: List[Dict[str, Any]]):
        """문서를 벡터 데이터베이스에 추가"""
        try:
            logger.info(f"📝 벡터 데이터베이스에 {len(texts)}개 문서 추가 중...")
            
            # 실제 임베딩 생성 (이미 normalize_embeddings=True로 정규화됨)
            embeddings = self.embedding_service.encode(texts)
            
            if self.use_faiss and embeddings:
                try:
                    import numpy as np
                    import faiss
                    
                    embeddings_array = np.array(embeddings, dtype=np.float32)
                    
                    # 임베딩이 이미 정규화되어 있으므로 추가 정규화 불필요
                    # (normalize_embeddings=True로 인해 이미 L2 정규화됨)
                    
                    # FAISS 인덱스에 추가
                    self.index.add(embeddings_array)
                    logger.info("✅ FAISS 인덱스에 문서 추가 완료")
                except Exception as e:
                    logger.warning(f"⚠️ FAISS 추가 실패: {e}")
            
            # 문서와 메타데이터 저장
            self.documents.extend(texts)
            self.document_metadata.extend(metadata)
            
            logger.info(f"✅ {len(texts)}개 문서 추가 완료")
            
        except Exception as e:
            logger.error(f"❌ 문서 추가 실패: {e}")
            raise e
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """쿼리와 유사한 문서 검색"""
        try:
            if len(self.documents) == 0:
                logger.warning("⚠️ 저장된 문서가 없습니다")
                return []
            
            logger.info(f"🔍 벡터 검색: '{query[:30]}...' (top_k={top_k})")
            
            # 실제 쿼리 임베딩 생성
            query_embedding = self.embedding_service.encode([query])
            if not query_embedding:
                logger.error("❌ 쿼리 임베딩 생성 실패")
                return []
            
            query_vec = query_embedding[0]
            
            if self.use_faiss and self.index:
                try:
                    results = self._faiss_search(query_vec, top_k)
                    if results:
                        logger.info(f"✅ FAISS 검색 완료: {len(results)}개 결과")
                        return results
                except Exception as e:
                    logger.warning(f"⚠️ FAISS 검색 실패: {e}")
            
            # 간단한 유사도 검색 (Fallback)
            results = self._simple_similarity_search(query_vec, top_k)
            logger.info(f"✅ 간단 검색 완료: {len(results)}개 결과")
            return results
            
        except Exception as e:
            logger.error(f"❌ 벡터 검색 실패: {e}")
            return []
    
    def _faiss_search(self, query_vec: List[float], top_k: int) -> List[Dict[str, Any]]:
        """FAISS를 사용한 검색"""
        import numpy as np
        import faiss
        
        query_array = np.array([query_vec], dtype=np.float32)
        # 쿼리 임베딩도 이미 정규화되어 있으므로 추가 정규화 불필요
        
        # FAISS 검색
        scores, indices = self.index.search(query_array, min(top_k, len(self.documents)))
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.documents) and idx >= 0:
                results.append({
                    "text": self.documents[idx],
                    "metadata": self.document_metadata[idx],
                    "score": float(score),
                    "rank": i + 1,
                    "search_type": "faiss"
                })
        
        return results
    
    def _simple_similarity_search(self, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """간단한 유사도 검색 (실제 임베딩 사용)"""
        similarities = []
        
        # 모든 문서와 유사도 계산
        for i, doc in enumerate(self.documents):
            try:
                doc_embeddings = self.embedding_service.encode([doc])
                if doc_embeddings:
                    doc_embedding = doc_embeddings[0]
                    similarity = self._cosine_similarity(query_embedding, doc_embedding)
                    similarities.append((similarity, i))
            except Exception as e:
                logger.warning(f"⚠️ 문서 {i} 유사도 계산 실패: {e}")
                similarities.append((0.0, i))
        
        # 유사도 순으로 정렬
        similarities.sort(reverse=True)
        
        # 상위 k개 결과 반환
        results = []
        for rank, (score, idx) in enumerate(similarities[:top_k]):
            results.append({
                "text": self.documents[idx],
                "metadata": self.document_metadata[idx],
                "score": float(score),
                "rank": rank + 1,
                "search_type": "simple"
            })
        
        return results
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """코사인 유사도 계산"""
        try:
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = sum(a * a for a in vec1) ** 0.5
            norm2 = sum(b * b for b in vec2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except:
            return 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """벡터 데이터베이스 통계 반환"""
        return {
            "total_documents": len(self.documents),
            "embedding_dimension": self.embedding_service.get_embedding_dim(),
            "using_faiss": self.use_faiss,
            "using_real_embeddings": self.embedding_service.is_using_real_model(),
            "embedding_status": self.embedding_service.get_status()
        }

