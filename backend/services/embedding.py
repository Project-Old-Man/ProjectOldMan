import logging
from typing import List
import os
import hashlib

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.embedding_dim = 384
        self.use_mock = True  # 호환성 문제로 일시적 Mock 모드
        
        # 환경변수로 실제 모델 강제 시도 가능
        force_real = os.getenv("FORCE_REAL_EMBEDDING", "false").lower() == "true"
        
        if force_real:
            logger.info(f"🔄 실제 임베딩 모델 로딩 시작: {model_name}")
            try:
                self._load_real_model()
                self.use_mock = False
            except Exception as e:
                logger.error(f"❌ 실제 임베딩 실패, Mock 모드로 전환: {e}")
                self.use_mock = True
        else:
            logger.info(f"🤖 Mock 임베딩 모드로 시작 (호환성 우선)")
    
    def _load_real_model(self):
        """실제 임베딩 모델 로딩"""
        import numpy as np
        numpy_version = np.__version__
        logger.info(f"📊 NumPy 버전: {numpy_version}")
        
        import torch
        logger.info(f"🔥 PyTorch 버전: {torch.__version__}")
        
        from sentence_transformers import SentenceTransformer
        logger.info("📚 SentenceTransformers 라이브러리 확인됨")
        
        logger.info(f"🔄 실제 임베딩 모델 로딩 중: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        
        test_texts = ["테스트 문장입니다."]
        test_embeddings = self.model.encode(test_texts, convert_to_numpy=True)
        
        if test_embeddings is not None and len(test_embeddings) > 0:
            self.embedding_dim = test_embeddings.shape[1]
            logger.info(f"✅ 실제 임베딩 모델 로딩 성공! 차원: {self.embedding_dim}")
        else:
            raise RuntimeError("테스트 인코딩 실패")
    
    def encode(self, texts: List[str]):
        """텍스트를 벡터로 변환"""
        if self.use_mock:
            return self._mock_encode(texts)
        
        if not self.model:
            logger.warning("⚠️ 실제 모델이 없어 Mock 모드로 전환")
            self.use_mock = True
            return self._mock_encode(texts)
        
        try:
            logger.info(f"🔄 실제 임베딩 인코딩: {len(texts)}개 텍스트")
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            logger.info(f"✅ 실제 임베딩 완료: {embeddings.shape}")
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"❌ 실제 임베딩 실패, Mock으로 대체: {e}")
            self.use_mock = True
            return self._mock_encode(texts)
    
    def _mock_encode(self, texts: List[str]) -> List[List[float]]:
        """Mock 임베딩 생성 (호환성 보장)"""
        logger.info(f"🤖 Mock 임베딩 생성: {len(texts)}개 텍스트")
        
        embeddings = []
        for text in texts:
            embedding = self._text_to_vector(text)
            embeddings.append(embedding)
        
        return embeddings
    
    def _text_to_vector(self, text: str) -> List[float]:
        """텍스트를 일관된 벡터로 변환 (Hash 기반)"""
        # SHA-256 해시를 사용하여 더 안정적인 벡터 생성
        hash_obj = hashlib.sha256(text.encode('utf-8'))
        hash_bytes = hash_obj.digest()
        
        # 해시를 float 값으로 변환
        vector = []
        for i in range(0, len(hash_bytes), 4):
            chunk = hash_bytes[i:i+4]
            if len(chunk) == 4:
                int_val = int.from_bytes(chunk, byteorder='big')
                float_val = (int_val / (2**32 - 1)) * 2 - 1  # -1 ~ 1 정규화
                vector.append(float_val)
        
        # 벡터 길이를 384로 맞춤
        while len(vector) < self.embedding_dim:
            # 기존 벡터를 반복하여 길이 맞춤
            remaining = self.embedding_dim - len(vector)
            vector.extend(vector[:min(len(vector), remaining)])
        
        vector = vector[:self.embedding_dim]
        
        # L2 정규화
        norm = sum(x*x for x in vector) ** 0.5
        if norm > 0:
            vector = [x / norm for x in vector]
        
        return vector
    
    def get_embedding_dim(self) -> int:
        """임베딩 차원 수 반환"""
        return self.embedding_dim
    
    def is_using_real_model(self) -> bool:
        """실제 모델 사용 여부 반환"""
        return not self.use_mock
    
    def get_status(self) -> dict:
        """임베딩 서비스 상태 반환"""
        return {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "using_real_model": not self.use_mock,
            "status": "real" if not self.use_mock else "mock",
            "compatibility_note": "Mock 모드 (PyTorch 호환성 문제)" if self.use_mock else "실제 모델"
        }
