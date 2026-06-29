"""
Genomic data classification models
Processes DNA/RNA sequences for classification
"""
import torch
import torch.nn as nn
import numpy as np
from Bio import SeqIO
from typing import Dict, List

class DNA_CNN(nn.Module):
    """
    1D CNN for DNA sequence classification
    Processes one-hot encoded DNA sequences
    """
    def __init__(
        self,
        num_classes: int = 2,
        sequence_length: int = 1000,
        dropout: float = 0.3
    ):
        super(DNA_CNN, self).__init__()
        
        # Input is 4 channels (A, C, G, T)
        self.conv_layers = nn.Sequential(
            # First 1D conv block
            nn.Conv1d(4, 64, kernel_size=8, padding=4),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=4),
            
            # Second 1D conv block
            nn.Conv1d(64, 128, kernel_size=8, padding=4),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=4),
            
            # Third 1D conv block
            nn.Conv1d(128, 256, kernel_size=8, padding=4),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=4),
            
            # Global average pooling
            nn.AdaptiveAvgPool1d(1)
        )
        
        self.fc_layers = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x):
        """
        Forward pass
        
        Args:
            x: One-hot encoded sequence (batch_size, 4, sequence_length)
        """
        x = self.conv_layers(x)
        x = torch.flatten(x, 1)
        x = self.fc_layers(x)
        return x


class SequenceEmbedding(nn.Module):
    """
    Sequence embedding model for genomic data
    Uses embedding layer + LSTM for sequence processing
    """
    def __init__(
        self,
        vocab_size: int = 5,  # A, C, G, T, N
        embedding_dim: int = 64,
        hidden_dim: int = 128,
        num_layers: int = 2,
        num_classes: int = 2,
        dropout: float = 0.3
    ):
        super(SequenceEmbedding, self).__init__()
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers=num_layers,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        self.fc = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_dim * 2, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x):
        """
        Forward pass
        
        Args:
            x: Encoded sequence indices (batch_size, sequence_length)
        """
        embedded = self.embedding(x)
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # Concatenate forward and backward hidden states
        hidden = torch.cat((hidden[-2], hidden[-1]), dim=1)
        
        output = self.fc(hidden)
        return output


class GenomicPreprocessor:
    """
    Preprocessor for genomic sequences
    Handles FASTA files and sequence encoding
    """
    def __init__(
        self,
        target_length: int = 1000,
        encoding_type: str = 'onehot'  # 'onehot' or 'index'
    ):
        self.target_length = target_length
        self.encoding_type = encoding_type
        
        # Nucleotide mappings
        self.nucleotide_to_index = {'A': 1, 'C': 2, 'G': 3, 'T': 4, 'N': 0}
        self.nucleotide_to_onehot = {
            'A': [1, 0, 0, 0],
            'C': [0, 1, 0, 0],
            'G': [0, 0, 1, 0],
            'T': [0, 0, 0, 1],
            'N': [0, 0, 0, 0]
        }
    
    def load_fasta(self, file_path: str) -> str:
        """
        Load sequence from FASTA file
        
        Args:
            file_path: Path to FASTA file
            
        Returns:
            DNA sequence string
        """
        try:
            record = next(SeqIO.parse(file_path, "fasta"))
            return str(record.seq).upper()
        except Exception as e:
            raise ValueError(f"Error loading FASTA file: {str(e)}")
    
    def encode_sequence_onehot(self, sequence: str) -> np.ndarray:
        """
        Encode DNA sequence as one-hot
        
        Args:
            sequence: DNA sequence string
            
        Returns:
            One-hot encoded array (4, sequence_length)
        """
        # Trim or pad sequence
        if len(sequence) > self.target_length:
            sequence = sequence[:self.target_length]
        elif len(sequence) < self.target_length:
            sequence = sequence + 'N' * (self.target_length - len(sequence))
        
        # One-hot encode
        encoded = np.array([self.nucleotide_to_onehot.get(nuc, [0, 0, 0, 0]) for nuc in sequence])
        
        # Transpose to (4, sequence_length)
        encoded = encoded.T
        
        return encoded.astype(np.float32)
    
    def encode_sequence_index(self, sequence: str) -> np.ndarray:
        """
        Encode DNA sequence as indices
        
        Args:
            sequence: DNA sequence string
            
        Returns:
            Index encoded array (sequence_length,)
        """
        # Trim or pad sequence
        if len(sequence) > self.target_length:
            sequence = sequence[:self.target_length]
        elif len(sequence) < self.target_length:
            sequence = sequence + 'N' * (self.target_length - len(sequence))
        
        # Index encode
        encoded = np.array([self.nucleotide_to_index.get(nuc, 0) for nuc in sequence])
        
        return encoded.astype(np.int64)
    
    def process_file(self, file_path: str) -> torch.Tensor:
        """
        Load and process FASTA file to tensor
        
        Args:
            file_path: Path to FASTA file
            
        Returns:
            Encoded tensor
        """
        sequence = self.load_fasta(file_path)
        
        if self.encoding_type == 'onehot':
            encoded = self.encode_sequence_onehot(sequence)
            return torch.FloatTensor(encoded)
        else:
            encoded = self.encode_sequence_index(sequence)
            return torch.LongTensor(encoded)


def create_genomic_model(
    model_type: str,
    num_classes: int = 2,
    **kwargs
) -> nn.Module:
    """
    Factory function to create genomic classification models
    
    Args:
        model_type: Type of model ('dna_cnn', 'sequence_embedding')
        num_classes: Number of output classes
        **kwargs: Additional model-specific arguments
        
    Returns:
        PyTorch model instance
    """
    if model_type.lower() == 'dna_cnn':
        return DNA_CNN(num_classes=num_classes, **kwargs)
    
    elif model_type.lower() == 'sequence_embedding':
        return SequenceEmbedding(num_classes=num_classes, **kwargs)
    
    else:
        raise ValueError(f"Unknown model type: {model_type}")


# Model configurations
MODEL_CONFIGS = {
    'dna_cnn': {
        'name': 'DNA CNN',
        'description': '1D CNN for DNA sequences',
        'params': '~2M',
        'speed': 'Fast',
        'accuracy': 'High'
    },
    'sequence_embedding': {
        'name': 'Sequence Embedding',
        'description': 'Learned sequence representations',
        'params': '~3M',
        'speed': 'Fast',
        'accuracy': 'High'
    }
}

