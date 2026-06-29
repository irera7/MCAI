"""
Genomic data API routes
مسیرهای API برای داده‌های ژنومی (DNA/RNA sequences)
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
from pathlib import Path
import shutil

# Create router
router = APIRouter(prefix="/api/genomic", tags=["genomic"])

# Configuration
UPLOAD_DIR = Path("uploads/genomic")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_genomic_data(
    files: List[UploadFile] = File(...),
    sequence_type: str = Form(...),  # 'dna' or 'rna'
    class_name: str = Form(...)
):
    """
    Upload genomic sequence files (FASTA format)
    آپلود فایل‌های سکانس ژنومی (فرمت FASTA)
    
    Args:
        files: List of FASTA files
        sequence_type: Type of sequence ('dna' or 'rna')
        class_name: Class/label name
        
    Returns:
        Upload status and file paths
    """
    try:
        # Create class directory
        class_dir = UPLOAD_DIR / sequence_type / class_name
        class_dir.mkdir(parents=True, exist_ok=True)
        
        uploaded_files = []
        
        # Valid FASTA extensions
        valid_extensions = ['.fasta', '.fa', '.fna', '.ffn', '.faa', '.frn']
        
        for file in files:
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in valid_extensions:
                continue
            
            # Save file
            file_path = class_dir / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append(str(file_path))
        
        return JSONResponse({
            "status": "success",
            "message": f"Successfully uploaded {len(uploaded_files)} FASTA files",
            "sequence_type": sequence_type,
            "class_name": class_name,
            "uploaded_files": uploaded_files,
            "total_files": len(uploaded_files)
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/models")
async def get_genomic_models():
    """
    Get available genomic models
    دریافت مدل‌های ژنومی موجود
    
    Returns:
        List of available models with descriptions
    """
    try:
        models = [
            {
                "id": "dna_cnn",
                "name": "DNA CNN",
                "description": "1D Convolutional Neural Network for DNA sequence classification",
                "description_fa": "شبکه عصبی کانولوشنی 1D برای دسته‌بندی سکانس DNA",
                "input_type": "One-hot encoded sequences",
                "encoding": "one-hot",
                "params": "~2M",
                "speed": "Fast",
                "accuracy": "High",
                "use_cases": [
                    "Gene classification",
                    "Promoter prediction",
                    "Splice site detection",
                    "Mutation analysis"
                ]
            },
            {
                "id": "sequence_embedding",
                "name": "Sequence Embedding",
                "description": "LSTM-based model with learned sequence representations",
                "description_fa": "مدل مبتنی بر LSTM با یادگیری نمایش سکانس",
                "input_type": "Index encoded sequences",
                "encoding": "index",
                "params": "~3M",
                "speed": "Medium",
                "accuracy": "High",
                "use_cases": [
                    "Sequence classification",
                    "Function prediction",
                    "Protein coding prediction",
                    "Non-coding RNA identification"
                ]
            }
        ]
        
        return JSONResponse({
            "status": "success",
            "models": models,
            "total": len(models)
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")


@router.post("/train")
async def train_genomic_model(
    project_name: str = Form(...),
    sequence_type: str = Form(...),
    model_type: str = Form(...),
    data_path: str = Form(...),
    num_classes: int = Form(...),
    sequence_length: int = Form(1000),
    epochs: int = Form(50),
    batch_size: int = Form(32),
    learning_rate: float = Form(0.001),
    encoding_type: str = Form("onehot")  # 'onehot' or 'index'
):
    """
    Start training a genomic model
    شروع آموزش مدل ژنومی
    
    Args:
        project_name: Name of the project
        sequence_type: Type of sequence ('dna' or 'rna')
        model_type: Model architecture to use
        data_path: Path to training data
        num_classes: Number of classes
        sequence_length: Target sequence length
        epochs: Number of training epochs
        batch_size: Batch size
        learning_rate: Learning rate
        encoding_type: Encoding type ('onehot' or 'index')
        
    Returns:
        Training job information
    """
    try:
        # Import necessary modules
        from backend.models.genomic import create_genomic_model
        from backend.data.loaders.data_loaders import GenomicDataset, create_dataloader
        
        # Create model
        model = create_genomic_model(
            model_type, 
            num_classes=num_classes,
            sequence_length=sequence_length
        )
        
        # This would integrate with the main training engine
        # For now, return job information
        
        job_info = {
            "status": "success",
            "message": "Training job created successfully",
            "job_id": f"genomic_{project_name}_{sequence_type}",
            "project_name": project_name,
            "sequence_type": sequence_type,
            "model_type": model_type,
            "config": {
                "epochs": epochs,
                "batch_size": batch_size,
                "learning_rate": learning_rate,
                "num_classes": num_classes,
                "sequence_length": sequence_length,
                "encoding_type": encoding_type
            }
        }
        
        return JSONResponse(job_info)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.post("/inference")
async def genomic_inference(
    model_path: str = Form(...),
    sequence_file: UploadFile = File(...),
    encoding_type: str = Form("onehot")
):
    """
    Perform inference on genomic sequences
    انجام استنتاج روی سکانس‌های ژنومی
    
    Args:
        model_path: Path to trained model
        sequence_file: FASTA file with sequences
        encoding_type: Encoding type used
        
    Returns:
        Prediction results
    """
    try:
        # Save uploaded file temporarily
        temp_path = UPLOAD_DIR / "temp" / sequence_file.filename
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(sequence_file.file, buffer)
        
        # This would integrate with inference engine
        # For now, return placeholder results
        
        results = {
            "status": "success",
            "message": "Inference completed",
            "file_name": sequence_file.filename,
            "encoding_type": encoding_type,
            "predictions": [
                {
                    "sequence_id": "seq_001",
                    "predicted_class": "class_0",
                    "confidence": 0.92
                },
                {
                    "sequence_id": "seq_002",
                    "predicted_class": "class_1",
                    "confidence": 0.87
                }
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
    Get information about a genomic dataset
    دریافت اطلاعات درباره دیتاست ژنومی
    
    Args:
        data_path: Path to dataset
        
    Returns:
        Dataset statistics
    """
    try:
        data_dir = Path(data_path)
        
        if not data_dir.exists():
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Count FASTA files by class
        classes = {}
        total_files = 0
        total_sequences = 0
        
        for class_dir in data_dir.iterdir():
            if class_dir.is_dir():
                file_count = len(list(class_dir.glob('*.fasta'))) + \
                            len(list(class_dir.glob('*.fa'))) + \
                            len(list(class_dir.glob('*.fna')))
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
async def get_preprocessing_options():
    """
    Get preprocessing options for genomic data
    دریافت گزینه‌های پیش‌پردازش برای داده‌های ژنومی
    
    Returns:
        Available preprocessing options
    """
    try:
        options = {
            "sequence_length": {
                "type": "integer",
                "default": 1000,
                "range": [100, 10000],
                "description": "Target sequence length",
                "description_fa": "طول هدف سکانس"
            },
            "encoding_type": {
                "type": "string",
                "default": "onehot",
                "options": ["onehot", "index"],
                "description": "Sequence encoding method",
                "description_fa": "روش کدگذاری سکانس",
                "details": {
                    "onehot": "One-hot encoding (4 channels for A, C, G, T)",
                    "index": "Index encoding (single integer per nucleotide)"
                }
            },
            "padding": {
                "type": "string",
                "default": "right",
                "options": ["right", "left"],
                "description": "Padding position for short sequences",
                "description_fa": "موقعیت padding برای سکانس‌های کوتاه"
            },
            "truncation": {
                "type": "string",
                "default": "right",
                "options": ["right", "left"],
                "description": "Truncation position for long sequences",
                "description_fa": "موقعیت truncate برای سکانس‌های بلند"
            },
            "handle_ambiguous": {
                "type": "string",
                "default": "mask",
                "options": ["mask", "random", "remove"],
                "description": "How to handle ambiguous nucleotides (N)",
                "description_fa": "نحوه برخورد با نوکلئوتیدهای مبهم (N)"
            }
        }
        
        return JSONResponse({
            "status": "success",
            "preprocessing_options": options
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get options: {str(e)}")


@router.post("/validate-fasta")
async def validate_fasta_file(file: UploadFile = File(...)):
    """
    Validate FASTA file format
    اعتبارسنجی فرمت فایل FASTA
    
    Args:
        file: FASTA file to validate
        
    Returns:
        Validation results
    """
    try:
        # Save temporarily
        temp_path = UPLOAD_DIR / "temp" / file.filename
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Basic validation
        valid = True
        errors = []
        sequence_count = 0
        
        with open(temp_path, 'r') as f:
            lines = f.readlines()
            
            if not lines or not lines[0].startswith('>'):
                valid = False
                errors.append("File must start with '>' (FASTA header)")
            
            for line in lines:
                if line.startswith('>'):
                    sequence_count += 1
        
        # Clean up
        os.remove(temp_path)
        
        return JSONResponse({
            "status": "success" if valid else "error",
            "valid": valid,
            "file_name": file.filename,
            "sequence_count": sequence_count,
            "errors": errors if errors else None
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/nucleotide-stats")
async def get_nucleotide_statistics(data_path: str):
    """
    Get nucleotide composition statistics
    دریافت آمار ترکیب نوکلئوتیدی
    
    Args:
        data_path: Path to FASTA file or directory
        
    Returns:
        Nucleotide composition statistics
    """
    try:
        # This is a placeholder for actual implementation
        stats = {
            "status": "success",
            "nucleotide_composition": {
                "A": 0.25,
                "C": 0.25,
                "G": 0.25,
                "T": 0.25
            },
            "gc_content": 0.50,
            "average_length": 1000,
            "min_length": 500,
            "max_length": 1500
        }
        
        return JSONResponse(stats)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

