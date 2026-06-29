# 🔍 چرا Training Dashboard داده نشان نمی‌دهد؟

## ✅ پاسخ کوتاه
**Training Dashboard فقط زمانی داده واقعی نمایش می‌دهد که یک آموزش فعال در حال اجرا باشد.**

❌ **هیچ داده Mock یا Hardcoded در Dashboard وجود ندارد**  
✅ **تمام داده‌ها به صورت Real-time از Backend API دریافت می‌شوند**

---

## 📋 مراحل کامل برای مشاهده داده‌های واقعی

### پیش‌نیاز: Backend باید در حال اجرا باشد

```bash
# Terminal 1: اجرای Backend
cd D:\Project\ModelCreator\backend
python main.py

# باید این پیام را ببینید:
# ✅ INFO: Uvicorn running on http://127.0.0.1:8181
```

```bash
# Terminal 2: اجرای Frontend
cd D:\Project\ModelCreator\frontend
dotnet run --project ModelCreator.UI
```

---

### مرحله 1️⃣: ایجاد پروژه جدید

1. **از صفحه Home، کلیک کنید روی** `"➕ Create New Project"`

2. **فرم را پر کنید:**
   - **Project Name**: `CatDog Classifier` (مثال)
   - **Modality**: `Image` را انتخاب کنید
   - **Description**: `تشخیص گربه از سگ` (اختیاری)

3. **کلیک کنید روی** `"Create Project"`

---

### مرحله 2️⃣: آپلود داده‌ها

بعد از ایجاد پروژه، به صفحه **Data Import** منتقل می‌شوید.

#### روش A: ساختار فولدر (توصیه می‌شود)

```
my_dataset/
├── train/
│   ├── cat/
│   │   ├── cat1.jpg
│   │   ├── cat2.jpg
│   │   └── ... (حداقل 20-30 تصویر)
│   └── dog/
│       ├── dog1.jpg
│       ├── dog2.jpg
│       └── ... (حداقل 20-30 تصویر)
└── val/
    ├── cat/
    │   └── ... (حداقل 5-10 تصویر)
    └── dog/
        └── ... (حداقل 5-10 تصویر)
```

**مراحل:**
1. کلیک کنید روی `"📁 Browse Folder"`
2. فولدر `my_dataset` را انتخاب کنید
3. منتظر بمانید تا آپلود تکمیل شود

#### روش B: فایل ZIP

1. فولدر بالا را به ZIP کنید: `my_dataset.zip`
2. کلیک کنید روی `"📦 Upload ZIP"`
3. فایل ZIP را انتخاب کنید
4. منتظر بمانید تا استخراج شود

#### روش C: آپلود دستی (برای تست کوچک)

1. کلیک کنید روی `"➕ Add Label"` و لیبل‌ها را اضافه کنید: `cat`, `dog`
2. کلیک کنید روی `"📄 Browse Files"` و چند تصویر انتخاب کنید
3. برای هر تصویر، از منوی کشویی یک لیبل انتخاب کنید
4. حداقل 10 تصویر با لیبل برای هر کلاس نیاز است

**نکات مهم:**
- ✅ حداقل **2 لیبل** (مثلاً cat و dog)
- ✅ حداقل **10 تصویر برای هر لیبل**
- ✅ حداقل **50% داده‌ها باید لیبل‌گذاری شده باشند**

5. بعد از آپلود، کلیک کنید روی `"Next Step"` یا `"Configure Training"`

---

### مرحله 3️⃣: پیکربندی آموزش

در صفحه **Training Configuration**:

#### A. انتخاب Model Architecture

از منوی کشویی یکی را انتخاب کنید:
- `ResNet18` - سریع، مناسب برای شروع
- `ResNet50` - دقیق‌تر، کندتر
- `EfficientNet-B0` - تعادل خوب
- `MobileNetV2` - سبک برای CPU

#### B. تنظیمات Hyperparameters

**برای تست سریع (2-5 دقیقه):**
```
Epochs: 5
Batch Size: 16
Learning Rate: 0.001
Optimizer: Adam
```

**برای آموزش واقعی (30-60 دقیقه):**
```
Epochs: 50
Batch Size: 32
Learning Rate: 0.001
Optimizer: Adam
Weight Decay: 0.0001
```

#### C. تنظیمات پیشرفته (اختیاری)

- ✅ **Data Augmentation**: فعال کنید (بهبود دقت)
- ✅ **Early Stopping**: فعال کنید (توقف خودکار)
  - Patience: 10
- ✅ **Mixed Precision**: فعال کنید (اگر GPU دارید)
- ✅ **Learning Rate Scheduler**: `CosineAnnealing` (توصیه می‌شود)

#### D. بررسی GPU

