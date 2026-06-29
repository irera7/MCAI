"""
Training API endpoints
"""
from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import json

from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

# Store active training sessions
active_trainings: Dict[str, Any] = {}

class TrainingConfig(BaseModel):
    """Training configuration"""
    epochs: int = 50
    batch_size: int = 32
    learning_rate: float = 0.001
    optimizer: str = "adam"
    device: str = "cuda"
    train_split: float = 0.8
    val_split: float = 0.1
    test_split: float = 0.1
    use_augmentation: bool = True
    dropout: float = 0.2
    weight_decay: float = 0.0001
    early_stopping: bool = True
    early_stopping_patience: int = 10
    mixed_precision: bool = False
    training_mode: str = "local"  # local or cloud
    model_id: Optional[str] = None  # Selected model architecture

@router.post("/start/{project_id}")
async def start_training(project_id: str, config: TrainingConfig):
    """
    Start model training for a project
    
    Args:
        project_id: Project identifier
        config: Training configuration
        
    Returns:
        Training start status
    """
    try:
        project_dir = settings.PROJECTS_DIR / project_id
        if not project_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}"
            )
        
        # Check if data directory exists and has data
        data_dir = project_dir / "data"
        if not data_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data directory not found. Please upload data before training."
            )
        
        # Check if data directory has any files or subdirectories
        has_data = False
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
        
        # Check for class subdirectories
        class_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
        if class_dirs:
            for class_dir in class_dirs:
                images = [f for f in class_dir.iterdir() if f.suffix.lower() in valid_extensions]
                if images:
                    has_data = True
                    break
        else:
            # Check for images in root data directory
            images = [f for f in data_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_extensions]
            if images:
                has_data = True
        
        if not has_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No images found in data directory. Please upload images before training."
            )
        
        # Check if already training
        if project_id in active_trainings and active_trainings[project_id].get('status') == 'training':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Training already in progress for this project"
            )
        
        # ✅ VALIDATE: Check if model_id is provided
        if not config.model_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Model architecture not selected. Please select a model before training."
            )
        
        # ✅ Clear any old training data before starting new one
        if project_id in active_trainings:
            logger.info(f"Clearing old training data for project {project_id}")
            del active_trainings[project_id]
        
        # ✅ UPDATE: Save training config to project.json
        project_file = project_dir / "project.json"
        if project_file.exists():
            with open(project_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # Update training configuration
            project_data['training'] = {
                'epochs': config.epochs,
                'batch_size': config.batch_size,
                'learning_rate': config.learning_rate,
                'optimizer': config.optimizer,
                'device': config.device,
                'train_split': config.train_split,
                'val_split': config.val_split,
                'test_split': config.test_split,
                'use_augmentation': config.use_augmentation,
                'dropout': config.dropout,
                'weight_decay': config.weight_decay,
                'early_stopping': config.early_stopping,
                'early_stopping_patience': config.early_stopping_patience,
                'mixed_precision': config.mixed_precision,
                'training_mode': config.training_mode,
            }
            
            # Update model info if provided
            if config.model_id:
                project_data['model_name'] = config.model_id
                project_data['model_type'] = config.model_id
            
            # Update timestamps
            from datetime import datetime
            project_data['updated_at'] = datetime.now().isoformat()
            project_data['status'] = 'training'
            
            # Save updated project.json
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2)
            
            logger.info(f"✅ Updated project.json with training config for {project_id}")
        
        # Initialize training session
        active_trainings[project_id] = {
            "status": "starting",
            "config": config.model_dump(),
            "current_epoch": 0,
            "total_epochs": config.epochs,
            "current_batch": 0,
            "train_loss": 0.0,
            "train_acc": 0.0,
            "metrics": {},
            "message": "Initializing training..."
        }
        
        logger.info(f"Started training for project {project_id}")
        
        # Start real training in background using ThreadPoolExecutor
        # This prevents blocking the main event loop during training
        import concurrent.futures
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        
        def run_training_sync():
            """Synchronous wrapper for training"""
            try:
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Run the training
                result = loop.run_until_complete(run_real_training(project_id, config))
                return result
            except Exception as e:
                logger.error(f"Error in training thread: {e}")
                # Update active_trainings with error
                if project_id in active_trainings:
                    active_trainings[project_id]["status"] = "failed"
                    active_trainings[project_id]["error"] = str(e)
                raise
            finally:
                loop.close()
        
        # Submit training task
        executor.submit(run_training_sync)
        
        return {
            "message": "Training started",
            "project_id": project_id,
            "status": "running"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting training: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start training: {str(e)}"
        )


