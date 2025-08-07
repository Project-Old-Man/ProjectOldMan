import logging
from typing import List
import os
import hashlib

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name: str = "jhgan/ko-sroberta-multitask"):
        self.model_name = model_name
        self.model = None
        self.embedding_dim = 768  # ko-sroberta-multitask의 출력 차원
        self.use_mock = False  # 실제 모델을 기본으로 변경
        
        # 환경변수로 Mock 모드 강제 가능 (디버깅용)
        force_mock = os.getenv("USE_MOCK_EMBEDDING", "false").lower() == "true"
        
        if force_mock:
            logger.info(f"🤖 Mock 임베딩 모드 강제 활성화")
            self.use_mock = True
        else:
            logger.info(f"🔄 실제 임베딩 모델 로딩 시작: {model_name}")
            try:
                self._load_real_model()
                self.use_mock = False
                logger.info(f"✅ 실제 임베딩 모델 활성화 완료")
            except Exception as e:
                logger.error(f"❌ 실제 임베딩 실패, Mock 모드로 전환: {e}")
                logger.error(f"   상세 오류: {type(e).__name__}: {str(e)}")
                self.use_mock = True
    
    def _load_real_model(self):
        """실제 임베딩 모델 로딩 - 여러 모델 시도"""
        import numpy as np
        import torch
        
        # 의존성 문제 해결 시도
        self._fix_dependencies()
        
        # NLTK 설치 및 데이터 다운로드 시도
        self._setup_nltk()
        
        # 사용할 모델 리스트 (한국어 특화 모델을 최우선으로)
        models_to_try = [
            "jhgan/ko-sroberta-multitask",  # 한국어 특화 모델 (768차원)
            "intfloat/multilingual-e5-small",  # 다국어 모델
            "sentence-transformers/all-MiniLM-L6-v2",  # 안정적 대안
            "sentence-transformers/paraphrase-MiniLM-L6-v2", 
            "sentence-transformers/all-mpnet-base-v2",
            "sentence-transformers/distilbert-base-nli-mean-tokens"
        ]
        
        for model_name in models_to_try:
            try:
                logger.info(f"🔄 모델 시도 중: {model_name}")
                from sentence_transformers import SentenceTransformer
                
                # 모델 로딩 시 추가 설정
                self.model = SentenceTransformer(model_name, device='cpu')
                
                # 테스트 (normalize_embeddings=True로 코사인 유사도 최적화)
                test_embeddings = self.model.encode(["테스트"], convert_to_numpy=True, normalize_embeddings=True)
                self.embedding_dim = test_embeddings.shape[1]
                self.model_name = model_name  # 실제 로딩된 모델명으로 업데이트
                logger.info(f"✅ 모델 로딩 성공: {model_name} (차원: {self.embedding_dim})")
                return
                
            except Exception as e:
                logger.warning(f"⚠️ 모델 {model_name} 실패: {e}")
                logger.warning(f"   상세 오류: {type(e).__name__}")
                continue
        
        raise RuntimeError("모든 임베딩 모델 로딩 실패")
    
    def _fix_dependencies(self):
        """의존성 문제 자동 해결"""
        try:
            # tokenizers 버전 체크
            import tokenizers
            current_version = tokenizers.__version__
            logger.info(f"📦 현재 tokenizers 버전: {current_version}")
            
            # 버전이 0.13.0 이상이면 다운그레이드 필요
            if self._version_compare(current_version, "0.13.0") >= 0:
                logger.warning(f"⚠️ tokenizers {current_version}는 호환되지 않음, 다운그레이드 시도...")
                self._downgrade_tokenizers()
            else:
                logger.info(f"✅ tokenizers 버전 호환 확인됨")
                
        except ImportError:
            logger.warning("⚠️ tokenizers가 설치되지 않음, 설치 시도...")
            self._install_compatible_tokenizers()
        except Exception as e:
            logger.warning(f"⚠️ tokenizers 체크 실패: {e}")
        
        # 추가 의존성 체크 및 설치
        self._install_missing_dependencies()
    
    def _install_missing_dependencies(self):
        """누락된 의존성 자동 설치"""
        # 패키지명과 import명이 다른 경우 매핑
        package_mappings = {
            'threadpoolctl': 'threadpoolctl',
            'scikit-learn': 'sklearn',  # scikit-learn -> sklearn로 import
            'scipy': 'scipy',
            'numpy': 'numpy'
        }
        
        for package_name, import_name in package_mappings.items():
            try:
                __import__(import_name)
                logger.info(f"✅ {package_name} 확인됨")
            except ImportError:
                logger.warning(f"⚠️ {package_name} 누락, 설치 시도...")
                self._install_package(package_name)
    
    def _install_package(self, package_name: str):
        """개별 패키지 설치"""
        try:
            import subprocess
            import sys
            
            logger.info(f"🔄 {package_name} 설치 중...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package_name
            ])
            logger.info(f"✅ {package_name} 설치 완료")
            
        except Exception as e:
            logger.warning(f"⚠️ {package_name} 설치 실패: {e}")
    
    def _version_compare(self, version1: str, version2: str) -> int:
        """버전 비교 함수 (version1 > version2이면 1, 같으면 0, 작으면 -1)"""
        def version_to_tuple(v):
            return tuple(map(int, v.split('.')))
        
        v1 = version_to_tuple(version1)
        v2 = version_to_tuple(version2)
        
        if v1 > v2:
            return 1
        elif v1 < v2:
            return -1
        else:
            return 0
    
    def _downgrade_tokenizers(self):
        """tokenizers를 호환 가능한 버전으로 다운그레이드"""
        try:
            import subprocess
            import sys
            
            # 호환 가능한 tokenizers 버전 설치
            compatible_version = "tokenizers==0.12.1"
            logger.info(f"🔄 {compatible_version} 설치 중...")
            
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                compatible_version, "--force-reinstall", "--no-deps"
            ])
            
            logger.info("✅ tokenizers 다운그레이드 완료")
            
        except Exception as e:
            logger.warning(f"⚠️ tokenizers 다운그레이드 실패: {e}")
    
    def _install_compatible_tokenizers(self):
        """호환 가능한 tokenizers 설치"""
        try:
            import subprocess
            import sys
            
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "tokenizers==0.12.1"
            ])
            
            logger.info("✅ 호환 가능한 tokenizers 설치 완료")
            
        except Exception as e:
            logger.warning(f"⚠️ tokenizers 설치 실패: {e}")
    
    def _setup_nltk(self):
        """NLTK 설치 및 설정"""
        try:
            import nltk
            logger.info("📚 NLTK 이미 설치됨")
            
            # 필요한 NLTK 데이터 다운로드
            try:
                nltk.data.find('tokenizers/punkt')
                logger.info("✅ NLTK punkt 데이터 확인됨")
            except LookupError:
                logger.info("🔄 NLTK punkt 데이터 다운로드 중...")
                nltk.download('punkt', quiet=True)
                
        except ImportError:
            logger.warning("⚠️ NLTK가 설치되지 않음, 설치 시도...")
            try:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "nltk"])
                
                import nltk
                nltk.download('punkt', quiet=True)
                logger.info("✅ NLTK 설치 및 설정 완료")
            except Exception as e:
                logger.warning(f"⚠️ NLTK 자동 설치 실패: {e}")
                logger.warning("   일부 모델에서 문제가 발생할 수 있습니다")
    
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
            # normalize_embeddings=True로 코사인 유사도 최적화
            embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
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
        
        # 벡터 길이를 768로 맞춤 (ko-sroberta-multitask에 맞춰)
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
            "compatibility_note": "실제 모델" if not self.use_mock else "Mock 모드 (의존성 문제)"
        }