در بالای صفحه باید ببینید:
- ✅ **اگر GPU دارید**: `✅ GPU: NVIDIA GeForce RTX 3080`
- ⚠️ **اگر GPU ندارید**: `⚠️ GPU: موجود نیست (آموزش با CPU)`

**نکته**: آموزش با CPU **20-50 برابر کندتر** است!

#### E. شروع آموزش

1. **بررسی کنید خلاصه در سمت راست:**
   ```
   📊 خلاصه پیکربندی:
   • Model: ResNet18
   • Epochs: 5
   • Batch Size: 16
   • Classes: 2 (cat, dog)
   • Train Samples: 50
   • Val Samples: 10
   ```

2. **کلیک کنید روی** `"▶️ شروع آموزش"` (Start Training)

3. **منتظر بمانید** (1-2 ثانیه) تا آموزش شروع شود

4. **صفحه Training Dashboard به طور خودکار باز می‌شود**

---

### مرحله 4️⃣: مشاهده Dashboard (Real-Time)

#### ✅ اگر همه چیز درست باشد، خواهید دید:

##### 1. **Status Bar (بالا)**
```
🔥 در حال آموزش... (زمان: 00:02:15)
```

##### 2. **Progress Bar (نوار پیشرفت)**
```
Epoch: 3 / 5 (60%)
█████████████░░░░░░░░░
```

##### 3. **متریک‌های فعلی (Current Metrics)**
```
Train Loss: 0.3421
Train Accuracy: 85.23%
Val Loss: 0.4125
Val Accuracy: 82.10%
```

##### 4. **بهترین متریک‌ها (Best Metrics)**
```
Best Accuracy: 84.50%
Best Loss: 0.3215
```

##### 5. **نمودارهای زنده (Live Charts)**

**نمودار Loss:**
- خط آبی: Train Loss (باید کاهش یابد ↓)
- خط نارنجی: Val Loss (باید کاهش یابد ↓)

**نمودار Accuracy:**
- خط سبز: Train Accuracy (باید افزایش یابد ↑)
- خط بنفش: Val Accuracy (باید افزایش یابد ↑)

##### 6. **اطلاعات اضافی**
```
ETA: 00:03:45 (زمان باقیمانده)
Learning Rate: 0.001000
Batch Speed: 42.5 samples/sec
```

##### 7. **Logs (لاگ‌ها)**
```
08:15:23 - Epoch 1: Loss: 0.6234, Acc: 0.6543 - 3.2s/epoch
08:15:26 - Epoch 2: Loss: 0.4521, Acc: 0.7823 - 3.1s/epoch
08:15:29 - Epoch 3: Loss: 0.3421, Acc: 0.8523 - 3.0s/epoch
...
```

#### ⏱️ زمان به‌روزرسانی
- Dashboard هر **2 ثانیه** داده‌ها را از Backend دریافت می‌کند
- نمودارها **فقط در پایان هر Epoch** به‌روز می‌شوند (برای جلوگیری از duplicate)

---

## ❌ عیب‌یابی: چرا داده نمی‌بینم؟

### مشکل 1: صفحه خالی است / "⏸️ آموزش شروع نشده"

**علت**: هیچ آموزشی در حال اجرا نیست

**راه حل**:
1. ✅ مطمئن شوید که در مرحله 3 روی `"▶️ شروع آموزش"` کلیک کرده‌اید
2. ✅ منتظر بمانید 2-5 ثانیه (ممکن است آماده‌سازی طول بکشد)
3. ✅ به صفحه Home برگردید و پروژه را دوباره باز کنید

---

### مشکل 2: "❌ Backend در دسترس نیست"

**علت**: Backend در حال اجرا نیست

**راه حل**:
```bash
# Terminal جدید
cd D:\Project\ModelCreator\backend
python main.py

# باید ببینید:
# INFO: Uvicorn running on http://127.0.0.1:8181

# اگر خطا دیدید:
pip install -r requirements.txt
python main.py
```

**چک کردن Backend از مرورگر:**
1. باز کنید: http://127.0.0.1:8181/docs
2. باید صفحه API Documentation را ببینید

---

### مشکل 3: "⏳ در حال بررسی وضعیت Backend..." (گیر کرده)

**علت**: Backend crash کرده یا port مسدود است

**راه حل**:
1. **چک کنید Terminal که Backend در آن اجرا می‌شود**
2. **اگر خطا دیدید:**
   ```bash
   # Kill کردن process قبلی
   # Windows:
   netstat -ano | findstr :8181
   taskkill /PID <PID> /F
   
   # یا:
   Ctrl+C در Terminal Backend
   python main.py
   ```

---

### مشکل 4: داده‌ها به‌روز نمی‌شوند

**علت A**: آموزش متوقف شده یا تکمیل شده

**راه حل**:
- اگر در Backend لاگی نمی‌بینید، احتمالاً آموزش تکمیل شده یا crash کرده
- چک کنید Terminal Backend برای خطاها

**علت B**: Project ID اشتباه است

**راه حل**:
- از صفحه Home، پروژه را دوباره باز کنید
- یا کلیک کنید روی `"View Training Dashboard"` از صفحه پروژه

---

### مشکل 5: "CUDA Out of Memory"

**علت**: GPU memory کافی نیست

**راه حل**:
1. کاهش `Batch Size`: `32` → `16` → `8` → `4`
2. استفاده از مدل کوچک‌تر: `ResNet50` → `ResNet18`
3. غیرفعال کردن `Mixed Precision`
4. یا استفاده از CPU (کندتر):
   ```bash
   # در backend
   set CUDA_VISIBLE_DEVICES=-1
   python main.py
   ```

---

### مشکل 6: آموزش خیلی کند است

**علت A**: استفاده از CPU به جای GPU

**راه حل**:
1. نصب PyTorch با CUDA:
   ```bash
   pip uninstall torch torchvision
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```
2. چک کنید GPU:
   ```bash
   cd backend
   python -c "import torch; print(torch.cuda.is_available())"
   # باید True بگوید
   ```

**علت B**: Batch Size خیلی کوچک است

**راه حل**:
- افزایش `Batch Size`: `8` → `16` → `32` (اگر memory کافی دارید)

**علت C**: Data Augmentation زیاد است

**راه حل**:
- برای تست سریع، Data Augmentation را غیرفعال کنید

---

## 📊 مثال کامل با داده‌های واقعی

### دانلود داده‌های نمونه (Cats vs Dogs)

```bash
# Option 1: Kaggle Dataset
# https://www.kaggle.com/c/dogs-vs-cats/data
# دانلود و استخراج کنید

# Option 2: ساخت دستی (برای تست)
# 1. یک فولدر ایجاد کنید:
mkdir test_dataset
cd test_dataset

# 2. ساختار ایجاد کنید:
mkdir train\cat train\dog val\cat val\dog

# 3. چند تصویر گربه و سگ از اینترنت دانلود کنید و در فولدرها قرار دهید
# حداقل 20 تصویر در train\cat
# حداقل 20 تصویر در train\dog
# حداقل 5 تصویر در val\cat
# حداقل 5 تصویر در val\dog
```

### تنظیمات پیشنهادی برای تست سریع

```yaml
Model: ResNet18
Epochs: 5
Batch Size: 16
Learning Rate: 0.001
Optimizer: Adam

Data Augmentation: ✅ فعال
Early Stopping: ✅ فعال (Patience: 10)
Mixed Precision: ✅ فعال (اگر GPU دارید)

زمان تقریبی:
- با GPU: 2-3 دقیقه
- با CPU: 10-20 دقیقه
```

### چک‌لیست قبل از شروع

- [ ] Backend در حال اجرا است (`http://127.0.0.1:8181/docs` باز می‌شود)
- [ ] پروژه ایجاد شده است
- [ ] داده‌ها آپلود شده‌اند (حداقل 20 نمونه per class)
- [ ] تنظیمات Training پر شده‌اند
- [ ] روی "شروع آموزش" کلیک شده است
- [ ] صفحه Dashboard باز شده است

---

## 🎯 خلاصه

### ✅ چرا Dashboard خالی است؟
**چون هیچ آموزشی در حال اجرا نیست!**

### ✅ چگونه داده واقعی ببینم؟
1. پروژه ایجاد کنید
2. داده آپلود کنید
3. تنظیمات را پر کنید
4. آموزش را شروع کنید
5. Dashboard را باز کنید

### ✅ داده‌ها از کجا می‌آیند؟
- **100% از Backend API** (`/api/training/status/{project_id}`)
- **Polling هر 2 ثانیه** برای real-time updates
- **هیچ داده Mock/Hardcoded نیست**

### ✅ چگونه مطمئن شوم که کار می‌کند؟
1. Backend Terminal را چک کنید - باید لاگ‌های آموزش را ببینید:
   ```
   [INFO] Epoch 1/5 - Train Loss: 0.6234, Acc: 0.6543
   [INFO] Epoch 2/5 - Train Loss: 0.4521, Acc: 0.7823
   ...
   ```
2. Dashboard باید همین مقادیر را نشان دهد

---

## 📚 مستندات مرتبط

- `TRAINING_DASHBOARD_GUIDE_FA.md` - راهنمای کامل Dashboard
- `QUICKSTART.md` - راهنمای شروع سریع
- `GPU_TROUBLESHOOTING_FA.md` - عیب‌یابی GPU
- `API_REFERENCE.md` - مستندات API

---

**نکته پایانی**: Dashboard یک ابزار **monitoring** است، نه یک ابزار **visualization**. 
بدون آموزش فعال، هیچ چیزی برای نمایش نیست! ✨

