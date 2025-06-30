import asyncio
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import json
import os
from model_manager import ModelManager

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.model_manager = ModelManager()
        self.models = {}
        self.tokenizers = {}
        self.pipelines = {}
        self.executor = ThreadPoolExecutor(max_workers=4)  # 병렬 처리용
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
    async def load_models(self):
        """모든 모델을 비동기적으로 로드"""
        try:
            models_config = self.model_manager.get_models()
            
            # 병렬로 모델 로드
            tasks = []
            for domain, config in models_config.items():
                if config.get("type") == "local":
                    task = asyncio.create_task(self._load_single_model(domain, config))
                    tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks)
                logger.info(f"Loaded {len(self.models)} local models")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    async def _load_single_model(self, domain: str, config: Dict[str, Any]):
        """단일 모델 로드"""
        try:
            model_name = config["model_name"]
            logger.info(f"Loading model for {domain}: {model_name}")
            
            # 토크나이저 로드
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # 모델 로드 (CPU 최적화)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32,  # CPU용 float32
                low_cpu_mem_usage=True,
                device_map="auto" if self.device == "cuda" else None
            )
            
            # 파이프라인 생성
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=self.device,
                torch_dtype=torch.float32
            )
            
            self.models[domain] = model
            self.tokenizers[domain] = tokenizer
            self.pipelines[domain] = pipe
            
            logger.info(f"Successfully loaded model for {domain}")
            
        except Exception as e:
            logger.error(f"Error loading model for {domain}: {e}")
            raise
    
    async def generate_response(self, domain: str, prompt: str, max_length: int = 512) -> str:
        """도메인별 응답 생성 (병렬 처리 지원)"""
        try:
            models_config = self.model_manager.get_models()
            
            if domain not in models_config:
                raise ValueError(f"Unknown domain: {domain}")
            
            config = models_config[domain]
            
            if config.get("type") == "local":
                return await self._generate_local_response(domain, prompt, max_length)
            else:
                return await self._generate_remote_response(domain, prompt, config)
                
        except Exception as e:
            logger.error(f"Error generating response for {domain}: {e}")
            return f"Error: {str(e)}"
    
    async def _generate_local_response(self, domain: str, prompt: str, max_length: int) -> str:
        """로컬 모델로 응답 생성"""
        try:
            if domain not in self.pipelines:
                raise ValueError(f"Model not loaded for domain: {domain}")
            
            pipe = self.pipelines[domain]
            
            # ThreadPoolExecutor를 사용한 병렬 처리
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._run_pipeline,
                pipe,
                prompt,
                max_length
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in local generation for {domain}: {e}")
            return f"Error: {str(e)}"
    
    def _run_pipeline(self, pipe, prompt: str, max_length: int) -> str:
        """파이프라인 실행 (스레드에서 실행)"""
        try:
            result = pipe(
                prompt,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=pipe.tokenizer.eos_token_id
            )
            
            if result and len(result) > 0:
                generated_text = result[0]['generated_text']
                # 프롬프트 제거하고 생성된 부분만 반환
                response = generated_text[len(prompt):].strip()
                return response if response else "No response generated."
            else:
                return "No response generated."
                
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            return f"Error: {str(e)}"
    
    async def _generate_remote_response(self, domain: str, prompt: str, config: Dict[str, Any]) -> str:
        """원격 API로 응답 생성"""
        try:
            # 기존 원격 API 로직 유지
            import requests
            
            api_url = config.get("api_url")
            api_key = config.get("api_key")
            
            if not api_url:
                raise ValueError(f"No API URL configured for domain: {domain}")
            
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            data = {
                "prompt": prompt,
                "max_tokens": config.get("max_tokens", 512),
                "temperature": config.get("temperature", 0.7)
            }
            
            # 비동기 HTTP 요청
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                lambda: requests.post(api_url, json=data, headers=headers, timeout=30)
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response from API")
            else:
                return f"API Error: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error in remote generation for {domain}: {e}")
            return f"Error: {str(e)}"
    
    async def generate_batch_responses(self, requests: List[Dict[str, Any]]) -> List[str]:
        """배치 요청 처리 (병렬 처리)"""
        try:
            tasks = []
            for req in requests:
                domain = req.get("domain")
                prompt = req.get("prompt")
                max_length = req.get("max_length", 512)
                
                if domain and prompt:
                    task = asyncio.create_task(
                        self.generate_response(domain, prompt, max_length)
                    )
                    tasks.append(task)
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                return [str(result) if not isinstance(result, Exception) else f"Error: {result}" 
                       for result in results]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error in batch generation: {e}")
            return [f"Error: {str(e)}"] * len(requests)
    
    def get_loaded_models(self) -> List[str]:
        """로드된 모델 목록 반환"""
        return list(self.models.keys())
    
    def cleanup(self):
        """리소스 정리"""
        try:
            self.executor.shutdown(wait=True)
            for model in self.models.values():
                del model
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            logger.info("LLM service cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def is_ready(self) -> bool:
        # 원격 API만 사용하는 경우 항상 True 반환
        return True

# 전역 인스턴스
llm_service = LLMService()