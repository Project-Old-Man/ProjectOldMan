import os
import asyncio
import logging
from llama_cpp import Llama

MODEL_PATH = "models/llama-3.2-korean-bllossom-3b-q4_k_m.gguf"
MODEL_NAME = "llama-3.2-korean-bllossom-3b-q4_k_m"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleLLMManager:
    def __init__(self):
        self.model = None
        self.use_mock = True
        self.model_info = {
            "name": MODEL_NAME,
            "path": MODEL_PATH,
            "status": "initializing",
            "loaded": False,
            "error_message": None
        }
        self._try_load_model()

    def _try_load_model(self):
        try:
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"모델 파일 없음: {MODEL_PATH}")

            self.model = Llama(
                model_path=MODEL_PATH,
                n_ctx=2048,
                n_threads=4,  # 환경에 맞게 조절
                verbose=False
            )

            self.model_info.update({
                "status": "loaded",
                "loaded": True,
                "error_message": None
            })
            self.use_mock = False
            logger.info("llama-cpp 모델 로딩 성공")

        except Exception as e:
            logger.error(f"모델 로딩 실패: {e}")
            # Add extra log if the error is related to unknown architecture
            if "unknown architecture" in str(e).lower():
                logger.error("❗ 모델 파일이 llama.cpp에서 지원하지 않는 아키텍처일 수 있습니다. 모델 파일과 llama.cpp 버전을 확인하세요.")
            self.model_info.update({
                "status": "load_error",
                "error_message": str(e)
            })
            self.use_mock = True

    async def generate_response(self, prompt: str, max_tokens: int = 256) -> str:
        if self.use_mock or not self.model:
            return await self._mock_response(prompt)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_generate, prompt, max_tokens)

    def _sync_generate(self, prompt: str, max_tokens: int) -> str:
        try:
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                repeat_penalty=1.1,
                stop=["Q:", "User:"]
            )
            result = response["choices"][0]["text"]
            return result.strip()
        except Exception as e:
            logger.error(f"추론 오류: {e}")
            return f"추론 오류: {e}"

    async def _mock_response(self, prompt: str) -> str:
        await asyncio.sleep(0.2)
        # If there was a model load error, include the error message in the mock response
        if self.model_info.get("error_message"):
            return f"[Mock] 질문: {prompt} (실제 모델이 로드되지 않았습니다. 오류: {self.model_info['error_message']})"
        return f"[Mock] 질문: {prompt} (실제 모델이 로드되지 않았습니다.)"

    def get_model_info(self):
        # Always include error_message if present
        return {
            **self.model_info,
            "is_mock": self.use_mock
        }

    def is_model_loaded(self):
        """Returns True if the model is loaded and usable, False otherwise."""
        return self.model_info.get("loaded", False)

    def get_status_message(self):
        """Returns a human-readable status message for UI or API."""
        if self.model_info["loaded"]:
            return "모델이 정상적으로 로드되었습니다."
        if self.model_info["error_message"]:
            return f"모델 로드 실패: {self.model_info['error_message']}"
        return "모델 초기화 중입니다."


# 싱글톤 인스턴스
_simple_llm_manager_instance = None

def get_llm_manager():
    global _simple_llm_manager_instance
    if _simple_llm_manager_instance is None:
        _simple_llm_manager_instance = SimpleLLMManager()
    return _simple_llm_manager_instance
