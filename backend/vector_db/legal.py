import faiss
import numpy as np
import pickle
import os

class LegalVectorDB:
    def __init__(self, index_path: str = "vector_db/legal_index.faiss", 
                 metadata_path: str = "vector_db/legal_metadata.pkl"):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = None
        self.metadata = []
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create empty one"""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatIP(384)
            self.metadata = []
    
    def search(self, query_embedding: np.ndarray, top_k: int = 3):
        """Search for similar documents"""
        if self.index.ntotal == 0:
            return self._get_mock_results()
        
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:
                results.append({
                    'text': self.metadata[idx]['text'],
                    'score': float(score),
                    'metadata': self.metadata[idx].get('metadata', {})
                })
        
        return results
    
    def _get_mock_results(self):
        """Return mock legal-related documents for testing"""
        return [
            {
                'text': '계약서 작성 시 조건과 책임 사항을 명확히 기재하는 것이 중요합니다.',
                'score': 0.91,
                'metadata': {'source': 'contract_law'}
            },
            {
                'text': '법률 문제 발생 시 전문 변호사와 상담하여 정확한 조언을 받으세요.',
                'score': 0.87,
                'metadata': {'source': 'legal_advice'}
            },
            {
                'text': '개인정보 보호법을 준수하여 타인의 정보를 안전하게 관리하세요.',
                'score': 0.84,
                'metadata': {'source': 'privacy_law'}
            }
        ]

_legal_db = LegalVectorDB()

def search(query_embedding: np.ndarray, top_k: int = 3):
    return _legal_db.search(query_embedding, top_k)
