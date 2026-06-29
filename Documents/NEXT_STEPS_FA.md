# 🎯 مراحل بعدی پروژه ModelCreator

**تاریخ:** 30 نوامبر 2025  
**وضعیت Phase 1:** ✅ **تکمیل شده** (Training Engine آماده)

---

## 📊 خلاصه وضعیت فعلی

### ✅ تکمیل شده (100%)
- ✅ Training Engine (Data Loader, Model Builder, Trainer, Callbacks)
- ✅ Export Module (PyTorch, ONNX, TorchScript)
- ✅ Inference Module (Single + Batch prediction)
- ✅ API Integration (Training, Export, Inference endpoints)
- ✅ Frontend UI (کامل با HTTP Polling)
- ✅ Documentation (ENGINE_READY_FA.md)

### 🔄 نیاز به بررسی و تست بیشتر
- 🔄 Export API - تست با مدل‌های واقعی
- 🔄 Inference API - تست با تصاویر مختلف
- 🔄 دیتاست‌های بزرگ‌تر (بیش از 30 تصویر)
- 🔄 GPU Training - تست با CUDA
- 🔄 Model Checkpointing - بازیابی از خطا

### ❌ هنوز پیاده‌سازی نشده
- ❌ TensorBoard Integration
- ❌ AutoML / Hyperparameter Optimization
- ❌ Model Comparison Dashboard
- ❌ Cloud Training
- ❌ More Modalities (Audio, Video, Text)

---

## 🚀 اولویت‌های فوری (این هفته)

### 1️⃣ تست و پولیش Phase 1 ⭐⭐⭐

#### 1.1 تست Export
```bash
cd D:\Project\ModelCreator\backend
.\venv\Scripts\activate
python -c "
from export import ModelExporter
from engine import ModelBuilder
import torch

# Create model
model = ModelBuilder.build_image_model('resnet18', 10, pretrained=False)

# Export to all formats
exported = ModelExporter.export_all_formats(
    model,
    'test_exports',
    'test_model'
)

print('Exported files:', exported)
"
```

**تسک‌ها:**
- [ ] تست export PyTorch format
- [ ] تست export ONNX format
- [ ] تست export TorchScript format
- [ ] تست download endpoint
- [ ] تست با مدل آموزش‌دیده واقعی

---

#### 1.2 تست Inference
```bash
# تست با تصویر واقعی
curl -X POST "http://127.0.0.1:8181/api/inference/predict/test-cat-dog" \
     -F "file=@path/to/test_image.jpg"
```

**تسک‌ها:**
- [ ] تست single prediction با تصاویر مختلف
- [ ] تست batch prediction
- [ ] بررسی accuracy
- [ ] بررسی inference time
- [ ] تست با ONNX exported model

---

#### 1.3 تست با دیتاست بزرگ

**دیتاست‌های پیشنهادی:**
- **CIFAR-10** (60,000 تصویر، 10 کلاس)
- **MNIST** (70,000 تصویر)
- **Fashion-MNIST** (70,000 تصویر)

**تسک‌ها:**
- [ ] دانلود و import CIFAR-10
- [ ] تست training با epoch های بیشتر (50-100)
- [ ] بررسی metrics (accuracy, loss)
- [ ] مقایسه با baseline results
- [ ] بررسی early stopping
- [ ] بررسی model checkpointing

**کد دانلود CIFAR-10:**
```python
# backend/download_cifar10.py
import torchvision
import torchvision.transforms as transforms
from pathlib import Path
import shutil

def download_cifar10():
    # Download
    dataset = torchvision.datasets.CIFAR10(
        root='./data/cifar10_raw',
        train=True,
        download=True
    )
    
    # Create project structure
    project_dir = Path('../projects/cifar10-project')
    data_dir = project_dir / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Class names
    classes = ['airplane', 'automobile', 'bird', 'cat', 'deer',
               'dog', 'frog', 'horse', 'ship', 'truck']
    
    # Create class folders
    for cls in classes:
        (data_dir / cls).mkdir(exist_ok=True)
    
    # Save images
    from PIL import Image
    for idx, (img, label) in enumerate(dataset):
        class_name = classes[label]
        img.save(data_dir / class_name / f'{class_name}_{idx:05d}.png')
        
        if idx % 1000 == 0:
            print(f'Processed {idx} images...')
    
    # Create labels.json
    import json
    labels = {name: idx for idx, name in enumerate(classes)}
    with open(project_dir / 'labels.json', 'w') as f:
        json.dump(labels, f, indent=2)
    
    print(f'✅ CIFAR-10 imported to {project_dir}')

if __name__ == '__main__':
    download_cifar10()
```

