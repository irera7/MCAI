"""
Metrics Module
Training and evaluation metrics
"""

import torch
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from typing import Tuple, Dict


def calculate_accuracy(predictions: torch.Tensor, targets: torch.Tensor) -> float:
    """
    Calculate classification accuracy
    
    Args:
        predictions: Model predictions (logits or probabilities)
        targets: Ground truth labels
        
    Returns:
        Accuracy as float
    """
    pred_labels = predictions.argmax(dim=1)
    correct = (pred_labels == targets).sum().item()
    total = targets.size(0)
    return correct / total if total > 0 else 0.0


def calculate_metrics(predictions: torch.Tensor, targets: torch.Tensor,
                     num_classes: int) -> Dict[str, float]:
    """
    Calculate comprehensive classification metrics
    
    Args:
        predictions: Model predictions
        targets: Ground truth labels
        num_classes: Number of classes
        
    Returns:
        Dictionary of metrics
    """
    pred_labels = predictions.argmax(dim=1).cpu().numpy()
    targets_np = targets.cpu().numpy()
    
    accuracy = accuracy_score(targets_np, pred_labels)
    
    # Precision, recall, F1
    precision, recall, f1, support = precision_recall_fscore_support(
        targets_np, pred_labels, average='weighted', zero_division=0
    )
    
    return {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1)
    }


def calculate_confusion_matrix(predictions: torch.Tensor, targets: torch.Tensor,
                               num_classes: int) -> np.ndarray:
    """
    Calculate confusion matrix
    
    Args:
        predictions: Model predictions
        targets: Ground truth labels
        num_classes: Number of classes
        
    Returns:
        Confusion matrix as numpy array
    """
    pred_labels = predictions.argmax(dim=1).cpu().numpy()
    targets_np = targets.cpu().numpy()
    
    return confusion_matrix(targets_np, pred_labels, labels=range(num_classes))


class AverageMeter:
    """Computes and stores the average and current value"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0
    
    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count if self.count > 0 else 0