async def run_real_training(project_id: str, config: TrainingConfig):
    """
    Real training loop using the training engine
    """
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from pathlib import Path
    
    # Import engine components
    from engine import create_data_loaders, create_text_loaders, create_audio_loaders, ModelBuilder, Trainer
    from engine.callbacks import EarlyStopping, ModelCheckpoint, ProgressCallback, TensorBoardCallback
    
    try:
        # Update status
        if project_id in active_trainings:
            active_trainings[project_id]["status"] = "starting"
            active_trainings[project_id]["message"] = "📁 Loading dataset..."
        
        project_dir = settings.PROJECTS_DIR / project_id
        
        # Detect project modality
        project_file = project_dir / "project.json"
        modality = "image"  # default
        if project_file.exists():
            with open(project_file, 'r', encoding='utf-8') as f:
                project_info = json.load(f)
                modality = project_info.get('modality', 'image')
        
        logger.info(f"Project modality: {modality}")
        
        # Create data loaders based on modality
        logger.info(f"Loading data for project {project_id}")
        config_dict = {
            'batch_size': config.batch_size,
            'num_workers': 2 if modality == 'image' else 0,  # Text/Audio better with 0
            'train_split': config.train_split,
            'val_split': config.val_split,
            'model_id': config.model_id,  # Add selected model
        }
        
        if modality == 'text':
            # Text data loading
            config_dict['max_length'] = 512  # Max sequence length
            train_loader, val_loader, test_loader = create_text_loaders(
                str(project_dir),
                config_dict
            )
            vocab_size = len(train_loader.dataset.dataset.vocab) if hasattr(train_loader.dataset, 'dataset') else len(train_loader.dataset.vocab)
            logger.info(f"Text project - Vocabulary size: {vocab_size}")
        elif modality == 'audio':
            # Audio data loading
            config_dict['sample_rate'] = 22050
            config_dict['n_mels'] = 128
            config_dict['duration'] = 3.0
            train_loader, val_loader, test_loader = create_audio_loaders(
                str(project_dir),
                config_dict
            )
            vocab_size = None
            logger.info(f"Audio project loaded")
        else:
            # Image data loading (default)
            train_loader, val_loader, test_loader = create_data_loaders(
                str(project_dir),
                config_dict
            )
            vocab_size = None
        
        # Update status
        if project_id in active_trainings:
            active_trainings[project_id]["message"] = f"✅ Dataset loaded - {len(train_loader.dataset)} train, {len(val_loader.dataset)} val samples"
        
        # Get number of classes from data loader
        num_classes = train_loader.dataset.dataset.label_map if hasattr(train_loader.dataset, 'dataset') else 2
        if isinstance(num_classes, dict):
            num_classes = len(num_classes)
        
        # Get model architecture
        model_id = config_dict.get('model_id', 'resnet18' if modality == 'image' else ('lstm' if modality == 'text' else 'spectrogram_cnn'))
        
        # Update status
        if project_id in active_trainings:
            active_trainings[project_id]["message"] = f"🏗️ Building {model_id} model with {num_classes} classes..."
        
        # Build model based on modality
        logger.info(f"Building {modality} model: {model_id}")
        
        if modality == 'text':
            # Build text model
            model = ModelBuilder.build_text_model(
                model_name=model_id,
                vocab_size=vocab_size,
                embed_dim=128,
                num_classes=num_classes,
                hidden_dim=256,
                num_layers=2,
                dropout=config.dropout
            )
        elif modality == 'audio':
            # Build audio model
            model = ModelBuilder.build_audio_model(
                model_name=model_id,
                num_classes=num_classes,
                n_mels=128,
                dropout=config.dropout
            )
        else:
            # Build image model (default)
            model = ModelBuilder.build_image_model(
                model_name=model_id,
                num_classes=num_classes,
                pretrained=True
            )
        
        # Setup device
        device = torch.device('cuda' if torch.cuda.is_available() and config.device == 'cuda' else 'cpu')
        logger.info(f"Using device: {device}")
        
        # Update status
        if project_id in active_trainings:
            active_trainings[project_id]["message"] = f"✅ Model built - Using {device}"
        
        # Loss and optimizer
        criterion = nn.CrossEntropyLoss()
        
        if config.optimizer.lower() == 'adam':
            optimizer = optim.Adam(
                model.parameters(),
                lr=config.learning_rate,
                weight_decay=config.weight_decay
            )
        elif config.optimizer.lower() == 'sgd':
            optimizer = optim.SGD(
                model.parameters(),
                lr=config.learning_rate,
                momentum=0.9,
                weight_decay=config.weight_decay
            )
        else:
            optimizer = optim.Adam(model.parameters(), lr=config.learning_rate)
        
        # Learning rate scheduler
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode='min',
            factor=0.1,
            patience=5
        )
        
        # Setup callbacks
        checkpoint_dir = project_dir / "checkpoints"
        checkpoint_dir.mkdir(exist_ok=True)
        
        tensorboard_dir = project_dir / "tensorboard"
        tensorboard_dir.mkdir(exist_ok=True)
        
        # Prepare metadata for checkpoints
        checkpoint_metadata = {
            'model_architecture': model_id,
            'modality': modality,
            'num_classes': num_classes,
            'project_id': project_id
        }
        
        callbacks = [
            ProgressCallback(project_id, active_trainings),
            TensorBoardCallback(log_dir=str(tensorboard_dir), project_id=project_id)
        ]
        
        if config.early_stopping:
            callbacks.append(
                EarlyStopping(
                    patience=config.early_stopping_patience,
                    min_delta=0.001,
                    mode='min',
                    active_trainings=active_trainings,
                    project_id=project_id
                )
            )
        
        callbacks.append(
            ModelCheckpoint(
                save_dir=str(checkpoint_dir),
                monitor='val_loss',
                mode='min',
                save_best_only=True,
                metadata=checkpoint_metadata
            )
        )
        
        # Update status
        if project_id in active_trainings:
            active_trainings[project_id]["status"] = "training"
            active_trainings[project_id]["message"] = f"🚀 Training started - {config.epochs} epochs on {device}"
        
        # Create trainer
        trainer = Trainer(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            criterion=criterion,
            optimizer=optimizer,
            device=device,
            scheduler=scheduler,
            callbacks=callbacks,
            mixed_precision=config.mixed_precision and torch.cuda.is_available()
        )
        
        # Train the model
        logger.info(f"Starting training for {config.epochs} epochs")
        history = trainer.fit(epochs=config.epochs)
        
        # Prepare metadata for model save
        metadata = {
            'model_architecture': model_id,
            'modality': modality,
            'num_classes': num_classes,
            'input_shape': None,  # Will be set based on modality
            'training_config': {
                'epochs': config.epochs,
                'batch_size': config.batch_size,
                'learning_rate': config.learning_rate,
                'optimizer': config.optimizer,
                'device': str(device)
            }
        }
        
        # Add modality-specific metadata
        if modality == 'image':
            metadata['input_shape'] = [3, 224, 224]  # RGB, 224x224
        elif modality == 'text':
            metadata['vocab_size'] = getattr(model, 'vocab_size', None)
            metadata['embed_dim'] = getattr(model, 'embed_dim', None)
        elif modality == 'audio':
            metadata['input_shape'] = [1, 128, 128]  # Mel spectrogram
        
        # Save final model with metadata in multiple locations
        # 1. Save in root of project (model.pt)
        final_model_path = project_dir / "model.pt"
        trainer.save_model(str(final_model_path), metadata=metadata)
        logger.info(f"Model saved to: {final_model_path}")
        
        # 2. Also save in models/ directory for organization
        models_dir = project_dir / "models"
        models_dir.mkdir(exist_ok=True)
        models_backup_path = models_dir / "final_model.pt"
        trainer.save_model(str(models_backup_path), metadata=metadata)
        logger.info(f"Model backup saved to: {models_backup_path}")
        
        logger.info(f"Model metadata: {metadata}")
        
        # Update active_trainings with model path
        if project_id in active_trainings:
            active_trainings[project_id]['model_path'] = str(final_model_path)
        
        # Training completed
        if project_id in active_trainings:
            best_val_acc = round(max(history['val_acc']), 4)
            best_val_loss = round(min(history['val_loss']), 4)
            total_epochs_trained = len(history['train_loss'])
            
            active_trainings[project_id]["status"] = "completed"
            active_trainings[project_id]["message"] = f"✅ Training completed! {total_epochs_trained} epochs - Best Acc: {best_val_acc*100:.2f}%, Best Loss: {best_val_loss:.4f}"
            active_trainings[project_id]["best_val_acc"] = best_val_acc
            active_trainings[project_id]["best_val_loss"] = best_val_loss
            active_trainings[project_id]["total_epochs_trained"] = total_epochs_trained
        
        logger.info(f"Training completed for project {project_id}")
        logger.info(f"Best Val Accuracy: {max(history['val_acc']):.4f}")
        logger.info(f"Best Val Loss: {min(history['val_loss']):.4f}")
        
    except Exception as e:
        logger.error(f"Error in training loop for project {project_id}: {str(e)}", exc_info=True)
        if project_id in active_trainings:
            active_trainings[project_id]["status"] = "failed"
            active_trainings[project_id]["error"] = str(e)
            active_trainings[project_id]["message"] = f"Training failed: {str(e)}"
        
        # Clean up after a delay to allow frontend to see the error
        await asyncio.sleep(5)
        if project_id in active_trainings and active_trainings[project_id]["status"] == "failed":
            # Remove from active trainings after error is displayed
            logger.info(f"Cleaning up failed training session for project {project_id}")
            del active_trainings[project_id]


