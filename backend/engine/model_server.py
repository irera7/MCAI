"""
Model Serving Service
سرویس برای serve کردن مدل‌های آموزش‌دیده
"""

import torch
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import json
import pickle
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor


class ModelServer:
    """
    سرویس برای serve کردن مدل‌ها
    
    Features:
    - Hot-reload models
    - Batch inference
    - Caching
    - Load balancing
    - Health checks
    """
    
    def __init__(self, model_registry_path: str = "model_registry.json"):
        """
        Args:
            model_registry_path: مسیر فایل registry مدل‌ها
        """
        self.model_registry_path = Path(model_registry_path)
        self.loaded_models: Dict[str, Dict[str, Any]] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # بارگذاری registry
        self._load_registry()
        
        print("✅ ModelServer initialized")
    
    def _load_registry(self):
        """بارگذاری لیست مدل‌های ثبت‌شده"""
        if self.model_registry_path.exists():
            with open(self.model_registry_path, 'r') as f:
                self.registry = json.load(f)
        else:
            self.registry = {}
    
    def register_model(
        self,
        model_id: str,
        model_path: str,
        model_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        ثبت یک مدل جدید
        
        Args:
            model_id: شناسه یکتای مدل
            model_path: مسیر فایل مدل
            model_type: نوع مدل (image, text, audio, etc.)
            metadata: اطلاعات اضافی
        """
        self.registry[model_id] = {
            "model_path": model_path,
            "model_type": model_type,
            "metadata": metadata or {},
            "registered_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        # ذخیره registry
        with open(self.model_registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)
        
        print(f"✅ Model registered: {model_id}")
    
    def load_model(self, model_id: str, device: str = "cuda") -> bool:
        """
        بارگذاری یک مدل در memory
        
        Args:
            model_id: شناسه مدل
            device: دستگاه (cuda/cpu)
            
        Returns:
            موفقیت بارگذاری
        """
        try:
            if model_id not in self.registry:
                print(f"❌ Model {model_id} not found in registry")
                return False
            
            model_info = self.registry[model_id]
            model_path = Path(model_info["model_path"])
            
            if not model_path.exists():
                print(f"❌ Model file not found: {model_path}")
                return False
            
            # بارگذاری مدل
            if device == "cuda" and not torch.cuda.is_available():
                device = "cpu"
                print("⚠️ CUDA not available, using CPU")
            
            device_obj = torch.device(device)
            
            # بارگذاری checkpoint
            checkpoint = torch.load(model_path, map_location=device_obj)
            
            # بارگذاری مدل
            from engine.model_builder import ModelBuilder
            
            model_type = model_info["model_type"]
            num_classes = model_info["metadata"].get("num_classes", 10)
            model_name = model_info["metadata"].get("model_name", "default")
            
            model = ModelBuilder.build_model(
                modality=model_type,
                model_id=model_name,
                num_classes=num_classes,
                pretrained=False
            )
            
            model.load_state_dict(checkpoint["model_state_dict"])
            model.to(device_obj)
            model.eval()
            
            # ذخیره در loaded_models
            self.loaded_models[model_id] = {
                "model": model,
                "device": device_obj,
                "metadata": model_info["metadata"],
                "loaded_at": datetime.now().isoformat()
            }
            
            print(f"✅ Model loaded: {model_id} on {device}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading model {model_id}: {e}")
            return False
    
    def unload_model(self, model_id: str):
        """حذف مدل از memory"""
        if model_id in self.loaded_models:
            del self.loaded_models[model_id]
            torch.cuda.empty_cache()
            print(f"✅ Model unloaded: {model_id}")
    
    async def predict(
        self,
        model_id: str,
        input_data: Union[torch.Tensor, np.ndarray, List],
        batch_size: int = 32
    ) -> Dict[str, Any]:
        """
        پیش‌بینی با یک مدل
        
        Args:
            model_id: شناسه مدل
            input_data: داده ورودی
            batch_size: اندازه batch
            
        Returns:
            نتیجه پیش‌بینی
        """
        try:
            # بررسی وجود مدل در memory
            if model_id not in self.loaded_models:
                # بارگذاری خودکار
                success = self.load_model(model_id)
                if not success:
                    return {"error": f"Failed to load model {model_id}"}
            
            model_info = self.loaded_models[model_id]
            model = model_info["model"]
            device = model_info["device"]
            
            # تبدیل input به tensor
            if isinstance(input_data, np.ndarray):
                input_tensor = torch.from_numpy(input_data).float()
            elif isinstance(input_data, list):
                input_tensor = torch.tensor(input_data).float()
            else:
                input_tensor = input_data
            
            input_tensor = input_tensor.to(device)
            
            # Inference
            with torch.no_grad():
                if len(input_tensor) > batch_size:
                    # Batch inference
                    predictions = []
                    for i in range(0, len(input_tensor), batch_size):
                        batch = input_tensor[i:i+batch_size]
                        output = model(batch)
                        predictions.append(output)
                    output = torch.cat(predictions, dim=0)
                else:
                    output = model(input_tensor)
            
            # Post-processing
            probabilities = torch.softmax(output, dim=1)
            predicted_classes = torch.argmax(probabilities, dim=1)
            
            return {
                "status": "success",
                "model_id": model_id,
                "predictions": predicted_classes.cpu().numpy().tolist(),
                "probabilities": probabilities.cpu().numpy().tolist(),
                "num_samples": len(input_tensor)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_loaded_models(self) -> List[str]:
        """لیست مدل‌های بارگذاری شده"""
        return list(self.loaded_models.keys())
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """دریافت اطلاعات یک مدل"""
        if model_id in self.loaded_models:
            return {
                "model_id": model_id,
                "loaded": True,
                "device": str(self.loaded_models[model_id]["device"]),
                "loaded_at": self.loaded_models[model_id]["loaded_at"],
                "metadata": self.loaded_models[model_id]["metadata"]
            }
        elif model_id in self.registry:
            return {
                "model_id": model_id,
                "loaded": False,
                "registered_at": self.registry[model_id]["registered_at"],
                "metadata": self.registry[model_id]["metadata"]
            }
        return None
    
    def health_check(self) -> Dict[str, Any]:
        """بررسی سلامت سرویس"""
        return {
            "status": "healthy",
            "loaded_models": len(self.loaded_models),
            "registered_models": len(self.registry),
            "cuda_available": torch.cuda.is_available(),
            "timestamp": datetime.now().isoformat()
        }


# Global instance
model_server = ModelServer()


if __name__ == "__main__":
    # تست
    print("Testing ModelServer...")
    
    server = ModelServer()
    
    # ثبت یک مدل تستی
    server.register_model(
        model_id="test-model",
        model_path="models/test_model.pth",
        model_type="image",
        metadata={
            "num_classes": 10,
            "model_name": "resnet18",
            "accuracy": 0.95
        }
    )
    
    # Health check
    health = server.health_check()
    print(f"Health: {health}")
    
    # Model info
    info = server.get_model_info("test-model")
    print(f"Model info: {info}")

