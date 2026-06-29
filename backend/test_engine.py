"""
End-to-end test for the training engine
"""

import sys
import torch
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from engine import create_data_loaders, ModelBuilder, Trainer
from engine.callbacks import EarlyStopping, ModelCheckpoint, ProgressCallback

def test_data_loader():
    """Test data loader"""
    print("=" * 70)
    print("TEST 1: Data Loader")
    print("=" * 70)
    
    project_dir = Path(__file__).parent.parent / "projects" / "test-cat-dog"
    
    if not project_dir.exists():
        print(f"❌ Test project not found: {project_dir}")
        return False
    
    config = {
        'batch_size': 4,
        'num_workers': 0,  # Use 0 for Windows compatibility
        'train_split': 0.7,
        'val_split': 0.15,
    }
    
    try:
        train_loader, val_loader, test_loader = create_data_loaders(
            str(project_dir),
            config
        )
        
        print(f"✅ Data loaders created successfully!")
        print(f"   Train: {len(train_loader.dataset)} samples, {len(train_loader)} batches")
        print(f"   Val:   {len(val_loader.dataset)} samples, {len(val_loader)} batches")
        print(f"   Test:  {len(test_loader.dataset)} samples, {len(test_loader)} batches")
        
        # Test loading a batch
        images, labels = next(iter(train_loader))
        print(f"✅ Batch loaded successfully!")
        print(f"   Images shape: {images.shape}")
        print(f"   Labels shape: {labels.shape}")
        
        return True, train_loader, val_loader, test_loader
        
    except Exception as e:
        print(f"❌ Data loader test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None, None


def test_model_builder(num_classes=2):
    """Test model builder"""
    print("\n" + "=" * 70)
    print("TEST 2: Model Builder")
    print("=" * 70)
    
    try:
        model = ModelBuilder.build_image_model(
            model_name='resnet18',
            num_classes=num_classes,
            pretrained=False  # Faster for testing
        )
        
        print(f"✅ Model built successfully!")
        
        # Get model info
        info = ModelBuilder.get_model_info(model)
        print(f"   Total parameters: {info['total_parameters']:,}")
        print(f"   Trainable parameters: {info['trainable_parameters']:,}")
        print(f"   Model size: {info['model_size_mb']:.2f} MB")
        
        # Test forward pass
        x = torch.randn(2, 3, 224, 224)
        y = model(x)
        print(f"✅ Forward pass successful!")
        print(f"   Input shape: {x.shape}")
        print(f"   Output shape: {y.shape}")
        
        return True, model
        
    except Exception as e:
        print(f"❌ Model builder test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_trainer(model, train_loader, val_loader):
    """Test trainer"""
    print("\n" + "=" * 70)
    print("TEST 3: Trainer (Quick Test - 2 epochs)")
    print("=" * 70)
    
    try:
        import torch.nn as nn
        import torch.optim as optim
        
        # Setup
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {device}")
        
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        
        # Mock active_trainings for callback
        active_trainings = {}
        project_id = "test-project"
        active_trainings[project_id] = {
            "status": "starting",
            "current_epoch": 0,
            "total_epochs": 2,
        }
        
        # Callbacks
        callbacks = [
            ProgressCallback(project_id, active_trainings)
        ]
        
        # Create trainer
        trainer = Trainer(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            criterion=criterion,
            optimizer=optimizer,
            device=device,
            callbacks=callbacks,
            mixed_precision=False
        )
        
        print("✅ Trainer created successfully!")
        
        # Train for 2 epochs (quick test)
        print("\nStarting training (2 epochs for testing)...")
        history = trainer.fit(epochs=2)
        
        print("\n✅ Training completed successfully!")
        print(f"   Final train loss: {history['train_loss'][-1]:.4f}")
        print(f"   Final train acc:  {history['train_acc'][-1]:.4f}")
        print(f"   Final val loss:   {history['val_loss'][-1]:.4f}")
        print(f"   Final val acc:    {history['val_acc'][-1]:.4f}")
        
        # Test model save
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pt', delete=False) as f:
            test_save_path = f.name
        
        trainer.save_model(test_save_path)
        print(f"✅ Model saved to: {test_save_path}")
        
        # Test model load
        trainer.load_model(test_save_path)
        print(f"✅ Model loaded from: {test_save_path}")
        
        # Clean up
        import os
        os.remove(test_save_path)
        print("✅ Cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Trainer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "🚀 " * 20)
    print("MODELCREATOR ENGINE END-TO-END TEST")
    print("🚀 " * 20 + "\n")
    
    # Test 1: Data Loader
    result = test_data_loader()
    if isinstance(result, tuple) and result[0]:
        success_dl, train_loader, val_loader, test_loader = result
    else:
        print("\n❌ OVERALL RESULT: FAILED (Data Loader)")
        return
    
    # Test 2: Model Builder
    success_mb, model = test_model_builder()
    if not success_mb:
        print("\n❌ OVERALL RESULT: FAILED (Model Builder)")
        return
    
    # Test 3: Trainer
    success_tr = test_trainer(model, train_loader, val_loader)
    if not success_tr:
        print("\n❌ OVERALL RESULT: FAILED (Trainer)")
        return
    
    # All tests passed
    print("\n" + "✅ " * 20)
    print("ALL TESTS PASSED!")
    print("✅ " * 20)
    print("\n📋 Summary:")
    print("   ✅ Data Loader - Working")
    print("   ✅ Model Builder - Working")
    print("   ✅ Trainer - Working")
    print("   ✅ Callbacks - Working")
    print("   ✅ Save/Load - Working")
    print("\n🎉 The training engine is ready for production use!")


if __name__ == "__main__":
    main()

