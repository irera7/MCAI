"""
Test AutoML (Hyperparameter Optimization) with Optuna
این اسکریپت AutoML را با یک dataset کوچک تست می‌کند

نکته: برای سرعت بیشتر، از dataset و epoch‌های کم استفاده می‌کنیم
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

import torch
from engine import create_data_loaders, optimize_hyperparameters
from create_text_dataset import create_sample_text_dataset


def test_automl_image(n_trials: int = 5):
    """
    تست AutoML برای Image Classification
    
    Args:
        n_trials: تعداد trial‌ها (آزمایش‌ها)
    """
    print("\n" + "="*70)
    print("TEST 1: AutoML for Image Classification")
    print("="*70)
    
    project_dir = Path("../projects/test-cat-dog")
    
    # بررسی وجود dataset
    if not project_dir.exists():
        print("⚠️  test-cat-dog project not found!")
        print("   Please create it first or use another project")
        return False
    
    print("\n1️⃣  Loading image dataset...")
    
    # Configuration برای data loading
    config = {
        'batch_size': 16,  # این بعداً توسط AutoML تغییر می‌کند
        'num_workers': 0,   # برای سرعت
        'train_split': 0.7,
        'val_split': 0.15
    }
    
    try:
        # ایجاد data loaders
        train_loader, val_loader, test_loader = create_data_loaders(
            str(project_dir),
            config
        )
        
        print(f"✅ Dataset loaded:")
        print(f"   Train: {len(train_loader.dataset)} samples")
        print(f"   Val: {len(val_loader.dataset)} samples")
        
        # تعداد کلاس‌ها
        num_classes = len(train_loader.dataset.dataset.label_map)
        print(f"   Classes: {num_classes}")
        
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return False
    
    print(f"\n2️⃣  Starting hyperparameter optimization...")
    print(f"   Model: resnet18")
    print(f"   Trials: {n_trials}")
    print(f"   Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")
    print()
    
    try:
        # اجرای AutoML
        # نکته: epochs را کم می‌گذاریم برای سرعت
        results = optimize_hyperparameters(
            train_loader=train_loader,
            val_loader=val_loader,
            num_classes=num_classes,
            modality='image',
            model_name='resnet18',
            n_trials=n_trials,
            device='cuda' if torch.cuda.is_available() else 'cpu',
            save_dir='optuna_studies',
            epochs=3,  # فقط 3 epoch برای هر trial (برای سرعت)
            direction='maximize'  # maximize accuracy
        )
        
        print(f"\n✅ Optimization completed!")
        print(f"\n3️⃣  Best hyperparameters found:")
        for key, value in results['best_params'].items():
            print(f"   {key}: {value}")
        
        print(f"\n   Best validation accuracy: {results['best_value']:.4f}")
        print(f"   Total trials: {results['n_trials']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during optimization: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_automl_text(n_trials: int = 5):
    """
    تست AutoML برای Text Classification
    
    Args:
        n_trials: تعداد trial‌ها
    """
    print("\n" + "="*70)
    print("TEST 2: AutoML for Text Classification")
    print("="*70)
    
    project_id = "text-sentiment-automl-test"
    project_dir = Path(f"../projects/{project_id}")
    
    print("\n1️⃣  Creating sample text dataset...")
    
    try:
        # ایجاد dataset نمونه
        create_sample_text_dataset(
            project_name=project_id,
            num_samples_per_class=15  # کم برای سرعت
        )
        print("✅ Dataset created")
        
    except Exception as e:
        print(f"❌ Error creating dataset: {e}")
        return False
    
    print("\n2️⃣  Loading text dataset...")
    
    try:
        from engine import create_text_loaders
        
        config = {
            'batch_size': 8,
            'num_workers': 0,
            'max_length': 128,
            'train_split': 0.6,
            'val_split': 0.2
        }
        
        train_loader, val_loader, test_loader = create_text_loaders(
            str(project_dir),
            config
        )
        
        print(f"✅ Dataset loaded:")
        print(f"   Train: {len(train_loader.dataset)} samples")
        print(f"   Val: {len(val_loader.dataset)} samples")
        
        num_classes = len(train_loader.dataset.dataset.label_map)
        print(f"   Classes: {num_classes}")
        
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n3️⃣  Starting hyperparameter optimization...")
    print(f"   Model: lstm")
    print(f"   Trials: {n_trials}")
    print()
    
    try:
        # اجرای AutoML برای Text
        results = optimize_hyperparameters(
            train_loader=train_loader,
            val_loader=val_loader,
            num_classes=num_classes,
            modality='text',
            model_name='lstm',
            n_trials=n_trials,
            device='cpu',  # Text معمولاً CPU سریع‌تر است
            save_dir='optuna_studies',
            epochs=3,  # کم برای سرعت
            direction='maximize'
        )
        
        print(f"\n✅ Optimization completed!")
        print(f"\n4️⃣  Best hyperparameters found:")
        for key, value in results['best_params'].items():
            print(f"   {key}: {value}")
        
        print(f"\n   Best validation accuracy: {results['best_value']:.4f}")
        print(f"   Total trials: {results['n_trials']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during optimization: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """
    اجرای تمام تست‌های AutoML
    """
    print("\n" + "🔍"*35)
    print("AUTOML (HYPERPARAMETER OPTIMIZATION) TEST")
    print("🔍"*35)
    
    # بررسی نصب Optuna
    print("\n📦 Checking dependencies...")
    try:
        import optuna
        print("✅ optuna")
    except ImportError:
        print("❌ optuna not installed!")
        print("   Install with: pip install optuna")
        print("   Optional: pip install plotly (for visualizations)")
        sys.exit(1)
    
    try:
        import torch
        print("✅ torch")
    except ImportError:
        print("❌ torch not installed!")
        sys.exit(1)
    
    print("\n✅ All dependencies available")
    
    # اجرای تست‌ها
    # نکته: n_trials را کم گذاشته‌ایم (5) برای سرعت
    # در استفاده واقعی، 50-100 trial توصیه می‌شود
    
    print("\n" + "="*70)
    print("NOTE: Using n_trials=5 for speed (real usage: 50-100 trials)")
    print("      Using epochs=3 for each trial (real usage: 20-50 epochs)")
    print("="*70)
    
    results = {}
    
    # Test 1: Image AutoML
    print("\n\n")
    results['image'] = test_automl_image(n_trials=5)
    
    # Test 2: Text AutoML
    print("\n\n")
    results['text'] = test_automl_text(n_trials=5)
    
    # خلاصه نتایج
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    if results['image']:
        print("✅ Image AutoML: PASSED")
    else:
        print("❌ Image AutoML: FAILED")
    
    if results['text']:
        print("✅ Text AutoML: PASSED")
    else:
        print("❌ Text AutoML: FAILED")
    
    print("\n📂 Results saved to: optuna_studies/")
    print("📊 View visualizations: optuna_studies/*.html")
    
    if all(results.values()):
        print("\n" + "🎉"*35)
        print("ALL AUTOML TESTS PASSED!")
        print("🎉"*35)
        return True
    else:
        print("\n⚠️  Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

