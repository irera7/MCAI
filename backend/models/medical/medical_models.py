"""
Medical data classification models
Includes models for MRI images and ECG/EEG signals
"""
import torch
import torch.nn as nn
import pydicom
import numpy as np
from pathlib import Path
from typing import Tuple, Optional

class MRI_CNN(nn.Module):
    """
    2D CNN for MRI image classification
    Processes medical images for diagnosis
    """
    def __init__(
        self,
        num_classes: int = 2,
        input_channels: int = 1,  # Typically grayscale
        dropout: float = 0.3
    ):
        super(MRI_CNN, self).__init__()
        
        self.conv_layers = nn.Sequential(
            # First block
            nn.Conv2d(input_channels, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            
            # Second block
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            
            # Third block
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            
            # Fourth block
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        
        self.fc_layers = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(256, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        """Forward pass"""
        x = self.conv_layers(x)
        x = torch.flatten(x, 1)
        x = self.fc_layers(x)
        return x


class ECG_CNN(nn.Module):
    """
    1D CNN for ECG/EEG signal classification
    Processes time-series physiological signals
    """
    def __init__(
        self,
        input_channels: int = 1,
        num_classes: int = 2,
        dropout: float = 0.3
    ):
        super(ECG_CNN, self).__init__()
        
        self.conv_layers = nn.Sequential(
            # First 1D conv block
            nn.Conv1d(input_channels, 64, kernel_size=7, padding=3),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=2),
            
            # Second 1D conv block
            nn.Conv1d(64, 128, kernel_size=5, padding=2),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=2),
            
            # Third 1D conv block
            nn.Conv1d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=2),
            
            # Fourth 1D conv block
            nn.Conv1d(256, 512, kernel_size=3, padding=1),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool1d(1)
        )
        
        self.fc_layers = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        """
        Forward pass
        
        Args:
            x: Input (batch_size, channels, signal_length)
        """
        x = self.conv_layers(x)
        x = torch.flatten(x, 1)
        x = self.fc_layers(x)
        return x


class DICOMPreprocessor:
    """
    Preprocessor for DICOM medical images
    Handles loading and preprocessing DICOM files
    """
    def __init__(
        self,
        target_size: Tuple[int, int] = (224, 224),
        normalize: bool = True
    ):
        self.target_size = target_size
        self.normalize = normalize
    
    def load_dicom(self, file_path: str) -> np.ndarray:
        """
        Load DICOM file
        
        Args:
            file_path: Path to DICOM file
            
        Returns:
            Image array
        """
        try:
            dicom = pydicom.dcmread(file_path)
            image = dicom.pixel_array.astype(float)
            
            # Normalize pixel values
            if self.normalize:
                image = (image - image.min()) / (image.max() - image.min())
            
            return image
        except Exception as e:
            raise ValueError(f"Error loading DICOM file: {str(e)}")
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess medical image
        
        Args:
            image: Input image array
            
        Returns:
            Preprocessed image
        """
        # Resize using simple interpolation
        from scipy.ndimage import zoom
        
        zoom_factors = (
            self.target_size[0] / image.shape[0],
            self.target_size[1] / image.shape[1]
        )
        resized = zoom(image, zoom_factors, order=1)
        
        # Normalize
        if self.normalize:
            resized = (resized - resized.mean()) / (resized.std() + 1e-8)
        
        return resized
    
    def process_file(self, file_path: str) -> torch.Tensor:
        """
        Load and process DICOM file to tensor
        
        Args:
            file_path: Path to DICOM file
            
        Returns:
            Preprocessed tensor
        """
        image = self.load_dicom(file_path)
        preprocessed = self.preprocess_image(image)
        
        # Convert to tensor and add channel dimension
        tensor = torch.FloatTensor(preprocessed).unsqueeze(0)
        
        return tensor


class SignalPreprocessor:
    """
    Preprocessor for physiological signals (ECG, EEG)
    """
    def __init__(
        self,
        target_length: int = 1000,
        sampling_rate: int = 250,
        normalize: bool = True
    ):
        self.target_length = target_length
        self.sampling_rate = sampling_rate
        self.normalize = normalize
    
    def load_signal(self, file_path: str) -> np.ndarray:
        """
        Load signal from file
        
        Args:
            file_path: Path to signal file
            
        Returns:
            Signal array
        """
        # This is a placeholder - actual implementation depends on file format
        signal = np.loadtxt(file_path)
        return signal
    
    def preprocess_signal(self, signal: np.ndarray) -> np.ndarray:
        """
        Preprocess signal
        
        Args:
            signal: Input signal
            
        Returns:
            Preprocessed signal
        """
        # Resample or pad to target length
        if len(signal) > self.target_length:
            # Downsample
            indices = np.linspace(0, len(signal) - 1, self.target_length, dtype=int)
            signal = signal[indices]
        elif len(signal) < self.target_length:
            # Pad
            signal = np.pad(signal, (0, self.target_length - len(signal)), mode='constant')
        
        # Normalize
        if self.normalize:
            signal = (signal - signal.mean()) / (signal.std() + 1e-8)
        
        return signal
    
    def process_file(self, file_path: str) -> torch.Tensor:
        """
        Load and process signal file to tensor
        
        Args:
            file_path: Path to signal file
            
        Returns:
            Preprocessed tensor
        """
        signal = self.load_signal(file_path)
        preprocessed = self.preprocess_signal(signal)
        
        # Convert to tensor and add channel dimension
        tensor = torch.FloatTensor(preprocessed).unsqueeze(0)
        
        return tensor


def create_medical_model(
    model_type: str,
    num_classes: int = 2,
    **kwargs
) -> nn.Module:
    """
    Factory function to create medical data classification models
    
    Args:
        model_type: Type of model ('mri_cnn', 'ecg_cnn')
        num_classes: Number of output classes
        **kwargs: Additional model-specific arguments
        
    Returns:
        PyTorch model instance
    """
    if model_type.lower() == 'mri_cnn':
        return MRI_CNN(num_classes=num_classes, **kwargs)
    
    elif model_type.lower() in ['ecg_cnn', 'eeg_cnn']:
        return ECG_CNN(num_classes=num_classes, **kwargs)
    
    else:
        raise ValueError(f"Unknown model type: {model_type}")


# Model configurations
MODEL_CONFIGS = {
    'mri_cnn': {
        'name': 'MRI CNN',
        'description': '2D CNN for medical images',
        'params': '~5M',
        'speed': 'Fast',
        'accuracy': 'High'
    },
    'ecg_cnn': {
        'name': 'ECG/EEG CNN',
        'description': '1D CNN for physiological signals',
        'params': '~3M',
        'speed': 'Fast',
        'accuracy': 'High'
    }
}

