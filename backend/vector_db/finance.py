import faiss
import numpy as np
import pickle
import os

class FinanceVectorDB:
    def __init__(self, index_path: str = "vector_db/finance_index.faiss", 
                 metadata_path: str = "vector_db/finance_metadata.pkl"):
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
        """Return mock finance-related documents for testing"""
        return [
            {
                'text': '분산 투자를 통해 위험을 줄이고 안정적인 수익을 추구하세요.',
                'score': 0.94,
                'metadata': {'source': 'investment_basics'}
            },
            {
                'text': '장기 투자 관점에서 시장의 단기 변동에 휘둘리지 마세요.',
                'score': 0.89,
                'metadata': {'source': 'investment_strategy'}
            },
            {
                'text': '투자 전 자신의 위험 성향과 투자 목표를 명확히 설정하세요.',
                'score': 0.86,
                'metadata': {'source': 'financial_planning'}
            }
        ]

_finance_db = FinanceVectorDB()

def search(query_embedding: np.ndarray, top_k: int = 3):
    return _finance_db.search(query_embedding, top_k)
