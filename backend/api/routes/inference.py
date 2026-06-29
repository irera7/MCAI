"""
Inference API endpoints
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import torch
import torchvision.transforms as transforms
from PIL import Image
import io
import time
import json

from utils.config import settings
from utils.logger import setup_logger
from engine import ModelBuilder
from export import load_pytorch_model

logger = setup_logger(__name__)
router = APIRouter()

class PredictionRequest(BaseModel):
    """Inference prediction request"""
    data: Any  # Can be different types based on modality

class PredictionResponse(BaseModel):
    """Inference prediction response"""
    predictions: List[Dict[str, Any]]
    confidence_scores: List[float]
    inference_time: float

# Image preprocessing transform
image_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

@router.post("/predict/{project_id}", response_model=PredictionResponse)
async def predict(project_id: str, file: UploadFile = File(...)):
    """
    Make prediction using trained model
    
    Args:
        project_id: Project identifier
        file: Input file for prediction
        
    Returns:
        Prediction results
    """
    try:
        project_dir = settings.PROJECTS_DIR / project_id
        if not project_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}"
            )
        
        logger.info(f"Running inference for project {project_id}")
        
        # Load trained model
        model_path = project_dir / "checkpoints" / "best_model.pt"
        if not model_path.exists():
            model_path = project_dir / "model.pt"
            if not model_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No trained model found for this project"
                )
        
        # Load model checkpoint
        checkpoint = torch.load(model_path, map_location='cpu')
        metadata = checkpoint.get('metadata', {})
        
        # Get model info
        num_classes = metadata.get('num_classes', 10)
        model_arch = metadata.get('model_architecture', 'resnet18')
        
        # Load label mapping
        labels_file = project_dir / "labels.json"
        if labels_file.exists():
            with open(labels_file, 'r', encoding='utf-8') as f:
                label_map = json.load(f)
            # Reverse mapping (id -> name)
            id_to_label = {v: k for k, v in label_map.items()}
        else:
            id_to_label = {i: f"Class_{i}" for i in range(num_classes)}
        
        # Build and load model
        model = ModelBuilder.build_image_model(model_arch, num_classes, pretrained=False)
        model.load_state_dict(checkpoint.get('model_state_dict', checkpoint))
        model.eval()
        
        # Setup device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = model.to(device)
        
        # Read and preprocess image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        # Transform image
        input_tensor = image_transform(image).unsqueeze(0)  # Add batch dimension
        input_tensor = input_tensor.to(device)
        
        # Run inference
        start_time = time.time()
        
        with torch.no_grad():
            output = model(input_tensor)
            probabilities = torch.softmax(output, dim=1)
            
        inference_time = time.time() - start_time
        
        # Get top-5 predictions
        top_probs, top_indices = torch.topk(probabilities, min(5, num_classes))
        top_probs = top_probs[0].cpu().numpy()
        top_indices = top_indices[0].cpu().numpy()
        
        # Format predictions
        predictions = []
        confidence_scores = []
        
        for prob, idx in zip(top_probs, top_indices):
            predictions.append({
                "class_id": int(idx),
                "class_name": id_to_label.get(int(idx), f"Class_{idx}"),
                "confidence": float(prob)
            })
            confidence_scores.append(float(prob))
        
        logger.info(f"Inference completed in {inference_time:.3f}s. Top prediction: {predictions[0]['class_name']} ({predictions[0]['confidence']:.2%})")
        
        return PredictionResponse(
            predictions=predictions,
            confidence_scores=confidence_scores,
            inference_time=round(inference_time, 4)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during inference: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed: {str(e)}"
        )

@router.post("/batch/{project_id}")
async def batch_predict(project_id: str, files: List[UploadFile] = File(...)):
    """
    Make batch predictions
    
    Args:
        project_id: Project identifier
        files: List of input files
        
    Returns:
        Batch prediction results
    """
    try:
        project_dir = settings.PROJECTS_DIR / project_id
        if not project_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}"
            )
        
        logger.info(f"Running batch inference for project {project_id} ({len(files)} files)")
        
        # Load model (same as single prediction)
        model_path = project_dir / "checkpoints" / "best_model.pt"
        if not model_path.exists():
            model_path = project_dir / "model.pt"
            if not model_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No trained model found"
                )
        
        checkpoint = torch.load(model_path, map_location='cpu')
        metadata = checkpoint.get('metadata', {})
        num_classes = metadata.get('num_classes', 10)
        model_arch = metadata.get('model_architecture', 'resnet18')
        
        # Load labels
        labels_file = project_dir / "labels.json"
        if labels_file.exists():
            with open(labels_file, 'r', encoding='utf-8') as f:
                label_map = json.load(f)
            id_to_label = {v: k for k, v in label_map.items()}
        else:
            id_to_label = {i: f"Class_{i}" for i in range(num_classes)}
        
        # Build model
        model = ModelBuilder.build_image_model(model_arch, num_classes, pretrained=False)
        model.load_state_dict(checkpoint.get('model_state_dict', checkpoint))
        model.eval()
        
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = model.to(device)
        
        # Process all images
        results = []
        start_time = time.time()
        
        for file in files:
            try:
                # Read image
                contents = await file.read()
                image = Image.open(io.BytesIO(contents)).convert('RGB')
                
                # Transform
                input_tensor = image_transform(image).unsqueeze(0).to(device)
                
                # Predict
                with torch.no_grad():
                    output = model(input_tensor)
                    probabilities = torch.softmax(output, dim=1)
                
                # Get top prediction
                top_prob, top_idx = torch.max(probabilities, dim=1)
                
                results.append({
                    "filename": file.filename,
                    "prediction": {
                        "class_id": int(top_idx[0]),
                        "class_name": id_to_label.get(int(top_idx[0]), f"Class_{top_idx[0]}"),
                        "confidence": float(top_prob[0])
                    }
                })
                
            except Exception as e:
                logger.error(f"Error processing {file.filename}: {e}")
                results.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        
        total_time = time.time() - start_time
        
        logger.info(f"Batch inference completed: {len(results)} files in {total_time:.2f}s")
        
        return {
            "message": f"Batch inference completed for {len(files)} files",
            "total_time": round(total_time, 4),
            "avg_time_per_image": round(total_time / len(files), 4) if files else 0,
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during batch inference: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch inference failed: {str(e)}"
        )

