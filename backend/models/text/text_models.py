"""
Text classification models
Includes BERT-small, LSTM, and TF-IDF based classifiers
"""
import torch
import torch.nn as nn
from transformers import BertModel, BertTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from typing import Optional, Dict, Any
import pickle

class LSTMClassifier(nn.Module):
    """
    LSTM-based text classifier
    Good for sequence modeling and text classification
    """
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 128,
        hidden_dim: int = 256,
        num_classes: int = 2,
        num_layers: int = 2,
        bidirectional: bool = True,
        dropout: float = 0.3
    ):
        super(LSTMClassifier, self).__init__()
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        
        # LSTM layers
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers=num_layers,
            bidirectional=bidirectional,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        # Calculate LSTM output dimension
        lstm_output_dim = hidden_dim * 2 if bidirectional else hidden_dim
        
        # Fully connected layers
        self.fc = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(lstm_output_dim, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x):
        """Forward pass"""
        # x shape: (batch_size, seq_length)
        embedded = self.embedding(x)
        
        # LSTM
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # Use last hidden state
        if self.lstm.bidirectional:
            # Concatenate forward and backward hidden states
            hidden = torch.cat((hidden[-2], hidden[-1]), dim=1)
        else:
            hidden = hidden[-1]
        
        # Classification
        output = self.fc(hidden)
        return output


class BERTClassifier(nn.Module):
    """
    BERT-based text classifier using transfer learning
    State-of-the-art for text classification tasks
    """
    def __init__(
        self,
        num_classes: int = 2,
        model_name: str = 'bert-base-uncased',
        dropout: float = 0.3
    ):
        super(BERTClassifier, self).__init__()
        
        # Load pretrained BERT
        self.bert = BertModel.from_pretrained(model_name)
        
        # Freeze BERT parameters for faster training (optional)
        # Uncomment to freeze:
        # for param in self.bert.parameters():
        #     param.requires_grad = False
        
        # Classification head
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_classes)
    
    def forward(self, input_ids, attention_mask):
        """
        Forward pass
        
        Args:
            input_ids: Token IDs from tokenizer
            attention_mask: Attention mask from tokenizer
        """
        # Get BERT outputs
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        # Use [CLS] token representation
        pooled_output = outputs.pooler_output
        
        # Classification
        output = self.dropout(pooled_output)
        output = self.classifier(output)
        return output


class TFIDFClassifier:
    """
    Traditional TF-IDF + Logistic Regression classifier
    Fast and efficient for simple text classification
    """
    def __init__(
        self,
        max_features: int = 10000,
        ngram_range: tuple = (1, 2)
    ):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            strip_accents='unicode',
            lowercase=True
        )
        self.classifier = LogisticRegression(
            max_iter=1000,
            random_state=42
        )
        self.is_fitted = False
    
    def fit(self, texts, labels):
        """
        Train the classifier
        
        Args:
            texts: List of text strings
            labels: List of labels
        """
        # Transform texts to TF-IDF features
        X = self.vectorizer.fit_transform(texts)
        
        # Train classifier
        self.classifier.fit(X, labels)
        self.is_fitted = True
    
    def predict(self, texts):
        """
        Make predictions
        
        Args:
            texts: List of text strings
            
        Returns:
            Predictions
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X = self.vectorizer.transform(texts)
        return self.classifier.predict(X)
    
    def predict_proba(self, texts):
        """
        Predict class probabilities
        
        Args:
            texts: List of text strings
            
        Returns:
            Probability predictions
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X = self.vectorizer.transform(texts)
        return self.classifier.predict_proba(X)
    
    def save(self, path: str):
        """Save model to disk"""
        with open(path, 'wb') as f:
            pickle.dump({
                'vectorizer': self.vectorizer,
                'classifier': self.classifier
            }, f)
    
    def load(self, path: str):
        """Load model from disk"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.vectorizer = data['vectorizer']
            self.classifier = data['classifier']
            self.is_fitted = True


def create_text_model(
    model_type: str,
    num_classes: int,
    **kwargs
):
    """
    Factory function to create text classification models
    
    Args:
        model_type: Type of model ('lstm', 'bert', 'tfidf')
        num_classes: Number of output classes
        **kwargs: Additional model-specific arguments
        
    Returns:
        Model instance
    """
    if model_type.lower() == 'lstm':
        vocab_size = kwargs.get('vocab_size', 10000)
        return LSTMClassifier(vocab_size=vocab_size, num_classes=num_classes)
    
    elif model_type.lower() == 'bert':
        return BERTClassifier(num_classes=num_classes)
    
    elif model_type.lower() == 'tfidf':
        return TFIDFClassifier()
    
    else:
        raise ValueError(f"Unknown model type: {model_type}")


# Model configurations
MODEL_CONFIGS = {
    'lstm': {
        'name': 'LSTM',
        'description': 'Recurrent neural network for text',
        'params': '~5M',
        'speed': 'Fast',
        'accuracy': 'Medium-High'
    },
    'bert': {
        'name': 'BERT-small',
        'description': 'Pre-trained language model',
        'params': '~110M',
        'speed': 'Medium',
        'accuracy': 'Very High'
    },
    'tfidf': {
        'name': 'TF-IDF + Logistic Regression',
        'description': 'Traditional text classifier',
        'params': '<1M',
        'speed': 'Very Fast',
        'accuracy': 'Medium'
    }
}

