import asyncio
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from typing import Optional

class SimpleLLMService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
    
    async def initialize(self, model_name: str = "microsoft/DialoGPT-medium"):
        """모델 초기화"""
        try:
            print(f"🔄 모델 로딩 중: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            self.is_loaded = True
            print("✅ 모델 로딩 완료!")
            
        except Exception as e:
            print(f"❌ 모델 로딩 실패: {e}")
            self.is_loaded = False
    
    async def generate_response(self, prompt: str, max_length: int = 512) -> str:
        """텍스트 생성"""
        if not self.is_loaded:
            return "모델이 로드되지 않았습니다."
        
        try:
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + max_length,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    top_p=0.9
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response[len(prompt):].strip()
            
            return response if response else "죄송합니다. 적절한 답변을 생성할 수 없습니다."
            
        except Exception as e:
            return f"응답 생성 중 오류가 발생했습니다: {str(e)}"

# 전역 LLM 서비스 인스턴스
llm_service = SimpleLLMService()
