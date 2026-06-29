"""
System information API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict
import torch
import platform
import psutil

from utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/info")
async def get_system_info():
    """
    Get system information including GPU availability
    
    Returns:
        System information dictionary
    """
    try:
        info = {
            "gpu_available": torch.cuda.is_available(),
            "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "cpu_count": psutil.cpu_count(),
            "python_version": platform.python_version(),
            "pytorch_version": torch.__version__,
            "platform": platform.system()
        }
        
        # Add GPU info if available
        if torch.cuda.is_available():
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_memory_total"] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system info: {str(e)}"
        )

@router.get("/devices")
async def get_available_devices():
    """
    Get available computing devices (CPU, GPU)
    
    Returns:
        List of available devices
    """
    try:
        devices = []
        
        # CPU is always available
        devices.append({
            "id": "cpu",
            "name": "CPU",
            "type": "cpu",
            "available": True
        })
        
        # Check for CUDA GPUs
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                devices.append({
                    "id": f"cuda:{i}",
                    "name": torch.cuda.get_device_name(i),
                    "type": "gpu",
                    "available": True,
                    "memory": torch.cuda.get_device_properties(i).total_memory / (1024**3)  # GB
                })
        
        return {"devices": devices}
        
    except Exception as e:
        logger.error(f"Error getting devices: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get devices: {str(e)}"
        )

@router.get("/health")
async def system_health():
    """
    Get system health information
    
    Returns:
        System health metrics
    """
    try:
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health = {
            "status": "healthy",
            "system": {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "python_version": platform.python_version()
            },
            "resources": {
                "cpu_percent": cpu_percent,
                "memory_total_gb": memory.total / (1024**3),
                "memory_available_gb": memory.available / (1024**3),
                "memory_percent": memory.percent,
                "disk_total_gb": disk.total / (1024**3),
                "disk_free_gb": disk.free / (1024**3),
                "disk_percent": disk.percent
            },
            "pytorch": {
                "version": torch.__version__,
                "cuda_available": torch.cuda.is_available(),
                "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
                "cudnn_version": torch.backends.cudnn.version() if torch.cuda.is_available() else None
            }
        }
        
        return health
        
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system health: {str(e)}"
        )

@router.get("/models/list/{modality}")
async def list_available_models(modality: str):
    """
    List available model architectures for a modality
    
    Args:
        modality: Data modality type
        
    Returns:
        List of available models
    """
    try:
        # Model registry for each modality
        model_registry = {
            "image": [
                {"id": "cnn", "name": "Custom CNN", "description": "Lightweight convolutional network"},
                {"id": "mobilenetv3", "name": "MobileNetV3", "description": "Efficient mobile architecture"},
                {"id": "vit", "name": "Vision Transformer", "description": "Transformer-based vision model"}
            ],
            "text": [
                {"id": "bert", "name": "BERT-small", "description": "Pre-trained language model"},
                {"id": "lstm", "name": "LSTM", "description": "Recurrent neural network"},
                {"id": "tfidf", "name": "TF-IDF", "description": "Traditional text classifier"}
            ],
            "audio": [
                {"id": "spectrogram_cnn", "name": "Spectrogram CNN", "description": "CNN on audio spectrograms"},
                {"id": "speech_commands", "name": "Speech Commands", "description": "Speech recognition model"}
            ],
            "video": [
                {"id": "3dcnn", "name": "3D CNN", "description": "Spatiotemporal convolutional network"},
                {"id": "frame_sampling", "name": "Frame Sampling", "description": "Process sampled video frames"}
            ],
            "tabular": [
                {"id": "mlp", "name": "Multi-Layer Perceptron", "description": "Neural network classifier"},
                {"id": "randomforest", "name": "Random Forest", "description": "Ensemble tree method"},
                {"id": "xgboost", "name": "XGBoost", "description": "Gradient boosting"}
            ],
            "timeseries": [
                {"id": "lstm", "name": "LSTM", "description": "Long short-term memory network"},
                {"id": "temporal_cnn", "name": "Temporal CNN", "description": "Convolutional network for sequences"},
                {"id": "transformer", "name": "Transformer", "description": "Attention-based model"}
            ],
            "medical": [
                {"id": "mri_cnn", "name": "MRI CNN", "description": "2D CNN for medical images"},
                {"id": "ecg_cnn", "name": "ECG/EEG CNN", "description": "1D CNN for signals"}
            ],
            "genomic": [
                {"id": "dna_cnn", "name": "DNA CNN", "description": "1D CNN for sequences"},
                {"id": "sequence_embedding", "name": "Sequence Embedding", "description": "Learned sequence representations"}
            ]
        }
        
        if modality not in model_registry:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown modality: {modality}"
            )
        
        return {"modality": modality, "models": model_registry[modality]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list models: {str(e)}"
        )

