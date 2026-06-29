"""
Audio Data Loader for ModelCreator
Handles loading and preprocessing of audio data for classification
"""

import torch
from torch.utils.data import Dataset, DataLoader, random_split
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path
import os
import numpy as np
import librosa

class AudioDataset(Dataset):
    """
    Dataset for audio classification
    Loads audio files and converts them to spectrograms
    """
    
    def __init__(
        self,
        data_dir: str,
        label_map: Dict[str, int],
        sample_rate: int = 22050,
        n_mels: int = 128,
        n_fft: int = 2048,
        hop_length: int = 512,
        duration: float = 3.0
    ):
        """
        Initialize Audio Dataset
        
        Args:
            data_dir: Directory containing audio files
            label_map: Mapping from label names to label IDs
            sample_rate: Target sample rate for audio
            n_mels: Number of mel bands
            n_fft: FFT window size
            hop_length: Hop length for spectrogram
            duration: Duration to which audio will be padded/trimmed (seconds)
        """
        self.data_dir = Path(data_dir)
        self.label_map = label_map
        self.sample_rate = sample_rate
        self.n_mels = n_mels
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.duration = duration
        self.target_length = int(sample_rate * duration)
        
        # Supported audio formats
        self.audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
        
        self.samples = self._load_samples()
        
        if not self.samples:
            raise ValueError(f"No audio samples found in {data_dir}")
        
        print(f"Loaded {len(self.samples)} audio samples from {data_dir}")
    
    def _load_samples(self) -> List[Tuple[str, int]]:
        """
        Load audio file paths and their labels
        
        Returns:
            List of (file_path, label_id) tuples
        """
        samples = []
        
        # Load from subdirectories (one per class)
        for label_name, label_id in self.label_map.items():
            label_dir = self.data_dir / label_name
            
            if not label_dir.exists() or not label_dir.is_dir():
                print(f"Warning: Directory not found for label '{label_name}': {label_dir}")
                continue
            
            # Find all audio files
            for audio_file in label_dir.iterdir():
                if audio_file.is_file() and audio_file.suffix.lower() in self.audio_extensions:
                    samples.append((str(audio_file), label_id))
        
        if not samples:
            print(f"WARNING: No audio files found in {self.data_dir}")
            print(f"Expected structure: {self.data_dir}/class_name/*.wav")
            print(f"Supported formats: {self.audio_extensions}")
        
        return samples
    
    def _load_audio(self, file_path: str) -> np.ndarray:
        """
        Load audio file and normalize length
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Audio waveform
        """
        try:
            # Load audio
            audio, sr = librosa.load(file_path, sr=self.sample_rate, duration=self.duration)
            
            # Pad or trim to target length
            if len(audio) < self.target_length:
                audio = np.pad(audio, (0, self.target_length - len(audio)))
            else:
                audio = audio[:self.target_length]
            
            return audio
            
        except Exception as e:
            print(f"Error loading audio file {file_path}: {e}")
            # Return silence on error
            return np.zeros(self.target_length)
    
    def _audio_to_spectrogram(self, audio: np.ndarray) -> np.ndarray:
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
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        """
        Get audio sample and label
        
        Args:
            idx: Sample index
            
        Returns:
            (spectrogram_tensor, label)
        """
        audio_path, label = self.samples[idx]
        
        # Load and process audio
        audio = self._load_audio(audio_path)
        spectrogram = self._audio_to_spectrogram(audio)
        
        # Convert to tensor and add channel dimension
        spec_tensor = torch.FloatTensor(spectrogram).unsqueeze(0)  # (1, n_mels, time_steps)
        
        return spec_tensor, label


