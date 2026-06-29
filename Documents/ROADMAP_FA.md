# 🎯 نقشه راه تکمیل پروژه ModelCreator

## 📋 وضعیت فعلی (✅ تکمیل شده)

### Frontend (WPF - .NET 8)
- ✅ صفحه اصلی (HomePage)
- ✅ مدیریت پروژه‌ها (ProjectsPage)
- ✅ ایجاد پروژه (CreateProjectPage)
- ✅ وارد کردن داده (DataImportPage) + لیبل‌گذاری
- ✅ انتخاب مدل (ModelSelectionPage)
- ✅ تنظیمات آموزش (TrainingConfigPage)
- ✅ داشبورد آموزش (TrainingDashboardPage) - HTTP Polling
- ✅ نتایج (ResultsPage)
- ✅ Inference Playground (InferencePlaygroundPage)
- ✅ UI فارسی کامل
- ✅ Value Converters
- ✅ Error Handling جامع

### Backend (FastAPI - Python)
- ✅ Project Management API
- ✅ Data Management API
- ✅ System Info API (GPU detection)
- ✅ Training API (Mock)
- ✅ Export API
- ✅ WebSocket endpoint (ولی غیرفعال)
- ✅ CORS configuration
- ✅ Logging
- ✅ File structure

### Documentation
- ✅ PERSIAN_README.md
- ✅ QUICK_START_FA.md
- ✅ TRAINING_GUIDE_FA.md
- ✅ GPU_TROUBLESHOOTING_FA.md
- ✅ WEBSOCKET_ERROR_FA.md
- ✅ HTTP_POLLING_FA.md
- ✅ COMMON_ERRORS_FA.md
- ✅ CHANGELOG_FA.md

---

# 🚀 Phase 1: آموزش واقعی (جایگزین Mock)

## 1.1 Core Training Engine ⭐ PRIORITY
**مدت تخمینی: 2-3 روز**

### فایل‌های مورد نیاز:
```
backend/
├── engine/
│   ├── __init__.py
│   ├── trainer.py           # کلاس اصلی Trainer
│   ├── data_loader.py       # بارگذاری داده
│   ├── model_builder.py     # ساخت مدل‌ها
│   ├── metrics.py           # محاسبه metrics
│   └── callbacks.py         # Early stopping, checkpointing
```

### Tasks:
- [ ] **1.1.1** پیاده‌سازی `DataLoader` برای هر modality
  - [ ] Image (torchvision.datasets)
  - [ ] Text (tokenization, vocab)
  - [ ] Audio (librosa, torchaudio)
  - [ ] Tabular (pandas → tensor)
  - [ ] Video (frame extraction)
  - [ ] Time Series (windowing)

- [ ] **1.1.2** پیاده‌سازی `ModelBuilder`
  - [ ] Image: ResNet, EfficientNet, ViT
  - [ ] Text: BERT, GPT-2, LSTM
  - [ ] Audio: Wav2Vec2, AST
  - [ ] Tabular: MLP, TabNet
  - [ ] Video: 3D CNN, TimeSformer
  - [ ] Time Series: LSTM, Transformer

- [ ] **1.1.3** پیاده‌سازی `Trainer`
  - [ ] Training loop واقعی
  - [ ] Validation loop
  - [ ] GPU/CPU automatic selection
  - [ ] Mixed precision training
  - [ ] Gradient accumulation
  - [ ] Learning rate scheduling

- [ ] **1.1.4** پیاده‌سازی `Callbacks`
  - [ ] Early Stopping
  - [ ] Model Checkpointing
  - [ ] TensorBoard logging
  - [ ] Progress reporting (برای frontend)

- [ ] **1.1.5** تغییر `training.py`
  - [ ] حذف `run_mock_training()`
  - [ ] جایگزینی با `engine.trainer.Trainer`
  - [ ] Threading یا multiprocessing برای training
  - [ ] Real-time metric updates

