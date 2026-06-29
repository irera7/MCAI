"""
Audio classification models using spectrogram-based CNN
"""
import torch
import torch.nn as nn
import librosa
import numpy as np
from typing import Tuple, Optional

class SpectrogramCNN(nn.Module):
    """
    CNN for audio classification using spectrograms
    Converts audio to spectrogram and processes with CNN
    """
    def __init__(
        self,
        num_classes: int = 10,
        n_mels: int = 128,
        dropout: float = 0.3
    ):
        super(SpectrogramCNN, self).__init__()
        
        self.n_mels = n_mels
        
        # Convolutional layers
        self.conv_layers = nn.Sequential(
            # First block
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
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
        
        # Fully connected layers
        self.fc_layers = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(256, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        """
        Forward pass
        
        Args:
            x: Spectrogram input (batch_size, 1, n_mels, time_steps)
        """
        x = self.conv_layers(x)
        x = torch.flatten(x, 1)
        x = self.fc_layers(x)
        return x


class AudioPreprocessor:
    """
    Preprocessor for audio data
    Handles loading and converting audio to spectrograms
    """
    def __init__(
        self,
        sample_rate: int = 22050,
        n_mels: int = 128,
        n_fft: int = 2048,
        hop_length: int = 512,
        duration: float = 3.0
    ):
        self.sample_rate = sample_rate
        self.n_mels = n_mels
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.duration = duration
        self.target_length = int(sample_rate * duration)
    
    def load_audio(self, file_path: str) -> np.ndarray:
        """
        Load audio file
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Audio waveform
        """
        audio, sr = librosa.load(file_path, sr=self.sample_rate, duration=self.duration)
        
        # Pad or trim to target length
        if len(audio) < self.target_length:
            audio = np.pad(audio, (0, self.target_length - len(audio)))
        else:
            audio = audio[:self.target_length]
        
        return audio
    
    def audio_to_spectrogram(self, audio: np.ndarray) -> np.ndarray:
        """
        Convert audio waveform to mel spectrogram
        
        Args:
            audio: Audio waveform
            
        Returns:
            Mel spectrogram
        """
        # Compute mel spectrogram
        mel_spec = librosa.feature.melspectrogram(
            y=audio,
            sr=self.sample_rate,
            n_mels=self.n_mels,
            n_fft=self.n_fft,
            hop_length=self.hop_length
        )
        
        # Convert to log scale (dB)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        # Normalize
        mel_spec_db = (mel_spec_db - mel_spec_db.mean()) / (mel_spec_db.std() + 1e-8)
        
        return mel_spec_db
    
    def process_file(self, file_path: str) -> torch.Tensor:
        """
        Load and process audio file to spectrogram tensor
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Spectrogram tensor ready for model input
        """
        audio = self.load_audio(file_path)
        spec = self.audio_to_spectrogram(audio)
        
        # Convert to tensor and add channel dimension
        spec_tensor = torch.FloatTensor(spec).unsqueeze(0)
        
        return spec_tensor


def create_audio_model(
    model_type: str,
    num_classes: int,
    **kwargs
) -> nn.Module:
    """
    Factory function to create audio classification models
    
    Args:
        model_type: Type of model ('spectrogram_cnn')
        num_classes: Number of output classes
        **kwargs: Additional model-specific arguments
        
    Returns:
        PyTorch model instance
    """
    if model_type.lower() == 'spectrogram_cnn':
        n_mels = kwargs.get('n_mels', 128)
        dropout = kwargs.get('dropout', 0.3)
        return SpectrogramCNN(num_classes=num_classes, n_mels=n_mels, dropout=dropout)
    
    else:
        raise ValueError(f"Unknown model type: {model_type}")


# Model configurations
MODEL_CONFIGS = {
    'spectrogram_cnn': {
        'name': 'Spectrogram CNN',
        'description': 'CNN on audio spectrograms',
        'params': '~2M',
        'speed': 'Fast',
        'accuracy': 'High'
    }
}

