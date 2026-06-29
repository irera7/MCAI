"""
Data loaders for different modalities
"""
import torch
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
import numpy as np
from PIL import Image
from typing import List, Tuple, Optional
import json

class ImageDataset(Dataset):
    """Dataset for image classification"""
    
    def __init__(self, data_dir: str, transform=None):
        """
        Initialize image dataset
        
        Args:
            data_dir: Directory containing images organized by class
            transform: Optional transforms to apply
        """
        self.data_dir = Path(data_dir)
        self.transform = transform
        self.samples = []
        self.class_to_idx = {}
        
        # Scan directory for images
        self._scan_directory()
    
    def _scan_directory(self):
        """Scan directory and build sample list"""
        classes = sorted([d.name for d in self.data_dir.iterdir() if d.is_dir()])
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(classes)}
        
        for class_name in classes:
            class_dir = self.data_dir / class_name
            class_idx = self.class_to_idx[class_name]
            
            for img_path in class_dir.glob('*'):
                if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                    self.samples.append((str(img_path), class_idx))
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        return image, label


class TextDataset(Dataset):
    """Dataset for text classification"""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer=None, max_length: int = 128):
        """
        Initialize text dataset
        
        Args:
            texts: List of text samples
            labels: List of labels
            tokenizer: Tokenizer for text processing
            max_length: Maximum sequence length
        """
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        
        if self.tokenizer:
            encoding = self.tokenizer(
                text,
                max_length=self.max_length,
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )
            return {
                'input_ids': encoding['input_ids'].squeeze(),
                'attention_mask': encoding['attention_mask'].squeeze(),
                'label': torch.tensor(label)
            }
        
        return text, label


class AudioDataset(Dataset):
    """Dataset for audio classification"""
    
    def __init__(self, data_dir: str, preprocessor=None):
        """
        Initialize audio dataset
        
        Args:
            data_dir: Directory containing audio files by class
            preprocessor: Audio preprocessor
        """
        self.data_dir = Path(data_dir)
        self.preprocessor = preprocessor
        self.samples = []
        self.class_to_idx = {}
        
        self._scan_directory()
    
    def _scan_directory(self):
        """Scan directory for audio files"""
        classes = sorted([d.name for d in self.data_dir.iterdir() if d.is_dir()])
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(classes)}
        
        for class_name in classes:
            class_dir = self.data_dir / class_name
            class_idx = self.class_to_idx[class_name]
            
            for audio_path in class_dir.glob('*'):
                if audio_path.suffix.lower() in ['.wav', '.mp3', '.flac']:
                    self.samples.append((str(audio_path), class_idx))
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        audio_path, label = self.samples[idx]
        
        if self.preprocessor:
            audio_tensor = self.preprocessor.process_file(audio_path)
        else:
            # Return placeholder
            audio_tensor = torch.zeros(1, 128, 128)
        
        return audio_tensor, label


class TabularDataset(Dataset):
    """Dataset for tabular data"""
    
    def __init__(self, features: np.ndarray, labels: np.ndarray):
        """
        Initialize tabular dataset
        
        Args:
            features: Feature matrix (n_samples, n_features)
            labels: Labels array (n_samples,)
        """
        self.features = torch.FloatTensor(features)
        self.labels = torch.LongTensor(labels)
    
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx]


class TimeSeriesDataset(Dataset):
    """Dataset for time series classification"""
    
    def __init__(self, sequences: np.ndarray, labels: np.ndarray):
        """
        Initialize time series dataset
        
        Args:
            sequences: Sequence array (n_samples, sequence_length, n_features)
            labels: Labels array (n_samples,)
        """
        self.sequences = torch.FloatTensor(sequences)
        self.labels = torch.LongTensor(labels)
    
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        return self.sequences[idx], self.labels[idx]


