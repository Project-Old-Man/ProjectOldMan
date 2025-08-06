import numpy as np

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", use_mock: bool = False):
        self.use_mock = use_mock
        self.model = None
        
        if not use_mock:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(model_name)
            except ImportError:
                print("sentence-transformers not installed, using mock embeddings")
                self.use_mock = True
    
    def encode(self, text: str) -> np.ndarray:
        """Encode text into embeddings"""
        if self.use_mock:
            return self._mock_encode(text)
        
        return self.model.encode([text])[0]
    
    def encode_batch(self, texts: list) -> np.ndarray:
        """Encode multiple texts into embeddings"""
        if self.use_mock:
            return np.array([self._mock_encode(text) for text in texts])
        
        return self.model.encode(texts)
    
    def _mock_encode(self, text: str) -> np.ndarray:
        """Generate mock embedding for testing"""
        # Generate deterministic embedding based on text hash
        hash_val = hash(text) % 1000000
        np.random.seed(hash_val)
        return np.random.rand(384).astype('float32')