class AudioDataLoader:
    """
    Data loader manager for audio classification
    Handles dataset creation and train/val/test splitting
    """
    
    def __init__(self, project_dir: str, config: dict):
        """
        Initialize Audio Data Loader
        
        Args:
            project_dir: Project directory containing data/ subdirectory
            config: Configuration dictionary with training parameters
        """
        self.project_dir = Path(project_dir)
        self.data_dir = self.project_dir / "data"
        self.config = config
        
        # Load or create label map
        self.label_map = self._load_label_map()
        self.num_classes = len(self.label_map)
        
        print(f"\nAudio Data Loader initialized for project: {project_dir}")
        print(f"Number of classes: {self.num_classes}")
        print(f"Classes: {list(self.label_map.keys())}")
    
    def _load_label_map(self) -> Dict[str, int]:
        """
        Load or auto-detect label mapping
        
        Returns:
            Dictionary mapping label names to IDs
        """
        label_file = self.project_dir / "labels.json"
        
        # Try loading existing labels.json
        if label_file.exists():
            with open(label_file, 'r', encoding='utf-8') as f:
                label_map = json.load(f)
            print(f"Loaded {len(label_map)} audio classes from labels.json")
            return label_map
        
        # Auto-detect from directory structure
        label_map = {}
        if self.data_dir.exists():
            subdirs = [d for d in self.data_dir.iterdir() if d.is_dir()]
            for idx, label_dir in enumerate(sorted(subdirs)):
                label_map[label_dir.name] = idx
        
        # Save detected labels
        if label_map:
            with open(label_file, 'w', encoding='utf-8') as f:
                json.dump(label_map, f, ensure_ascii=False, indent=2)
            print(f"Auto-detected and saved {len(label_map)} audio classes")
        else:
            # Default fallback
            label_map = {"class_0": 0}
            print("WARNING: No audio classes found, using default class_0")
        
        return label_map
    
    def create_loaders(self) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """
        Create train, validation, and test data loaders
        
        Returns:
            Tuple of (train_loader, val_loader, test_loader)
        """
        # Get config parameters
        batch_size = self.config.get('batch_size', 16)
        num_workers = self.config.get('num_workers', 0)  # 0 for audio to avoid multiprocessing issues
        train_split = self.config.get('train_split', 0.7)
        val_split = self.config.get('val_split', 0.15)
        
        # Audio-specific parameters
        sample_rate = self.config.get('sample_rate', 22050)
        n_mels = self.config.get('n_mels', 128)
        n_fft = self.config.get('n_fft', 2048)
        hop_length = self.config.get('hop_length', 512)
        duration = self.config.get('duration', 3.0)
        
        # Create full dataset
        full_dataset = AudioDataset(
            str(self.data_dir),
            self.label_map,
            sample_rate=sample_rate,
            n_mels=n_mels,
            n_fft=n_fft,
            hop_length=hop_length,
            duration=duration
        )
        
        total_samples = len(full_dataset)
        if total_samples == 0:
            raise ValueError(f"No audio samples found in {self.data_dir}")
        
        # Calculate split sizes
        train_size = int(total_samples * train_split)
        val_size = int(total_samples * val_split)
        test_size = total_samples - train_size - val_size
        
        # Ensure at least 1 sample in each split if possible
        if train_size == 0 and total_samples > 0:
            train_size = 1
        if val_size == 0 and total_samples > 1:
            val_size = 1
        if test_size == 0 and total_samples > 2:
            test_size = 1
        
        # Adjust if sum exceeds total
        if train_size + val_size + test_size > total_samples:
            test_size = max(0, total_samples - train_size - val_size)
        
        print(f"\nSplitting {total_samples} audio samples:")
        print(f"  Train: {train_size} samples")
        print(f"  Val:   {val_size} samples")
        print(f"  Test:  {test_size} samples")
        
        # Split dataset
        generator = torch.Generator().manual_seed(42)
        train_dataset, val_dataset, test_dataset = random_split(
            full_dataset,
            [train_size, val_size, test_size],
            generator=generator
        )
        
        # Create data loaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available()
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available()
        )
        
        test_loader = DataLoader(
            test_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available()
        )
        
        print(f"\nCreated audio data loaders:")
        print(f"  Train: {len(train_dataset)} samples, {len(train_loader)} batches")
        print(f"  Val:   {len(val_dataset)} samples, {len(val_loader)} batches")
        print(f"  Test:  {len(test_dataset)} samples, {len(test_loader)} batches")
        
        return train_loader, val_loader, test_loader


def create_audio_loaders(
    project_dir: str,
    config: dict
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Convenience function to create audio data loaders
    
    Args:
        project_dir: Project directory path
        config: Configuration dictionary
        
    Returns:
        Tuple of (train_loader, val_loader, test_loader)
    """
    loader = AudioDataLoader(project_dir, config)
    return loader.create_loaders()

