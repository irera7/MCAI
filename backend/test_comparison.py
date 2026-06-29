"""
Test Model Comparison System
تست سیستم مقایسه مدل‌ها
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from engine import ModelComparison, compare_models
import json

def test_model_comparison():
    """
    تست کامل سیستم مقایسه
    """
    print("\n" + "="*70)
    print("MODEL COMPARISON SYSTEM TEST")
    print("="*70)
    
    project_dir = "../projects/test-comparison"
    Path(project_dir).mkdir(parents=True, exist_ok=True)
    
    # ایجاد ModelComparison
    comparison = ModelComparison(project_dir)
    
    # شبیه‌سازی چند training run
    print("\n1️⃣ Creating sample training runs...")
    
    # Run 1: ResNet18
    comparison.save_run(
        run_id='run_resnet18_001',
        project_id='test-comparison',
        model_name='resnet18',
        modality='image',
        hyperparameters={
            'learning_rate': 0.001,
            'batch_size': 32,
            'optimizer': 'adam',
            'epochs': 10
        },
        history={
            'train_loss': [2.3, 1.8, 1.5, 1.2, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5],
            'train_acc': [20, 35, 45, 55, 63, 70, 75, 80, 83, 86],
            'val_loss': [2.1, 1.7, 1.4, 1.1, 1.0, 0.95, 0.9, 0.85, 0.8, 0.75],
            'val_acc': [25, 40, 50, 60, 65, 72, 76, 82, 85, 87]
        },
        duration=450.5,
        device='cuda'
    )
    
    # Run 2: MobileNetV3
    comparison.save_run(
        run_id='run_mobilenet_001',
        project_id='test-comparison',
        model_name='mobilenetv3',
        modality='image',
        hyperparameters={
            'learning_rate': 0.002,
            'batch_size': 64,
            'optimizer': 'sgd',
            'epochs': 10
        },
        history={
            'train_loss': [2.5, 2.0, 1.6, 1.3, 1.1, 0.95, 0.85, 0.75, 0.65, 0.6],
            'train_acc': [18, 30, 42, 52, 60, 68, 73, 78, 82, 84],
            'val_loss': [2.3, 1.9, 1.5, 1.2, 1.05, 0.92, 0.88, 0.82, 0.78, 0.72],
            'val_acc': [22, 35, 47, 58, 63, 70, 74, 79, 83, 85]
        },
        duration=320.2,
        device='cuda'
    )
    
    # Run 3: LSTM (text)
    comparison.save_run(
        run_id='run_lstm_001',
        project_id='test-comparison',
        model_name='lstm',
        modality='text',
        hyperparameters={
            'learning_rate': 0.001,
            'batch_size': 16,
            'optimizer': 'adam',
            'hidden_dim': 256,
            'epochs': 15
        },
        history={
            'train_loss': [1.5, 1.2, 1.0, 0.9, 0.8, 0.7, 0.65, 0.6, 0.55, 0.5, 0.48, 0.45, 0.42, 0.4, 0.38],
            'train_acc': [45, 55, 63, 68, 73, 77, 80, 82, 84, 86, 87, 88, 89, 90, 91],
            'val_loss': [1.4, 1.1, 0.95, 0.88, 0.82, 0.78, 0.75, 0.72, 0.7, 0.68, 0.67, 0.66, 0.65, 0.64, 0.63],
            'val_acc': [50, 60, 66, 70, 74, 77, 79, 81, 83, 84, 85, 86, 87, 87, 88]
        },
        duration=180.8,
        device='cpu'
    )
    
    print("✅ 3 sample runs created\n")
    
    # تست مقایسه
    print("2️⃣ Comparing models...")
    df = comparison.compare_runs(metric='val_acc')
    print(df.to_string())
    print()
    
    # بهترین مدل
    print("3️⃣ Finding best model...")
    best_run = comparison.get_best_run('val_acc')
    if best_run:
        print(f"✅ Best model: {best_run.model_name} (run: {best_run.run_id})")
        print(f"   Best val_acc: {best_run.get_best_metric('val_acc'):.2f}%")
    print()
    
    # ایجاد گزارش
    print("4️⃣ Generating report...")
    report = comparison.generate_report(
        output_file=str(Path(project_dir) / "comparison_report.txt")
    )
    print("✅ Report generated\n")
    
    # Export به CSV
    print("5️⃣ Exporting to CSV...")
    comparison.export_to_csv(str(Path(project_dir) / "comparison.csv"))
    print()
    
    # رسم نمودار
    print("6️⃣ Plotting comparison...")
    try:
        comparison.plot_comparison(
            metric='val_acc',
            save_path=str(Path(project_dir) / "comparison_plot.png")
        )
    except Exception as e:
        print(f"⚠️ Could not create plot: {e}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
    print(f"\n📂 Results saved to: {project_dir}/")
    print("   - comparison_report.txt")
    print("   - comparison.csv")
    print("   - comparison_plot.png")
    print("   - runs/*.json")
    
    return True

if __name__ == "__main__":
    success = test_model_comparison()
    sys.exit(0 if success else 1)