@router.post("/stop/{project_id}")
async def stop_training(project_id: str):
    """
    Stop training for a project
    
    Args:
        project_id: Project identifier
        
    Returns:
        Stop status
    """
    try:
        if project_id not in active_trainings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active training found for this project"
            )
        
        # Set stop flag
        active_trainings[project_id]["status"] = "stopping"
        
        logger.info(f"Stopping training for project {project_id}")
        
        # Give it a moment to stop gracefully
        await asyncio.sleep(2)
        
        # Remove from active trainings
        if project_id in active_trainings:
            del active_trainings[project_id]
            logger.info(f"Removed training session for project {project_id}")
        
        return {
            "message": "Training stopped",
            "project_id": project_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping training: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop training: {str(e)}"
        )


@router.post("/reset/{project_id}")
async def reset_training(project_id: str):
    """
    Reset/clear training session for a project
    Useful when training is stuck or failed
    
    Args:
        project_id: Project identifier
        
    Returns:
        Reset status
    """
    try:
        if project_id in active_trainings:
            logger.info(f"Resetting training session for project {project_id}")
            del active_trainings[project_id]
            
            return {
                "message": "Training session reset successfully",
                "project_id": project_id
            }
        else:
            return {
                "message": "No active training session found",
                "project_id": project_id
            }
        
    except Exception as e:
        logger.error(f"Error resetting training: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset training: {str(e)}"
        )


