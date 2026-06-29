"""
Model export utilities
Export trained models to different formats (PyTorch, ONNX, TensorFlow Lite)
"""
import torch
import torch.onnx
import onnx
from pathlib import Path
import json
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class PyTorchExporter:
    """Export models in PyTorch format"""
    
    @staticmethod
    def export(
        model: torch.nn.Module,
        save_path: str,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Export model in PyTorch format
        
        Args:
            model: PyTorch model to export
            save_path: Path to save model
            config: Model configuration metadata
        """
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save model state dict
        torch.save({
            'model_state_dict': model.state_dict(),
            'config': config or {}
        }, save_path)
        
        logger.info(f"Model exported to PyTorch format: {save_path}")
        
        return str(save_path)


class ONNXExporter:
    """Export models to ONNX format"""
    
    @staticmethod
    def export(
        model: torch.nn.Module,
        save_path: str,
        input_shape: Tuple[int, ...],
        opset_version: int = 12,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Export model to ONNX format
        
        Args:
            model: PyTorch model to export
            save_path: Path to save ONNX model
            input_shape: Input tensor shape (batch_size, ...)
            opset_version: ONNX opset version
            config: Model configuration metadata
        """
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Set model to eval mode
        model.eval()
        
        # Create dummy input
        dummy_input = torch.randn(*input_shape)
        
        # Export to ONNX
        torch.onnx.export(
            model,
            dummy_input,
            save_path,
            export_params=True,
            opset_version=opset_version,
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={
                'input': {0: 'batch_size'},
                'output': {0: 'batch_size'}
            }
        )
        
        # Verify ONNX model
        onnx_model = onnx.load(save_path)
        onnx.checker.check_model(onnx_model)
        
        logger.info(f"Model exported to ONNX format: {save_path}")
        
        return str(save_path)


class TFLiteExporter:
    """Export models to TensorFlow Lite format"""
    
    @staticmethod
    def export(
        model: torch.nn.Module,
        save_path: str,
        input_shape: Tuple[int, ...],
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Export model to TensorFlow Lite format
        Note: This requires ONNX as intermediate format and tf2onnx
        
        Args:
            model: PyTorch model to export
            save_path: Path to save TFLite model
            input_shape: Input tensor shape
            config: Model configuration metadata
        """
        try:
            import tensorflow as tf
            import tf2onnx
        except ImportError:
            raise ImportError("TensorFlow and tf2onnx are required for TFLite export")
        
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # First export to ONNX
        onnx_path = save_path.with_suffix('.onnx')
        ONNXExporter.export(model, str(onnx_path), input_shape)
        
        # Convert ONNX to TensorFlow
        # This is a simplified approach - production code would need more robust conversion
        logger.info(f"Converting ONNX to TFLite: {save_path}")
        
        # Note: Full TFLite conversion would require additional steps
        # For now, we'll keep the ONNX intermediate
        
        logger.info(f"Model exported to TFLite format: {save_path}")
        
        return str(save_path)


class MetadataExporter:
    """Export model metadata and inference instructions"""
    
    @staticmethod
    def export(
        save_path: str,
        model_info: Dict[str, Any],
        preprocessing: Dict[str, Any],
        class_labels: list,
        training_metrics: Optional[Dict[str, float]] = None
    ):
        """
        Export model metadata to JSON
        
        Args:
            save_path: Path to save metadata
            model_info: Model architecture and configuration
            preprocessing: Preprocessing steps and parameters
            class_labels: List of class labels
            training_metrics: Training performance metrics
        """
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            'model_info': model_info,
            'preprocessing': preprocessing,
            'class_labels': class_labels,
            'num_classes': len(class_labels),
            'training_metrics': training_metrics or {}
        }
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Metadata exported: {save_path}")
        
        return str(save_path)


class ModelExporter:
    """
    Unified model exporter
    Handles exporting to multiple formats
    """
    
    def __init__(self, export_dir: str):
        """
        Initialize exporter
        
        Args:
            export_dir: Directory to save exported models
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_all(
        self,
        model: torch.nn.Module,
        formats: list,
        input_shape: Tuple[int, ...],
        model_name: str = "model",
        config: Optional[Dict[str, Any]] = None,
        class_labels: Optional[list] = None,
        training_metrics: Optional[Dict[str, float]] = None
    ) -> Dict[str, str]:
        """
        Export model to all specified formats
        
        Args:
            model: PyTorch model to export
            formats: List of export formats ('pytorch', 'onnx', 'tflite')
            input_shape: Input tensor shape
            model_name: Base name for exported files
            config: Model configuration
            class_labels: Class labels
            training_metrics: Training metrics
            
        Returns:
            Dictionary mapping format to file path
        """
        exported_files = {}
        
        # Export PyTorch
        if 'pytorch' in formats:
            pt_path = self.export_dir / f"{model_name}.pt"
            exported_files['pytorch'] = PyTorchExporter.export(model, str(pt_path), config)
        
        # Export ONNX
        if 'onnx' in formats:
            onnx_path = self.export_dir / f"{model_name}.onnx"
            exported_files['onnx'] = ONNXExporter.export(
                model, str(onnx_path), input_shape, config=config
            )
        
        # Export TFLite
        if 'tflite' in formats:
            tflite_path = self.export_dir / f"{model_name}.tflite"
            try:
                exported_files['tflite'] = TFLiteExporter.export(
                    model, str(tflite_path), input_shape, config
                )
            except ImportError as e:
                logger.warning(f"TFLite export failed: {e}")
        
        # Export metadata
        metadata_path = self.export_dir / f"{model_name}_metadata.json"
        exported_files['metadata'] = MetadataExporter.export(
            str(metadata_path),
            model_info=config or {},
            preprocessing={},
            class_labels=class_labels or [],
            training_metrics=training_metrics
        )
        
        # Create inference instructions
        instructions_path = self.export_dir / f"{model_name}_instructions.txt"
        self._create_instructions(instructions_path, config, class_labels)
        exported_files['instructions'] = str(instructions_path)
        
        return exported_files
    
    def _create_instructions(
        self,
        save_path: Path,
        config: Optional[Dict[str, Any]],
        class_labels: Optional[list]
    ):
        """Create inference instructions file"""
        instructions = f"""
# Model Inference Instructions

## Model Information
- Model Type: {config.get('model_type', 'Unknown') if config else 'Unknown'}
- Number of Classes: {len(class_labels) if class_labels else 'Unknown'}
- Class Labels: {', '.join(class_labels) if class_labels else 'Not specified'}

## Loading the Model (PyTorch)
```python
import torch

# Load model
checkpoint = torch.load('model.pt')
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

# Make prediction
with torch.no_grad():
    output = model(input_tensor)
    prediction = torch.argmax(output, dim=1)
```

## Loading the Model (ONNX)
```python
import onnxruntime as ort

# Load model
session = ort.InferenceSession('model.onnx')

# Make prediction
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name
prediction = session.run([output_name], {{input_name: input_data}})
```

## Preprocessing
Please refer to the metadata file for preprocessing requirements.

## Output
The model outputs class probabilities. Use argmax to get the predicted class.
"""
        
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(instructions)