### کد نمونه (Trainer اصلی):
```python
# backend/engine/trainer.py
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

class Trainer:
    def __init__(self, model, train_loader, val_loader, optimizer, 
                 criterion, device, callbacks=None):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device
        self.callbacks = callbacks or []
        
    def train_epoch(self, epoch):
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        pbar = tqdm(self.train_loader, desc=f'Epoch {epoch}')
        for batch_idx, (data, target) in enumerate(pbar):
            data, target = data.to(self.device), target.to(self.device)
            
            self.optimizer.zero_grad()
            output = self.model(data)
            loss = self.criterion(output, target)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            pred = output.argmax(dim=1)
            correct += pred.eq(target).sum().item()
            total += target.size(0)
            
            # Update progress bar
            pbar.set_postfix({
                'loss': total_loss / (batch_idx + 1),
                'acc': 100. * correct / total
            })
            
        return total_loss / len(self.train_loader), correct / total
    
    def validate(self):
        self.model.eval()
        val_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in self.val_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                val_loss += self.criterion(output, target).item()
                pred = output.argmax(dim=1)
                correct += pred.eq(target).sum().item()
                total += target.size(0)
        
        return val_loss / len(self.val_loader), correct / total
    
    def fit(self, epochs, project_id, active_trainings):
        for epoch in range(1, epochs + 1):
            # Check if stopped
            if active_trainings[project_id]["status"] == "stopping":
                break
                
            train_loss, train_acc = self.train_epoch(epoch)
            val_loss, val_acc = self.validate()
            
            # Update active_trainings for frontend
            active_trainings[project_id].update({
                "current_epoch": epoch,
                "train_loss": round(train_loss, 4),
                "train_acc": round(train_acc, 4),
                "val_loss": round(val_loss, 4),
                "val_acc": round(val_acc, 4),
                "message": f"Epoch {epoch}/{epochs} completed"
            })
            
            # Run callbacks
            for callback in self.callbacks:
                callback(epoch, train_loss, val_loss)
```

---

## 1.2 Data Preprocessing ⭐ PRIORITY
**مدت تخمینی: 1-2 روز**

### Tasks:
- [ ] **1.2.1** Image preprocessing
  - [ ] Resize, normalize, augmentation
  - [ ] Handle different formats (JPEG, PNG, etc.)

- [ ] **1.2.2** Text preprocessing
  - [ ] Tokenization
  - [ ] Vocabulary building
  - [ ] Padding/truncation

- [ ] **1.2.3** Audio preprocessing
  - [ ] Resampling
  - [ ] Spectrogram conversion
  - [ ] Feature extraction (MFCC, etc.)

- [ ] **1.2.4** Data validation
  - [ ] Check file integrity
  - [ ] Verify labels
  - [ ] Handle missing data

---

## 1.3 Model Zoo 🏗️
**مدت تخمینی: 3-4 روز**

### Tasks:
- [ ] **1.3.1** Image Models
  - [ ] ResNet-18, 34, 50
  - [ ] EfficientNet-B0 to B7
  - [ ] Vision Transformer (ViT)
  - [ ] MobileNet v2/v3

- [ ] **1.3.2** Text Models
  - [ ] BERT (base, large)
  - [ ] GPT-2
  - [ ] LSTM/GRU variants
  - [ ] Transformer encoder

- [ ] **1.3.3** Audio Models
  - [ ] Wav2Vec2
  - [ ] Audio Spectrogram Transformer
  - [ ] CNN-based audio classifier

- [ ] **1.3.4** Tabular Models
  - [ ] Multi-layer Perceptron
  - [ ] TabNet
  - [ ] Wide & Deep

- [ ] **1.3.5** Video Models
  - [ ] 3D CNN (C3D)
  - [ ] Two-stream CNN
  - [ ] TimeSformer

- [ ] **1.3.6** Time Series Models
  - [ ] LSTM/GRU
  - [ ] Temporal Convolutional Network
  - [ ] Transformer for time series

---

## 1.4 Export & Deployment 📦
**مدت تخمینی: 1 روز**