---

### 2️⃣ بهبودهای فوری ⭐⭐

#### 2.1 TensorBoard Integration

**چرا مهم است:**
- Visualization بهتر metrics
- Real-time monitoring پیشرفته
- مقایسه آسان‌تر runs مختلف

**پیاده‌سازی:**
```python
# backend/engine/callbacks.py - اضافه کنید

from torch.utils.tensorboard import SummaryWriter

class TensorBoardCallback(Callback):
    """TensorBoard logging callback"""
    
    def __init__(self, log_dir: str, project_id: str):
        self.writer = SummaryWriter(log_dir=log_dir)
        self.project_id = project_id
    
    def on_epoch_end(self, epoch: int, metrics: Dict[str, float]):
        # Log metrics
        self.writer.add_scalar('Loss/train', metrics['train_loss'], epoch)
        self.writer.add_scalar('Loss/val', metrics['val_loss'], epoch)
        self.writer.add_scalar('Accuracy/train', metrics['train_acc'], epoch)
        self.writer.add_scalar('Accuracy/val', metrics['val_acc'], epoch)
        
        # Log learning rate
        if 'learning_rate' in metrics:
            self.writer.add_scalar('LearningRate', metrics['learning_rate'], epoch)
    
    def on_training_end(self):
        self.writer.close()
```

**استفاده:**
```python
# در training.py
from engine.callbacks import TensorBoardCallback

callbacks = [
    TensorBoardCallback(
        log_dir=str(project_dir / 'tensorboard'),
        project_id=project_id
    ),
    ProgressCallback(...),
    EarlyStopping(...),
]
```

**مشاهده:**
```bash
cd D:\Project\ModelCreator\projects\{project_id}
tensorboard --logdir tensorboard
# باز کنید: http://localhost:6006
```

**تسک‌ها:**
- [ ] اضافه کردن TensorBoardCallback
- [ ] لاگ کردن metrics
- [ ] لاگ کردن model graph
- [ ] لاگ کردن sample images
- [ ] تست و بررسی در browser

---

#### 2.2 بهبود Error Handling

**مشکلات فعلی:**
- خطاهای GPU/CUDA به خوبی handle نمی‌شوند
- Out of Memory errors ناگهانی هستند
- Data loading errors گاهی واضح نیستند

**بهبودهای پیشنهادی:**

```python
# backend/engine/trainer.py - بهبود error handling

class Trainer:
    def fit(self, epochs: int) -> Dict[str, List[float]]:
        try:
            # Existing training code
            ...
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                # OOM error
                logger.error("GPU Out of Memory!")
                logger.info("Suggestions:")
                logger.info("  1. Reduce batch_size")
                logger.info("  2. Use smaller model")
                logger.info("  3. Enable gradient accumulation")
                logger.info("  4. Use CPU instead")
                
                # Update active_trainings
                if hasattr(self, 'project_id'):
                    self.active_trainings[self.project_id].update({
                        'status': 'failed',
                        'error': 'Out of Memory',
                        'suggestions': [
                            'Reduce batch size',
                            'Use smaller model',
                            'Try CPU training'
                        ]
                    })
                raise
            elif "CUDA" in str(e):
                # CUDA error
                logger.error(f"CUDA Error: {e}")
                logger.info("Falling back to CPU...")
                
                # Retry on CPU
                self.device = torch.device('cpu')
                self.model = self.model.to(self.device)
                return self.fit(epochs)
            else:
                raise
        except FileNotFoundError as e:
            logger.error(f"Data file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise
```

**تسک‌ها:**
- [ ] بهبود CUDA error handling
- [ ] بهبود OOM error handling
- [ ] بهبود data loading errors
- [ ] اضافه کردن retry logic
- [ ] بهبود error messages در frontend

---

#### 2.3 Performance Optimization

**مسائل بالقوه:**
- Data loading bottleneck
- GPU underutilization
- Memory leaks
- Slow validation

**بهینه‌سازی‌های پیشنهادی:**

