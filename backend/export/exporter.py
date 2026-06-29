"""
Model Export Module
Export trained models to various formats
"""

import torch
import torch.nn as nn
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ModelExporter:
    """
    Export trained models to different formats
    Supports PyTorch, ONNX, and TorchScript
    """
    
    @staticmethod
    def export_pytorch(model: nn.Module, save_path: str,
                      include_optimizer: bool = False,
                      optimizer: Optional[torch.optim.Optimizer] = None,
                      metadata: Optional[dict] = None):
        """
        Export model in PyTorch format (.pt, .pth)
        
        Args:
            model: PyTorch model
            save_path: Path to save the model
            include_optimizer: Whether to include optimizer state
            optimizer: Optimizer (if include_optimizer=True)
            metadata: Additional metadata to save
        """
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare checkpoint
        checkpoint = {
            'model_state_dict': model.state_dict(),
            'metadata': metadata or {}
        }
        
        if include_optimizer and optimizer is not None:
            checkpoint['optimizer_state_dict'] = optimizer.state_dict()
        
        # Save
        torch.save(checkpoint, save_path)
        logger.info(f"Model exported to PyTorch format: {save_path}")
        
        return str(save_path)
    
    @staticmethod
    def export_onnx(model: nn.Module, save_path: str,
                   input_shape: Tuple[int, ...] = (1, 3, 224, 224),
                   input_names: list = ['input'],
                   output_names: list = ['output'],
                   dynamic_axes: Optional[dict] = None,
                   opset_version: int = 14):
        """
        Export model to ONNX format (.onnx)
        
        Args:
            model: PyTorch model
            save_path: Path to save the model
            input_shape: Shape of input tensor (batch_size, channels, height, width)
            input_names: Names for input tensors
            output_names: Names for output tensors
            dynamic_axes: Dynamic axes specification
            opset_version: ONNX opset version
        """
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Set model to eval mode
        model.eval()
        
        # Create dummy input
        dummy_input = torch.randn(*input_shape)
        
        # Dynamic axes for variable batch size
        if dynamic_axes is None:
            dynamic_axes = {
                'input': {0: 'batch_size'},
                'output': {0: 'batch_size'}
            }
        
        # Export
        try:
            torch.onnx.export(
                model,
                dummy_input,
                save_path,
                input_names=input_names,
                output_names=output_names,
                dynamic_axes=dynamic_axes,
                opset_version=opset_version,
                do_constant_folding=True,
                export_params=True
            )
            logger.info(f"Model exported to ONNX format: {save_path}")
            return str(save_path)
            
        except Exception as e:
            logger.error(f"Failed to export to ONNX: {e}")
            raise
    
    @staticmethod
    def export_torchscript(model: nn.Module, save_path: str,
                          input_shape: Tuple[int, ...] = (1, 3, 224, 224),
                          method: str = 'trace'):
        """
        Export model to TorchScript format (.pt)
        
        Args:
            model: PyTorch model
            save_path: Path to save the model
            input_shape: Shape of input tensor
            method: 'trace' or 'script'
        """
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Set model to eval mode
        model.eval()
        
        try:
            if method == 'trace':
                # Trace the model
                dummy_input = torch.randn(*input_shape)
                traced_model = torch.jit.trace(model, dummy_input)
                traced_model.save(save_path)
            elif method == 'script':
                # Script the model
                scripted_model = torch.jit.script(model)
                scripted_model.save(save_path)
            else:
                raise ValueError(f"Unknown method: {method}. Use 'trace' or 'script'")
            
            logger.info(f"Model exported to TorchScript format: {save_path}")
            return str(save_path)
            
        except Exception as e:
            logger.error(f"Failed to export to TorchScript: {e}")
            raise
    
    @staticmethod
    def export_all_formats(model: nn.Module, output_dir: str,
                          model_name: str = 'model',
                          input_shape: Tuple[int, ...] = (1, 3, 224, 224),
                          metadata: Optional[dict] = None):
        """
        Export model to all supported formats
        
        Args:
            model: PyTorch model
            output_dir: Directory to save exported models
            model_name: Base name for exported files
            input_shape: Input shape for ONNX/TorchScript
            metadata: Metadata to include
            
        Returns:
            Dictionary with paths to exported files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = {}
        
        # PyTorch
        try:
            pt_path = output_dir / f"{model_name}.pt"
            ModelExporter.export_pytorch(model, str(pt_path), metadata=metadata)
            exported_files['pytorch'] = str(pt_path)
        except Exception as e:
            logger.error(f"Failed to export PyTorch: {e}")
        
        # ONNX
        try:
            onnx_path = output_dir / f"{model_name}.onnx"
            ModelExporter.export_onnx(model, str(onnx_path), input_shape=input_shape)
            exported_files['onnx'] = str(onnx_path)
        except Exception as e:
            logger.error(f"Failed to export ONNX: {e}")
        
        # TorchScript
        try:
            ts_path = output_dir / f"{model_name}_torchscript.pt"
            ModelExporter.export_torchscript(model, str(ts_path), input_shape=input_shape)
            exported_files['torchscript'] = str(ts_path)
        except Exception as e:
            logger.error(f"Failed to export TorchScript: {e}")
        
        return exported_files


def load_pytorch_model(model_path: str, model: nn.Module) -> nn.Module:
    """
    Load a PyTorch model from checkpoint
    
    Args:
        model_path: Path to model checkpoint
        model: Model architecture (for loading state_dict)
        
    Returns:
        Loaded model
    """
    checkpoint = torch.load(model_path, map_location='cpu')
    
    if 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
    else:
        model.load_state_dict(checkpoint)
    
    model.eval()
    return model


# Test code
if __name__ == "__main__":
    from engine.model_builder import ModelBuilder
    
    print("Testing Model Exporter...")
    
    # Create a simple model
    model = ModelBuilder.build_image_model('resnet18', num_classes=10, pretrained=False)
    
    # Export to all formats
    output_dir = "test_exports"
    exported = ModelExporter.export_all_formats(
        model,
        output_dir,
        model_name='test_model',
        metadata={'classes': 10, 'architecture': 'resnet18'}
    )
    
    print("\nExported files:")
    for format_name, path in exported.items():
        print(f"  {format_name}: {path}")
    
    print("\nExport test complete!")

