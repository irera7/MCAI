"""
Training callbacks
"""
from typing import Dict, Any
import json

class TrainingCallback:
    """Base callback class"""
    
    def __call__(self, epoch: int, train_metrics: Dict[str, float], val_metrics: Dict[str, float]):
        """Execute callback"""
        pass

class EarlyStoppingCallback(TrainingCallback):
    """Early stopping callback"""
    
    def __init__(self, patience: int = 10, min_delta: float = 0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.best_loss = float('inf')
        self.counter = 0
        self.should_stop = False
    
    def __call__(self, epoch: int, train_metrics: Dict[str, float], val_metrics: Dict[str, float]):
        current_loss = val_metrics.get('loss', train_metrics.get('loss', float('inf')))
        
        if current_loss < self.best_loss - self.min_delta:
            self.best_loss = current_loss
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.should_stop = True

class MetricsLoggerCallback(TrainingCallback):
    """Log metrics to file"""
    
    def __init__(self, log_file: str):
        self.log_file = log_file
        self.metrics = []
    
    def __call__(self, epoch: int, train_metrics: Dict[str, float], val_metrics: Dict[str, float]):
        self.metrics.append({
            "epoch": epoch,
            "train": train_metrics,
            "val": val_metrics
        })
        
        # Save to file
        with open(self.log_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)