```python
# 1. استفاده از num_workers مناسب
train_loader = DataLoader(
    train_dataset,
    batch_size=batch_size,
    shuffle=True,
    num_workers=4,  # تنظیم بهینه
    pin_memory=True,  # برای GPU
    prefetch_factor=2  # پیش‌بارگذاری
)

# 2. Mixed Precision Training
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for data, target in train_loader:
    optimizer.zero_grad()
    
    with autocast():  # Mixed precision
        output = model(data)
        loss = criterion(output, target)
    
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()

# 3. Gradient Accumulation (برای batch size بزرگ‌تر)
accumulation_steps = 4

for i, (data, target) in enumerate(train_loader):
    output = model(data)
    loss = criterion(output, target) / accumulation_steps
    loss.backward()
    
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

**تسک‌ها:**
- [ ] پروفایل کردن training loop
- [ ] بهینه‌سازی num_workers
- [ ] اضافه کردن gradient accumulation option
- [ ] بهینه‌سازی validation loop
- [ ] کاهش memory usage

---

### 3️⃣ Documentation و Testing ⭐

#### 3.1 Unit Tests

```python
# backend/tests/test_engine.py
import pytest
import torch
from engine import create_data_loaders, ModelBuilder, Trainer

def test_data_loader():
    """Test data loader creation"""
    config = {'batch_size': 4, 'num_workers': 0}
    train_loader, val_loader, test_loader = create_data_loaders(
        'projects/test-cat-dog',
        config
    )
    
    assert len(train_loader) > 0
    assert len(val_loader) > 0
    assert len(test_loader) > 0
    
    # Test batch
    images, labels = next(iter(train_loader))
    assert images.shape[0] <= 4
    assert labels.shape[0] <= 4

def test_model_builder():
    """Test model creation"""
    model = ModelBuilder.build_image_model('resnet18', 10, pretrained=False)
    assert model is not None
    
    # Test forward pass
    x = torch.randn(2, 3, 224, 224)
    y = model(x)
    assert y.shape == (2, 10)

def test_trainer():
    """Test trainer"""
    # Mock test
    pass
```

**تسک‌ها:**
- [ ] نوشتن unit tests برای data_loader
- [ ] نوشتن unit tests برای model_builder
- [ ] نوشتن unit tests برای trainer
- [ ] نوشتن unit tests برای callbacks
- [ ] اجرا و بررسی coverage

---

#### 3.2 Integration Tests

```python
# backend/tests/test_integration.py
def test_full_training_workflow():
    """Test complete training workflow"""
    # 1. Create data loaders
    # 2. Build model
    # 3. Train for 2 epochs
    # 4. Export model
    # 5. Load and inference
    # 6. Verify results
    pass
```

---

#### 3.3 API Documentation

**Swagger/OpenAPI:**
```python
# backend/main.py - اضافه کنید

from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="ModelCreator API",
        version="1.0.0",
        description="AI Model Builder Backend API",
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

مشاهده: `http://127.0.0.1:8181/docs`

---

## 🌟 ویژگی‌های بعدی (Phase 2)

### 1️⃣ AutoML / Hyperparameter Optimization

**کتابخانه:** Optuna

```python
# backend/automl/optimizer.py
import optuna

class AutoMLOptimizer:
    def __init__(self, project_dir, n_trials=20):
        self.project_dir = project_dir
        self.n_trials = n_trials
    
    def objective(self, trial):
        # Sample hyperparameters
        lr = trial.suggest_loguniform('lr', 1e-5, 1e-2)
        batch_size = trial.suggest_categorical('batch_size', [16, 32, 64])
        optimizer_name = trial.suggest_categorical('optimizer', ['adam', 'sgd'])
        
        # Train model
        config = {
            'learning_rate': lr,
            'batch_size': batch_size,
            'optimizer': optimizer_name,
            'epochs': 10  # Short training
        }
        
        # ... training code ...
        
        return val_loss
    
    def optimize(self):
        study = optuna.create_study(direction='minimize')
        study.optimize(self.objective, n_trials=self.n_trials)
        
        return study.best_params
```

---

### 2️⃣ Model Comparison Dashboard

**Backend:**
```python
# backend/api/routes/comparison.py

@router.get("/compare")
async def compare_models(project_ids: List[str]):
    """Compare multiple trained models"""
    results = []
    
    for project_id in project_ids:
        # Load training history
        history_file = settings.PROJECTS_DIR / project_id / "history.json"
        with open(history_file) as f:
            history = json.load(f)
        
        results.append({
            'project_id': project_id,
            'best_val_acc': max(history['val_acc']),
            'best_val_loss': min(history['val_loss']),
            'history': history
        })
    
    return results
```

