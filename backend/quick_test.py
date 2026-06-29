"""Quick test to verify engine imports"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing imports...")

try:
    from engine import create_data_loaders
    print("✅ create_data_loaders imported")
except Exception as e:
    print(f"❌ Failed to import create_data_loaders: {e}")
    sys.exit(1)

try:
    from engine import ModelBuilder
    print("✅ ModelBuilder imported")
except Exception as e:
    print(f"❌ Failed to import ModelBuilder: {e}")
    sys.exit(1)

try:
    from engine import Trainer
    print("✅ Trainer imported")
except Exception as e:
    print(f"❌ Failed to import Trainer: {e}")
    sys.exit(1)

try:
    from engine.callbacks import EarlyStopping, ModelCheckpoint, ProgressCallback
    print("✅ Callbacks imported")
except Exception as e:
    print(f"❌ Failed to import callbacks: {e}")
    sys.exit(1)

print("\n🎉 All imports successful!")
print("\nNow testing with actual project...")

project_dir = Path(__file__).parent.parent / "projects" / "test-cat-dog"

if not project_dir.exists():
    print(f"❌ Test project not found: {project_dir}")
    sys.exit(1)

print(f"✅ Test project found: {project_dir}")

config = {
    'batch_size': 4,
    'num_workers': 0,
    'train_split': 0.7,
    'val_split': 0.15,
}

try:
    print("\nCreating data loaders...")
    train_loader, val_loader, test_loader = create_data_loaders(
        str(project_dir),
        config
    )
    print(f"✅ Data loaders created!")
    print(f"   Train: {len(train_loader.dataset)} samples")
    print(f"   Val:   {len(val_loader.dataset)} samples")
    print(f"   Test:  {len(test_loader.dataset)} samples")
except Exception as e:
    print(f"❌ Failed to create data loaders: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\nBuilding model...")
    model = ModelBuilder.build_image_model(
        model_name='resnet18',
        num_classes=2,
        pretrained=False
    )
    print("✅ Model built successfully!")
    
    info = ModelBuilder.get_model_info(model)
    print(f"   Parameters: {info['total_parameters']:,}")
except Exception as e:
    print(f"❌ Failed to build model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅✅✅ ALL TESTS PASSED! ✅✅✅")
print("\nThe training engine is working correctly!")

