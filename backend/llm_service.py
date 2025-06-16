import asyncio
import aiohttp
import json
import os
import logging
from typing import AsyncGenerator, Dict, Any, List, Optional
from vllm import AsyncLLMEngine, AsyncEngineArgs, SamplingParams
from transformers import AutoTokenizer

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.engine = None
        self.tokenizer = None
        self.model_name = os.getenv("LLM_MODEL", "microsoft/DialoGPT-medium")
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
        """vLLM 엔진 초기화"""
        try:
            logger.info(f"LLM 모델 로딩 중: {self.model_name}")
            
            # vLLM 엔진 설정
            engine_args = AsyncEngineArgs(
                model=self.model_name,
                tensor_parallel_size=self.tensor_parallel_size,
                gpu_memory_utilization=self.gpu_memory_utilization,
                max_model_len=2048,
                disable_log_stats=False
            )
            
            # 엔진 생성
            self.engine = AsyncLLMEngine.from_engine_args(engine_args)
            
            # 토크나이저 로드
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info("LLM 초기화 완료")
            
        except Exception as e:
            logger.error(f"LLM 초기화 실패: {e}")
            # 백업으로 외부 API 사용
            if self.openai_api_key or self.hf_api_key:
                logger.info("외부 API를 백업으로 사용합니다")
            else:
                raise
    
    async def shutdown(self):
        """리소스 정리"""
        if self.engine:
            # vLLM 엔진은 자동으로 정리됨
            self.engine = None
        logger.info("LLM 서비스 종료")
    
    def is_ready(self) -> bool:
        """서비스 준비 상태 확인"""
        return self.engine is not None or self.openai_api_key or self.hf_api_key
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """단일 응답 생성"""
        try:
            if self.engine:
                return await self._generate_with_vllm(prompt, **kwargs)
            elif self.openai_api_key:
                return await self._generate_with_openai(prompt, **kwargs)
            elif self.hf_api_key:
                return await self._generate_with_huggingface(prompt, **kwargs)
            else:
                raise RuntimeError("사용 가능한 LLM 서비스가 없습니다")
                
        except Exception as e:
            logger.error(f"응답 생성 실패: {e}")
            return "죄송합니다. 현재 서비스에 문제가 있어 응답을 생성할 수 없습니다."
    
    async def stream_response(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """스트리밍 응답 생성"""
        try:
            if self.engine:
                async for chunk in self._stream_with_vllm(prompt, **kwargs):
                    yield chunk
            elif self.openai_api_key:
                async for chunk in self._stream_with_openai(prompt, **kwargs):
                    yield chunk
            else:
                # 스트리밍 미지원시 일반 응답을 청크로 분할
                response = await self.generate_response(prompt, **kwargs)
                words = response.split()
                for i, word in enumerate(words):
                    yield word + (" " if i < len(words) - 1 else "")
                    await asyncio.sleep(0.05)  # 자연스러운 타이핑 효과
                    
        except Exception as e:
            logger.error(f"스트리밍 응답 실패: {e}")
            yield "죄송합니다. 현재 서비스에 문제가 있어 응답을 생성할 수 없습니다."
    
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
        return {
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "engine_type": "vLLM" if self.engine else "API",
            "ready": self.is_ready()
        }