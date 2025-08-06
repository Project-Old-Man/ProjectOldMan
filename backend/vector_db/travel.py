import faiss
import numpy as np
import pickle
import os

class TravelVectorDB:
    def __init__(self, index_path: str = "vector_db/travel_index.faiss", 
                 metadata_path: str = "vector_db/travel_metadata.pkl"):
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
        """Return mock travel-related documents for testing"""
        return [
            {
                'text': '여행 전 목적지의 날씨와 현지 문화를 미리 조사하는 것이 중요합니다.',
                'score': 0.92,
                'metadata': {'source': 'travel_planning'}
            },
            {
                'text': '여권, 비자, 항공권 등 필수 서류를 미리 준비하고 사본을 보관하세요.',
                'score': 0.88,
                'metadata': {'source': 'travel_documents'}
            },
            {
                'text': '여행자 보험 가입을 통해 예상치 못한 상황에 대비하세요.',
                'score': 0.85,
                'metadata': {'source': 'travel_safety'}
            }
        ]

_travel_db = TravelVectorDB()

def search(query_embedding: np.ndarray, top_k: int = 3):
    return _travel_db.search(query_embedding, top_k)
