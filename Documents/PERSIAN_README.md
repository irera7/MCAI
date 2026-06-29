# پروژه AI Model Builder - راهنمای کامل فارسی

## 🎯 خلاصه پروژه

**AI Model Builder** یک اپلیکیشن دسکتاپ حرفه‌ای برای آموزش مدل‌های هوش مصنوعی بدون نیاز به کدنویسی است. این پروژه از 8 نوع داده مختلف پشتیبانی می‌کند و با معماری مدرن .NET WPF و Python FastAPI ساخته شده است.

## ✅ وضعیت پروژه: کامل شده

تمام بخش‌های اصلی پروژه پیاده‌سازی شده‌اند:

### ✔️ Frontend (WPF .NET)
- ✅ صفحه خانه (HomePage) 
- ✅ صفحه ایجاد پروژه (CreateProjectPage)
- ✅ صفحه لیست پروژه‌ها (ProjectsPage)
- ✅ صفحه import داده (DataImportPage) - جدید
- ✅ صفحه انتخاب مدل (ModelSelectionPage) - جدید
- ✅ صفحه تنظیمات آموزش (TrainingConfigPage) - جدید
- ✅ داشبورد آموزش (TrainingDashboardPage)
- ✅ صفحه نتایج و export (ResultsPage) - جدید
- ✅ صفحه تست مدل (InferencePlaygroundPage)

### ✔️ Backend (FastAPI Python)
- ✅ API مدیریت پروژه
- ✅ API داده‌ها
- ✅ API آموزش مدل
- ✅ API inference
- ✅ API export مدل
- ✅ API اطلاعات سیستم
- ✅ WebSocket برای آپدیت لحظه‌ای

### ✔️ سرویس‌ها و معماری
- ✅ Dependency Injection
- ✅ MVVM Architecture
- ✅ Theme Service (Dark/Light)
- ✅ API Service با HttpClient
- ✅ WebSocket Service
- ✅ Project Service

## 🚀 راه‌اندازی پروژه

### پیش‌نیازها

**Backend:**
- Python 3.10 یا بالاتر
- (اختیاری) GPU با پشتیبانی CUDA برای آموزش سریع‌تر

**Frontend:**
- .NET 8.0 SDK
- Visual Studio 2022 یا Visual Studio Code
- Windows 10/11

### نصب و راه‌اندازی

#### 1. راه‌اندازی Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend روی `http://127.0.0.1:8181` اجرا می‌شود.

#### 2. راه‌اندازی Frontend

```bash
cd frontend
dotnet restore
dotnet run --project ModelCreator.UI
```

یا در Visual Studio:
- فایل `ModelCreator.sln` را باز کنید
- F5 را فشار دهید

## 📋 گردش کار کامل

### 1. ایجاد پروژه جدید
- روی "Create New Project" کلیک کنید
- نام پروژه و توضیحات را وارد کنید
- نوع داده را انتخاب کنید (Image, Text, Audio, etc.)

### 2. Import و لیبل‌گذاری داده
- فایل‌ها یا فولدرها را Drag & Drop کنید
- لیبل‌های کلاس را ایجاد کنید
- به هر فایل یک لیبل اختصاص دهید
- آمار داده‌ها را بررسی کنید

### 3. انتخاب مدل
- از بین مدل‌های پیشنهادی انتخاب کنید
- مدل Recommended را برای شروع امتحان کنید
- مشخصات هر مدل (Speed, Accuracy, Memory) را مقایسه کنید

### 4. تنظیمات آموزش
- تعداد Epochs (پیشنهاد: 50)
- Batch Size (پیشنهاد: 32)
- Learning Rate (پیشنهاد: 0.001)
- Optimizer (پیشنهاد: Adam)
- Data Augmentation را فعال کنید
- Early Stopping را فعال کنید

### 5. آموزش مدل
- روی "Start Training" کلیک کنید
- نمودارهای Loss و Accuracy را مشاهده کنید
- متریک‌های لحظه‌ای را پیگیری کنید
- در صورت نیاز آموزش را متوقف کنید

### 6. مشاهده نتایج
- دقت نهایی و Loss را ببینید
- Performance هر کلاس را بررسی کنید
- مدل را Export کنید (PyTorch, ONNX, TFLite)

### 7. تست مدل
- به Inference Playground بروید
- فایل‌های جدید را آپلود کنید
- پیش‌بینی مدل را ببینید

## 🎨 انواع داده پشتیبانی‌شده

### 1. Image Classification
- **فرمت‌ها:** JPG, PNG, BMP, TIFF
- **مدل‌ها:** CNN, MobileNetV3, ResNet-50, Vision Transformer
- **کاربردها:** تشخیص اشیاء، کنترل کیفیت، تشخیص پزشکی

### 2. Text Classification
- **فرمت‌ها:** TXT, CSV
- **مدل‌ها:** TF-IDF, LSTM, BERT-Small
- **کاربردها:** تحلیل احساسات، دسته‌بندی متن، تشخیص spam

### 3. Audio Classification
- **فرمت‌ها:** WAV, MP3, FLAC
- **مدل‌ها:** Spectrogram CNN, Audio Transformer
- **کاربردها:** تشخیص صدا، دستورات صوتی

### 4. Video Classification
- **فرمت‌ها:** MP4, AVI, MOV
- **مدل‌ها:** 3D CNN
- **کاربردها:** تشخیص عمل، دسته‌بندی ویدیو

### 5. Tabular Data
- **فرمت‌ها:** CSV, Excel
- **مدل‌ها:** MLP, XGBoost, Random Forest
- **کاربردها:** پیش‌بینی، دسته‌بندی داده‌های جدولی

### 6. Time Series
- **فرمت‌ها:** CSV
- **مدل‌ها:** LSTM, Temporal CNN, Transformer
- **کاربردها:** پیش‌بینی، تشخیص anomaly

### 7. Medical Data
- **فرمت‌ها:** DICOM, NIfTI, PNG
- **مدل‌ها:** MRI CNN, ECG/EEG CNN
- **کاربردها:** تشخیص بیماری، تحلیل تصاویر پزشکی

### 8. Genomic Data
- **فرمت‌ها:** FASTA, FASTQ
- **مدل‌ها:** DNA CNN, Sequence Embedding
- **کاربردها:** دسته‌بندی ژن، پیش‌بینی عملکرد

## 🔧 معماری فنی

### Frontend Stack
- **.NET 8.0 WPF** - UI Framework
- **MVVM Pattern** - معماری
- **Dependency Injection** - مدیریت سرویس‌ها
- **LiveCharts** - نمودارهای لحظه‌ای
- **HttpClient** - ارتباط با API
- **WebSocket** - آپدیت‌های real-time

### Backend Stack
- **FastAPI** - REST API Framework
- **PyTorch** - Deep Learning
- **Uvicorn** - ASGI Server
- **Pydantic** - Data Validation
- **WebSocket** - Live Updates
- **File-based Storage** - ذخیره پروژه‌ها

### ساختار پروژه

```
ModelCreator/
├── backend/
│   ├── main.py                    # Entry point
│   ├── api/routes/                # API endpoints
│   │   ├── project.py            # پروژه‌ها
│   │   ├── data.py               # داده‌ها
│   │   ├── training.py           # آموزش
│   │   ├── inference.py          # تست
│   │   ├── export_routes.py      # Export
│   │   └── system.py             # سیستم
│   ├── models/                    # معماری‌های مدل
│   ├── training/                  # منطق آموزش
│   ├── data/                      # Data loaders
│   └── exporters/                 # Export utilities
│
├── frontend/
│   └── ModelCreator.UI/
│       ├── Views/                 # صفحات XAML
│       │   ├── HomePage.xaml
│       │   ├── CreateProjectPage.xaml
│       │   ├── ProjectsPage.xaml
│       │   ├── DataImportPage.xaml      ✨ جدید
│       │   ├── ModelSelectionPage.xaml  ✨ جدید
│       │   ├── TrainingConfigPage.xaml  ✨ جدید
│       │   ├── TrainingDashboardPage.xaml
│       │   ├── ResultsPage.xaml         ✨ جدید
│       │   └── InferencePlaygroundPage.xaml
│       ├── ViewModels/            # MVVM ViewModels
│       ├── Services/              # سرویس‌ها
│       └── Themes/                # Dark/Light Themes
│
└── projects/                      # پروژه‌های کاربر
    └── {project-id}/
        ├── data/                  # داده‌های آموزش
        ├── models/                # مدل‌های ذخیره‌شده
        ├── exports/               # مدل‌های export شده
        ├── logs/                  # لاگ‌های آموزش
        └── project.json           # تنظیمات پروژه
```

## 📝 ویژگی‌های کلیدی

### ✨ صفحات جدید اضافه شده

#### DataImportPage
- Drag & Drop فایل‌ها و فولدرها
- مدیریت لیبل‌ها
- لیست داده‌های import شده
- آمار و توزیع داده
- Validation قبل از ادامه

#### ModelSelectionPage  
- نمایش کارت‌های مدل با جزئیات
- مقایسه Speed, Accuracy, Memory
- مدل‌های Recommended
- اطلاعات زمان آموزش و پارامترها

#### TrainingConfigPage
- تنظیمات پایه: Epochs, Batch Size, Learning Rate
- تنظیمات پیشرفته: Dropout, Weight Decay, Data Split
- خلاصه تنظیمات در سایدبار
- تخمین زمان آموزش
- بررسی GPU و سیستم

#### ResultsPage
- نمایش متریک‌های نهایی
- جدول Performance هر کلاس
- Export به فرمت‌های مختلف
- دسترسی سریع به Playground و Dashboard

## 🌟 ویژگی‌های برجسته

### UI/UX
- ✅ طراحی مدرن و حرفه‌ای
- ✅ Dark/Light Theme
- ✅ Drag & Drop
- ✅ نمودارهای لحظه‌ای
- ✅ Progress Indicators
- ✅ Validation و Error Handling

### عملکرد
- ✅ Real-time Training Updates
- ✅ GPU Acceleration (اختیاری)
- ✅ Data Augmentation
- ✅ Early Stopping
- ✅ Mixed Precision Training
- ✅ Checkpoint Saving

### Export و Deployment
- ✅ PyTorch (.pt)
- ✅ ONNX (.onnx)
- ✅ TensorFlow Lite (.tflite)
- ✅ شامل Metadata و دستورالعمل‌ها

## 🔍 API Endpoints

### System
- `GET /api/system/info` - اطلاعات سیستم و GPU
- `GET /api/system/devices` - لیست دستگاه‌های محاسباتی
- `GET /api/system/health` - وضعیت سلامت سیستم

### Project
- `POST /api/project/create` - ایجاد پروژه
- `GET /api/project/list` - لیست پروژه‌ها
- `GET /api/project/{id}` - جزئیات پروژه
- `DELETE /api/project/{id}` - حذف پروژه

### Training
- `POST /api/training/start/{project_id}` - شروع آموزش
- `POST /api/training/stop/{project_id}` - توقف آموزش
- `GET /api/training/status/{project_id}` - وضعیت آموزش
- `GET /api/training/results/{project_id}` - نتایج آموزش
- `WS /api/training/live/{project_id}` - WebSocket برای آپدیت لحظه‌ای

### Export
- `POST /api/export/model` - Export مدل
- `GET /api/export/download/{project_id}/{filename}` - دانلود فایل

## 🐛 رفع مشکلات

### Backend اجرا نمی‌شود
```bash
# بررسی نسخه Python
python --version

# نصب مجدد dependencies
pip install -r requirements.txt --force-reinstall

# بررسی port
# مطمئن شوید port 8181 باز است
```

### Frontend build خطا می‌دهد
```bash
# پاک‌سازی و restore
dotnet clean
dotnet restore
dotnet build
```

### GPU تشخیص داده نمی‌شود
```bash
# بررسی CUDA
python -c "import torch; print(torch.cuda.is_available())"

# نصب درایور NVIDIA
# نصب CUDA Toolkit 11.8+
```

## 📚 مستندات بیشتر

- `README.md` - راهنمای اصلی (انگلیسی)
- `PROJECT_DOCUMENTATION.md` - مستندات کامل
- `QUICKSTART.md` - شروع سریع
- `backend/README.md` - مستندات Backend
- `frontend/README.md` - مستندات Frontend

## 🎓 نکات و توصیه‌ها

### برای شروع
1. با dataset کوچک شروع کنید (50-100 نمونه)
2. از مدل Recommended استفاده کنید
3. Data Augmentation را فعال کنید
4. تعداد Epoch را 30-50 قرار دهید

### برای نتایج بهتر
1. داده‌های balanced داشته باشید (تعداد مساوی در هر کلاس)
2. کیفیت داده مهم‌تر از تعداد است
3. Learning Rate را تنظیم کنید
4. از Early Stopping استفاده کنید
5. نمودارهای Loss و Accuracy را دنبال کنید

### Overfitting
اگر Training Accuracy بالا اما Validation پایین است:
- Dropout را افزایش دهید
- Data Augmentation را فعال کنید
- Weight Decay را افزایش دهید
- تعداد Epochs را کم کنید
- داده بیشتر اضافه کنید

## 🚀 ویژگی‌های آینده

- [ ] Cloud Training (AWS, Azure, GCP)
- [ ] AutoML Hyperparameter Tuning
- [ ] Model Comparison Dashboard
- [ ] Ensemble Methods
- [ ] Real-time Inference API
- [ ] Collaboration Features
- [ ] Mobile App

## 🙏 تشکر

از استفاده از AI Model Builder متشکریم! برای سؤال یا مشکل، لطفاً یک Issue ایجاد کنید.

---

**AI Model Builder** - هوش مصنوعی برای همه 🚀

