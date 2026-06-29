# 🤖 AutoML - Hyperparameter Optimization Guide

**Automatic Hyperparameter Tuning با Optuna**  
**Status:** ✅ **100% Complete**  
**Date:** 30 November 2025

---

## 📊 Overview

AutoML (Automatic Machine Learning) module به صورت خودکار بهترین hyperparameter‌ها را پیدا می‌کند تا بهترین performance را داشته باشید.

### ✅ چه چیزی بهینه می‌شود؟
- **Learning Rate** - سرعت یادگیری
- **Batch Size** - اندازه batch
- **Optimizer** - نوع optimizer (Adam, SGD, RMSprop, AdamW)
- **Weight Decay** - Regularization
- **Dropout Rate** - جلوگیری از overfitting
- **Hidden Dimensions** - اندازه لایه‌های مخفی (برای Text/Audio)
- **Number of Layers** - تعداد لایه‌ها
- **Learning Rate Scheduler** - تنظیم خودکار learning rate

### 🎯 مزایا:
- ✅ **خودکار** - نیازی به tuning دستی نیست
- ✅ **هوشمند** - از Optuna's Bayesian optimization استفاده می‌کند
- ✅ **سریع** - با pruning، trial‌های ضعیف را زودتر متوقف می‌کند
- ✅ **قابل تنظیم** - می‌توانید فضای جستجو را تنظیم کنید
- ✅ **Visualization** - نمودارهای تحلیلی

---

## 🚀 Quick Start

### 1. نصب Dependencies:

```bash
pip install optuna
pip install plotly  # برای visualization (اختیاری)
```

### 2. استفاده ساده:

```python
from engine import create_data_loaders, optimize_hyperparameters

# 1. لود کردن data
train_loader, val_loader, test_loader = create_data_loaders(
    'projects/my-project',
    {'batch_size': 32, 'num_workers': 2}
)

# 2. اجرای AutoML
results = optimize_hyperparameters(
    train_loader=train_loader,
    val_loader=val_loader,
    num_classes=10,
    modality='image',
    model_name='resnet18',
    n_trials=50,  # تعداد آزمایش‌ها
    device='cuda'
)

# 3. بهترین hyperparameter‌ها
print("Best parameters:")
for key, value in results['best_params'].items():
    print(f"  {key}: {value}")

print(f"Best accuracy: {results['best_value']:.4f}")
```

---

## 🎓 استفاده پیشرفته

### Class-based API:

```python
from engine import HyperparameterOptimizer

# ایجاد optimizer
optimizer = HyperparameterOptimizer(
    train_loader=train_loader,
    val_loader=val_loader,
    num_classes=10,
    modality='image',
    model_name='resnet18',
    device='cuda',
    n_trials=100,
    timeout=3600,  # 1 hour max
    direction='maximize',  # maximize accuracy
    pruning=True,  # enable smart pruning
    save_dir='my_studies'
)

# اجرای optimization
results = optimizer.optimize()

# دریافت بهترین parameters
best_params = optimizer.get_best_params()

# دریافت تاریخچه تمام trial‌ها
trials_df = optimizer.get_trials_dataframe()
print(trials_df.head())
```

---

## 📋 پارامترهای قابل تنظیم

### HyperparameterOptimizer Parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `train_loader` | DataLoader | Required | DataLoader آموزش |
| `val_loader` | DataLoader | Required | DataLoader validation |
| `num_classes` | int | Required | تعداد کلاس‌ها |
| `modality` | str | 'image' | نوع داده ('image', 'text', 'audio') |
| `model_name` | str | Required | نام مدل |
| `device` | str | 'cuda' | 'cuda' یا 'cpu' |
| `n_trials` | int | 50 | تعداد trial‌ها |
| `timeout` | int | None | حداکثر زمان (ثانیه) |
| `study_name` | str | Auto | نام study |
| `direction` | str | 'maximize' | 'maximize' یا 'minimize' |
| `pruning` | bool | True | فعال/غیرفعال کردن pruning |
| `save_dir` | str | 'optuna_studies' | مسیر ذخیره |
| `**fixed_params` | dict | {} | پارامترهای ثابت |

---

