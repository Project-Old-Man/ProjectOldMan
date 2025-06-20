import json
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self, models_config_path: str = "./model/models.json"):
        self.models_config_path = models_config_path
        self.models_config = self._load_models_config()
        self.active_model = self.models_config.get("active_model", "default")
        
    def _load_models_config(self) -> Dict[str, Any]:
        """모델 설정 파일 로드"""
        try:
            if os.path.exists(self.models_config_path):
                with open(self.models_config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"모델 설정 파일을 찾을 수 없습니다: {self.models_config_path}")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"모델 설정 파일 로드 실패: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """기본 설정 반환"""
        return {
            "models": {
                "default": {
                    "name": "microsoft/DialoGPT-medium",
                    "type": "huggingface",
                    "description": "기본 다이얼로그 모델",
                    "parameters": {
                        "max_tokens": 512,
                        "temperature": 0.7,
                        "top_p": 0.9
                    },
                    "supported_tasks": ["text-generation", "chat"],
                    "language": "en",
                    "domain": "general"
                }
            },
            "active_model": "default",
            "model_switching": {
                "enabled": True,
                "auto_switch_by_domain": True
            }
        }
    
    def get_active_model_config(self) -> Dict[str, Any]:
        """현재 활성 모델 설정 반환"""
        return self.models_config["models"].get(self.active_model, {})
    
    def get_model_by_page(self, page: str) -> Optional[str]:
        """페이지별 고정 모델 찾기"""
        page_mapping = self.models_config.get("page_mapping", {})
        return page_mapping.get(page, self.active_model)
    
    def get_model_by_domain(self, domain: str) -> Optional[str]:
        """도메인에 맞는 모델 찾기 (페이지 매핑 우선)"""
        # 페이지 매핑이 있으면 그것을 우선 사용
        page_mapping = self.models_config.get("page_mapping", {})
        if domain in page_mapping:
            return page_mapping[domain]
        
        # 페이지 매핑이 없으면 도메인 기반 선택
        if not self.models_config["model_switching"]["auto_switch_by_domain"]:
            return self.active_model
            
        for model_id, model_config in self.models_config["models"].items():
            if model_config.get("domain") == domain:
                return model_id
        return self.active_model
    
    def get_api_config(self, model_id: str) -> Dict[str, str]:
        """원격 API 설정 반환"""
        model_config = self.models_config["models"].get(model_id, {})
        return {
            "api_url": model_config.get("api_url", ""),
            "api_key": model_config.get("api_key", ""),
            "type": model_config.get("type", "local")
        }

    def switch_model(self, model_id: str) -> bool:
        """모델 전환"""
        if model_id not in self.models_config["models"]:
            logger.error(f"모델을 찾을 수 없습니다: {model_id}")
            return False
        
        self.active_model = model_id
        self.models_config["active_model"] = model_id
        
        # 설정 파일 업데이트
        try:
            with open(self.models_config_path, 'w', encoding='utf-8') as f:
                json.dump(self.models_config, f, indent=2, ensure_ascii=False)
            logger.info(f"모델 전환 완료: {model_id}")
            return True
        except Exception as e:
            logger.error(f"모델 설정 저장 실패: {e}")
            return False
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """사용 가능한 모델 목록 반환"""
        models = []
        for model_id, config in self.models_config["models"].items():
            model_info = {
                "id": model_id,
                "name": config["name"],
                "type": config["type"],
                "description": config["description"],
                "language": config.get("language", "unknown"),
                "domain": config.get("domain", "general"),
                "is_active": model_id == self.active_model
            }
            models.append(model_info)
        return models
    
    def validate_model_path(self, model_path: str) -> bool:
        """모델 경로 유효성 검사"""
        if model_path.startswith("./") or model_path.startswith("/"):
            # 로컬 모델 경로 확인
            full_path = os.path.join(os.getcwd(), model_path.lstrip("./"))
            return os.path.exists(full_path)
        else:
            # HuggingFace 모델명은 항상 유효하다고 가정
            return True
    
    def get_model_parameters(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """모델 파라미터 반환"""
        if model_id is None:
            model_id = self.active_model
        
        model_config = self.models_config["models"].get(model_id, {})
        return model_config.get("parameters", {})
    
    def add_model(self, model_id: str, model_config: Dict[str, Any]) -> bool:
        """새 모델 추가"""
        try:
            self.models_config["models"][model_id] = model_config
            
            # 설정 파일 저장
            with open(self.models_config_path, 'w', encoding='utf-8') as f:
                json.dump(self.models_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"모델 추가 완료: {model_id}")
            return True
        except Exception as e:
            logger.error(f"모델 추가 실패: {e}")
            return False
    
    def remove_model(self, model_id: str) -> bool:
        """모델 제거"""
        if model_id == "default":
            logger.error("기본 모델은 제거할 수 없습니다")
            return False
        
        if model_id not in self.models_config["models"]:
            logger.error(f"모델을 찾을 수 없습니다: {model_id}")
            return False
        
        try:
            del self.models_config["models"][model_id]
            
            # 현재 활성 모델이 제거된 모델이면 기본 모델로 전환
            if self.active_model == model_id:
                self.active_model = "default"
                self.models_config["active_model"] = "default"
            
            # 설정 파일 저장
            with open(self.models_config_path, 'w', encoding='utf-8') as f:
                json.dump(self.models_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"모델 제거 완료: {model_id}")
            return True
        except Exception as e:
            logger.error(f"모델 제거 실패: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """현재 모델 정보 반환"""
        active_config = self.get_active_model_config()
        return {
            "active_model": self.active_model,
            "model_name": active_config.get("name", ""),
            "model_type": active_config.get("type", ""),
            "description": active_config.get("description", ""),
            "language": active_config.get("language", ""),
            "domain": active_config.get("domain", ""),
            "parameters": active_config.get("parameters", {}),
            "available_models": len(self.models_config["models"]),
            "auto_switch_enabled": self.models_config["model_switching"]["auto_switch_by_domain"]
        } 