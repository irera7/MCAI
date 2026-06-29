"""
Inference engine for all modalities
Handles model loading and prediction
"""
import torch
import torch.nn as nn
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import numpy as np
import time

from utils.logger import setup_logger

logger = setup_logger(__name__)

class InferenceEngine:
    """
    Universal inference engine for all model types
    """
    
    def __init__(
        self,
        model_path: str,
        device: str = "cuda",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize inference engine
        
        Args:
            model_path: Path to trained model
            device: Device to run inference on
            config: Model configuration
        """
        self.model_path = Path(model_path)
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.config = config or {}
        self.model = None
        self.class_labels = self.config.get('class_labels', [])
        
        logger.info(f"InferenceEngine initialized on device: {self.device}")
    
    def load_model(self, model: nn.Module):
        """
        Load model for inference
        
        Args:
            model: PyTorch model instance
        """
        # Load checkpoint
        checkpoint = torch.load(self.model_path, map_location=self.device)
        
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint)
        
        model.to(self.device)
        model.eval()
        
        self.model = model
        logger.info("Model loaded successfully")
    
    @torch.no_grad()
    def predict(self, input_data: torch.Tensor) -> Dict[str, Any]:
        """
        Make prediction
        
        Args:
            input_data: Input tensor
            
        Returns:
            Prediction results with probabilities
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        start_time = time.time()
        
        # Move to device
        if not isinstance(input_data, torch.Tensor):
            input_data = torch.tensor(input_data, dtype=torch.float32)
        
        input_data = input_data.to(self.device)
        
        # Add batch dimension if needed
        if input_data.dim() == 3:  # For images (C, H, W)
            input_data = input_data.unsqueeze(0)
        
        # Forward pass
        outputs = self.model(input_data)
        
        # Get probabilities
        probabilities = torch.softmax(outputs, dim=1)
        
        # Get top prediction
        confidence, predicted_idx = torch.max(probabilities, dim=1)
        
        inference_time = time.time() - start_time
        
        # Prepare results
        predicted_idx = predicted_idx.item()
        confidence = confidence.item()
        
        result = {
            'predicted_class': predicted_idx,
            'predicted_label': self.class_labels[predicted_idx] if predicted_idx < len(self.class_labels) else f"Class {predicted_idx}",
            'confidence': confidence,
            'probabilities': probabilities[0].cpu().numpy().tolist(),
            'inference_time': inference_time
        }
        
        # Add top-k predictions
        top_k = min(5, len(probabilities[0]))
        top_probs, top_indices = torch.topk(probabilities[0], top_k)
        
        result['top_predictions'] = [
            {
                'class': idx.item(),
                'label': self.class_labels[idx.item()] if idx.item() < len(self.class_labels) else f"Class {idx.item()}",
                'probability': prob.item()
            }
            for idx, prob in zip(top_indices, top_probs)
        ]
        
        return result
    
    @torch.no_grad()
    def predict_batch(self, input_batch: torch.Tensor) -> List[Dict[str, Any]]:
        """
        Make batch predictions
        
        Args:
            input_batch: Batch of input tensors
            
        Returns:
            List of prediction results
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        input_batch = input_batch.to(self.device)
        
        # Forward pass
        outputs = self.model(input_batch)
        probabilities = torch.softmax(outputs, dim=1)
        
        # Process each prediction
        results = []
        for i in range(len(probabilities)):
            confidence, predicted_idx = torch.max(probabilities[i], dim=0)
            
            result = {
                'predicted_class': predicted_idx.item(),
                'predicted_label': self.class_labels[predicted_idx.item()] if predicted_idx.item() < len(self.class_labels) else f"Class {predicted_idx.item()}",
                'confidence': confidence.item(),
                'probabilities': probabilities[i].cpu().numpy().tolist()
            }
            
            results.append(result)
        
        return results


class ONNXInferenceEngine:
    """
    Inference engine for ONNX models
    """
    
    def __init__(self, model_path: str, class_labels: Optional[List[str]] = None):
        """
        Initialize ONNX inference engine
        
        Args:
            model_path: Path to ONNX model
            class_labels: List of class labels
        """
        import onnxruntime as ort
        
        self.model_path = model_path
        self.class_labels = class_labels or []
        
        # Create inference session
        self.session = ort.InferenceSession(model_path)
        
        # Get input/output names
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        
        logger.info(f"ONNX model loaded: {model_path}")
    
    def predict(self, input_data: np.ndarray) -> Dict[str, Any]:
        """
        Make prediction with ONNX model
        
        Args:
            input_data: Input numpy array
            
        Returns:
            Prediction results
        """
        start_time = time.time()
        
        # Run inference
        outputs = self.session.run(
            [self.output_name],
            {self.input_name: input_data}
        )[0]
        
        # Apply softmax
        exp_outputs = np.exp(outputs - np.max(outputs, axis=1, keepdims=True))
        probabilities = exp_outputs / np.sum(exp_outputs, axis=1, keepdims=True)
        
        predicted_idx = np.argmax(probabilities[0])
        confidence = probabilities[0][predicted_idx]
        
        inference_time = time.time() - start_time
        
        return {
            'predicted_class': int(predicted_idx),
            'predicted_label': self.class_labels[predicted_idx] if predicted_idx < len(self.class_labels) else f"Class {predicted_idx}",
            'confidence': float(confidence),
            'probabilities': probabilities[0].tolist(),
            'inference_time': inference_time
        }