@router.post("/resume/{project_id}")
async def resume_training(project_id: str):
    """
    Resume training for a project from last checkpoint
    
    Args:
        project_id: Project identifier
        
    Returns:
        Resume status
    """
    try:
        project_dir = settings.PROJECTS_DIR / project_id
        if not project_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}"
            )
        
        # Check if there's already active training
        if project_id in active_trainings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Training is already active for this project"
            )
        
        # Check if checkpoint exists
        checkpoint_path = project_dir / "checkpoint.pt"
        if not checkpoint_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No checkpoint found. Please start training from scratch."
            )
        
        # Load project config
        project_file = project_dir / "project.json"
        with open(project_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        # Load last training config from checkpoint metadata
        import torch
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        
        # Create training config from checkpoint
        config = TrainingConfig(
            epochs=checkpoint.get('total_epochs', 50),
            batch_size=checkpoint.get('batch_size', 32),
            learning_rate=checkpoint.get('learning_rate', 0.001),
            optimizer=checkpoint.get('optimizer', 'adam'),
            model_id=project_data.get('model_name', 'resnet18'),
        )
        
        logger.info(f"Resuming training for project {project_id} from epoch {checkpoint.get('epoch', 0)}")
        
        # Start training (will auto-load checkpoint in start_training)
        return await start_training(project_id, config)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming training: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume training: {str(e)}"
        )


@router.get("/tensorboard/{project_id}")
async def get_tensorboard_url(project_id: str):
    """
    Get TensorBoard URL for a project
    
    Args:
        project_id: Project identifier
        
    Returns:
        TensorBoard information
    """
    try:
        project_dir = settings.PROJECTS_DIR / project_id
        tensorboard_dir = project_dir / "tensorboard"
        
        if not tensorboard_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No TensorBoard logs found for this project"
            )
        
        # Return the logdir path for launching TensorBoard
        return {
            "logdir": str(tensorboard_dir.absolute()),
            "command": f"tensorboard --logdir {tensorboard_dir.absolute()}",
            "url": "http://localhost:6006",
            "message": "Run the command in terminal to start TensorBoard"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting TensorBoard info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get TensorBoard info: {str(e)}"
        )


