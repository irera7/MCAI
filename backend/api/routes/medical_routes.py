"""
Medical data API routes
مسیرهای API برای داده‌های پزشکی (MRI, ECG, EEG)
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
from pathlib import Path
import shutil

# Create router
router = APIRouter(prefix="/api/medical", tags=["medical"])

# Configuration
UPLOAD_DIR = Path("uploads/medical")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_medical_data(
    files: List[UploadFile] = File(...),
    data_type: str = Form(...),  # 'mri', 'ecg', or 'eeg'
    class_name: str = Form(...)
):
    """
    Upload medical data files
    آپلود فایل‌های پزشکی
    
    Args:
        files: List of medical data files (DICOM, CSV, etc.)
        data_type: Type of medical data ('mri', 'ecg', 'eeg')
        class_name: Class/label name
        
    Returns:
        Upload status and file paths
    """
    try:
        # Create class directory
        class_dir = UPLOAD_DIR / data_type / class_name
        class_dir.mkdir(parents=True, exist_ok=True)
        
        uploaded_files = []
        
        for file in files:
            # Validate file extension based on data type
            if data_type == 'mri':
                valid_extensions = ['.dcm', '.dicom', '.nii', '.gz']
            else:  # ecg or eeg
                valid_extensions = ['.csv', '.txt', '.dat']
            
            file_ext = Path(file.filename).suffix.lower()
            if not any(file.filename.endswith(ext) for ext in valid_extensions):
                continue
            
            # Save file
            file_path = class_dir / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append(str(file_path))
        
        return JSONResponse({
            "status": "success",
            "message": f"Successfully uploaded {len(uploaded_files)} files",
            "data_type": data_type,
            "class_name": class_name,
            "uploaded_files": uploaded_files,
            "total_files": len(uploaded_files)
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/models")
async def get_medical_models(data_type: str):
    """
    Get available medical models
    دریافت مدل‌های پزشکی موجود
    
    Args:
        data_type: Type of medical data ('mri', 'ecg', 'eeg')
        
    Returns:
        List of available models with descriptions
    """
    try:
        if data_type.lower() == 'mri':
            models = [
                {
                    "id": "mri_cnn",
                    "name": "MRI CNN",
                    "description": "2D Convolutional Neural Network for MRI image classification",
                    "description_fa": "شبکه عصبی کانولوشنی 2D برای دسته‌بندی تصاویر MRI",
                    "input_type": "DICOM images",
                    "params": "~5M",
                    "speed": "Fast",
                    "accuracy": "High",
                    "use_cases": [
                        "Brain tumor detection",
                        "Alzheimer's diagnosis",
                        "Multiple sclerosis detection"
                    ]
                }
            ]
        else:  # ecg or eeg
            models = [
                {
                    "id": "ecg_cnn",
                    "name": "ECG/EEG CNN",
                    "description": "1D Convolutional Neural Network for physiological signal classification",
                    "description_fa": "شبکه عصبی کانولوشنی 1D برای دسته‌بندی سیگنال‌های فیزیولوژیکی",
                    "input_type": "Time-series signals",
                    "params": "~3M",
                    "speed": "Fast",
                    "accuracy": "High",
                    "use_cases": [
                        "Arrhythmia detection",
                        "Epilepsy seizure prediction",
                        "Sleep stage classification"
                    ]
                }
            ]
        
        return JSONResponse({
            "status": "success",
            "data_type": data_type,
            "models": models,
            "total": len(models)
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")


@router.post("/train")
async def train_medical_model(
    project_name: str = Form(...),
    data_type: str = Form(...),
    model_type: str = Form(...),
    data_path: str = Form(...),
    num_classes: int = Form(...),
    epochs: int = Form(50),
    batch_size: int = Form(32),
    learning_rate: float = Form(0.001)
):
    """
    Start training a medical model
    شروع آموزش مدل پزشکی
    
    Args:
        project_name: Name of the project
        data_type: Type of medical data ('mri', 'ecg', 'eeg')
        model_type: Model architecture to use
        data_path: Path to training data
        num_classes: Number of classes
        epochs: Number of training epochs
        batch_size: Batch size
        learning_rate: Learning rate
        
    Returns:
        Training job information
    """
    try:
        # Import necessary modules
        from backend.models.medical import create_medical_model
        from backend.data.loaders.data_loaders import MedicalDataset, create_dataloader
        
        # Create model
        model = create_medical_model(model_type, num_classes=num_classes)
        
        # This would integrate with the main training engine
        # For now, return job information
        
        job_info = {
            "status": "success",
            "message": "Training job created successfully",
            "job_id": f"medical_{project_name}_{data_type}",
            "project_name": project_name,
            "data_type": data_type,
            "model_type": model_type,
            "config": {
                "epochs": epochs,
                "batch_size": batch_size,
                "learning_rate": learning_rate,
                "num_classes": num_classes
            }
        }
        
        return JSONResponse(job_info)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.post("/inference")
async def medical_inference(
    model_path: str = Form(...),
    data_file: UploadFile = File(...),
    data_type: str = Form(...)
):
    """
    Perform inference on medical data
    انجام استنتاج روی داده‌های پزشکی
    
    Args:
        model_path: Path to trained model
        data_file: Medical data file
        data_type: Type of medical data
        
    Returns:
        Prediction results
    """
    try:
        # Save uploaded file temporarily
        temp_path = UPLOAD_DIR / "temp" / data_file.filename
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(data_file.file, buffer)
        
        # This would integrate with inference engine
        # For now, return placeholder results
        
        results = {
            "status": "success",
            "message": "Inference completed",
            "data_type": data_type,
            "file_name": data_file.filename,
            "predictions": [
                {"class": "class_0", "confidence": 0.85},
                {"class": "class_1", "confidence": 0.15}
            ]
        }
        
        # Clean up
        os.remove(temp_path)
        
        return JSONResponse(results)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")


@router.get("/datasets/info")
async def get_dataset_info(data_path: str):
    """
    Get information about a medical dataset
    دریافت اطلاعات درباره دیتاست پزشکی
    
    Args:
        data_path: Path to dataset
        
    Returns:
        Dataset statistics
    """
    try:
        data_dir = Path(data_path)
        
        if not data_dir.exists():
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Count files by class
        classes = {}
        total_files = 0
        
        for class_dir in data_dir.iterdir():
            if class_dir.is_dir():
                file_count = len(list(class_dir.glob('*')))
                classes[class_dir.name] = file_count
                total_files += file_count
        
        return JSONResponse({
            "status": "success",
            "dataset_path": str(data_dir),
            "total_files": total_files,
            "num_classes": len(classes),
            "classes": classes
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dataset info: {str(e)}")


@router.get("/preprocessing/options")
async def get_preprocessing_options(data_type: str):
    """
    Get preprocessing options for medical data
    دریافت گزینه‌های پیش‌پردازش برای داده‌های پزشکی
    
    Args:
        data_type: Type of medical data
        
    Returns:
        Available preprocessing options
    """
    try:
        if data_type.lower() == 'mri':
            options = {
                "target_size": {
                    "type": "tuple",
                    "default": [224, 224],
                    "description": "Target image size (height, width)",
                    "description_fa": "اندازه هدف تصویر (ارتفاع، عرض)"
                },
                "normalize": {
                    "type": "boolean",
                    "default": True,
                    "description": "Normalize pixel values",
                    "description_fa": "نرمال‌سازی مقادیر پیکسل"
                },
                "window_level": {
                    "type": "integer",
                    "default": 50,
                    "range": [0, 100],
                    "description": "DICOM window level",
                    "description_fa": "سطح پنجره DICOM"
                }
            }
        else:  # ecg or eeg
            options = {
                "target_length": {
                    "type": "integer",
                    "default": 1000,
                    "description": "Target signal length",
                    "description_fa": "طول هدف سیگنال"
                },
                "sampling_rate": {
                    "type": "integer",
                    "default": 250,
                    "description": "Sampling rate (Hz)",
                    "description_fa": "نرخ نمونه‌برداری (هرتز)"
                },
                "normalize": {
                    "type": "boolean",
                    "default": True,
                    "description": "Normalize signal values",
                    "description_fa": "نرمال‌سازی مقادیر سیگنال"
                },
                "filter": {
                    "type": "string",
                    "default": "none",
                    "options": ["none", "lowpass", "highpass", "bandpass"],
                    "description": "Signal filtering",
                    "description_fa": "فیلتر کردن سیگنال"
                }
            }
        
        return JSONResponse({
            "status": "success",
            "data_type": data_type,
            "preprocessing_options": options
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get options: {str(e)}")

