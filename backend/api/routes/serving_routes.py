"""
API Gateway for Model Serving
API Gateway برای مدیریت درخواست‌های inference
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import numpy as np
import torch
from engine.model_server import model_server
from utils.logger import setup_logger
import io
from PIL import Image
import json

router = APIRouter(prefix="/api/serve", tags=["Model Serving"])
logger = setup_logger(__name__)


# ============================================
# Model Management Endpoints
# ============================================

@router.post("/register")
async def register_model(
    model_id: str = Form(...),
    model_path: str = Form(...),
    model_type: str = Form(...),
    metadata: Optional[str] = Form(None)
):
    """
    ثبت یک مدل جدید در سرویس
    
    Args:
        model_id: شناسه یکتای مدل
        model_path: مسیر فایل مدل
        model_type: نوع مدل (image, text, audio, etc.)
        metadata: اطلاعات اضافی (JSON string)
    """
    try:
        metadata_dict = json.loads(metadata) if metadata else {}
        
        model_server.register_model(
            model_id=model_id,
            model_path=model_path,
            model_type=model_type,
            metadata=metadata_dict
        )
        
        logger.info(f"Model registered: {model_id}")
        
        return JSONResponse({
            "status": "success",
            "message": f"Model '{model_id}' registered successfully",
            "model_id": model_id
        })
        
    except Exception as e:
        logger.error(f"Error registering model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load/{model_id}")
async def load_model(model_id: str, device: str = "cuda"):
    """
    بارگذاری مدل در memory
    
    Args:
        model_id: شناسه مدل
        device: دستگاه (cuda/cpu)
    """
    try:
        success = model_server.load_model(model_id, device)
        
        if success:
            logger.info(f"Model loaded: {model_id}")
            return JSONResponse({
                "status": "success",
                "message": f"Model '{model_id}' loaded on {device}",
                "model_id": model_id,
                "device": device
            })
        else:
            raise HTTPException(status_code=404, detail=f"Failed to load model '{model_id}'")
            
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/unload/{model_id}")
async def unload_model(model_id: str):
    """حذف مدل از memory"""
    try:
        model_server.unload_model(model_id)
        
        logger.info(f"Model unloaded: {model_id}")
        
        return JSONResponse({
            "status": "success",
            "message": f"Model '{model_id}' unloaded",
            "model_id": model_id
        })
        
    except Exception as e:
        logger.error(f"Error unloading model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_loaded_models():
    """دریافت لیست مدل‌های بارگذاری شده"""
    try:
        models = model_server.get_loaded_models()
        
        models_info = []
        for model_id in models:
            info = model_server.get_model_info(model_id)
            if info:
                models_info.append(info)
        
        return JSONResponse({
            "status": "success",
            "loaded_models": models_info,
            "total": len(models_info)
        })
        
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_id}")
async def get_model_info(model_id: str):
    """دریافت اطلاعات یک مدل"""
    try:
        info = model_server.get_model_info(model_id)
        
        if info:
            return JSONResponse({
                "status": "success",
                "model": info
            })
        else:
            raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
            
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """بررسی سلامت سرویس"""
    try:
        health = model_server.health_check()
        return JSONResponse(health)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Inference Endpoints
# ============================================

@router.post("/predict/{model_id}")
async def predict_image(
    model_id: str,
    file: UploadFile = File(...)
):
    """
    پیش‌بینی برای یک تصویر
    
    Args:
        model_id: شناسه مدل
        file: فایل تصویر
    """
    try:
        # خواندن و پیش‌پردازش تصویر
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        # تبدیل به tensor
        from torchvision import transforms
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                              std=[0.229, 0.224, 0.225])
        ])
        
        input_tensor = transform(image).unsqueeze(0)
        
        # پیش‌بینی
        result = await model_server.predict(model_id, input_tensor)
        
        if result.get("status") == "success":
            logger.info(f"Prediction made with model {model_id}")
            return JSONResponse(result)
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Prediction failed"))
            
    except Exception as e:
        logger.error(f"Error in prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/batch/{model_id}")
async def predict_batch(
    model_id: str,
    files: List[UploadFile] = File(...)
):
    """
    پیش‌بینی برای چند تصویر
    
    Args:
        model_id: شناسه مدل
        files: لیست فایل‌های تصویر
    """
    try:
        from torchvision import transforms
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                              std=[0.229, 0.224, 0.225])
        ])
        
        # پیش‌پردازش تمام تصاویر
        input_tensors = []
        for file in files:
            image_data = await file.read()
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            input_tensor = transform(image)
            input_tensors.append(input_tensor)
        
        # Stack تمام tensors
        batch_tensor = torch.stack(input_tensors)
        
        # پیش‌بینی
        result = await model_server.predict(model_id, batch_tensor, batch_size=32)
        
        if result.get("status") == "success":
            logger.info(f"Batch prediction made with model {model_id} for {len(files)} images")
            return JSONResponse(result)
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Batch prediction failed"))
            
    except Exception as e:
        logger.error(f"Error in batch prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/text/{model_id}")
async def predict_text(
    model_id: str,
    text: str = Form(...)
):
    """
    پیش‌بینی برای متن
    
    Args:
        model_id: شناسه مدل
        text: متن ورودی
    """
    try:
        # TODO: پیش‌پردازش متن (tokenization)
        # این بخش نیاز به یک tokenizer دارد
        
        logger.warning("Text prediction not fully implemented yet")
        
        return JSONResponse({
            "status": "error",
            "message": "Text prediction endpoint under development"
        })
        
    except Exception as e:
        logger.error(f"Error in text prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/audio/{model_id}")
async def predict_audio(
    model_id: str,
    file: UploadFile = File(...)
):
    """
    پیش‌بینی برای صوت
    
    Args:
        model_id: شناسه مدل
        file: فایل صوتی
    """
    try:
        # TODO: پیش‌پردازش صوت (mel-spectrogram, etc.)
        
        logger.warning("Audio prediction not fully implemented yet")
        
        return JSONResponse({
            "status": "error",
            "message": "Audio prediction endpoint under development"
        })
        
    except Exception as e:
        logger.error(f"Error in audio prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Statistics & Monitoring
# ============================================

@router.get("/stats")
async def get_statistics():
    """دریافت آمار کلی سرویس"""
    try:
        health = model_server.health_check()
        
        # اضافه کردن اطلاعات بیشتر
        stats = {
            **health,
            "endpoints": {
                "register": "/api/serve/register",
                "load": "/api/serve/load/{model_id}",
                "predict": "/api/serve/predict/{model_id}",
                "batch_predict": "/api/serve/predict/batch/{model_id}",
                "health": "/api/serve/health"
            }
        }
        
        return JSONResponse(stats)
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("API Gateway for Model Serving")
    print("Endpoints:")
    print("  POST /api/serve/register - Register a model")
    print("  POST /api/serve/load/{model_id} - Load a model")
    print("  DELETE /api/serve/unload/{model_id} - Unload a model")
    print("  GET /api/serve/models - List loaded models")
    print("  GET /api/serve/models/{model_id} - Get model info")
    print("  GET /api/serve/health - Health check")
    print("  POST /api/serve/predict/{model_id} - Predict (image)")
    print("  POST /api/serve/predict/batch/{model_id} - Batch predict")
    print("  GET /api/serve/stats - Get statistics")

