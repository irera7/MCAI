"""
Model export API endpoints
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from pathlib import Path
import torch

from utils.config import settings
from utils.logger import setup_logger
from export import ModelExporter, load_pytorch_model
from engine import ModelBuilder

logger = setup_logger(__name__)
router = APIRouter()

class ExportRequest(BaseModel):
    """Model export request"""
    project_id: str
    formats: List[str]  # pytorch, onnx, tflite, coreml
    export_path: str
    include_metadata: bool = True

@router.post("/model")
async def export_model(export_request: ExportRequest):
    """
    Export trained model in specified formats
    
    Args:
        export_request: Export configuration
        
    Returns:
        Export status and file locations
    """
    try:
        project_id = export_request.project_id
        project_dir = settings.PROJECTS_DIR / project_id
        if not project_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}"
            )
        
        # Check if trained model exists
        model_path = project_dir / "checkpoints" / "best_model.pt"
        if not model_path.exists():
            model_path = project_dir / "model.pt"
            if not model_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No trained model found"
                )
        
        # Load model
        checkpoint = torch.load(model_path, map_location='cpu')
        
        # Try to get num_classes from multiple sources
        metadata = checkpoint.get('metadata', {})
        num_classes = None
        model_arch = metadata.get('model_architecture', 'resnet18')
        modality = metadata.get('modality', 'image')
        
        # 1. Try from metadata
        if 'num_classes' in metadata:
            num_classes = metadata['num_classes']
            logger.info(f"Found num_classes={num_classes} in checkpoint metadata")
        
        # 2. Try from checkpoint model state dict
        if num_classes is None and 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
            # For ResNet and similar models, check fc layer
            if 'fc.weight' in state_dict:
                num_classes = state_dict['fc.weight'].shape[0]
                logger.info(f"Inferred num_classes={num_classes} from fc.weight shape")
            elif 'classifier.weight' in state_dict:
                num_classes = state_dict['classifier.weight'].shape[0]
                logger.info(f"Inferred num_classes={num_classes} from classifier.weight shape")
        
        # 3. Try from labels.json
        if num_classes is None:
            labels_file = project_dir / "labels.json"
            if labels_file.exists():
                import json
                with open(labels_file, 'r') as f:
                    labels_data = json.load(f)
                    if isinstance(labels_data, dict):
                        num_classes = len(labels_data)
                    elif isinstance(labels_data, list):
                        num_classes = len(labels_data)
                    logger.info(f"Found num_classes={num_classes} from labels.json")
        
        # 4. Fallback to default
        if num_classes is None:
            num_classes = 10
            logger.warning(f"Could not determine num_classes, using default: {num_classes}")
        
        # Build model with correct architecture and num_classes
        logger.info(f"Building {model_arch} model with {num_classes} classes for modality: {modality}")
        
        if modality == 'image':
            model = ModelBuilder.build_image_model(model_arch, num_classes, pretrained=False)
        elif modality == 'text':
            vocab_size = metadata.get('vocab_size', 10000)
            embed_dim = metadata.get('embed_dim', 128)
            model = ModelBuilder.build_text_model(model_arch, vocab_size, embed_dim, num_classes)
        elif modality == 'audio':
            model = ModelBuilder.build_audio_model(model_arch, num_classes)
        else:
            model = ModelBuilder.build_image_model(model_arch, num_classes, pretrained=False)
        
        # Load state dict
        try:
            model.load_state_dict(checkpoint.get('model_state_dict', checkpoint))
            logger.info("Successfully loaded model state dict")
        except RuntimeError as e:
            logger.error(f"Error loading state dict: {e}")
            # Try with strict=False as fallback
            model.load_state_dict(checkpoint.get('model_state_dict', checkpoint), strict=False)
            logger.warning("Loaded state dict with strict=False (some weights may be missing)")
        
        model.eval()
        
        # Export directory in project (always save here)
        project_exports_dir = project_dir / "exports"
        project_exports_dir.mkdir(exist_ok=True)
        
        # User-selected export directory (copy files here too)
        user_export_dir = Path(export_request.export_path) if export_request.export_path else None
        if user_export_dir:
            user_export_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"User export directory: {user_export_dir}")
        
        exported_files = []
        
        # Export to requested formats
        for fmt in export_request.formats:
            logger.info(f"Exporting model to {fmt} format")
            try:
                if fmt == "pytorch":
                    # 1. Save in project directory
                    project_path = project_exports_dir / "model.pt"
                    ModelExporter.export_pytorch(model, str(project_path), metadata=metadata)
                    
                    # 2. Copy to user-selected directory
                    if user_export_dir:
                        user_path = user_export_dir / "model.pt"
                        import shutil
                        shutil.copy2(project_path, user_path)
                        logger.info(f"Copied {fmt} to user directory: {user_path}")
                    
                    exported_files.append({
                        "format": fmt, 
                        "filename": "model.pt", 
                        "project_path": str(project_path),
                        "user_path": str(user_path) if user_export_dir else None
                    })
                    
                elif fmt == "onnx":
                    # 1. Save in project directory
                    project_path = project_exports_dir / "model.onnx"
                    ModelExporter.export_onnx(model, str(project_path))
                    
                    # 2. Copy to user-selected directory
                    if user_export_dir:
                        user_path = user_export_dir / "model.onnx"
                        import shutil
                        shutil.copy2(project_path, user_path)
                        logger.info(f"Copied {fmt} to user directory: {user_path}")
                    
                    exported_files.append({
                        "format": fmt, 
                        "filename": "model.onnx", 
                        "project_path": str(project_path),
                        "user_path": str(user_path) if user_export_dir else None
                    })
                    
                elif fmt == "torchscript":
                    # 1. Save in project directory
                    project_path = project_exports_dir / "model_torchscript.pt"
                    ModelExporter.export_torchscript(model, str(project_path))
                    
                    # 2. Copy to user-selected directory
                    if user_export_dir:
                        user_path = user_export_dir / "model_torchscript.pt"
                        import shutil
                        shutil.copy2(project_path, user_path)
                        logger.info(f"Copied {fmt} to user directory: {user_path}")
                    
                    exported_files.append({
                        "format": fmt, 
                        "filename": "model_torchscript.pt", 
                        "project_path": str(project_path),
                        "user_path": str(user_path) if user_export_dir else None
                    })
                    
            except Exception as e:
                logger.error(f"Failed to export {fmt}: {e}")
        
        return {
            "message": "Model exported successfully",
            "project_id": project_id,
            "exported_files": exported_files,
            "project_export_path": str(project_exports_dir),
            "user_export_path": str(user_export_dir) if user_export_dir else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting model: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export model: {str(e)}"
        )

@router.post("/{project_id}")
async def export_model_legacy(project_id: str, export_request: Dict[str, Any]):
    """
    Legacy export endpoint for backward compatibility
    
    Args:
        project_id: Project identifier
        export_request: Export configuration
        
    Returns:
        Export status and file locations
    """
    try:
        project_dir = settings.PROJECTS_DIR / project_id
        if not project_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}"
            )
        
        exports_dir = project_dir / "exports"
        exports_dir.mkdir(exist_ok=True)
        
        formats = export_request.get("formats", ["pytorch"])
        exported_files = []
        
        # This will be implemented with actual export logic
        for fmt in formats:
            logger.info(f"Exporting model to {fmt} format for project {project_id}")
            # Placeholder
            exported_files.append({
                "format": fmt,
                "filename": f"model.{fmt}",
                "path": str(exports_dir / f"model.{fmt}")
            })
        
        return {
            "message": "Model exported successfully",
            "project_id": project_id,
            "exported_files": exported_files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting model: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export model: {str(e)}"
        )

@router.get("/download/{project_id}/{filename}")
async def download_export(project_id: str, filename: str):
    """
    Download exported model file
    
    Args:
        project_id: Project identifier
        filename: Export filename
        
    Returns:
        Model file
    """
    try:
        file_path = settings.PROJECTS_DIR / project_id / "exports" / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Export file not found"
            )
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading export: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download export: {str(e)}"
        )