@router.post("/tensorboard/launch/{project_id}")
async def launch_tensorboard(project_id: str):
    """
    Launch TensorBoard process for a project
    
    Args:
        project_id: Project identifier
        
    Returns:
        Launch status
    """
    try:
        import subprocess
        import sys
        
        project_dir = settings.PROJECTS_DIR / project_id
        tensorboard_dir = project_dir / "tensorboard"
        
        if not tensorboard_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No TensorBoard logs found for this project"
            )
        
        # Check if TensorBoard is already running
        try:
            import requests
            response = requests.get("http://localhost:6006", timeout=1)
            if response.status_code == 200:
                return {
                    "message": "TensorBoard is already running",
                    "url": "http://localhost:6006",
                    "status": "running"
                }
        except:
            pass
        
        # Launch TensorBoard in background
        if sys.platform == "win32":
            # Windows: use CREATE_NEW_PROCESS_GROUP to detach
            subprocess.Popen(
                [sys.executable, "-m", "tensorboard.main", "--logdir", str(tensorboard_dir), "--port", "6006"],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            # Unix: use nohup or similar
            subprocess.Popen(
                [sys.executable, "-m", "tensorboard.main", "--logdir", str(tensorboard_dir), "--port", "6006"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        
        logger.info(f"Launched TensorBoard for project {project_id}")
        
        # Wait a moment for TensorBoard to start
        await asyncio.sleep(3)
        
        return {
            "message": "TensorBoard launched successfully",
            "url": "http://localhost:6006",
            "logdir": str(tensorboard_dir),
            "status": "launched"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error launching TensorBoard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to launch TensorBoard: {str(e)}"
        )

@router.get("/debug/active")
async def get_active_trainings_debug():
    """
    🔍 DEBUG: Get all active training sessions
    """
    return {
        "active_count": len(active_trainings),
        "project_ids": list(active_trainings.keys()),
        "details": {pid: {"status": t.get("status"), "epoch": t.get("current_epoch")} for pid, t in active_trainings.items()}
    }

@router.get("/status/{project_id}")
async def get_training_status(project_id: str):
    """
    Get training status for a project
    
    Args:
        project_id: Project identifier
        
    Returns:
        Training status
    """
    try:
        # 🔍 Log for debugging
        logger.info(f"[Status Check] Requested: {project_id}")
        logger.info(f"[Status Check] Active trainings: {list(active_trainings.keys())}")
        
        if project_id not in active_trainings:
            logger.debug(f"[Status Check] Project {project_id} not in active_trainings")
            return {
                "project_id": project_id,
                "status": "not_started",
                "message": "No training in progress"
            }
        
        # Get current status
        status_data = active_trainings[project_id].copy()
        logger.debug(f"[Status Check] Project {project_id} - Epoch: {status_data.get('current_epoch', 0)}, Status: {status_data.get('status', 'unknown')}")
        
        return {
            "project_id": project_id,
            **status_data
        }
        
    except Exception as e:
        logger.error(f"Error getting training status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get training status: {str(e)}"
        )

@router.get("/results/{project_id}")
async def get_training_results(project_id: str):
    """
    Get training results for a completed project
    
    Args:
        project_id: Project identifier
        
    Returns:
        Training results including metrics
    """
    try:
        project_dir = settings.PROJECTS_DIR / project_id
        if not project_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}"
            )
        
        # Return mock results for now - will be replaced with actual saved results
        return {
            "project_id": project_id,
            "status": "completed",
            "final_accuracy": 0.9567,
            "final_loss": 0.1234,
            "training_time": 1122.5,  # seconds
            "epochs_trained": 50,
            "class_metrics": [
                {
                    "class_name": "Class_A",
                    "precision": 0.96,
                    "recall": 0.94,
                    "f1_score": 0.95,
                    "sample_count": 120
                },
                {
                    "class_name": "Class_B",
                    "precision": 0.93,
                    "recall": 0.97,
                    "f1_score": 0.95,
                    "sample_count": 115
                }
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting training results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get training results: {str(e)}"
        )

@router.websocket("/live/{project_id}")
async def training_websocket(websocket: WebSocket, project_id: str):
    """
    WebSocket endpoint for live training updates
    
    Args:
        websocket: WebSocket connection
        project_id: Project identifier
    """
    await websocket.accept()
    logger.info(f"WebSocket connected for project {project_id}")
    
    try:
        while True:
            # Send training updates if training is active
            if project_id in active_trainings:
                training_data = active_trainings[project_id]
                await websocket.send_json(training_data)
            else:
                # Send idle status
                await websocket.send_json({
                    "status": "idle",
                    "message": "No training in progress"
                })
            
            # Wait before next update
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for project {project_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()

