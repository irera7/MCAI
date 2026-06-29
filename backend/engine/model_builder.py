"""
Model Builder Module
Creates neural network models for different architectures
"""

import torch
import torch.nn as nn
import timm
from typing import Optional, Dict, Any


class ModelBuilder:
    """
    Factory class for building neural network models
    Supports various architectures from torchvision and timm
    """
    
    SUPPORTED_MODELS = {
        'image': [
            'resnet18', 'resnet34', 'resnet50',
            'efficientnet_b0', 'efficientnet_b1',  'efficientnet_b2',
            'mobilenetv2_100', 'mobilenetv3_small_100',
            'vit_tiny_patch16_224', 'vit_small_patch16_224',
        ],
        'text': [
            'lstm', 'gru', 'transformer', 'bert'
        ],
        'audio': [
            'spectrogram_cnn'
        ],
        'medical': [
            'mri_cnn', 'ecg_cnn', 'eeg_cnn'
        ],
        'genomic': [
            'dna_cnn', 'sequence_embedding'
        ]
    }
    
    @staticmethod
    def build_image_model(model_name: str, num_classes: int, 
                         pretrained: bool = True) -> nn.Module:
        """
        Build an image classification model
        
        Args:
            model_name: Name of the model architecture
            num_classes: Number of output classes
            pretrained: Whether to use pretrained weights
            
        Returns:
            PyTorch model
        """
        print(f"Building {model_name} for {num_classes} classes (pretrained={pretrained})")
        
        try:
            # Use timm for model creation
            model = timm.create_model(
                model_name,
                pretrained=pretrained,
                num_classes=num_classes
            )
            
            print(f"Model created successfully")
            print(f"  Total parameters: {sum(p.numel() for p in model.parameters()):,}")
            print(f"  Trainable parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
            
            return model
            
        except Exception as e:
            raise ValueError(f"Failed to create model {model_name}: {e}")
    
    @staticmethod
    def build_text_model(model_name: str, vocab_size: int, embed_dim: int,
                        num_classes: int, **kwargs) -> nn.Module:
        """
        Build a text classification model
        
        Args:
            model_name: 'lstm', 'gru', 'transformer', or 'bert'
            vocab_size: Size of vocabulary
            embed_dim: Embedding dimension
            num_classes: Number of output classes
            **kwargs: Additional model-specific arguments
            
        Returns:
            PyTorch model
        """
        model_name_lower = model_name.lower()
        
        if model_name_lower == 'lstm':
            return LSTMClassifier(vocab_size, embed_dim, num_classes, **kwargs)
        elif model_name_lower == 'gru':
            return GRUClassifier(vocab_size, embed_dim, num_classes, **kwargs)
        elif model_name_lower == 'transformer':
            return TransformerClassifier(vocab_size, embed_dim, num_classes, **kwargs)
        elif model_name_lower == 'bert':
            # BERT doesn't use vocab_size/embed_dim from here
            # Import BERT model from models folder
            try:
                from models.text.text_models import BERTClassifier
                dropout = kwargs.get('dropout', 0.3)
                model_type = kwargs.get('model_type', 'bert-base-uncased')
                return BERTClassifier(num_classes=num_classes, model_name=model_type, dropout=dropout)
            except ImportError:
                print("Warning: BERT model not available. Using LSTM instead.")
                return LSTMClassifier(vocab_size, embed_dim, num_classes, **kwargs)
        else:
            raise ValueError(f"Unsupported text model: {model_name}")
    
    @staticmethod
    def build_audio_model(model_name: str, num_classes: int, **kwargs) -> nn.Module:
        """
        Build an audio classification model
        
        Args:
            model_name: 'spectrogram_cnn'
            num_classes: Number of output classes
            **kwargs: Additional model-specific arguments (n_mels, dropout, etc.)
            
        Returns:
            PyTorch model
        """
        print(f"Building {model_name} for {num_classes} classes")
        
        if model_name.lower() == 'spectrogram_cnn':
            from models.audio.audio_models import SpectrogramCNN
            n_mels = kwargs.get('n_mels', 128)
            dropout = kwargs.get('dropout', 0.3)
            return SpectrogramCNN(num_classes=num_classes, n_mels=n_mels, dropout=dropout)
        else:
            raise ValueError(f"Unsupported audio model: {model_name}")
    
    @staticmethod
    def build_medical_model(model_name: str, num_classes: int, **kwargs) -> nn.Module:
        """
        Build a medical data classification model
        بناء مدل دسته‌بندی داده‌های پزشکی
        
        Args:
            model_name: 'mri_cnn', 'ecg_cnn', or 'eeg_cnn'
            num_classes: Number of output classes
            **kwargs: Additional model-specific arguments
            
        Returns:
            PyTorch model
        """
        print(f"Building medical model: {model_name} for {num_classes} classes")
        
        try:
            from models.medical.medical_models import create_medical_model
            
            # Map eeg_cnn to ecg_cnn (same architecture)
            if model_name.lower() == 'eeg_cnn':
                model_name = 'ecg_cnn'
            
            model = create_medical_model(
                model_name, 
                num_classes=num_classes,
                **kwargs
            )
            
            print(f"Medical model created successfully")
            print(f"  Model type: {model_name}")
            print(f"  Total parameters: {sum(p.numel() for p in model.parameters()):,}")
            
            return model
            
        except Exception as e:
            raise ValueError(f"Failed to create medical model {model_name}: {e}")
    
    @staticmethod
    def build_genomic_model(model_name: str, num_classes: int, **kwargs) -> nn.Module:
        """
        Build a genomic data classification model
        بناء مدل دسته‌بندی داده‌های ژنومی
        
        Args:
            model_name: 'dna_cnn' or 'sequence_embedding'
            num_classes: Number of output classes
            **kwargs: Additional model-specific arguments (sequence_length, etc.)
            
        Returns:
            PyTorch model
        """
        print(f"Building genomic model: {model_name} for {num_classes} classes")
        
        try:
            from models.genomic.genomic_models import create_genomic_model
            
            model = create_genomic_model(
                model_name,
                num_classes=num_classes,
                **kwargs
            )
            
            print(f"Genomic model created successfully")
            print(f"  Model type: {model_name}")
            print(f"  Total parameters: {sum(p.numel() for p in model.parameters()):,}")
            
            return model
            
        except Exception as e:
            raise ValueError(f"Failed to create genomic model {model_name}: {e}")
    
    @staticmethod
    def get_model_info(model: nn.Module) -> Dict[str, Any]:
        """
        Get information about a model
        
        Args:
            model: PyTorch model
            
        Returns:
            Dictionary with model info
        """
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        return {
            'total_parameters': total_params,
            'trainable_parameters': trainable_params,
            'model_size_mb': total_params * 4 / (1024 ** 2),  # Assuming float32
        }


class LSTMClassifier(nn.Module):
    """Simple LSTM-based text classifier"""
    
    def __init__(self, vocab_size: int, embed_dim: int, num_classes: int,
                 hidden_dim: int = 256, num_layers: int = 2, 
                 dropout: float = 0.5, bidirectional: bool = True):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embed_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional
        )
        
        lstm_output_dim = hidden_dim * 2 if bidirectional else hidden_dim
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(lstm_output_dim, num_classes)
        
    def forward(self, x):
        # x: (batch_size, seq_len)
        embedded = self.embedding(x)  # (batch_size, seq_len, embed_dim)
        
        # LSTM
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # Use last hidden state
        if self.lstm.bidirectional:
            hidden = torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim=1)
        else:
            hidden = hidden[-1,:,:]
        
        # Classifier
        dropped = self.dropout(hidden)
        output = self.fc(dropped)
        
        return output


