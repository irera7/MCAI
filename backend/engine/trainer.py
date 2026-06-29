"""
Trainer Module
Main training engine for model training
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import Optimizer
from torch.optim.lr_scheduler import _LRScheduler
from typing import List, Optional, Dict, Any
from tqdm import tqdm
import time

from .metrics import calculate_accuracy, AverageMeter
from .callbacks import Callback


class Trainer:
    """
    Main trainer class for model training
    Handles training loop, validation, and callbacks
    """
    
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        criterion: nn.Module,
        optimizer: Optimizer,
        device: torch.device,
        scheduler: Optional[_LRScheduler] = None,
        callbacks: Optional[List[Callback]] = None,
        mixed_precision: bool = False
    ):
        """
        Args:
            model: Neural network model
            train_loader: Training data loader
            val_loader: Validation data loader
            criterion: Loss function
            optimizer: Optimizer
            device: Device to train on (cuda/cpu)
            scheduler: Learning rate scheduler
            callbacks: List of callbacks
            mixed_precision: Use mixed precision training
        """
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device
        self.scheduler = scheduler
        self.callbacks = callbacks or []
        self.mixed_precision = mixed_precision
        
        # Setup mixed precision
        self.scaler = torch.cuda.amp.GradScaler() if mixed_precision else None
        
        # Pass model and optimizer to callbacks that need them
        for callback in self.callbacks:
            if hasattr(callback, 'model'):
                callback.model = self.model
            if hasattr(callback, 'optimizer'):
                callback.optimizer = self.optimizer
        
        self.history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': []
        }
    
    def train_epoch(self, epoch: int) -> Dict[str, float]:
        """
        Train for one epoch
        
        Args:
            epoch: Current epoch number
            
        Returns:
            Dictionary with training metrics
        """
        self.model.train()
        
        loss_meter = AverageMeter()
        acc_meter = AverageMeter()
        
        pbar = tqdm(self.train_loader, desc=f'Epoch {epoch} [Train]')
        
        for batch_idx, (data, target) in enumerate(pbar):
            data, target = data.to(self.device), target.to(self.device)
            
            self.optimizer.zero_grad()
            
            # Mixed precision training
            if self.mixed_precision and self.scaler:
                with torch.cuda.amp.autocast():
                    output = self.model(data)
                    loss = self.criterion(output, target)
                
                self.scaler.scale(loss).backward()
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                output = self.model(data)
                loss = self.criterion(output, target)
                loss.backward()
                self.optimizer.step()
            
            # Calculate accuracy
            acc = calculate_accuracy(output, target)
            
            # Update meters
            batch_size = data.size(0)
            loss_meter.update(loss.item(), batch_size)
            acc_meter.update(acc, batch_size)
            
            # Update progress bar
            pbar.set_postfix({
                'loss': f'{loss_meter.avg:.4f}',
                'acc': f'{acc_meter.avg:.4f}'
            })
        
        return {
            'train_loss': loss_meter.avg,
            'train_acc': acc_meter.avg
        }
    
    @torch.no_grad()
    def validate(self, epoch: int) -> Dict[str, float]:
        """
        Validate the model
        
        Args:
            epoch: Current epoch number
            
        Returns:
            Dictionary with validation metrics
        """
        self.model.eval()
        
        loss_meter = AverageMeter()
        acc_meter = AverageMeter()
        
        pbar = tqdm(self.val_loader, desc=f'Epoch {epoch} [Val]')
        
        for data, target in pbar:
            data, target = data.to(self.device), target.to(self.device)
            
            output = self.model(data)
            loss = self.criterion(output, target)
            
            acc = calculate_accuracy(output, target)
            
            batch_size = data.size(0)
            loss_meter.update(loss.item(), batch_size)
            acc_meter.update(acc, batch_size)
            
            pbar.set_postfix({
                'loss': f'{loss_meter.avg:.4f}',
                'acc': f'{acc_meter.avg:.4f}'
            })
        
        return {
            'val_loss': loss_meter.avg,
            'val_acc': acc_meter.avg
        }
    
    def fit(self, epochs: int) -> Dict[str, List[float]]:
        """
        Train the model for specified number of epochs
        
        Args:
            epochs: Number of epochs to train
            
        Returns:
            Training history
        """
        print(f"Starting training for {epochs} epochs")
        print(f"Device: {self.device}")
        print(f"Model: {self.model.__class__.__name__}")
        print(f"Optimizer: {self.optimizer.__class__.__name__}")
        print(f"Mixed Precision: {self.mixed_precision}")
        print("=" * 70)
        
        start_time = time.time()
        
        for epoch in range(1, epochs + 1):
            # Epoch begin callbacks
            for callback in self.callbacks:
                callback.on_epoch_begin(epoch)
            
            # Training
            train_metrics = self.train_epoch(epoch)
            
            # Validation
            val_metrics = self.validate(epoch)
            
            # Combine metrics
            epoch_metrics = {**train_metrics, **val_metrics}
            
            # Update history
            self.history['train_loss'].append(train_metrics['train_loss'])
            self.history['train_acc'].append(train_metrics['train_acc'])
            self.history['val_loss'].append(val_metrics['val_loss'])
            self.history['val_acc'].append(val_metrics['val_acc'])
            
            # Learning rate scheduling
            if self.scheduler:
                if isinstance(self.scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                    self.scheduler.step(val_metrics['val_loss'])
                else:
                    self.scheduler.step()
            
            # Print epoch summary
            current_lr = self.optimizer.param_groups[0]['lr']
            print(f"\nEpoch {epoch}/{epochs} Summary:")
            print(f"  Train Loss: {train_metrics['train_loss']:.4f} | Train Acc: {train_metrics['train_acc']:.4f}")
            print(f"  Val Loss:   {val_metrics['val_loss']:.4f} | Val Acc:   {val_metrics['val_acc']:.4f}")
            print(f"  Learning Rate: {current_lr:.6f}")
            
            # Epoch end callbacks
            for callback in self.callbacks:
                callback.on_epoch_end(epoch, epoch_metrics)
            
            # Check early stopping
            for callback in self.callbacks:
                if hasattr(callback, 'should_stop') and callback.should_stop:
                    print(f"\nEarly stopping triggered at epoch {epoch}")
                    break
            else:
                continue
            break
        
        # Training end callbacks
        for callback in self.callbacks:
            callback.on_training_end()
        
        total_time = time.time() - start_time
        print("=" * 70)
        print(f"Training completed in {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        print(f"Best Val Accuracy: {max(self.history['val_acc']):.4f}")
        print(f"Best Val Loss: {min(self.history['val_loss']):.4f}")
        
        return self.history
    
    def save_model(self, path: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Save model checkpoint with metadata
        
        Args:
            path: Path to save checkpoint
            metadata: Optional metadata (model architecture, num_classes, etc.)
        """
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'history': self.history
        }
        
        # Add metadata if provided
        if metadata:
            checkpoint['metadata'] = metadata
        
        torch.save(checkpoint, path)
        print(f"Model saved to {path}")
    
    
    def load_model(self, path: str):
        """Load model checkpoint"""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        if 'history' in checkpoint:
            self.history = checkpoint['history']
        print(f"Model loaded from {path}")