### Tasks:
- [ ] **1.4.1** Export formats
  - [ ] PyTorch (.pt, .pth)
  - [ ] ONNX (.onnx)
  - [ ] TorchScript (.pt)
  - [ ] TensorFlow Lite (.tflite)

- [ ] **1.4.2** Model optimization
  - [ ] Quantization
  - [ ] Pruning
  - [ ] Knowledge distillation

- [ ] **1.4.3** Inference optimization
  - [ ] Batch inference
  - [ ] TensorRT integration
  - [ ] ONNX Runtime

---

# 🌟 Phase 2: ویژگی‌های پیشرفته

## 2.1 AutoML & Hyperparameter Tuning 🤖
**مدت تخمینی: 4-5 روز**

### فایل‌های مورد نیاز:
```
backend/
├── automl/
│   ├── __init__.py
│   ├── hpo.py              # Hyperparameter Optimization
│   ├── search_space.py     # تعریف فضای جستجو
│   ├── nas.py              # Neural Architecture Search
│   └── ensemble.py         # Ensemble methods
```

### Tasks:
- [ ] **2.1.1** Grid Search
  - [ ] تمام ترکیبات hyperparameters
  - [ ] Parallel execution

- [ ] **2.1.2** Random Search
  - [ ] نمونه‌برداری تصادفی
  - [ ] Early stopping for bad trials

- [ ] **2.1.3** Bayesian Optimization
  - [ ] استفاده از Optuna یا Hyperopt
  - [ ] Sequential model-based optimization

- [ ] **2.1.4** Neural Architecture Search
  - [ ] DARTS-based NAS
  - [ ] Architecture evolution

- [ ] **2.1.5** Frontend Integration
  - [ ] AutoML Configuration Page
  - [ ] Trial monitoring dashboard
  - [ ] Best model selection

### کد نمونه:
```python
# backend/automl/hpo.py
import optuna

class HyperparameterOptimizer:
    def __init__(self, train_fn, search_space, n_trials=20):
        self.train_fn = train_fn
        self.search_space = search_space
        self.n_trials = n_trials
        
    def objective(self, trial):
        # Sample hyperparameters
        lr = trial.suggest_loguniform('lr', 1e-5, 1e-1)
        batch_size = trial.suggest_categorical('batch_size', [16, 32, 64])
        dropout = trial.suggest_uniform('dropout', 0.1, 0.5)
        
        # Train model with these hyperparameters
        val_loss = self.train_fn(lr, batch_size, dropout)
        
        return val_loss
    
    def optimize(self):
        study = optuna.create_study(direction='minimize')
        study.optimize(self.objective, n_trials=self.n_trials)
        
        return study.best_params, study.best_value
```

---

## 2.2 Cloud Training ☁️
**مدت تخمینی: 5-7 روز**

### Tasks:
- [ ] **2.2.1** AWS Integration
  - [ ] SageMaker training jobs
  - [ ] S3 data storage
  - [ ] EC2 instance management

- [ ] **2.2.2** Azure Integration
  - [ ] Azure ML training
  - [ ] Blob storage
  - [ ] VM management

- [ ] **2.2.3** GCP Integration
  - [ ] AI Platform training
  - [ ] Cloud Storage
  - [ ] Compute Engine

- [ ] **2.2.4** Cost Estimation
  - [ ] Training cost calculator
  - [ ] Instance type recommendations

- [ ] **2.2.5** Frontend
  - [ ] Cloud provider selection
  - [ ] Instance type picker
  - [ ] Cost dashboard

---

## 2.3 Model Comparison Dashboard 📊
**مدت تخمینی: 3-4 روز**

### Tasks:
- [ ] **2.3.1** Backend
  - [ ] Store multiple training runs
  - [ ] Comparison API endpoint
  - [ ] Leaderboard generation

- [ ] **2.3.2** Frontend
  - [ ] ComparisonPage.xaml
  - [ ] Side-by-side metrics
  - [ ] Chart overlays
  - [ ] Export comparison report

