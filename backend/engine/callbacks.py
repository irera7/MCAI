"""
Callbacks Module
Training callbacks for monitoring and control
"""

import torch
import os
from pathlib import Path
from typing import Optional, Dict, Any
import time


class Callback:
    """Base callback class"""
    
    def on_epoch_begin(self, epoch: int):
        pass
    
    def on_epoch_end(self, epoch: int, metrics: Dict[str, float]):
        pass
    
    def on_training_end(self):
        pass


class EarlyStopping(Callback):
    """
    Early stopping callback
    Stops training if validation loss doesn't improve
    """
    
    def __init__(self, patience: int = 10, min_delta: float = 0.0001, 
                 mode: str = 'min', active_trainings: dict = None, project_id: str = None):
        """
        Args:
            patience: Number of epochs to wait before stopping
            min_delta: Minimum change to qualify as improvement
            mode: 'min' for loss, 'max' for accuracy
            active_trainings: Dictionary to update with early stopping messages
            project_id: Project ID for updating status
        """
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.best_score = None
        self.counter = 0
        self.should_stop = False
        self.active_trainings = active_trainings
        self.project_id = project_id
        
    def on_epoch_end(self, epoch: int, metrics: Dict[str, float]):
        score = metrics.get('val_loss', metrics.get('val_acc', None))
        
        if score is None:
            return
        
        if self.mode == 'max':
            score = -score
        
        if self.best_score is None:
            self.best_score = score
        elif score > self.best_score - self.min_delta:
            self.counter += 1
            print(f"EarlyStopping counter: {self.counter}/{self.patience}")
            
            # Update active_trainings with warning
            if self.active_trainings and self.project_id and self.project_id in self.active_trainings:
                self.active_trainings[self.project_id]['early_stopping_counter'] = self.counter
                
            if self.counter >= self.patience:
                print(f"Early stopping triggered! Best score: {-self.best_score if self.mode == 'max' else self.best_score:.4f}")
                self.should_stop = True
                
                # Update active_trainings
                if self.active_trainings and self.project_id and self.project_id in self.active_trainings:
                    best_val = -self.best_score if self.mode == 'max' else self.best_score
                    self.active_trainings[self.project_id]['message'] = f"🛑 Early stopping triggered! Best val_loss: {best_val:.4f}"
        else:
            self.best_score = score
            self.counter = 0
            
            # Reset counter in active_trainings
            if self.active_trainings and self.project_id and self.project_id in self.active_trainings:
                self.active_trainings[self.project_id]['early_stopping_counter'] = 0