class MedicalDataset(Dataset):
    """
    Dataset for medical data (MRI images, ECG/EEG signals)
    دیتاست برای داده‌های پزشکی (تصاویر MRI، سیگنال‌های ECG/EEG)
    """
    
    def __init__(
        self, 
        data_dir: str, 
        data_type: str = 'mri',  # 'mri', 'ecg', or 'eeg'
        preprocessor=None
    ):
        """
        Initialize medical dataset
        
        Args:
            data_dir: Directory containing medical data organized by class
            data_type: Type of medical data ('mri', 'ecg', 'eeg')
            preprocessor: Medical data preprocessor (DICOMPreprocessor or SignalPreprocessor)
        """
        self.data_dir = Path(data_dir)
        self.data_type = data_type.lower()
        self.preprocessor = preprocessor
        self.samples = []
        self.class_to_idx = {}
        
        # Scan directory for medical data files
        self._scan_directory()
    
    def _scan_directory(self):
        """Scan directory and build sample list"""
        classes = sorted([d.name for d in self.data_dir.iterdir() if d.is_dir()])
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(classes)}
        
        # Define file extensions based on data type
        if self.data_type == 'mri':
            valid_extensions = ['.dcm', '.dicom', '.nii', '.nii.gz']
        else:  # ecg or eeg
            valid_extensions = ['.csv', '.txt', '.dat']
        
        for class_name in classes:
            class_dir = self.data_dir / class_name
            class_idx = self.class_to_idx[class_name]
            
            for file_path in class_dir.glob('*'):
                if file_path.suffix.lower() in valid_extensions:
                    self.samples.append((str(file_path), class_idx))
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        """
        Get medical data sample
        
        Returns:
            tuple: (data_tensor, label)
        """
        file_path, label = self.samples[idx]
        
        try:
            if self.preprocessor:
                # Use provided preprocessor
                data_tensor = self.preprocessor.process_file(file_path)
            else:
                # Return placeholder based on data type
                if self.data_type == 'mri':
                    # MRI image placeholder (1, 224, 224)
                    data_tensor = torch.zeros(1, 224, 224)
                else:
                    # Signal placeholder (1, 1000)
                    data_tensor = torch.zeros(1, 1000)
        except Exception as e:
            print(f"Warning: Error loading {file_path}: {str(e)}")
            # Return placeholder on error
            if self.data_type == 'mri':
                data_tensor = torch.zeros(1, 224, 224)
            else:
                data_tensor = torch.zeros(1, 1000)
        
        return data_tensor, label


class GenomicDataset(Dataset):
    """
    Dataset for genomic data (DNA/RNA sequences)
    دیتاست برای داده‌های ژنومی (سکانس‌های DNA/RNA)
    """
    
    def __init__(
        self,
        data_dir: str,
        preprocessor=None,
        sequence_length: int = 1000
    ):
        """
        Initialize genomic dataset
        
        Args:
            data_dir: Directory containing FASTA files organized by class
            preprocessor: GenomicPreprocessor instance
            sequence_length: Target sequence length
        """
        self.data_dir = Path(data_dir)
        self.preprocessor = preprocessor
        self.sequence_length = sequence_length
        self.samples = []
        self.class_to_idx = {}
        
        # Scan directory for FASTA files
        self._scan_directory()
    
    def _scan_directory(self):
        """Scan directory and build sample list"""
        classes = sorted([d.name for d in self.data_dir.iterdir() if d.is_dir()])
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(classes)}
        
        # Valid FASTA file extensions
        valid_extensions = ['.fasta', '.fa', '.fna', '.ffn', '.faa', '.frn']
        
        for class_name in classes:
            class_dir = self.data_dir / class_name
            class_idx = self.class_to_idx[class_name]
            
            for file_path in class_dir.glob('*'):
                if file_path.suffix.lower() in valid_extensions:
                    self.samples.append((str(file_path), class_idx))
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        """
        Get genomic sequence sample
        
        Returns:
            tuple: (sequence_tensor, label)
        """
        file_path, label = self.samples[idx]
        
        try:
            if self.preprocessor:
                # Use provided preprocessor
                sequence_tensor = self.preprocessor.process_file(file_path)
            else:
                # Return placeholder (4, sequence_length) for one-hot encoding
                sequence_tensor = torch.zeros(4, self.sequence_length)
        except Exception as e:
            print(f"Warning: Error loading {file_path}: {str(e)}")
            # Return placeholder on error
            sequence_tensor = torch.zeros(4, self.sequence_length)
        
        return sequence_tensor, label


def create_dataloader(
    dataset: Dataset,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: int = 4
) -> DataLoader:
    """
    Create DataLoader from dataset
    
    Args:
        dataset: PyTorch dataset
        batch_size: Batch size
        shuffle: Whether to shuffle data
        num_workers: Number of worker processes
        
    Returns:
        DataLoader instance
    """
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=True
    )