- [ ] **2.3.3** Features
  - [ ] Filter by date, modality
  - [ ] Sort by metric
  - [ ] Heatmap visualization
  - [ ] Statistical tests (t-test, etc.)

---

## 2.4 Ensemble Methods 🎭
**مدت تخمینی: 2-3 روز**

### Tasks:
- [ ] **2.4.1** Voting Ensemble
  - [ ] Hard voting
  - [ ] Soft voting (probability averaging)

- [ ] **2.4.2** Stacking
  - [ ] Meta-learner training
  - [ ] Cross-validation for stacking

- [ ] **2.4.3** Boosting
  - [ ] AdaBoost
  - [ ] Gradient Boosting

- [ ] **2.4.4** Bagging
  - [ ] Bootstrap aggregating
  - [ ] Random subspace method

---

## 2.5 Real-time Inference API 🚀
**مدت تخمینی: 2-3 روز**

### Tasks:
- [ ] **2.5.1** REST API for inference
  - [ ] `/predict` endpoint
  - [ ] Batch prediction
  - [ ] Async inference

- [ ] **2.5.2** gRPC API
  - [ ] High-performance inference
  - [ ] Streaming predictions

- [ ] **2.5.3** Model serving
  - [ ] TorchServe integration
  - [ ] TensorFlow Serving
  - [ ] ONNX Runtime server

- [ ] **2.5.4** API Documentation
  - [ ] OpenAPI/Swagger
  - [ ] Code examples
  - [ ] Rate limiting

---

## 2.6 Collaboration Features 👥
**مدت تخمینی: 5-7 روز**

### Tasks:
- [ ] **2.6.1** User Management
  - [ ] Authentication (JWT)
  - [ ] Authorization (roles)
  - [ ] User profiles

- [ ] **2.6.2** Project Sharing
  - [ ] Share by link
  - [ ] Access control (view, edit)
  - [ ] Team workspaces

- [ ] **2.6.3** Comments & Annotations
  - [ ] Comment on training runs
  - [ ] Annotate charts
  - [ ] Discussion threads

- [ ] **2.6.4** Version Control
  - [ ] Model versioning
  - [ ] Dataset versioning
  - [ ] Experiment tracking

---

## 2.7 Mobile App 📱
**مدت تخمینی: 14-21 روز**

### Technology Stack:
- **Flutter** (Android + iOS)
- **React Native** (alternative)

### Tasks:
- [ ] **2.7.1** Core Features
  - [ ] Project list
  - [ ] Training monitoring
  - [ ] Model inference (on-device)

- [ ] **2.7.2** Mobile-specific
  - [ ] Camera integration
  - [ ] Microphone for audio
  - [ ] On-device ML (TFLite, Core ML)

- [ ] **2.7.3** Push Notifications
  - [ ] Training completed
  - [ ] Training failed
  - [ ] Milestones reached

---

# 📊 Phase 3: بهبود UI/UX

## 3.1 Dashboard Improvements
**مدت تخمینی: 2-3 روز**

### Tasks:
- [ ] **3.1.1** Homepage Dashboard
  - [ ] Recent projects
  - [ ] Quick stats
  - [ ] Recent activity feed

- [ ] **3.1.2** Better Charts
  - [ ] Interactive charts (LiveCharts)
  - [ ] Zoom, pan
  - [ ] Export to image

- [ ] **3.1.3** Dark Mode
  - [ ] Theme switcher
  - [ ] Save preference

---

## 3.2 Advanced Features
**مدت تخمینی: 3-4 روز**

### Tasks:
- [ ] **3.2.1** Data Augmentation Preview
  - [ ] Show augmented samples
  - [ ] Before/after comparison

- [ ] **3.2.2** Model Architecture Visualization
  - [ ] Layer-by-layer view
  - [ ] Parameter count
  - [ ] FLOPs calculation

- [ ] **3.2.3** Error Analysis
  - [ ] Confusion matrix
  - [ ] Per-class metrics
  - [ ] Misclassified samples viewer

---

