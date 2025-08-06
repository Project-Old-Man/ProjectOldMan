import os
import asyncio
import logging
from typing import Optional, Dict, Any
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMManager:
    def __init__(self, model_path: str = "models/tinyllama.gguf"):
        self.model_path = model_path
        self.llm = None
        self.use_mock = True  # 기본적으로 mock 모드로 시작
        self.model_info = {
            "name": "TinyLlama GGUF",
            "type": "gguf",
            "status": "initializing",
            "path": model_path,
            "loaded": False,
            "error_message": None
        }
        
        # 서버 시작 시 모델 로딩 시도
        self.load_local_model()
    
    def load_local_model(self) -> bool:
        """로컬 GGUF 모델 로딩 시도"""
        try:
            logger.info(f"🤖 모델 로딩 시도: {self.model_path}")
            
            # 1. 파일 존재 확인
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {self.model_path}")
            
            # 2. 파일 크기 확인
            file_size = os.path.getsize(self.model_path) / (1024 * 1024)  # MB
            logger.info(f"📁 모델 파일 크기: {file_size:.1f}MB")
            
            # 3. llama-cpp-python 임포트 시도
            try:
                from llama_cpp import Llama
                logger.info("✅ llama-cpp-python 라이브러리 확인됨")
            except ImportError as e:
                logger.error(f"❌ llama-cpp-python 설치 필요")
                logger.error("💡 설치 명령어: pip install llama-cpp-python")
                logger.error("💡 또는 CPU 최적화: pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu")
                raise ImportError("llama-cpp-python이 설치되지 않았습니다. 위의 명령어로 설치해주세요.")
            
            # 4. 모델 로딩 (CPU 최적화 설정 - 성능 개선)
            logger.info("🔄 모델 로딩 중... (CPU 모드, 시간이 걸릴 수 있습니다)")
            
            try:
                self.llm = Llama(
                    model_path=self.model_path,
                    n_ctx=4096,           # 컨텍스트 길이 증가 (모델 훈련 크기에 맞춤)
                    n_threads=4,          # CPU 스레드 수
                    n_batch=512,          # 배치 크기
                    verbose=False,        # 상세 로그 비활성화
                    use_mlock=False,      # 메모리 잠금 비활성화 (호환성)
                    use_mmap=True,        # 메모리 맵 사용 (성능 향상)
                    n_gpu_layers=0,       # GPU 사용 안함 (CPU 전용)
                    rope_scaling_type=None,  # RoPE 스케일링 비활성화
                    logits_all=False,     # 메모리 절약
                )
                logger.info("✅ GGUF 모델 로딩 완료!")
            except Exception as load_error:
                logger.error(f"❌ GGUF 모델 로딩 실패: {load_error}")
                raise load_error
            
            # 5. 테스트 추론으로 모델 검증
            logger.info("🧪 모델 테스트 추론 중...")
            try:
                test_response = self.llm(
                    "Hello",
                    max_tokens=10,
                    temperature=0.1,
                    echo=False
                )
                
                if test_response and test_response.get('choices'):
                    test_text = test_response['choices'][0]['text'].strip()
                    logger.info(f"✅ 모델 테스트 성공! 응답: '{test_text}'")
                    
                    self.use_mock = False
                    self.model_info.update({
                        "status": "loaded",
                        "loaded": True,
                        "error_message": None,
                        "file_size_mb": round(file_size, 1),
                        "test_response": test_text
                    })
                    return True
                else:
                    raise RuntimeError("모델 테스트 응답이 비어있습니다")
                    
            except Exception as test_error:
                logger.error(f"❌ 모델 테스트 실패: {test_error}")
                raise test_error
                
        except FileNotFoundError as e:
            logger.warning(f"⚠️ {e}")
            self.model_info.update({
                "status": "file_not_found",
                "error_message": str(e)
            })
            
        except ImportError as e:
            logger.warning(f"⚠️ {e}")
            self.model_info.update({
                "status": "dependency_missing", 
                "error_message": str(e)
            })
            
        except Exception as e:
            logger.error(f"❌ 모델 로딩 실패: {e}")
            self.model_info.update({
                "status": "load_error",
                "error_message": str(e)
            })
        
        # Fallback to mock mode
        logger.info("🔄 Mock 모드로 전환")
        self.model_info.update({
            "name": "Mock AI Assistant",
            "type": "mock"
        })
        return False
    
    async def generate_response(self, prompt: str, max_tokens: int = 256) -> str:
        """메인 응답 생성 함수"""
        if self.use_mock:
            return await self._generate_mock_response(prompt)
        
        if not self.llm:
            logger.error("❌ LLM 모델이 로드되지 않았습니다")
            return await self._generate_mock_response(prompt)
        
        try:
            # 비동기 실행 (CPU 집약적 작업을 별도 스레드에서)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self._generate_sync, 
                prompt, 
                max_tokens
            )
            return response
            
        except Exception as e:
            logger.error(f"❌ 추론 중 오류 발생: {e}")
            return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"
    
    def _generate_sync(self, prompt: str, max_tokens: int) -> str:
        """동기 추론 함수 (별도 스레드에서 실행됨)"""
        try:
            logger.info(f"🤖 추론 시작 (max_tokens: {max_tokens})")
            
            # 한국어 대화 형식 프롬프트 구성
            formatted_prompt = f"""사용자와의 대화입니다. 친절하고 도움이 되는 답변을 해주세요.

사용자: {prompt}
AI 어시스턴트:"""
            
            # 추론 실행
            output = self.llm(
                formatted_prompt,
                max_tokens=max_tokens,
                temperature=0.7,          # 창의성 조절
                top_p=0.9,               # 토큰 선택 다양성
                top_k=40,                # 상위 K개 토큰만 고려
                repeat_penalty=1.1,      # 반복 방지
                echo=False,              # 입력 프롬프트 제외
                stop=["사용자:", "User:", "\n\n", "AI 어시스턴트:", "Human:"]  # 중단 토큰
            )
            
            if output and output.get('choices') and len(output['choices']) > 0:
                response_text = output['choices'][0]['text'].strip()
                
                # 응답 후처리
                response_text = self._clean_response(response_text)
                
                logger.info(f"✅ 추론 완료 (응답 길이: {len(response_text)}자)")
                return response_text
            else:
                return "죄송합니다. 응답을 생성할 수 없었습니다."
                
        except Exception as e:
            logger.error(f"❌ 동기 추론 오류: {e}")
            return f"추론 중 오류가 발생했습니다: {str(e)}"
    
    def _clean_response(self, text: str) -> str:
        """응답 텍스트 정리"""
        # 불필요한 문자 제거
        text = text.strip()
        
        # 중복 줄바꿈 제거
        import re
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # 너무 긴 응답 자르기
        if len(text) > 500:
            text = text[:500] + "..."
        
        return text
    
    async def _generate_mock_response(self, prompt: str) -> str:
        """Mock 응답 생성"""
        await asyncio.sleep(0.5)  # 실제 추론 시간 시뮬레이션
        
        mock_prefix = "🤖 [Mock AI] "
        
        # 카테고리별 응답
        prompt_lower = prompt.lower()
        
        if any(keyword in prompt_lower for keyword in ["건강", "health", "혈압", "당뇨", "운동"]):
            return f"{mock_prefix}건강에 관한 질문이시군요. 균형 잡힌 식단과 규칙적인 운동이 중요합니다. 구체적인 증상이 있다면 의료진과 상담하시기 바랍니다."
            
        elif any(keyword in prompt_lower for keyword in ["여행", "travel", "제주도", "부산", "관광"]):
            return f"{mock_prefix}여행 계획을 세우고 계시는군요! 목적지의 날씨, 현지 문화, 필수 서류 등을 미리 확인하시고 안전한 여행 되시기 바랍니다."
            
        elif any(keyword in prompt_lower for keyword in ["투자", "investment", "주식", "부동산", "연금"]):
            return f"{mock_prefix}투자와 재정 관리에 대해 문의하셨군요. 분산 투자와 장기적 관점이 중요하며, 전문가와 상담하시는 것을 권합니다."
            
        elif any(keyword in prompt_lower for keyword in ["법률", "legal", "계약", "상속", "변호사"]):
            return f"{mock_prefix}법률 관련 문의사항이군요. 일반적인 정보는 제공드릴 수 있지만, 구체적인 사안은 변호사와 상담하시기 바랍니다."
            
        else:
            return f"{mock_prefix}안녕하세요! 질문에 대해 도움을 드리고 싶습니다. 더 구체적인 정보를 제공해주시면 더 정확한 답변을 드릴 수 있습니다."
    
    def get_model_info(self) -> Dict[str, Any]:
        """현재 모델 정보 반환"""
        return {
            **self.model_info,
            "loaded": self.llm is not None,
            "available_models": self._scan_available_models(),
            "is_mock": self.use_mock
        }
    
    def _scan_available_models(self) -> list:
        """사용 가능한 모델 파일 스캔"""
        models_dir = Path("models")
        available_models = []
        
        if models_dir.exists():
            for file_path in models_dir.glob("*"):
                if file_path.suffix.lower() in ['.gguf', '.bin', '.safetensors']:
                    try:
                        size_mb = file_path.stat().st_size / (1024 * 1024)
                        available_models.append({
                            "name": file_path.name,
                            "path": str(file_path),
                            "size_mb": round(size_mb, 1),
                            "extension": file_path.suffix
                        })
                    except Exception as e:
                        logger.warning(f"파일 정보 읽기 실패: {file_path} - {e}")
        
        return available_models
    
    def reload_model(self, new_model_path: Optional[str] = None) -> bool:
        """모델 재로딩"""
        if new_model_path:
            self.model_path = new_model_path
            self.model_info["path"] = new_model_path
        
        # 기존 모델 해제
        if self.llm:
            del self.llm
            self.llm = None
        
        return self.load_local_model()

# 전역 LLM 매니저 인스턴스
_llm_manager_instance = None

def get_llm_manager() -> LLMManager:
    """싱글톤 LLM 매니저 인스턴스 반환"""
    global _llm_manager_instance
    if _llm_manager_instance is None:
        _llm_manager_instance = LLMManager()
    return _llm_manager_instance
