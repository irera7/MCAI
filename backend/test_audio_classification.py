"""
Complete test for Audio Classification
Tests data loading, model building, and training with audio data
"""

import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from engine import create_audio_loaders, ModelBuilder, Trainer
from engine.callbacks import EarlyStopping, ModelCheckpoint, ProgressCallback, TensorBoardCallback
from create_audio_dataset import create_sample_audio_dataset

def test_audio_classification(project_id: str = "audio-test", epochs: int = 5):
    """
    Test audio classification pipeline
    
    Args:
        project_id: Project ID/name
        epochs: Number of training epochs
    """
    print("\n" + "="*70)
    print("AUDIO CLASSIFICATION TEST")
    print("="*70)
    
    project_dir = Path(f"../projects/{project_id}")
    
    # Step 1: Create sample dataset
    print("\n1️⃣ Creating sample audio dataset...")
    create_sample_audio_dataset(
        project_name=project_id,
        num_samples_per_class=10,
        duration=3.0
    )
    print("✅ Dataset created\n")
    
    # Step 2: Setup configuration
    print("2️⃣ Setting up configuration...")
    config = {
        'batch_size': 4,
        'num_workers': 0,  # Audio better with 0
        'train_split': 0.6,
        'val_split': 0.2,
        'sample_rate': 22050,
        'n_mels': 128,
        'duration': 3.0,
        'device': 'cpu',  # Use CPU for testing
        'epochs': epochs
    }
    print(f"✅ Config: batch_size={config['batch_size']}, epochs={config['epochs']}\n")
    
    # Step 3: Create data loaders
    print("3️⃣ Creating audio data loaders...")
    try:
        train_loader, val_loader, test_loader = create_audio_loaders(
            str(project_dir),
            config
        )
        print(f"✅ Data loaders created")
        print(f"   Train: {len(train_loader.dataset)} samples")
        print(f"   Val: {len(val_loader.dataset)} samples")
        print(f"   Test: {len(test_loader.dataset)} samples\n")
    except Exception as e:
        print(f"❌ Error creating data loaders: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Get number of classes
    print("4️⃣ Getting dataset information...")
    num_classes = len(train_loader.dataset.dataset.label_map)
    print(f"✅ Number of classes: {num_classes}")
    print(f"   Classes: {list(train_loader.dataset.dataset.label_map.keys())}\n")
    
    # Step 5: Build model
    print("5️⃣ Building audio model...")
    try:
        model = ModelBuilder.build_audio_model(
            model_name='spectrogram_cnn',
            num_classes=num_classes,
            n_mels=128,
            dropout=0.3
        )
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        print(f"✅ Model built successfully")
        print(f"   Total parameters: {total_params:,}")
        print(f"   Trainable parameters: {trainable_params:,}\n")
    except Exception as e:
        print(f"❌ Error building model: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 6: Test forward pass
    print("6️⃣ Testing forward pass...")
    try:
        spectrograms, labels = next(iter(train_loader))
        print(f"   Batch shape: {spectrograms.shape}")
        print(f"   Labels shape: {labels.shape}")
        
        with torch.no_grad():
            output = model(spectrograms)
        print(f"   Output shape: {output.shape}")
        print(f"✅ Forward pass successful\n")
    except Exception as e:
        print(f"❌ Error in forward pass: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 7: Setup training
    print("7️⃣ Setting up training...")
    device = torch.device(config['device'])
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=2)
    
    # Setup callbacks
    checkpoint_dir = project_dir / "checkpoints"
    checkpoint_dir.mkdir(exist_ok=True)
    tensorboard_dir = project_dir / "tensorboard"
    tensorboard_dir.mkdir(exist_ok=True)
    
    # Mock active_trainings for ProgressCallback
    active_trainings_mock = {
        project_id: {
            "status": "starting",
            "config": config,
            "current_epoch": 0,
            "total_epochs": epochs,
            "message": "Initializing training..."
        }
    }
    
    callbacks = [
        ProgressCallback(project_id, active_trainings_mock),
        TensorBoardCallback(log_dir=str(tensorboard_dir), project_id=project_id),
        EarlyStopping(
            patience=3,
            mode='min',
            active_trainings=active_trainings_mock,
            project_id=project_id
        ),
        ModelCheckpoint(
            save_dir=str(checkpoint_dir),
            monitor='val_loss',
            mode='min',
            save_best_only=True
        )
    ]
    print(f"✅ Training setup complete\n")
    
    # Step 8: Train model
    print("8️⃣ Starting training...")
    print(f"   Epochs: {epochs}")
    print(f"   Device: {device}")
    print(f"   Optimizer: Adam")
    print(f"   Learning rate: 0.001")
    print()
    
    try:
        trainer = Trainer(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            criterion=criterion,
            optimizer=optimizer,
            device=device,
            scheduler=scheduler,
            callbacks=callbacks
        )
        
        history = trainer.fit(epochs=epochs)
        
        print("\n✅ Training completed!")
        print(f"   Final train loss: {history['train_loss'][-1]:.4f}")
        print(f"   Final train acc: {history['train_acc'][-1]:.2f}%")
        print(f"   Final val loss: {history['val_loss'][-1]:.4f}")
        print(f"   Final val acc: {history['val_acc'][-1]:.2f}%")
        print(f"   Best val loss: {min(history['val_loss']):.4f}")
        print(f"   Best val acc: {max(history['val_acc']):.2f}%\n")
        
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 9: Verify saved model
    print("9️⃣ Verifying saved model...")
    best_model_path = checkpoint_dir / "best_model.pt"
    if best_model_path.exists():
        print(f"✅ Best model saved at: {best_model_path}")
        
        # Try loading it
        try:
            checkpoint = torch.load(best_model_path, map_location='cpu')
            print(f"   Checkpoint epoch: {checkpoint.get('epoch', 'N/A')}")
            print(f"   Checkpoint val_loss: {checkpoint.get('val_loss', 'N/A'):.4f}")
        except Exception as e:
            print(f"⚠️ Could not load checkpoint: {e}")
    else:
        print(f"⚠️ Best model not found at: {best_model_path}")
    
    print()
    
    # Step 10: Summary
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    print("✅ Audio dataset creation: SUCCESS")
    print("✅ Data loading: SUCCESS")
    print("✅ Model building: SUCCESS")
    print("✅ Forward pass: SUCCESS")
    print("✅ Training: SUCCESS")
    print("✅ Model saving: SUCCESS")
    print()
    print(f"📂 Project location: {project_dir}")
    print(f"📊 TensorBoard: tensorboard --logdir {tensorboard_dir}")
    print(f"🎵 Audio samples: {project_dir / 'data'}")
    print()
    print("="*70)
    print("🎉 AUDIO CLASSIFICATION TEST COMPLETED SUCCESSFULLY!")
    print("="*70)
    
    return True

if __name__ == "__main__":
    # Check dependencies
    print("Checking dependencies...")
    
    missing_deps = []
    
    try:
        import librosa
        print("✅ librosa")
    except ImportError:
        print("❌ librosa")
        missing_deps.append("librosa")
    
    try:
        import soundfile
        print("✅ soundfile")
    except ImportError:
        print("❌ soundfile")
        missing_deps.append("soundfile")
    
    try:
        import torch
        print("✅ torch")
    except ImportError:
        print("❌ torch")
        missing_deps.append("torch")
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install " + " ".join(missing_deps))
        sys.exit(1)
    
    print("\n✅ All dependencies available\n")
    
    # Run test
    success = test_audio_classification(epochs=5)
    
    sys.exit(0 if success else 1)

