"""
Data preprocessing utilities for all modalities
"""
import torch
import torchvision.transforms as transforms
import numpy as np
from PIL import Image
from typing import Tuple, Optional

class ImagePreprocessor:
    """Image preprocessing pipeline"""
    
    def __init__(
        self,
        image_size: Tuple[int, int] = (224, 224),
        augment: bool = True,
        normalize: bool = True
    ):
        """
        Initialize image preprocessor
        
        Args:
            image_size: Target image size (height, width)
            augment: Whether to apply data augmentation
            normalize: Whether to normalize images
        """
        self.image_size = image_size
        self.augment = augment
        self.normalize = normalize
        
        # Build transform pipeline
        self.train_transform = self._build_train_transform()
        self.val_transform = self._build_val_transform()
    
    def _build_train_transform(self):
        """Build training transform pipeline"""
        transform_list = [
            transforms.Resize(self.image_size),
        ]
        
        if self.augment:
            transform_list.extend([
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomRotation(15),
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
                transforms.RandomAffine(degrees=0, translate=(0.1, 0.1))
            ])
        
        transform_list.append(transforms.ToTensor())
        
        if self.normalize:
            transform_list.append(
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            )
        
        return transforms.Compose(transform_list)
    
    def _build_val_transform(self):
        """Build validation transform pipeline"""
        transform_list = [
            transforms.Resize(self.image_size),
            transforms.ToTensor()
        ]
        
        if self.normalize:
            transform_list.append(
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            )
        
        return transforms.Compose(transform_list)
    
    def get_train_transform(self):
        """Get training transform"""
        return self.train_transform
    
    def get_val_transform(self):
        """Get validation transform"""
        return self.val_transform


class DataAugmentor:
    """Data augmentation for various modalities"""
    
    @staticmethod
    def augment_audio(audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Augment audio data
        
        Args:
            audio: Audio waveform
            sr: Sample rate
            
        Returns:
            Augmented audio
        """
        import librosa
        
        # Random time stretch
        if np.random.random() < 0.5:
            rate = np.random.uniform(0.8, 1.2)
            audio = librosa.effects.time_stretch(audio, rate=rate)
        
        # Random pitch shift
        if np.random.random() < 0.5:
            n_steps = np.random.randint(-2, 3)
            audio = librosa.effects.pitch_shift(audio, sr=sr, n_steps=n_steps)
        
        # Add noise
        if np.random.random() < 0.3:
            noise = np.random.randn(len(audio)) * 0.005
            audio = audio + noise
        
        return audio
    
    @staticmethod
    def augment_timeseries(series: np.ndarray) -> np.ndarray:
        """
        Augment time series data
        
        Args:
            series: Time series array
            
        Returns:
            Augmented series
        """
        # Random scaling
        if np.random.random() < 0.5:
            scale = np.random.uniform(0.8, 1.2)
            series = series * scale
        
        # Random jittering
        if np.random.random() < 0.5:
            jitter = np.random.randn(*series.shape) * 0.05
            series = series + jitter
        
        # Random time warping
        if np.random.random() < 0.3:
            from scipy.ndimage import zoom
            zoom_factor = np.random.uniform(0.9, 1.1)
            series = zoom(series, zoom_factor)
        
        return series


class DataNormalizer:
    """Data normalization utilities"""
    
    @staticmethod
    def normalize_features(data: np.ndarray, method: str = 'standard') -> Tuple[np.ndarray, dict]:
        """
        Normalize feature data
        
        Args:
            data: Feature matrix
            method: Normalization method ('standard', 'minmax')
            
        Returns:
            Normalized data and normalization parameters
        """
        if method == 'standard':
            mean = np.mean(data, axis=0)
            std = np.std(data, axis=0) + 1e-8
            normalized = (data - mean) / std
            params = {'mean': mean, 'std': std, 'method': 'standard'}
        
        elif method == 'minmax':
            min_val = np.min(data, axis=0)
            max_val = np.max(data, axis=0)
            normalized = (data - min_val) / (max_val - min_val + 1e-8)
            params = {'min': min_val, 'max': max_val, 'method': 'minmax'}
        
        else:
            raise ValueError(f"Unknown normalization method: {method}")
        
        return normalized, params
    
    @staticmethod
    def apply_normalization(data: np.ndarray, params: dict) -> np.ndarray:
        """
        Apply normalization with given parameters
        
        Args:
            data: Data to normalize
            params: Normalization parameters
            
        Returns:
            Normalized data
        """
        method = params['method']
        
        if method == 'standard':
            return (data - params['mean']) / params['std']
        elif method == 'minmax':
            return (data - params['min']) / (params['max'] - params['min'])
        else:
            raise ValueError(f"Unknown method: {method}")