class GRUClassifier(nn.Module):
    """Simple GRU-based text classifier"""
    
    def __init__(self, vocab_size: int, embed_dim: int, num_classes: int,
                 hidden_dim: int = 256, num_layers: int = 2, 
                 dropout: float = 0.5, bidirectional: bool = True):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.gru = nn.GRU(
            embed_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional
        )
        
        gru_output_dim = hidden_dim * 2 if bidirectional else hidden_dim
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(gru_output_dim, num_classes)
        
    def forward(self, x):
        embedded = self.embedding(x)
        gru_out, hidden = self.gru(embedded)
        
        if self.gru.bidirectional:
            hidden = torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim=1)
        else:
            hidden = hidden[-1,:,:]
        
        dropped = self.dropout(hidden)
        output = self.fc(dropped)
        
        return output


class TransformerClassifier(nn.Module):
    """Transformer-based text classifier"""
    
    def __init__(self, vocab_size: int, embed_dim: int, num_classes: int,
                 num_heads: int = 8, num_layers: int = 6, 
                 hidden_dim: int = 2048, dropout: float = 0.1,
                 max_seq_len: int = 512):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.pos_encoding = PositionalEncoding(embed_dim, max_seq_len, dropout)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=hidden_dim,
            dropout=dropout,
            batch_first=True
        )
        
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(embed_dim, num_classes)
        
    def forward(self, x):
        embedded = self.embedding(x)
        embedded = self.pos_encoding(embedded)
        
        # Transformer
        transformer_out = self.transformer(embedded)
        
        # Use [CLS] token (first token) or mean pooling
        pooled = transformer_out.mean(dim=1)
        
        dropped = self.dropout(pooled)
        output = self.fc(dropped)
        
        return output


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer"""
    
    def __init__(self, d_model: int, max_len: int = 512, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-torch.log(torch.tensor(10000.0)) / d_model))
        
        pe = torch.zeros(1, max_len, d_model)
        pe[0, :, 0::2] = torch.sin(position * div_term)
        pe[0, :, 1::2] = torch.cos(position * div_term)
        
        self.register_buffer('pe', pe)
        
    def forward(self, x):
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)


# Test code
if __name__ == "__main__":
    print("=" * 60)
    print("Testing ModelBuilder")
    print("=" * 60)
    
    # Test image model
    print("\n1. Testing Image Models:")
    for model_name in ['resnet18', 'efficientnet_b0', 'mobilenetv2_100']:
        try:
            model = ModelBuilder.build_image_model(model_name, num_classes=10, pretrained=False)
            info = ModelBuilder.get_model_info(model)
            print(f"\n{model_name}:")
            print(f"  Parameters: {info['total_parameters']:,}")
            print(f"  Size: {info['model_size_mb']:.2f} MB")
            
            # Test forward pass
            x = torch.randn(2, 3, 224, 224)
            y = model(x)
            print(f"  Output shape: {y.shape}")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    # Test text model
    print("\n2. Testing Text Models:")
    for model_name in ['lstm', 'gru']:
        try:
            model = ModelBuilder.build_text_model(
                model_name,
                vocab_size=10000,
                embed_dim=128,
                num_classes=5,
                hidden_dim=256,
                num_layers=2
            )
            info = ModelBuilder.get_model_info(model)
            print(f"\n{model_name}:")
            print(f"  Parameters: {info['total_parameters']:,}")
            
            # Test forward pass
            x = torch.randint(0, 10000, (2, 50))  # batch_size=2, seq_len=50
            y = model(x)
            print(f"  Output shape: {y.shape}")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n" + "=" * 60)
    print("Testing complete!")

