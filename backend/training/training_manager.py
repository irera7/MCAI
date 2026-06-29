"""
Enhanced training infrastructure with local and cloud support
"""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
import json
import time
from datetime import datetime
from tqdm import tqdm

from training.callbacks import EarlyStoppingCallback, MetricsLoggerCallback
from utils.logger import get_project_logger

class TrainingManager:
    """
    Enhanced training manager with local and cloud support
    Manages training lifecycle, monitoring, and checkpointing
    """
    
    def __init__(
        self,
        project_id: str,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: Optional[DataLoader] = None,
        config: Optional[Dict[str, Any]] = None,
        device: str = "cuda"
    ):
        """
        Initialize training manager
        
        Args:
            project_id: Project identifier
            model: PyTorch model
            train_loader: Training data loader
            val_loader: Validation data loader
            config: Training configuration
            device: Device to train on
        """
        self.project_id = project_id
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
        self.best_val_loss = float('inf')
        self.best_val_acc = 0.0
        self.training_history = {
            "train_loss": [],
            "train_acc": [],
            "val_loss": [],
            "val_acc": [],
            "learning_rates": []
        }
        
        # Setup optimizer and criterion
        self._setup_optimizer()
        self._setup_criterion()
        self._setup_scheduler()
        
        # Setup logger
        self.logger = get_project_logger(project_id)
        
        # Callbacks
        self.callbacks = []
        
        # Training control
        self.should_stop = False
        self.is_paused = False
        
        self.logger.info(f"TrainingManager initialized on device: {self.device}")
    
    def _setup_optimizer(self):
        """Setup optimizer"""
        optimizer_name = self.config.get('optimizer', 'adam').lower()
        lr = self.config.get('learning_rate', 0.001)
        weight_decay = self.config.get('weight_decay', 0.0001)
        
        if optimizer_name == 'adam':
            self.optimizer = torch.optim.Adam(
                self.model.parameters(),
                lr=lr,
                weight_decay=weight_decay
            )
        elif optimizer_name == 'sgd':
            momentum = self.config.get('momentum', 0.9)
            self.optimizer = torch.optim.SGD(
                self.model.parameters(),
                lr=lr,
                momentum=momentum,
                weight_decay=weight_decay
            )
        elif optimizer_name == 'rmsprop':
            self.optimizer = torch.optim.RMSprop(
                self.model.parameters(),
                lr=lr,
                weight_decay=weight_decay
            )
        elif optimizer_name == 'adamw':
            self.optimizer = torch.optim.AdamW(
                self.model.parameters(),
                lr=lr,
                weight_decay=weight_decay
            )
        else:
            raise ValueError(f"Unknown optimizer: {optimizer_name}")
    
    def _setup_criterion(self):
        """Setup loss criterion"""
        self.criterion = nn.CrossEntropyLoss()
    
    def _setup_scheduler(self):
        """Setup learning rate scheduler"""
        if self.config.get('use_scheduler', False):
            self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer,
                mode='min',
                factor=0.5,
                patience=5,
                verbose=True
            )
        else:
            self.scheduler = None
    
    def train(
        self,
        epochs: int,
        callbacks: Optional[List[Callable]] = None,
        status_callback: Optional[Callable] = None
    ):
        """
        Train the model
        
        Args:
            epochs: Number of epochs to train
            callbacks: List of callback functions
            status_callback: Callback for real-time status updates
        """
        self.callbacks = callbacks or []
        start_time = time.time()
        
        self.logger.info(f"Starting training for {epochs} epochs")
        
        for epoch in range(epochs):
            if self.should_stop:
                self.logger.info("Training stopped by user")
                break
            
            self.current_epoch = epoch
            epoch_start_time = time.time()
            
            # Training phase
            train_metrics = self._train_epoch(status_callback)
            
            # Validation phase
            if self.val_loader:
                val_metrics = self._validate_epoch(status_callback)
            else:
                val_metrics = {}
            
            # Update history
            self.training_history["train_loss"].append(train_metrics['loss'])
            self.training_history["train_acc"].append(train_metrics['accuracy'])
            if val_metrics:
                self.training_history["val_loss"].append(val_metrics['loss'])
                self.training_history["val_acc"].append(val_metrics['accuracy'])
            
            # Learning rate scheduling
            if self.scheduler and val_metrics:
                self.scheduler.step(val_metrics['loss'])
            
            current_lr = self.optimizer.param_groups[0]['lr']
            self.training_history["learning_rates"].append(current_lr)
            
            # Save best model
            if val_metrics:
                if val_metrics['accuracy'] > self.best_val_acc:
                    self.best_val_acc = val_metrics['accuracy']
                    self.save_checkpoint('best_model.pt')
            
            # Execute callbacks
            for callback in self.callbacks:
                callback(epoch, train_metrics, val_metrics)
            
            # Status update
            if status_callback:
                status_callback({
                    'epoch': epoch + 1,
                    'total_epochs': epochs,
                    'train_loss': train_metrics['loss'],
                    'train_acc': train_metrics['accuracy'],
                    'val_loss': val_metrics.get('loss', 0),
                    'val_acc': val_metrics.get('accuracy', 0),
                    'learning_rate': current_lr,
                    'epoch_time': time.time() - epoch_start_time
                })
            
            # Log epoch summary
            epoch_time = time.time() - epoch_start_time
            self.logger.info(
                f"Epoch {epoch+1}/{epochs} - "
                f"Train Loss: {train_metrics['loss']:.4f}, "
                f"Train Acc: {train_metrics['accuracy']:.4f}, "
                f"Val Loss: {val_metrics.get('loss', 0):.4f}, "
                f"Val Acc: {val_metrics.get('accuracy', 0):.4f}, "
                f"Time: {epoch_time:.2f}s"
            )
        
        total_time = time.time() - start_time
        self.logger.info(f"Training completed in {total_time:.2f}s")
        
        return self.training_history
    
    def _train_epoch(self, status_callback: Optional[Callable] = None) -> Dict[str, float]:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(self.train_loader, desc=f"Epoch {self.current_epoch+1}")
        
        for batch_idx, (inputs, targets) in enumerate(pbar):
            if self.should_stop:
                break
            
            while self.is_paused:
                time.sleep(0.1)
            
            self.current_batch = batch_idx
            
            # Move to device
            inputs = inputs.to(self.device)
            targets = targets.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(inputs)
            loss = self.criterion(outputs, targets)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Statistics
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
            
            # Update progress bar
            pbar.set_postfix({
                'loss': total_loss / (batch_idx + 1),
                'acc': 100. * correct / total
            })
        
        return {
            'loss': total_loss / len(self.train_loader),
            'accuracy': correct / total
        }
    
    def _validate_epoch(self, status_callback: Optional[Callable] = None) -> Dict[str, float]:
        """Validate for one epoch"""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, targets in self.val_loader:
                inputs = inputs.to(self.device)
                targets = targets.to(self.device)
                
                outputs = self.model(inputs)
                loss = self.criterion(outputs, targets)
                
                total_loss += loss.item()
                _, predicted = outputs.max(1)
                total += targets.size(0)
                correct += predicted.eq(targets).sum().item()
        
        return {
            'loss': total_loss / len(self.val_loader),
            'accuracy': correct / total
        }
    
    def stop_training(self):
        """Stop training"""
        self.should_stop = True
        self.logger.info("Training stop requested")
    
    def pause_training(self):
        """Pause training"""
        self.is_paused = True
        self.logger.info("Training paused")
    
    def resume_training(self):
        """Resume training"""
        self.is_paused = False
        self.logger.info("Training resumed")
    
    def save_checkpoint(self, filename: str):
        """Save training checkpoint"""
        checkpoint_path = Path(f"../projects/{self.project_id}/models/{filename}")
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        
        checkpoint = {
            'epoch': self.current_epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'best_val_acc': self.best_val_acc,
            'history': self.training_history,
            'config': self.config
        }
        
        torch.save(checkpoint, checkpoint_path)
        self.logger.info(f"Checkpoint saved: {checkpoint_path}")
    
    def load_checkpoint(self, filename: str):
        """Load training checkpoint"""
        checkpoint_path = Path(f"../projects/{self.project_id}/models/{filename}")
        
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
        
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.current_epoch = checkpoint['epoch']
        self.best_val_acc = checkpoint['best_val_acc']
        self.training_history = checkpoint['history']
        
        self.logger.info(f"Checkpoint loaded: {checkpoint_path}")


class CloudTrainingManager:
    """
    Cloud training manager (placeholder for future implementation)
    Manages training on cloud platforms (AWS, Azure, GCP)
    """
    
    def __init__(self, provider: str = "aws"):
        """
        Initialize cloud training manager
        
        Args:
            provider: Cloud provider ('aws', 'azure', 'gcp')
        """
        self.provider = provider
        self.logger = get_project_logger("cloud")
    
    def submit_training_job(self, config: Dict[str, Any]) -> str:
        """
        Submit training job to cloud
        
        Args:
            config: Training configuration
            
        Returns:
            Job ID
        """
        # Placeholder for cloud training submission
        self.logger.info(f"Cloud training job submitted to {self.provider}")
        return "job_placeholder_id"
    
    def check_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check cloud training job status
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status information
        """
        # Placeholder
        return {
            "status": "running",
            "progress": 0.5,
            "metrics": {}
        }
    
    def download_trained_model(self, job_id: str, save_path: str):
        """
        Download trained model from cloud
        
        Args:
            job_id: Job identifier
            save_path: Local path to save model
        """
        # Placeholder
        self.logger.info(f"Downloading model from cloud job {job_id}")