## 🔍 فضای جستجوی Hyperparameter‌ها

### همه Modality‌ها:

```python
# Learning Rate (log scale)
learning_rate: 1e-5 to 1e-2

# Batch Size (powers of 2)
batch_size: [8, 16, 32, 64, 128]

# Optimizer
optimizer: ['adam', 'adamw', 'sgd', 'rmsprop']

# Weight Decay (log scale)
weight_decay: 1e-6 to 1e-3

# Scheduler
scheduler: ['none', 'step', 'cosine', 'plateau']
```

### Text-specific:

```python
# Hidden Dimension
hidden_dim: [128, 256, 512]

# Number of Layers
num_layers: 1 to 3

# Bidirectional (for LSTM/GRU)
bidirectional: [True, False]

# Dropout
dropout: 0.1 to 0.5
```

### Audio-specific:

```python
# Dropout
dropout: 0.1 to 0.5

# (می‌توان n_mels و سایر پارامترهای صوتی را هم اضافه کرد)
```

---

## 💡 Examples

### Example 1: Image Classification با AutoML

```python
from engine import create_data_loaders, optimize_hyperparameters

# Load dataset
train_loader, val_loader, test_loader = create_data_loaders(
    'projects/cifar10',
    {'batch_size': 32, 'num_workers': 4}
)

# Run AutoML
# نکته: برای dataset بزرگ، epochs کمتر استفاده کنید
results = optimize_hyperparameters(
    train_loader=train_loader,
    val_loader=val_loader,
    num_classes=10,
    modality='image',
    model_name='resnet18',
    n_trials=100,  # 100 آزمایش
    device='cuda',
    epochs=10,  # فقط 10 epoch برای هر trial
    direction='maximize'
)

# استفاده از بهترین hyperparameter‌ها برای training کامل
best_params = results['best_params']

print(f"""
بهترین تنظیمات پیدا شده:
  Learning Rate: {best_params['learning_rate']}
  Batch Size: {best_params['batch_size']}
  Optimizer: {best_params['optimizer']}
  Weight Decay: {best_params['weight_decay']}
  
بهترین Accuracy: {results['best_value']:.2f}%
""")

# حالا با این hyperparameter‌ها training کامل انجام دهید
# (با epoch‌های بیشتر - مثلاً 100 epoch)
```

---

### Example 2: Text Classification با AutoML

```python
from engine import create_text_loaders, HyperparameterOptimizer

# Load text data
config = {'batch_size': 32, 'max_length': 128}
train_loader, val_loader, test_loader = create_text_loaders(
    'projects/sentiment-analysis',
    config
)

# ایجاد optimizer با تنظیمات خاص
optimizer = HyperparameterOptimizer(
    train_loader=train_loader,
    val_loader=val_loader,
    num_classes=2,  # positive/negative
    modality='text',
    model_name='lstm',
    device='cpu',  # text معمولاً CPU سریع‌تر است
    n_trials=50,
    direction='maximize',
    pruning=True,
    save_dir='sentiment_automl',
    # پارامترهای ثابت (بهینه نمی‌شوند)
    epochs=15,
    embed_dim=128
)

# اجرای optimization
results = optimizer.optimize()

# نمایش اهمیت هر hyperparameter
import optuna
fig = optuna.visualization.plot_param_importances(optimizer.study)
fig.show()

# یا ذخیره به HTML
fig.write_html('sentiment_automl/param_importance.html')
```

---

### Example 3: استفاده از Fixed Parameters

```python
# می‌خواهید برخی hyperparameter‌ها را ثابت نگه دارید:

results = optimize_hyperparameters(
    train_loader=train_loader,
    val_loader=val_loader,
    num_classes=10,
    modality='image',
    model_name='resnet18',
    n_trials=30,
    # پارامترهای ثابت:
    optimizer='adam',  # فقط Adam
    batch_size=32,     # batch size ثابت
    scheduler='cosine', # فقط cosine scheduler
    # پارامترهای زیر بهینه می‌شوند:
    # learning_rate, weight_decay
)
```

---

## 📊 Visualization و تحلیل

### 1. Optimization History:

```python
import optuna

# Load study
study = optuna.load_study(
    study_name='my_study',
    storage='sqlite:///optuna_studies/my_study.db'
)

# Plot optimization history
fig = optuna.visualization.plot_optimization_history(study)
fig.show()  # یا fig.write_html('history.html')
```

این نمودار نشان می‌دهد که accuracy در طول optimization چطور بهبود یافته است.

### 2. Parameter Importance:

```python
# کدام hyperparameter‌ها مهم‌ترند؟
fig = optuna.visualization.plot_param_importances(study)
fig.show()
```

این نمودار نشان می‌دهد کدام hyperparameter بیشترین تأثیر را دارد.

### 3. Parallel Coordinate Plot:

```python
# رابطه بین hyperparameter‌ها و performance
fig = optuna.visualization.plot_parallel_coordinate(study)
fig.show()
```

### 4. Contour Plot:

```python
# رابطه بین دو hyperparameter
fig = optuna.visualization.plot_contour(
    study,
    params=['learning_rate', 'batch_size']
)
fig.show()
```

---

## 🔧 تنظیمات پیشرفته

### 1. Pruning Strategy:

```python
# متوقف کردن خودکار trial‌های ضعیف

from optuna.pruners import MedianPruner, PercentilePruner

# استفاده از MedianPruner (default)
optimizer = HyperparameterOptimizer(
    ...,
    pruning=True  # trials ضعیف زودتر متوقف می‌شوند
)

# یا Percentile pruner (aggressive‌تر)
# این باید در کد اصلی تغییر کند
```

### 2. Multi-Objective Optimization:

```python
# بهینه‌سازی چند هدف (مثلاً accuracy و speed)
# این feature در Optuna موجود است اما در کد فعلی پیاده‌سازی نشده
# می‌تواند در نسخه‌های بعدی اضافه شود
```

### 3. Distributed Optimization:

```python
# اجرای موازی optimization روی چند machine
# نیاز به database مشترک دارد (مثلاً PostgreSQL)

import optuna

# Machine 1
study = optuna.create_study(
    study_name='shared_study',
    storage='postgresql://user:pass@host/db',
    load_if_exists=True
)

# Machine 2 (همزمان)
study = optuna.create_study(
    study_name='shared_study',  # same name
    storage='postgresql://user:pass@host/db',
    load_if_exists=True
)

# هر دو machine روی study مشترک کار می‌کنند
```

---

## 🎯 Best Practices

### 1. تعداد مناسب Trial‌ها:

```python
# Small dataset (< 1000 samples): 20-30 trials
# Medium dataset (1000-10000): 50-100 trials
# Large dataset (> 10000): 100-200 trials

# هر trial با epoch‌های کم (5-15) برای سرعت
```

### 2. Balance بین سرعت و دقت:

```python
# برای سرعت بیشتر:
results = optimize_hyperparameters(
    ...,
    n_trials=30,      # کم‌تر
    epochs=5,         # epoch کم
    pruning=True      # فعال
)

# برای دقت بیشتر:
results = optimize_hyperparameters(
    ...,
    n_trials=100,     # بیشتر
    epochs=15,        # epoch بیشتر
    pruning=False     # غیرفعال
)
```

### 3. استفاده از نتایج:

```python
# بعد از پیدا کردن بهترین hyperparameter‌ها:

# 1. ذخیره آنها
best_params = results['best_params']
with open('best_hyperparameters.json', 'w') as f:
    json.dump(best_params, f, indent=2)

# 2. Training کامل با epoch‌های بیشتر
# (در AutoML از epoch کم استفاده کردیم)

from engine import create_data_loaders, ModelBuilder, Trainer

# با hyperparameter‌های بهینه:
model = ModelBuilder.build_image_model(...)
optimizer = optim.Adam(
    model.parameters(),
    lr=best_params['learning_rate'],
    weight_decay=best_params['weight_decay']
)

trainer = Trainer(...)
history = trainer.fit(epochs=100)  # epoch زیاد
```

---

## 🐛 Troubleshooting

### مشکل: "Out of memory"

```python
# حل: batch size کوچک‌تر یا model کوچک‌تر
results = optimize_hyperparameters(
    ...,
    # محدود کردن batch size
    batch_size=16  # fixed, کوچک
)
```

