import faiss
import numpy as np
import pickle
import os

class HealthVectorDB:
    def __init__(self, index_path: str = "vector_db/health_index.faiss", 
                 metadata_path: str = "vector_db/health_metadata.pkl"):
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
            # Create empty index (384 dimensions for MiniLM-L6-v2)
            self.index = faiss.IndexFlatIP(384)
            self.metadata = []
    
    def search(self, query_embedding: np.ndarray, top_k: int = 3):
        """Search for similar documents"""
        if self.index.ntotal == 0:
            # Return mock results if no documents
            return self._get_mock_results()
        
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:  # Valid index
                results.append({
                    'text': self.metadata[idx]['text'],
                    'score': float(score),
                    'metadata': self.metadata[idx].get('metadata', {})
                })
        
        return results
    
    def _get_mock_results(self):
        """Return mock health-related documents for testing"""
        return [
            {
                'text': '균형 잡힌 식단은 건강한 생활의 기초입니다. 다양한 영양소를 골고루 섭취하세요.',
                'score': 0.95,
                'metadata': {'source': 'health_guide'}
            },
            {
                'text': '규칙적인 운동은 면역력 강화와 스트레스 해소에 도움이 됩니다.',
                'score': 0.87,
                'metadata': {'source': 'fitness_tips'}
            },
            {
                'text': '충분한 수면은 신체 회복과 정신 건강에 필수적입니다.',
                'score': 0.82,
                'metadata': {'source': 'wellness_basics'}
            }
        ]

# Create global instance
_health_db = HealthVectorDB()

def search(query_embedding: np.ndarray, top_k: int = 3):
    return _health_db.search(query_embedding, top_k)
