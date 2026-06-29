"""
Test Ensemble Methods
تست روش‌های Ensemble
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import torch
import torch.nn as nn
from engine import ModelBuilder
from engine.ensemble import (
    VotingEnsemble, StackingEnsemble, BaggingEnsemble,
    evaluate_ensemble, quick_ensemble
)


def create_dummy_data(num_samples=100, num_classes=5):
    """ایجاد داده dummy برای تست"""
    # برای Image: (B, 3, 224, 224)
    data = torch.randn(num_samples, 3, 224, 224)
    labels = torch.randint(0, num_classes, (num_samples,))
    
    dataset = torch.utils.data.TensorDataset(data, labels)
    loader = torch.utils.data.DataLoader(dataset, batch_size=16, shuffle=False)
    
    return loader


def test_voting_ensemble():
    """تست Voting Ensemble"""
    print("\n" + "="*70)
    print("TEST 1: VOTING ENSEMBLE")
    print("="*70)
    
    num_classes = 5
    
    # ساخت 3 مدل مختلف
    print("\n1️⃣ Creating 3 different models...")
    model1 = ModelBuilder.build_image_model('resnet18', num_classes, pretrained=False)
    model2 = ModelBuilder.build_image_model('mobilenetv3_small_100', num_classes, pretrained=False)
    model3 = ModelBuilder.build_image_model('efficientnet_b0', num_classes, pretrained=False)
    
    models = [model1, model2, model3]
    
    # Soft Voting
    print("\n2️⃣ Testing Soft Voting...")
    soft_ensemble = VotingEnsemble(models, voting='soft')
    
    dummy_input = torch.randn(4, 3, 224, 224)
    output = soft_ensemble(dummy_input)
    print(f"   Output shape: {output.shape}")
    print(f"   ✅ Soft Voting works!")
    
    # Hard Voting
    print("\n3️⃣ Testing Hard Voting...")
    hard_ensemble = VotingEnsemble(models, voting='hard')
    output = hard_ensemble(dummy_input)
    print(f"   Output shape: {output.shape}")
    print(f"   ✅ Hard Voting works!")
    
    # Weighted Voting
    print("\n4️⃣ Testing Weighted Voting...")
    weighted_ensemble = VotingEnsemble(models, voting='soft', weights=[0.5, 0.3, 0.2])
    output = weighted_ensemble(dummy_input)
    print(f"   ✅ Weighted Voting works!")
    
    return True


def test_stacking_ensemble():
    """تست Stacking Ensemble"""
    print("\n" + "="*70)
    print("TEST 2: STACKING ENSEMBLE")
    print("="*70)
    
    num_classes = 5
    
    # ساخت base models
    print("\n1️⃣ Creating base models...")
    model1 = ModelBuilder.build_image_model('resnet18', num_classes, pretrained=False)
    model2 = ModelBuilder.build_image_model('mobilenetv3_small_100', num_classes, pretrained=False)
    
    base_models = [model1, model2]
    
    # ساخت meta model (یک MLP ساده)
    print("\n2️⃣ Creating meta model...")
    class SimpleMeta(nn.Module):
        def __init__(self, input_dim, output_dim):
            super().__init__()
            self.fc = nn.Sequential(
                nn.Linear(input_dim, 64),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(64, output_dim)
            )
        
        def forward(self, x):
            return self.fc(x)
    
    meta_model = SimpleMeta(input_dim=2 * num_classes, output_dim=num_classes)
    
    # ساخت ensemble
    print("\n3️⃣ Creating Stacking Ensemble...")
    stacking_ensemble = StackingEnsemble(base_models, meta_model)
    
    # تست forward
    dummy_input = torch.randn(4, 3, 224, 224)
    output = stacking_ensemble(dummy_input)
    print(f"   Output shape: {output.shape}")
    print(f"   ✅ Stacking Ensemble works!")
    
    # تست آموزش meta model
    print("\n4️⃣ Testing meta model training...")
    train_loader = create_dummy_data(num_samples=50, num_classes=num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(stacking_ensemble.meta_model.parameters(), lr=0.001)
    
    stacking_ensemble.train_meta(
        train_loader=train_loader,
        criterion=criterion,
        optimizer=optimizer,
        epochs=2,
        device='cpu'
    )
    print(f"   ✅ Meta model training works!")
    
    return True


def test_bagging_ensemble():
    """تست Bagging Ensemble"""
    print("\n" + "="*70)
    print("TEST 3: BAGGING ENSEMBLE")
    print("="*70)
    
    num_classes = 5
    
    # ساخت چند مدل یکسان (شبیه‌سازی bootstrap training)
    print("\n1️⃣ Creating multiple ResNet18 models...")
    models = []
    for i in range(3):
        model = ModelBuilder.build_image_model('resnet18', num_classes, pretrained=False)
        models.append(model)
    
    # ساخت ensemble
    print("\n2️⃣ Creating Bagging Ensemble...")
    bagging_ensemble = BaggingEnsemble(models)
    
    # تست forward
    dummy_input = torch.randn(4, 3, 224, 224)
    output = bagging_ensemble(dummy_input)
    print(f"   Output shape: {output.shape}")
    print(f"   ✅ Bagging Ensemble works!")
    
    return True


def test_evaluate_ensemble():
    """تست ارزیابی ensemble"""
    print("\n" + "="*70)
    print("TEST 4: ENSEMBLE EVALUATION")
    print("="*70)
    
    num_classes = 5
    
    # ساخت یک ensemble ساده
    print("\n1️⃣ Creating simple ensemble...")
    model1 = ModelBuilder.build_image_model('resnet18', num_classes, pretrained=False)
    model2 = ModelBuilder.build_image_model('mobilenetv3_small_100', num_classes, pretrained=False)
    ensemble = VotingEnsemble([model1, model2], voting='soft')
    
    # ایجاد test data
    print("\n2️⃣ Creating test data...")
    test_loader = create_dummy_data(num_samples=50, num_classes=num_classes)
    
    # ارزیابی
    print("\n3️⃣ Evaluating ensemble...")
    metrics = evaluate_ensemble(ensemble, test_loader, device='cpu')
    
    print(f"   Accuracy: {metrics['accuracy']:.2f}%")
    print(f"   Correct: {metrics['correct']}/{metrics['total']}")
    print(f"   ✅ Evaluation works!")
    
    return True


def test_quick_ensemble():
    """تست تابع quick_ensemble"""
    print("\n" + "="*70)
    print("TEST 5: QUICK ENSEMBLE HELPER")
    print("="*70)
    
    num_classes = 5
    
    print("\n1️⃣ Creating models...")
    models = [
        ModelBuilder.build_image_model('resnet18', num_classes, pretrained=False),
        ModelBuilder.build_image_model('mobilenetv3_small_100', num_classes, pretrained=False)
    ]
    
    # تست voting
    print("\n2️⃣ Testing quick_ensemble with voting...")
    ensemble = quick_ensemble(models, ensemble_type='voting', voting='soft')
    dummy_input = torch.randn(2, 3, 224, 224)
    output = ensemble(dummy_input)
    print(f"   ✅ Quick voting ensemble works!")
    
    # تست bagging
    print("\n3️⃣ Testing quick_ensemble with bagging...")
    ensemble = quick_ensemble(models, ensemble_type='bagging')
    output = ensemble(dummy_input)
    print(f"   ✅ Quick bagging ensemble works!")
    
    return True


def main():
    """اجرای تمام تست‌ها"""
    print("\n" + "="*70)
    print("🧪 ENSEMBLE METHODS - COMPLETE TEST SUITE")
    print("="*70)
    
    tests = [
        ("Voting Ensemble", test_voting_ensemble),
        ("Stacking Ensemble", test_stacking_ensemble),
        ("Bagging Ensemble", test_bagging_ensemble),
        ("Evaluate Ensemble", test_evaluate_ensemble),
        ("Quick Ensemble", test_quick_ensemble),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} FAILED: {e}")
    
    print("\n" + "="*70)
    print(f"✅ PASSED: {passed}/{len(tests)}")
    print(f"❌ FAILED: {failed}/{len(tests)}")
    print("="*70)
    
    if failed == 0:
        print("\n🎉 ALL ENSEMBLE TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️ {failed} tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

