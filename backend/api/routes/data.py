"""
Data management API endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Form
from typing import List, Optional
from pathlib import Path
import shutil
import json

from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.post("/upload/{project_id}")
async def upload_data(
    project_id: str,
    files: List[UploadFile] = File(...),
    label: Optional[str] = Form(None)
):
    """
    Upload data files to a project
    
    Args:
        project_id: Project identifier
        files: List of files to upload
        label: Optional label/class for the files
        
    Returns:
        Upload status
    """
    try:
        project_dir = settings.PROJECTS_DIR / project_id
        if not project_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}"
            )
        
        data_dir = project_dir / "data"
        uploaded_files = []
        
        # Create label directory if specified
        if label:
            label_dir = data_dir / label
            label_dir.mkdir(parents=True, exist_ok=True)
            target_dir = label_dir
        else:
            target_dir = data_dir
        
        # Save uploaded files
        for file in files:
            # Extract just the filename without any path components
            filename = Path(file.filename).name
            file_path = target_dir / filename
            
            with open(file_path, 'wb') as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append({
                "filename": filename,
                "size": file_path.stat().st_size,
                "label": label
            })
        
        logger.info(f"Uploaded {len(files)} files to project {project_id}")
        
        return {
            "message": f"Successfully uploaded {len(files)} files",
            "files": uploaded_files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload data: {str(e)}"
        )

@router.get("/preview/{project_id}")
async def preview_data(project_id: str, limit: int = 10):
    """
    Get preview of project data
    
    Args:
        project_id: Project identifier
        limit: Maximum number of samples to return
        
    Returns:
        Data preview information
    """
    try:
        project_dir = settings.PROJECTS_DIR / project_id
        if not project_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}"
            )
        
        data_dir = project_dir / "data"
        preview = {
            "labels": [],
            "samples": []
        }
        
        # Get labels (subdirectories in data folder)
        if data_dir.exists():
            labels = [d.name for d in data_dir.iterdir() if d.is_dir()]
            preview["labels"] = labels
            
            # Get sample files for each label
            for label in labels[:limit]:
                label_dir = data_dir / label
                files = list(label_dir.iterdir())[:5]  # 5 samples per label
                
                for file in files:
                    preview["samples"].append({
                        "label": label,
                        "filename": file.name,
                        "path": str(file.relative_to(project_dir)),
                        "size": file.stat().st_size
                    })
        
        return preview
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview data: {str(e)}"
        )

@router.get("/stats/{project_id}")
async def get_data_stats(project_id: str):
    """
    Get statistics about project data
    
    Args:
        project_id: Project identifier
        
    Returns:
        Data statistics
    """
    try:
        project_dir = settings.PROJECTS_DIR / project_id
        if not project_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}"
            )
        
        data_dir = project_dir / "data"
        stats = {
            "total_files": 0,
            "total_size": 0,
            "num_classes": 0,
            "classes": {},
            "ready_for_training": False,
            "warnings": []
        }
        
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
        
        if data_dir.exists():
            # Count files per class
            class_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
            
            if class_dirs:
                # Class-based structure
                for label_dir in class_dirs:
                    files = [f for f in label_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_extensions]
                    file_count = len(files)
                    total_size = sum(f.stat().st_size for f in files)
                    
                    stats["classes"][label_dir.name] = {
                        "count": file_count,
                        "size": total_size
                    }
                    
                    stats["total_files"] += file_count
                    stats["total_size"] += total_size
                    
                    # Add warning if class has too few samples
                    if file_count < 10:
                        stats["warnings"].append(f"Class '{label_dir.name}' has only {file_count} images. Consider adding more samples.")
                
                stats["num_classes"] = len(stats["classes"])
            else:
                # Images in root directory
                files = [f for f in data_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_extensions]
                if files:
                    file_count = len(files)
                    total_size = sum(f.stat().st_size for f in files)
                    
                    stats["classes"]["class_0"] = {
                        "count": file_count,
                        "size": total_size
                    }
                    stats["total_files"] = file_count
                    stats["total_size"] = total_size
                    stats["num_classes"] = 1
                    stats["warnings"].append("Images found in root directory. Consider organizing them into class folders for multi-class classification.")
        
        # Check if ready for training
        if stats["total_files"] >= 10 and stats["num_classes"] > 0:
            stats["ready_for_training"] = True
        else:
            if stats["total_files"] == 0:
                stats["warnings"].append("No images found. Please upload images before training.")
            elif stats["total_files"] < 10:
                stats["warnings"].append(f"Only {stats['total_files']} images found. Recommend at least 10 images per class for meaningful training.")
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting data stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get data stats: {str(e)}"
        )

@router.post("/preprocess/{project_id}")
async def preprocess_data(project_id: str):
    """
    Preprocess project data
    
    Args:
        project_id: Project identifier
        
    Returns:
        Preprocessing status
    """
    try:
        # This will be implemented with specific preprocessing for each modality
        logger.info(f"Preprocessing data for project {project_id}")
        
        return {
            "message": "Data preprocessing queued",
            "project_id": project_id
        }
        
    except Exception as e:
        logger.error(f"Error preprocessing data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preprocess data: {str(e)}"
        )

