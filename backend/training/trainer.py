"""
Base trainer class for all model training
"""
import torch
from torch.utils.data import DataLoader
from typing import Dict, Any, Optional, Callable
from pathlib import Path
import json
from tqdm import tqdm

from utils.logger import setup_logger

logger = setup_logger(__name__)

class BaseTrainer:
    """Base trainer class for all models"""
    
    def __init__(
        self,
        model: torch.nn.Module,
        train_loader: DataLoader,
        val_loader: Optional[DataLoader] = None,
        config: Optional[Dict[str, Any]] = None,
        device: str = "cuda"
    ):
        """
        Initialize trainer
        
        Args:
            model: PyTorch model to train
            train_loader: Training data loader
            val_loader: Validation data loader
            config: Training configuration
            device: Device to train on
        """
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.config = config or {}
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        
        # Move model to device
        self.model.to(self.device)
        
        # Training state
        self.current_epoch = 0
        self.current_batch = 0
        self.best_metric = 0.0
        self.training_history = {
            "train_loss": [],
            "train_acc": [],
            "val_loss": [],
            "val_acc": []
        }
        
        # Callbacks
        self.callbacks = []
        
        logger.info(f"Trainer initialized on device: {self.device}")
    
    def train(self, epochs: int, callbacks: Optional[list] = None):
        """
        Train the model
        
        Args:
            epochs: Number of epochs to train
            callbacks: Optional list of callback functions
        """
        self.callbacks = callbacks or []
        
        for epoch in range(epochs):
            self.current_epoch = epoch
            
            # Training phase
            train_metrics = self._train_epoch()
            
            # Validation phase
            if self.val_loader:
                val_metrics = self._validate_epoch()
            else:
                val_metrics = {}
            
            # Update history
            self.training_history["train_loss"].append(train_metrics.get("loss", 0))
            self.training_history["train_acc"].append(train_metrics.get("accuracy", 0))
            if val_metrics:
                self.training_history["val_loss"].append(val_metrics.get("loss", 0))
                self.training_history["val_acc"].append(val_metrics.get("accuracy", 0))
            
            # Execute callbacks
            for callback in self.callbacks:
                callback(epoch, train_metrics, val_metrics)
            
            logger.info(
                f"Epoch {epoch+1}/{epochs} - "
                f"Train Loss: {train_metrics['loss']:.4f}, "
                f"Train Acc: {train_metrics['accuracy']:.4f}"
            )
    
    def _train_epoch(self) -> Dict[str, float]:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        # This is a placeholder - will be overridden by specific trainers
        return {"loss": 0.0, "accuracy": 0.0}
    
    def _validate_epoch(self) -> Dict[str, float]:
        """Validate for one epoch"""
        self.model.eval()
        
        # This is a placeholder - will be overridden by specific trainers
        return {"loss": 0.0, "accuracy": 0.0}
    
    def save_checkpoint(self, path: Path):
        """Save training checkpoint"""
        checkpoint = {
            "epoch": self.current_epoch,
            "model_state_dict": self.model.state_dict(),
            "config": self.config,
            "history": self.training_history
        }
        torch.save(checkpoint, path)
        logger.info(f"Checkpoint saved to {path}")
    
    def load_checkpoint(self, path: Path):
        """Load training checkpoint"""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.current_epoch = checkpoint.get("epoch", 0)
        self.training_history = checkpoint.get("history", {})
        logger.info(f"Checkpoint loaded from {path}")