class ModelCheckpoint(Callback):
    """
    Model checkpoint callback
    Saves model checkpoints based on validation performance
    """
    
    def __init__(self, save_dir: str, monitor: str = 'val_loss',
                 mode: str = 'min', save_best_only: bool = True,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Args:
            save_dir: Directory to save checkpoints
            monitor: Metric to monitor ('val_loss', 'val_acc', etc.)
            mode: 'min' for loss, 'max' for accuracy
            save_best_only: Only save when metric improves
            metadata: Model metadata to save with checkpoint
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.monitor = monitor
        self.mode = mode
        self.save_best_only = save_best_only
        self.best_score = None
        self.metadata = metadata or {}
        
    def on_epoch_end(self, epoch: int, metrics: Dict[str, float]):
        score = metrics.get(self.monitor, None)
        
        if score is None:
            print(f"Warning: Metric '{self.monitor}' not found in metrics")
            return
        
        save = False
        
        if not self.save_best_only:
            save = True
        else:
            if self.best_score is None:
                save = True
                self.best_score = score
            elif (self.mode == 'min' and score < self.best_score) or \
                 (self.mode == 'max' and score > self.best_score):
                save = True
                self.best_score = score
        
        if save and hasattr(self, 'model'):
            checkpoint_path = self.save_dir / f"checkpoint_epoch_{epoch}.pt"
            best_path = self.save_dir / "best_model.pt"
            
            checkpoint_data = {
                'epoch': epoch,
                'model_state_dict': self.model.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict() if hasattr(self, 'optimizer') else None,
                'metrics': metrics,
            }
            
            # Add metadata if available
            if self.metadata:
                checkpoint_data['metadata'] = self.metadata
            
            torch.save(checkpoint_data, checkpoint_path)
            
            # Also save as best model
            if self.save_best_only or (self.best_score == score):
                best_data = {
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'metrics': metrics,
                }
                if self.metadata:
                    best_data['metadata'] = self.metadata
                torch.save(best_data, best_path)
                print(f"Saved best model to {best_path} ({self.monitor}={score:.4f})")


class ProgressCallback(Callback):
    """
    Progress callback for updating frontend
    Updates active_trainings dict with current metrics
    """
    
    def __init__(self, project_id: str, active_trainings: Dict):
        self.project_id = project_id
        self.active_trainings = active_trainings
        self.start_time = None
        self.epoch_start_time = None
        self.best_train_loss = float('inf')
        self.best_val_loss = float('inf')
        self.best_val_acc = 0.0
        
    def on_epoch_begin(self, epoch: int):
        if self.start_time is None:
            self.start_time = time.time()
        self.epoch_start_time = time.time()
    
    def on_epoch_end(self, epoch: int, metrics: Dict[str, float]):
        try:
            if self.project_id not in self.active_trainings:
                print(f"[ProgressCallback] Project {self.project_id} not in active_trainings")
                return
                
            print(f"[ProgressCallback] Updating epoch {epoch} metrics...")
            
            current_time = time.time()
            elapsed = current_time - self.start_time if self.start_time else 0
            epoch_time = current_time - self.epoch_start_time if self.epoch_start_time else 0
            
            # Update best metrics
            train_loss = metrics.get('train_loss', 0.0)
            val_loss = metrics.get('val_loss', 0.0)
            val_acc = metrics.get('val_acc', 0.0)
            
            if train_loss < self.best_train_loss:
                self.best_train_loss = train_loss
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
            if val_acc > self.best_val_acc:
                self.best_val_acc = val_acc
            
            # Calculate ETA (Estimated Time Remaining)
            total_epochs = self.active_trainings[self.project_id].get('total_epochs', epoch)
            if epoch > 0:
                avg_epoch_time = elapsed / epoch
                remaining_epochs = total_epochs - epoch
                eta = int(avg_epoch_time * remaining_epochs)
            else:
                eta = 0
            
            # Format times
            elapsed_str = self._format_time(int(elapsed))
            eta_str = self._format_time(eta)
            epoch_time_str = f"{epoch_time:.2f}s"
            
            # Update active_trainings
            self.active_trainings[self.project_id].update({
                'current_epoch': epoch,
                'train_loss': round(train_loss, 4),
                'train_acc': round(metrics.get('train_acc', 0.0), 4),
                'val_loss': round(val_loss, 4),
                'val_acc': round(val_acc, 4),
                'best_train_loss': round(self.best_train_loss, 4),
                'best_val_loss': round(self.best_val_loss, 4),
                'best_val_acc': round(self.best_val_acc, 4),
                'elapsed_time': int(elapsed),
                'elapsed_time_str': elapsed_str,
                'eta': eta,
                'eta_str': eta_str,
                'epoch_time': epoch_time_str,
                'progress_percent': int((epoch / total_epochs) * 100),
                'message': f"Epoch {epoch}/{total_epochs} - Loss: {val_loss:.4f}, Acc: {val_acc:.4f} - {epoch_time_str}/epoch",
                'status': 'training'
            })
            
            print(f"[ProgressCallback] Updated: Epoch {epoch}/{total_epochs}, Loss: {val_loss:.4f}, Acc: {val_acc:.4f}")
            
        except Exception as e:
            print(f"[ProgressCallback] Error updating metrics: {e}")
            import traceback
            traceback.print_exc()
    
    def on_training_end(self):
        if self.project_id in self.active_trainings:
            elapsed = time.time() - self.start_time if self.start_time else 0
            self.active_trainings[self.project_id].update({
                'status': 'completed',
                'message': f'Training completed successfully in {self._format_time(int(elapsed))}',
                'elapsed_time': int(elapsed),
                'elapsed_time_str': self._format_time(int(elapsed))
            })
    
    def _format_time(self, seconds: int) -> str:
        """Format seconds to human readable time"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            mins = seconds // 60
            secs = seconds % 60
            return f"{mins}m {secs}s"
        else:
            hours = seconds // 3600
            mins = (seconds % 3600) // 60
            return f"{hours}h {mins}m"


class LearningRateScheduler(Callback):
    """Learning rate scheduling callback"""
    
    def __init__(self, scheduler):
        self.scheduler = scheduler
    
    def on_epoch_end(self, epoch: int, metrics: Dict[str, float]):
        if hasattr(self.scheduler, 'step'):
            # ReduceLROnPlateau needs a metric
            if 'ReduceLROnPlateau' in str(type(self.scheduler)):
                val_loss = metrics.get('val_loss', None)
                if val_loss is not None:
                    self.scheduler.step(val_loss)
            else:
                self.scheduler.step()


class TensorBoardCallback(Callback):
    """
    TensorBoard logging callback
    Logs training metrics and model graph to TensorBoard
    """
    
    def __init__(self, log_dir: str, project_id: str):
        """
        Args:
            log_dir: Directory to save TensorBoard logs
            project_id: Project identifier
        """
        try:
            from torch.utils.tensorboard import SummaryWriter
            self.writer = SummaryWriter(log_dir=log_dir)
            self.project_id = project_id
            self.enabled = True
            print(f"TensorBoard logging enabled: {log_dir}")
            print(f"  View with: tensorboard --logdir {log_dir}")
        except ImportError:
            print("Warning: TensorBoard not available. Install with: pip install tensorboard")
            self.enabled = False
    
    def on_epoch_end(self, epoch: int, metrics: Dict[str, float]):
        if not self.enabled:
            return
        
        # Log scalar metrics
        if 'train_loss' in metrics:
            self.writer.add_scalar('Loss/train', metrics['train_loss'], epoch)
        if 'val_loss' in metrics:
            self.writer.add_scalar('Loss/val', metrics['val_loss'], epoch)
        if 'train_acc' in metrics:
            self.writer.add_scalar('Accuracy/train', metrics['train_acc'], epoch)
        if 'val_acc' in metrics:
            self.writer.add_scalar('Accuracy/val', metrics['val_acc'], epoch)
        
        # Log learning rate if available
        if hasattr(self, 'optimizer') and self.optimizer:
            lr = self.optimizer.param_groups[0]['lr']
            self.writer.add_scalar('LearningRate', lr, epoch)
    
    def on_training_end(self):
        if self.enabled:
            self.writer.close()
            print(f"TensorBoard logs saved for project: {self.project_id}")