**Frontend:**
- صفحه ComparisonPage.xaml
- نمایش chart های مقایسه‌ای
- جدول metrics

---

### 3️⃣ More Modalities

#### Text Classification
```python
# backend/models/text/text_models.py
from transformers import BertModel

class BertClassifier(nn.Module):
    def __init__(self, num_classes=2):
        super().__init__()
        self.bert = BertModel.from_pretrained('bert-base-uncased')
        self.classifier = nn.Linear(768, num_classes)
    
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids, attention_mask=attention_mask)
        pooled = outputs.pooler_output
        return self.classifier(pooled)
```

#### Audio Classification
```python
# backend/models/audio/audio_models.py
import torchaudio

class AudioCNN(nn.Module):
    # ... implementation
    pass
```

---

## 📅 تایم‌لاین پیشنهادی

### این هفته (1-7 دسامبر)
- [x] بررسی کدبیس ✅
- [ ] تست Export API
- [ ] تست Inference API
- [ ] TensorBoard Integration
- [ ] بهبود Error Handling

### هفته آینده (8-14 دسامبر)
- [ ] تست با CIFAR-10
- [ ] Performance Optimization
- [ ] Unit Tests
- [ ] AutoML شروع

### هفته سوم (15-21 دسامبر)
- [ ] AutoML تکمیل
- [ ] Model Comparison
- [ ] Text Classification

### هفته چهارم (22-28 دسامبر)
- [ ] Audio Classification
- [ ] Cloud Training شروع
- [ ] Documentation کامل

---

## 🎯 Quick Wins (می‌توانید همین الان انجام دهید)

### 1. اضافه کردن Model Info به Results

```python
# backend/api/routes/training.py - در get_training_results

# اضافه کنید:
'model_info': {
    'architecture': 'resnet18',
    'parameters': 11_689_512,
    'size_mb': 44.59
}
```

### 2. بهبود Progress Messages

```python
# backend/engine/callbacks.py - در ProgressCallback

# پیام‌های فارسی بهتر:
messages = [
    f"🏃 عصر {epoch}: در حال آموزش...",
    f"📊 عصر {epoch}: Loss={val_loss:.4f}, Accuracy={val_acc*100:.1f}%",
    f"💾 بهترین مدل ذخیره شد! (Acc: {val_acc*100:.1f}%)",
    f"⚡ سرعت: {epoch_time:.2f} ثانیه/epoch",
]
```

### 3. اضافه کردن Keyboard Shortcuts به Frontend

```xml
<!-- frontend/MainWindow.xaml -->
<Window.InputBindings>
    <KeyBinding Key="N" Modifiers="Ctrl" Command="{Binding NewProjectCommand}"/>
    <KeyBinding Key="O" Modifiers="Ctrl" Command="{Binding OpenProjectCommand}"/>
    <KeyBinding Key="S" Modifiers="Ctrl" Command="{Binding SaveCommand}"/>
</Window.InputBindings>
```

---

## 📞 سوالات متداول

### Q: از کجا شروع کنم؟
**A:** شروع کنید با تست Export و Inference API. سپس TensorBoard را اضافه کنید.

### Q: آیا نیاز به تغییر frontend است؟
**A:** نه، frontend کامل است. فقط ممکن است بخواهید ویژگی‌های جدید (مثل AutoML page) اضافه کنید.

### Q: چطور می‌توانم performance را بهبود دهم؟
**A:** استفاده از Mixed Precision, بهینه‌سازی num_workers, و Gradient Accumulation.

### Q: کدام دیتاست برای تست بهتر است؟
**A:** CIFAR-10 یا Fashion-MNIST برای تست کامل عالی هستند.

---

## ✅ Checklist برای هفته جاری

```markdown
### Export & Inference
- [ ] تست export PyTorch
- [ ] تست export ONNX
- [ ] تست single inference
- [ ] تست batch inference

### Improvements
- [ ] TensorBoard integration
- [ ] بهبود error messages
- [ ] بهینه‌سازی data loading

### Testing
- [ ] تست با CIFAR-10
- [ ] تست GPU training
- [ ] تست early stopping

### Documentation
- [ ] API documentation (Swagger)
- [ ] Code comments
- [ ] User guide updates
```

---

**آماده برای شروع؟** 🚀

من اینجا هستم تا در هر مرحله کمک کنم!