### مشکل: "AutoML خیلی کند است"

```python
# حل‌ها:
# 1. تعداد trial کمتر
n_trials=20

# 2. epoch کمتر
epochs=3

# 3. pruning فعال
pruning=True

# 4. dataset کوچک‌تر برای validation
# استفاده از subset
```

### مشکل: "optuna not found"

```bash
pip install optuna
pip install plotly  # برای visualization
```

### مشکل: "نتایج stable نیستند"

```python
# set seed برای reproducibility
import torch
import random
import numpy as np

torch.manual_seed(42)
random.seed(42)
np.random.seed(42)

# بعد اجرای AutoML
```

---

## 📊 مثال واقعی: CIFAR-10

```python
"""
مثال کامل: پیدا کردن بهترین hyperparameter‌ها برای CIFAR-10
"""

from engine import create_data_loaders, optimize_hyperparameters
import torch

# 1. Load CIFAR-10
train_loader, val_loader, test_loader = create_data_loaders(
    'projects/cifar10',
    {'batch_size': 64, 'num_workers': 4}
)

# 2. Run AutoML (می‌تواند چند ساعت طول بکشد)
print("Starting hyperparameter optimization...")
print("This will take approximately 2-3 hours...")

results = optimize_hyperparameters(
    train_loader=train_loader,
    val_loader=val_loader,
    num_classes=10,
    modality='image',
    model_name='resnet18',
    n_trials=100,
    device='cuda',
    epochs=10,  # کم برای سرعت
    timeout=7200,  # 2 hours max
    save_dir='cifar10_automl'
)

# 3. نمایش نتایج
print("\n" + "="*70)
print("OPTIMIZATION RESULTS")
print("="*70)

best = results['best_params']
print(f"""
بهترین Hyperparameters:
  Learning Rate:    {best['learning_rate']:.6f}
  Batch Size:       {best['batch_size']}
  Optimizer:        {best['optimizer']}
  Weight Decay:     {best['weight_decay']:.6f}
  Scheduler:        {best['scheduler']}
  
Validation Accuracy: {results['best_value']:.2f}%
Total Trials:        {results['n_trials']}
""")

# 4. حالا training کامل با epoch زیاد
print("\nTraining final model with best hyperparameters...")

from engine import ModelBuilder, Trainer
import torch.nn as nn
import torch.optim as optim

model = ModelBuilder.build_image_model('resnet18', 10, pretrained=True)
device = torch.device('cuda')
criterion = nn.CrossEntropyLoss()

# استفاده از بهترین hyperparameters
optimizer = optim.Adam(
    model.parameters(),
    lr=best['learning_rate'],
    weight_decay=best['weight_decay']
)

trainer = Trainer(model, train_loader, val_loader, criterion, optimizer, device)
history = trainer.fit(epochs=100)  # training کامل

print(f"\nFinal Test Accuracy: {max(history['val_acc']):.2f}%")
```

---

## ✅ Testing

```bash
# تست AutoML
cd D:\Project\ModelCreator\backend
python test_automl.py

# این تست:
# 1. Image AutoML (5 trials)
# 2. Text AutoML (5 trials)
# 3. ذخیره نتایج و visualizations
```

---

## 📚 منابع بیشتر

- **Optuna Documentation:** https://optuna.readthedocs.io/
- **Optuna Tutorials:** https://github.com/optuna/optuna-examples
- **Paper:** "Optuna: A Next-generation Hyperparameter Optimization Framework"

---

## 🎉 Conclusion

**AutoML هوشمند برای پیدا کردن بهترین hyperparameter‌ها!**

### مزایا:
- ✅ خودکار و آسان
- ✅ Bayesian optimization (هوشمند)
- ✅ Pruning (سریع)
- ✅ Visualization (قابل فهم)
- ✅ Production-ready

### استفاده:
```python
from engine import optimize_hyperparameters

results = optimize_hyperparameters(
    train_loader, val_loader, num_classes,
    modality='image', n_trials=50
)
```

**بهترین hyperparameter‌ها را بدون دردسر پیدا کنید! 🤖✨**

---

*Documentation Created: 30 November 2025*  
*ModelCreator v1.3.0 - AutoML Support*