# 🧪 Phase 4: Testing & Quality

## 4.1 Unit Tests
**مدت تخمینی: 3-4 روز**

### Tasks:
- [ ] **4.1.1** Backend Tests
  - [ ] pytest for all API endpoints
  - [ ] Data loader tests
  - [ ] Model builder tests
  - [ ] Trainer tests

- [ ] **4.1.2** Frontend Tests
  - [ ] xUnit for ViewModels
  - [ ] UI automation tests

---

## 4.2 Integration Tests
**مدت تخمینی: 2 روز**

### Tasks:
- [ ] **4.2.1** End-to-end tests
  - [ ] Complete training workflow
  - [ ] Export workflow
  - [ ] Inference workflow

---

## 4.3 Performance Testing
**مدت تخمینی: 2 روز**

### Tasks:
- [ ] **4.3.1** Load testing
  - [ ] Concurrent training jobs
  - [ ] API response times

- [ ] **4.3.2** Memory profiling
  - [ ] Memory leaks
  - [ ] GPU memory optimization

---

# 📦 Phase 5: Deployment & Distribution

## 5.1 Packaging
**مدت تخمینی: 2-3 روز**

### Tasks:
- [ ] **5.1.1** Backend
  - [ ] Docker container
  - [ ] Kubernetes deployment
  - [ ] Helm chart

- [ ] **5.1.2** Frontend
  - [ ] Windows installer (.msi)
  - [ ] Portable version
  - [ ] Auto-updater

---

## 5.2 CI/CD
**مدت تخمینی: 2 روز**

### Tasks:
- [ ] **5.2.1** GitHub Actions
  - [ ] Build pipeline
  - [ ] Test pipeline
  - [ ] Release pipeline

- [ ] **5.2.2** Docker Hub
  - [ ] Automated builds
  - [ ] Multi-arch images

---

# 📅 تخمین زمانی کلی

| Phase | مدت زمان | اولویت |
|-------|---------|--------|
| **Phase 1: آموزش واقعی** | 7-10 روز | ⭐⭐⭐ CRITICAL |
| **Phase 2: ویژگی‌های پیشرفته** | 25-35 روز | ⭐⭐ HIGH |
| **Phase 3: UI/UX** | 5-7 روز | ⭐⭐ HIGH |
| **Phase 4: Testing** | 7-8 روز | ⭐ MEDIUM |
| **Phase 5: Deployment** | 4-5 روز | ⭐ MEDIUM |
| **TOTAL** | **48-65 روز** | |

---

# 🎯 Milestone Plan

## Milestone 1: MVP با آموزش واقعی (2 هفته)
- ✅ Image training کامل
- ✅ Text training کامل
- ✅ Export واقعی
- ✅ Inference واقعی

## Milestone 2: Multi-modal (3 هفته)
- ✅ همه 8 modality
- ✅ AutoML basic
- ✅ Model comparison

## Milestone 3: Cloud & Advanced (4 هفته)
- ✅ Cloud training
- ✅ Collaboration
- ✅ API serving

## Milestone 4: Production Ready (2 هفته)
- ✅ Tests 90%+ coverage
- ✅ CI/CD complete
- ✅ Documentation complete

---

# 🚀 Quick Start برای Phase 1

## روز 1-2: DataLoader
```bash
cd backend
mkdir -p engine
touch engine/__init__.py engine/data_loader.py

# پیاده‌سازی ImageDataLoader
# پیاده‌سازی TextDataLoader
```

## روز 3-4: ModelBuilder
```bash
touch engine/model_builder.py

# پیاده‌سازی ResNet
# پیاده‌سازی BERT
```

## روز 5-7: Trainer
```bash
touch engine/trainer.py engine/callbacks.py

# پیاده‌سازی training loop
# Integration با FastAPI
```

## روز 8-10: Testing & Integration
```bash
# تست با dataset واقعی
# Fix bugs
# Polish UI updates
```

---

**آیا می‌خواهید از Phase 1 شروع کنیم؟** 🚀

