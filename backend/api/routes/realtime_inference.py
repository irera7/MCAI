"""
Real-time Inference API
API برای استنباط و پیش‌بینی real-time

این ماژول endpoint‌های FastAPI برای inference را فراهم می‌کند
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import torch
import numpy as np
from PIL import Image
import io
import json
from pathlib import Path

from engine import ModelBuilder
from inference.predictor import InferenceEngine

router = APIRouter(prefix="/api/v1/inference", tags=["Real-time Inference"])


# پیشینه‌ی مدل‌های بارگذاری شده (برای سرعت بیشتر)
_loaded_models: Dict[str, InferenceEngine] = {}


class PredictionRequest(BaseModel):
    """درخواست پیش‌بینی"""
    project_id: str
    model_checkpoint: Optional[str] = "best"  # 'best', 'last', or specific path


class PredictionResponse(BaseModel):
    """پاسخ پیش‌بینی"""
    predictions: List[Dict[str, Any]]
    inference_time: float
    model_info: Dict[str, str]


class BatchPredictionRequest(BaseModel):
    """درخواست پیش‌بینی batch"""
    project_id: str
    input_paths: List[str]
    model_checkpoint: Optional[str] = "best"


def _get_or_load_model(project_id: str, checkpoint: str = "best") -> InferenceEngine:
    """
    دریافت مدل از cache یا بارگذاری آن
    
    این تابع مدل را در حافظه نگه می‌دارد تا سرعت inference بالا برود
    
    Args:
        project_id: شناسه پروژه
        checkpoint: کدام checkpoint بارگذاری شود
        
    Returns:
        InferenceEngine
    """
    cache_key = f"{project_id}:{checkpoint}"
    
    if cache_key in _loaded_models:
        print(f"✅ Using cached model for {cache_key}")
        return _loaded_models[cache_key]
    
    # بارگذاری مدل
    project_dir = Path("projects") / project_id
    
    if not project_dir.exists():
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # خواندن اطلاعات پروژه
    project_file = project_dir / "project.json"
    with open(project_file, 'r') as f:
        project_info = json.load(f)
    
    modality = project_info.get('modality', 'image')
    num_classes = len(project_info.get('classes', []))
    
    # مسیر model
    if checkpoint == "best":
        model_path = project_dir / "checkpoints" / "best_model.pt"
    elif checkpoint == "last":
        model_path = project_dir / "model.pt"
    else:
        model_path = Path(checkpoint)
    
    if not model_path.exists():
        raise HTTPException(status_code=404, detail=f"Model checkpoint not found: {model_path}")
    
    # ساخت InferenceEngine
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    inference_engine = InferenceEngine(
        model_path=str(model_path),
        modality=modality,
        num_classes=num_classes,
        device=device
    )
    
    # ذخیره در cache
    _loaded_models[cache_key] = inference_engine
    
    print(f"✅ Model loaded and cached: {cache_key}")
    
    return inference_engine


@router.post("/predict/image", response_model=PredictionResponse)
async def predict_image(
    file: UploadFile = File(...),
    project_id: str = "default",
    checkpoint: str = "best"
):
    """
    پیش‌بینی روی یک تصویر
    
    این endpoint یک تصویر دریافت کرده و کلاس آن را پیش‌بینی می‌کند
    
    Args:
        file: فایل تصویر (JPEG, PNG)
        project_id: شناسه پروژه
        checkpoint: کدام model checkpoint استفاده شود
        
    Returns:
        پیش‌بینی و زمان inference
        
    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/inference/predict/image" \\
             -F "file=@image.jpg" \\
             -F "project_id=my-project"
        ```
    """
    try:
        import time
        start_time = time.time()
        
        # بارگذاری مدل
        inference_engine = _get_or_load_model(project_id, checkpoint)
        
        # خواندن تصویر
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # پیش‌بینی
        prediction = inference_engine.predict_single(image)
        
        inference_time = time.time() - start_time
        
        return PredictionResponse(
            predictions=[prediction],
            inference_time=inference_time,
            model_info={
                "project_id": project_id,
                "checkpoint": checkpoint,
                "device": inference_engine.device
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@router.post("/predict/text", response_model=PredictionResponse)
async def predict_text(
    text: str,
    project_id: str,
    checkpoint: str = "best"
):
    """
    پیش‌بینی روی متن
    
    Args:
        text: متن ورودی
        project_id: شناسه پروژه
        checkpoint: model checkpoint
        
    Returns:
        پیش‌بینی کلاس متن
        
    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/inference/predict/text" \\
             -H "Content-Type: application/json" \\
             -d '{"text": "This is a sample text", "project_id": "my-text-project"}'
        ```
    """
    try:
        import time
        start_time = time.time()
        
        # بارگذاری مدل
        inference_engine = _get_or_load_model(project_id, checkpoint)
        
        # پیش‌بینی
        prediction = inference_engine.predict_text(text)
        
        inference_time = time.time() - start_time
        
        return PredictionResponse(
            predictions=[prediction],
            inference_time=inference_time,
            model_info={
                "project_id": project_id,
                "checkpoint": checkpoint,
                "device": inference_engine.device
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@router.post("/predict/audio", response_model=PredictionResponse)
async def predict_audio(
    file: UploadFile = File(...),
    project_id: str = "default",
    checkpoint: str = "best"
):
    """
    پیش‌بینی روی فایل صوتی
    
    Args:
        file: فایل صوتی (WAV, MP3, FLAC)
        project_id: شناسه پروژه
        checkpoint: model checkpoint
        
    Returns:
        پیش‌بینی کلاس صدا
        
    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/inference/predict/audio" \\
             -F "file=@audio.wav" \\
             -F "project_id=my-audio-project"
        ```
    """
    try:
        import time
        start_time = time.time()
        
        # بارگذاری مدل
        inference_engine = _get_or_load_model(project_id, checkpoint)
        
        # ذخیره موقت فایل
        temp_path = Path("temp") / file.filename
        temp_path.parent.mkdir(exist_ok=True)
        
        with open(temp_path, 'wb') as f:
            f.write(await file.read())
        
        # پیش‌بینی
        prediction = inference_engine.predict_audio(str(temp_path))
        
        # پاک کردن فایل موقت
        temp_path.unlink()
        
        inference_time = time.time() - start_time
        
        return PredictionResponse(
            predictions=[prediction],
            inference_time=inference_time,
            model_info={
                "project_id": project_id,
                "checkpoint": checkpoint,
                "device": inference_engine.device
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@router.post("/predict/batch", response_model=PredictionResponse)
async def predict_batch(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks
):
    """
    پیش‌بینی batch روی چند ورودی
    
    این endpoint برای پیش‌بینی روی تعداد زیادی داده مناسب است
    
    Args:
        request: شامل project_id و لیست مسیرهای ورودی
        background_tasks: برای اجرای async
        
    Returns:
        لیست پیش‌بینی‌ها
        
    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/inference/predict/batch" \\
             -H "Content-Type: application/json" \\
             -d '{
                   "project_id": "my-project",
                   "input_paths": ["data/img1.jpg", "data/img2.jpg", "data/img3.jpg"]
                 }'
        ```
    """
    try:
        import time
        start_time = time.time()
        
        # بارگذاری مدل
        inference_engine = _get_or_load_model(request.project_id, request.model_checkpoint)
        
        # پیش‌بینی batch
        predictions = []
        for input_path in request.input_paths:
            if not Path(input_path).exists():
                predictions.append({
                    "input": input_path,
                    "error": "File not found"
                })
                continue
            
            # تشخیص نوع ورودی
            if input_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                image = Image.open(input_path)
                pred = inference_engine.predict_single(image)
            elif input_path.lower().endswith(('.wav', '.mp3', '.flac')):
                pred = inference_engine.predict_audio(input_path)
            else:
                pred = {"error": "Unsupported file format"}
            
            pred['input'] = input_path
            predictions.append(pred)
        
        inference_time = time.time() - start_time
        
        return PredictionResponse(
            predictions=predictions,
            inference_time=inference_time,
            model_info={
                "project_id": request.project_id,
                "checkpoint": request.model_checkpoint,
                "batch_size": len(request.input_paths)
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch inference error: {str(e)}")


@router.get("/models/list")
async def list_loaded_models():
    """
    لیست مدل‌های بارگذاری شده در cache
    
    این endpoint مدل‌هایی که در حافظه هستند را نمایش می‌دهد
    
    Returns:
        لیست مدل‌های loaded
    """
    return {
        "loaded_models": list(_loaded_models.keys()),
        "count": len(_loaded_models)
    }


@router.post("/models/unload")
async def unload_model(project_id: str, checkpoint: str = "best"):
    """
    حذف مدل از cache
    
    برای آزاد کردن حافظه
    
    Args:
        project_id: شناسه پروژه
        checkpoint: کدام checkpoint
        
    Returns:
        وضعیت
    """
    cache_key = f"{project_id}:{checkpoint}"
    
    if cache_key in _loaded_models:
        del _loaded_models[cache_key]
        return {"message": f"Model unloaded: {cache_key}"}
    
    return {"message": "Model not found in cache"}


@router.post("/models/clear-cache")
async def clear_model_cache():
    """
    پاک کردن تمام cache
    
    تمام مدل‌های loaded را از حافظه حذف می‌کند
    
    Returns:
        تعداد مدل‌های حذف شده
    """
    count = len(_loaded_models)
    _loaded_models.clear()
    
    return {
        "message": "Model cache cleared",
        "unloaded_count": count
    }


@router.get("/health")
async def health_check():
    """
    بررسی سلامت API
    
    Returns:
        وضعیت API
    """
    return {
        "status": "healthy",
        "loaded_models": len(_loaded_models),
        "gpu_available": torch.cuda.is_available(),
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }

