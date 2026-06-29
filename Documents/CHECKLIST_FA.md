# ✅ چک‌لیست تکمیل پروژه ModelCreator

## 🎯 Phase 1: جایگزینی Mock Training با آموزش واقعی

### Week 1: Core Engine

#### Day 1-2: Data Loading ⭐ PRIORITY #1
- [ ] ایجاد ساختار پوشه `backend/engine/`
- [ ] پیاده‌سازی `ImageDataLoader`
  - [ ] خواندن فایل‌های image (JPEG, PNG, etc.)
  - [ ] Label mapping
  - [ ] Train/Val/Test split
  - [ ] PyTorch Dataset & DataLoader
  - [ ] Augmentation (torchvision.transforms)
- [ ] پیاده‌سازی `TextDataLoader`
  - [ ] Tokenization
  - [ ] Vocabulary building
  - [ ] Padding & truncation
- [ ] تست با دیتاست واقعی (CIFAR-10, MNIST)

**کد شروع:**
```bash
cd D:\Project\ModelCreator\backend
mkdir engine
cd engine
type nul > __init__.py
type nul > data_loader.py
```

---

#### Day 3-4: Model Builder ⭐ PRIORITY #2
- [ ] پیاده‌سازی `ModelBuilder` class
- [ ] Image Models:
  - [ ] ResNet-18 (از torchvision)
  - [ ] ResNet-50
  - [ ] EfficientNet-B0
  - [ ] MobileNetV2
- [ ] Text Models:
  - [ ] Simple LSTM
  - [ ] BERT (از transformers)
- [ ] تست forward pass هر مدل
- [ ] بررسی parameter count

**کد شروع:**
```bash
type nul > model_builder.py
```

---

#### Day 5-7: Training Engine ⭐ PRIORITY #3
- [ ] پیاده‌سازی `Trainer` class
- [ ] Training loop:
  - [ ] Forward pass
  - [ ] Loss calculation
  - [ ] Backward pass
  - [ ] Optimizer step
  - [ ] Metrics logging
- [ ] Validation loop
- [ ] Callbacks:
  - [ ] EarlyStopping
  - [ ] ModelCheckpoint
  - [ ] ProgressCallback (برای frontend)
- [ ] GPU/CPU automatic selection
- [ ] Mixed precision training (torch.cuda.amp)

**کد شروع:**
```bash
type nul > trainer.py
type nul > callbacks.py
type nul > metrics.py
```

---

#### Day 8-10: Integration با Backend ⭐ PRIORITY #4
- [ ] تغییر `backend/api/routes/training.py`
  - [ ] حذف `run_mock_training()`
  - [ ] اضافه کردن `run_real_training()`
  - [ ] Threading برای background training
  - [ ] Update `active_trainings` با metrics واقعی
- [ ] تست end-to-end:
  - [ ] Import image dataset
  - [ ] Select ResNet-18
  - [ ] Start training
  - [ ] Monitor در frontend
  - [ ] بررسی model checkpoint ذخیره شده

---

### Week 2: Model Export & Inference

#### Day 11-12: Export واقعی
- [ ] پیاده‌سازی export به فرمت‌های مختلف:
  - [ ] PyTorch (.pt, .pth)
  - [ ] ONNX (.onnx)
  - [ ] TorchScript (.pt)
- [ ] تست: آموزش → export → load → inference

**کد شروع:**
```bash
cd D:\Project\ModelCreator\backend
mkdir -p export
cd export
type nul > __init__.py
type nul > exporter.py
```

---

#### Day 13-14: Inference واقعی
- [ ] تغییر `backend/api/routes/inference.py`
  - [ ] Load trained model
  - [ ] Preprocess input
  - [ ] Forward pass
  - [ ] Post-process output
- [ ] تست در Inference Playground
- [ ] بررسی latency & throughput

---

### Week 3: Testing & Polish

#### Day 15-17: Testing
- [ ] Unit tests برای:
  - [ ] DataLoader
  - [ ] ModelBuilder
  - [ ] Trainer
  - [ ] Export
  - [ ] Inference
- [ ] Integration tests:
  - [ ] Complete workflow
- [ ] Fix bugs

---

#### Day 18-21: Polish & Documentation
- [ ] بهبود error handling
- [ ] Logging بهتر
- [ ] Documentation update
- [ ] Performance optimization
- [ ] UI/UX improvements

---

## 📋 Phase 2: ویژگی‌های پیشرفته (Optional)

### AutoML (Week 4-5)
- [ ] Hyperparameter optimization با Optuna
- [ ] Grid search
- [ ] Random search
- [ ] Bayesian optimization
- [ ] Frontend: AutoML page

### Cloud Training (Week 6-7)
- [ ] AWS SageMaker integration
- [ ] Azure ML integration
- [ ] GCP AI Platform integration
- [ ] Cost calculator
- [ ] Frontend: Cloud config page

### Model Comparison (Week 8)
- [ ] Store multiple runs
- [ ] Comparison API
- [ ] Frontend: Comparison dashboard
- [ ] Export comparison report

### Ensemble Methods (Week 9)
- [ ] Voting ensemble
- [ ] Stacking
- [ ] Bagging
- [ ] Frontend: Ensemble config

### Real-time Inference API (Week 10)
- [ ] REST API `/predict`
- [ ] Batch prediction
- [ ] Model serving (TorchServe)
- [ ] API documentation (Swagger)

### Collaboration (Week 11-12)
- [ ] User authentication
- [ ] Project sharing
- [ ] Comments
- [ ] Version control

### Mobile App (Week 13-16)
- [ ] Flutter app
- [ ] Project monitoring
- [ ] On-device inference
- [ ] Push notifications

---

## 🎯 لیست اولویت‌ها برای شروع فوری

### Must Have (هفته 1-3) ⭐⭐⭐
1. ✅ DataLoader واقعی (Image + Text)
2. ✅ ModelBuilder واقعی (ResNet + LSTM)
3. ✅ Training Engine واقعی
4. ✅ Export واقعی (PyTorch + ONNX)
5. ✅ Inference واقعی
6. ✅ Testing basic

### Should Have (هفته 4-8) ⭐⭐
1. ✅ **AutoML (Optuna)** - **100% Complete** ✅ (30 Nov 2025)
   - ✅ HyperparameterOptimizer پیاده‌سازی شد
   - ✅ Support for Image, Text, Audio
   - ✅ Optuna integration
   - ✅ Complete test suite
2. ✅ **Model Comparison** - **100% Complete** ✅ (30 Nov 2025)
   - ✅ ModelComparison engine
   - ✅ TrainingRun tracking
   - ✅ Compare multiple models
   - ✅ Report generation
   - ✅ CSV export
   - ✅ Plot comparisons
3. ⚠️ باقی modalities:
   - ✅ **Text** (LSTM, BERT, GRU, Transformer) - **100% Complete** ✅
     - ✅ TextDataLoader پیاده‌سازی شد
     - ✅ Text models integration
     - ✅ API modality detection
     - ✅ **UI for text projects** - **100% Complete** ✅ (30 Nov 2025)
   - ✅ **Audio** (Spectrogram CNN) - **100% Complete** ✅ (30 Nov 2025)
     - ✅ AudioDataLoader پیاده‌سازی شد
     - ✅ SpectrogramCNN model
     - ✅ API integration کامل
     - ✅ Sample dataset generator
     - ✅ Complete test suite
     - ✅ **UI for audio projects** - **100% Complete** ✅ (30 Nov 2025)
   - ❌ Video, Tabular (نیاز به بررسی)
4. ✅ **Ensemble methods** - **100% Complete** ✅ (30 Nov 2025)
   - ✅ VotingEnsemble (Hard, Soft, Weighted)
   - ✅ StackingEnsemble (Meta learner)
   - ✅ BaggingEnsemble
   - ✅ Helper functions
   - ✅ Complete test suite
5. ⚠️ Better UI/UX - **70% تکمیل**
6. ✅ **More models - 100% موجود!**
   - ✅ EfficientNet (B0-B7 از timm)
   - ✅ BERT (در text_models.py + integrated)
   - ✅ MobileNetV3
   - ✅ Vision Transformer
   - ✅ LSTM, GRU, Transformer (text)
   - ✅ SpectrogramCNN (audio)
7. ✅ **TensorBoard Integration** ✅

### Nice to Have (هفته 9+) ⭐
1. ❌ Cloud training
2. ❌ Real-time API
3. ❌ Collaboration
4. ❌ Mobile app
5. ❌ Advanced features

---

## 🚀 دستورات Quick Start

### Setup Engine Structure
```powershell
cd D:\Project\ModelCreator\backend

# ایجاد پوشه‌ها
mkdir engine
mkdir export
mkdir tests

# ایجاد فایل‌های اصلی
cd engine
type nul > __init__.py
type nul > data_loader.py
type nul > model_builder.py
type nul > trainer.py
type nul > callbacks.py
type nul > metrics.py
type nul > utils.py

# نصب dependencies اضافی
cd ..
.\venv\Scripts\activate
pip install timm transformers datasets optuna tensorboard
pip freeze > requirements.txt
```

### اولین تست
```python
# backend/engine/data_loader.py - نمونه ساده
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import os

class ImageDataset(Dataset):
    def __init__(self, data_dir, label_map, transform=None):
        self.data_dir = data_dir
        self.label_map = label_map
        self.transform = transform or transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], 
                                 [0.229, 0.224, 0.225])
        ])
        self.samples = self._load_samples()
    
    def _load_samples(self):
        samples = []
        for label_name, label_id in self.label_map.items():
            label_dir = os.path.join(self.data_dir, label_name)
            if os.path.exists(label_dir):
                for img_file in os.listdir(label_dir):
                    if img_file.endswith(('.jpg', '.jpeg', '.png')):
                        samples.append((
                            os.path.join(label_dir, img_file),
                            label_id
                        ))
        return samples
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert('RGB')
        if self.transform:
            image = self.transform(image)
        return image, label

# تست
if __name__ == "__main__":
    # فرض: data/ پوشه با cat/ و dog/ زیرپوشه‌ها
    label_map = {"cat": 0, "dog": 1}
    dataset = ImageDataset("../projects/test-project/data", label_map)
    loader = DataLoader(dataset, batch_size=4, shuffle=True)
    
    for images, labels in loader:
        print(f"Batch: {images.shape}, Labels: {labels}")
        break
```

---

## 📊 Progress Tracker

### Legend:
- ✅ Done
- 🔄 In Progress
- ❌ Not Started
- ⏸️ Blocked
- 🔥 Priority

### Current Status:
```
Mock Training            ✅ Done
HTTP Polling             ✅ Done
UI Complete              ✅ Done (40% for text/audio)
Documentation            ✅ Done

DataLoader               ✅ Done ⭐
  - ImageDataLoader      ✅ 100%
  - TextDataLoader       ✅ 100% (30 Nov 2025)
  - AudioDataLoader      ✅ 100% ⭐ NEW (30 Nov 2025)
  
ModelBuilder             ✅ Done ⭐
  - Image models         ✅ 100%
  - Text models          ✅ 100% (30 Nov 2025)
  - Audio models         ✅ 100% ⭐ NEW (30 Nov 2025)
  
Trainer                  ✅ Done ⭐
Export                   ✅ Done ⭐
Inference                ✅ Done ⭐
TensorBoard              ✅ Done ⭐ (30 Nov 2025)
API Modality Detection   ✅ Done ⭐ (30 Nov 2025)

Image Classification     ✅ 100% Complete
Text Classification      ✅ 100% Complete (Backend) ⭐⭐ (30 Nov 2025)
  - Backend             ✅ 100%
  - UI                  ⏳ 0%

Audio Classification     ✅ 100% Complete (Backend) ⭐⭐ NEW (30 Nov 2025)
  - Backend             ✅ 100%
  - UI                  ⏳ 0%

AutoML                   ✅ 100% Complete ⭐ NEW (30 Nov 2025)
  - HyperparameterOptimizer  ✅ 100%
  - Test suite              ✅ 100%
  - Documentation           ✅ 100%
  
Cloud Training           ❌ Not Started
Model Comparison         ❌ Not Started 🔥 NEXT
Ensemble                 ❌ Not Started
Real-time API            ❌ Not Started
Collaboration            ❌ Not Started
Mobile App               ❌ Not Started
```

### 🎉 Phase 1 Complete! (30 Nov 2025)
**Real Training Engine is READY!** See `ENGINE_READY_FA.md` for details.

### 🎊 Text Classification Complete! (30 Nov 2025)
**Text Classification Backend is READY!** See `TEXT_COMPLETE_SUMMARY.md` and `COMPLETE_PROJECT_REPORT.md` for details.

### 🎵 Audio Classification Complete! (30 Nov 2025) ⭐ NEW
**Audio Classification Backend is READY!** See `AUDIO_CLASSIFICATION_COMPLETE.md` for details.

### 🤖 AutoML Complete! (30 Nov 2025) ⭐ NEW
**Hyperparameter Optimization is READY!** See `AUTOML_COMPLETE.md` for details.

---

## 💡 نکات مهم

### 1. شروع از کوچک
- ابتدا فقط Image Classification
- بعد Text Classification
- سپس بقیه modalities

### 2. تست مداوم
- هر component را جداگانه تست کنید
- Integration test بعد از هر feature

### 3. Git workflow
```bash
git checkout -b feature/real-training-engine
# کار روی feature
git commit -m "feat: add DataLoader for images"
git push origin feature/real-training-engine
# Pull request & review
```

### 4. Documentation
- هر تابع → docstring
- هر module → README
- Complex logic → comments

---

## 🎓 منابع یادگیری

### PyTorch Training
- https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html
- https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html

### Best Practices
- https://github.com/IgorSusmelj/pytorch-styleguide
- https://pytorch.org/docs/stable/notes/cuda.html

### Model Zoo
- https://pytorch.org/vision/stable/models.html (torchvision)
- https://huggingface.co/models (transformers)
- https://github.com/rwightman/pytorch-image-models (timm)

---

**✅ Phase 1 تکمیل شد!** 🎉

همه اهداف Week 1-3 پیاده‌سازی شده:
1. ✅ Backend engine structure ساخته شد
2. ✅ ImageDataLoader پیاده‌سازی شد (377 خط)
3. ✅ ModelBuilder پیاده‌سازی شد (300 خط)
4. ✅ Trainer پیاده‌سازی شد (268 خط)
5. ✅ Callbacks پیاده‌سازی شد (275 خط)
6. ✅ Integration با API انجام شد (540 خط)
7. ✅ تست با test-cat-dog پروژه موفق

**برای اطلاعات کامل، فایل `ENGINE_READY_FA.md` را ببینید.**

**آماده برای Phase 2؟** 🚀
- AutoML با Optuna
- Model Comparison Dashboard
- Cloud Training Integration
- More Modalities (Audio, Video, Tabular)

من در کنار شما هستم برای هر مرحله! 💪

