import asyncio
import aiohttp
import json
import os
import logging
from typing import AsyncGenerator, Dict, Any, List, Optional
from model_manager import ModelManager

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.engine = None
        self.tokenizer = None
        self.model_manager = ModelManager()
        
        # 기본 설정
        self.max_tokens = int(os.getenv("MAX_TOKENS", "512"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.top_p = float(os.getenv("TOP_P", "0.9"))
        
        # vLLM 설정
        self.tensor_parallel_size = int(os.getenv("TENSOR_PARALLEL_SIZE", "1"))
        self.gpu_memory_utilization = float(os.getenv("GPU_MEMORY_UTILIZATION", "0.9"))
        
        # 외부 API 설정 (백업용)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        
    async def initialize(self):
        """원격 API 모델 초기화"""
        try:
            # 현재 활성 모델 설정 가져오기
            active_config = self.model_manager.get_active_model_config()
            model_name = active_config.get("name", "my-chat-model")
            model_type = active_config.get("type", "remote_api")
            
            logger.info(f"모델 초기화 중: {model_name} (타입: {model_type})")
            
            if model_type == "remote_api":
                # 원격 API 모델은 엔진 초기화 불필요
                logger.info(f"원격 API 모델 사용: {model_name}")
            else:
                logger.warning(f"지원하지 않는 모델 타입: {model_type}")
                
            logger.info("모델 초기화 완료")
            
        except Exception as e:
            logger.error(f"모델 초기화 실패: {e}")
            raise
    
    async def shutdown(self):
        """리소스 정리"""
        logger.info("모델 서비스 종료")
    
    def is_ready(self) -> bool:
        """서비스 준비 상태 확인"""
        try:
            active_config = self.model_manager.get_active_model_config()
            model_type = active_config.get("type", "remote_api")
            return model_type == "remote_api"
        except:
            return False
    
    async def generate_response(self, prompt: str, page: str = None, domain: str = "general", **kwargs) -> str:
        """응답 생성 - 당신의 모델만 사용"""
        try:
            # 페이지별 고정 모델 우선 선택
            if page:
                model_id = self.model_manager.get_model_by_page(page)
            else:
                # 페이지가 없으면 도메인 기반 선택
                model_id = self.model_manager.get_model_by_domain(domain)
            
            model_config = self.model_manager.models_config["models"].get(model_id, {})
            model_type = model_config.get("type", "remote_api")
            
            # 모델별 파라미터 적용
            model_params = model_config.get("parameters", {})
            kwargs = {**model_params, **kwargs}
            
            logger.info(f"사용 모델: {model_id} (타입: {model_type}, 페이지: {page})")
            
            if model_type == "remote_api":
                return await self._generate_with_remote_api(model_config, prompt, **kwargs)
            else:
                raise RuntimeError(f"지원하지 않는 모델 타입: {model_type}")
                
        except Exception as e:
            logger.error(f"응답 생성 실패: {e}")
            return f"모델 서비스 오류: {str(e)}"
    
    async def _generate_with_remote_api(self, model_config: Dict[str, Any], prompt: str, **kwargs) -> str:
        """원격 API로 응답 생성"""
        try:
            api_url = model_config.get("api_url")
            api_key = model_config.get("api_key", "")
            
            if not api_url:
                raise ValueError("API URL이 설정되지 않았습니다")
            
            headers = {
                "Content-Type": "application/json"
            }
            
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            # API 엔드포인트 결정
            if api_url.endswith("/"):
                api_url = api_url.rstrip("/")
            
            # 다양한 API 형식 지원
            data = {
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "top_p": kwargs.get("top_p", self.top_p)
            }
            
            # OpenAI 형식도 지원
            if "openai" in api_url.lower():
                data = {
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                    "temperature": kwargs.get("temperature", self.temperature)
                }
                endpoint = "/v1/chat/completions"
            else:
                endpoint = "/generate"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{api_url}{endpoint}",
                    headers=headers,
                    json=data,
                    timeout=30
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # 다양한 응답 형식 지원
                        if "choices" in result and len(result["choices"]) > 0:
                            # OpenAI 형식
                            return result["choices"][0]["message"]["content"].strip()
                        elif "response" in result:
                            # 커스텀 형식
                            return result["response"].strip()
                        elif "text" in result:
                            # 단순 텍스트 형식
                            return result["text"].strip()
                        else:
                            # JSON 전체를 문자열로 반환
                            return str(result).strip()
                    else:
                        error_text = await response.text()
                        logger.error(f"Remote API 오류 ({response.status}): {error_text}")
                        return "원격 모델 서버에서 오류가 발생했습니다."
                        
        except Exception as e:
            logger.error(f"Remote API 호출 실패: {e}")
            return "원격 모델 연결 실패"
    
    async def stream_response(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """스트리밍 응답 생성"""
        try:
            # 스트리밍 미지원시 일반 응답을 청크로 분할
            response = await self.generate_response(prompt, **kwargs)
            words = response.split()
            for i, word in enumerate(words):
                yield word + (" " if i < len(words) - 1 else "")
                await asyncio.sleep(0.05)  # 자연스러운 타이핑 효과
                    
        except Exception as e:
            logger.error(f"스트리밍 응답 실패: {e}")
            yield "스트리밍 중 오류가 발생했습니다."
    
    async def _generate_with_vllm(self, prompt: str, **kwargs) -> str:
        """vLLM으로 응답 생성"""
        # 샘플링 파라미터 설정
        sampling_params = SamplingParams(
            temperature=kwargs.get("temperature", self.temperature),
            top_p=kwargs.get("top_p", self.top_p),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            stop=[self.tokenizer.eos_token] if self.tokenizer else None
        )
        
        # 응답 생성
        results = await self.engine.generate(prompt, sampling_params, request_id=None)
        
        if results and len(results) > 0:
            return results[0].outputs[0].text.strip()
        else:
            return "응답을 생성할 수 없습니다."
    
    async def _stream_with_vllm(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """vLLM 스트리밍 응답"""
        sampling_params = SamplingParams(
            temperature=kwargs.get("temperature", self.temperature),
            top_p=kwargs.get("top_p", self.top_p),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            stop=[self.tokenizer.eos_token] if self.tokenizer else None
        )
        
        # 스트리밍 생성
        previous_text = ""
        async for output in self.engine.generate(prompt, sampling_params, request_id=None):
            current_text = output.outputs[0].text
            new_text = current_text[len(previous_text):]
            if new_text:
                yield new_text
                previous_text = current_text
    
    async def _generate_with_openai(self, prompt: str, **kwargs) -> str:
        """OpenAI API로 응답 생성"""
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "top_p": kwargs.get("top_p", self.top_p)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        return result["choices"][0]["message"]["content"].strip()
                    else:
                        logger.error(f"OpenAI API 오류: {result}")
                        return "OpenAI API 호출 중 오류가 발생했습니다."
                        
        except Exception as e:
            logger.error(f"OpenAI API 호출 실패: {e}")
            return "OpenAI API 호출 중 오류가 발생했습니다."
    
    async def _stream_with_openai(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """OpenAI API 스트리밍"""
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "stream": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            data_str = line[6:]  # 'data: ' 제거
                            if data_str == '[DONE]':
                                break
                            
                            try:
                                data_json = json.loads(data_str)
                                if 'choices' in data_json and len(data_json['choices']) > 0:
                                    delta = data_json['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            logger.error(f"OpenAI 스트리밍 실패: {e}")
            yield "스트리밍 중 오류가 발생했습니다."
    
    async def _generate_with_huggingface(self, prompt: str, **kwargs) -> str:
        """HuggingFace API로 응답 생성"""
        try:
            headers = {
                "Authorization": f"Bearer {self.hf_api_key}",
                "Content-Type": "application/json"
            }
            
            # HuggingFace Inference API 사용
            api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
            
            data = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": kwargs.get("max_tokens", self.max_tokens),
                    "temperature": kwargs.get("temperature", self.temperature),
                    "top_p": kwargs.get("top_p", self.top_p),
                    "do_sample": True
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers, json=data) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        if isinstance(result, list) and len(result) > 0:
                            generated_text = result[0].get("generated_text", "")
                            # 입력 프롬프트 제거하고 새로 생성된 부분만 반환
                            if generated_text.startswith(prompt):
                                return generated_text[len(prompt):].strip()
                            return generated_text.strip()
                        else:
                            return "응답을 생성할 수 없습니다."
                    else:
                        logger.error(f"HuggingFace API 오류: {result}")
                        return "HuggingFace API 호출 중 오류가 발생했습니다."
                        
        except Exception as e:
            logger.error(f"HuggingFace API 호출 실패: {e}")
            return "HuggingFace API 호출 중 오류가 발생했습니다."
    
    async def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """배치 응답 생성"""
        try:
            if self.engine:
                # vLLM 배치 처리
                sampling_params = SamplingParams(
                    temperature=kwargs.get("temperature", self.temperature),
                    top_p=kwargs.get("top_p", self.top_p),
                    max_tokens=kwargs.get("max_tokens", self.max_tokens)
                )
                
                results = await asyncio.gather(*[
                    self.engine.generate(prompt, sampling_params, request_id=None)
                    for prompt in prompts
                ])
                
                return [
                    result[0].outputs[0].text.strip() if result else "응답 생성 실패"
                    for result in results
                ]
            else:
                # 순차 처리
                responses = []
                for prompt in prompts:
                    response = await self.generate_response(prompt, **kwargs)
                    responses.append(response)
                return responses
                
        except Exception as e:
            logger.error(f"배치 생성 실패: {e}")
            return ["배치 처리 중 오류가 발생했습니다."] * len(prompts)
    
    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보 반환"""
        active_config = self.model_manager.get_active_model_config()
        return {
            "model_name": active_config.get("name", ""),
            "model_type": active_config.get("type", "remote_api"),
            "description": active_config.get("description", ""),
            "api_url": active_config.get("api_url", ""),
            "parameters": active_config.get("parameters", {}),
            "ready": self.is_ready()
        }