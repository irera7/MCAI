# 🐛 خطای "No images found" - راه‌حل

## ❌ خطایی که دیدید:

```
ValueError: num_samples should be a positive integer value, but got num_samples=0
Loaded 0 samples for train split
```

## ✅ راه‌حل:

### مشکل: ساختار دایرکتوری داده اشتباه است!

---

## 📁 ساختار صحیح داده

برای Image Classification، باید این ساختار را داشته باشید:

```
projects/
└── your-project-id/
    └── data/
        ├── class1/
        │   ├── image1.jpg
        │   ├── image2.jpg
        │   └── image3.jpg
        ├── class2/
        │   ├── image1.jpg
        │   ├── image2.jpg
        │   └── image3.jpg
        └── class3/
            ├── image1.jpg
            ├── image2.jpg
            └── image3.jpg
```

### مثال واقعی (Cat vs Dog):

```
projects/
└── my-cat-dog-project/
    └── data/
        ├── cat/
        │   ├── cat1.jpg
        │   ├── cat2.jpg
        │   ├── cat3.jpg
        │   └── ... (حداقل 10 عکس)
        └── dog/
            ├── dog1.jpg
            ├── dog2.jpg
            ├── dog3.jpg
            └── ... (حداقل 10 عکس)
```

---

## 🔧 چطور درست کنیم؟

### گزینه 1: از طریق Frontend (توصیه می‌شود!)

1. **Create New Project**
   - Name: `my-classifier`
   - Modality: Image Classification

2. **Data Import Page**:
   - کلیک "Add Label" → نام کلاس اول (مثلاً `cat`)
   - کلیک "Add Label" → نام کلاس دوم (مثلاً `dog`)
   - برای هر کلاس:
     - انتخاب عکس‌ها
     - Upload
     - انتخاب لیبل از ComboBox

3. **Frontend خودکار** این ساختار را می‌سازد:
   ```
   projects/my-classifier/data/cat/
   projects/my-classifier/data/dog/
   ```

### گزینه 2: دستی (برای تست سریع)

```powershell
# 1. پیدا کردن project directory
cd D:\Project\ModelCreator\projects

# 2. لیست پروژه‌ها
dir

# 3. رفتن به پروژه
cd your-project-id

# 4. ساختار data
mkdir data
cd data
mkdir cat
mkdir dog

# 5. کپی عکس‌ها
copy C:\path\to\your\cat\images\*.jpg cat\
copy C:\path\to\your\dog\images\*.jpg dog\

# 6. بررسی
dir cat
dir dog
```

---

## ✅ چک‌کردن ساختار

### PowerShell:
```powershell
cd D:\Project\ModelCreator\projects\your-project-id
tree /F data
```

**باید ببینید:**
```
data
├── cat
│   ├── cat1.jpg
│   ├── cat2.jpg
│   └── ...
└── dog
    ├── dog1.jpg
    ├── dog2.jpg
    └── ...
```

### Python Script:
```python
from pathlib import Path

project_dir = Path(r"D:\Project\ModelCreator\projects\your-project-id")
data_dir = project_dir / "data"

print(f"Data directory: {data_dir}")
print(f"Exists: {data_dir.exists()}")

if data_dir.exists():
    for class_dir in data_dir.iterdir():
        if class_dir.is_dir():
            images = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.png"))
            print(f"  {class_dir.name}: {len(images)} images")
```

---

## 📋 حداقل نیاز

### برای تست:
- **حداقل 2 کلاس**
- **حداقل 5 عکس** per class
- **مجموع حداقل 10 عکس**

### برای Training واقعی:
- **2+ کلاس**
- **20+ عکس** per class
- **40+ عکس** مجموع

### برای نتایج خوب:
- **100+ عکس** per class
- **متنوع** (زوایای مختلف، نورهای مختلف)
- **کیفیت خوب** (حداقل 224x224)

---

## 🎯 فرمت‌های پشتیبانی شده

- ✅ `.jpg` / `.jpeg`
- ✅ `.png`
- ✅ `.bmp`
- ✅ `.gif`

---

## 🐛 Troubleshooting

### 1. "No images found"
**علت**: هیچ عکسی در `data/` نیست

**راه‌حل**:
```powershell
cd projects\your-project-id\data
dir /s *.jpg
# باید حداقل چند فایل نمایش دهد
```

### 2. "Directory does not exist"
**علت**: پوشه `data/` وجود ندارد

**راه‌حل**:
```powershell
cd projects\your-project-id
mkdir data
```

### 3. "Loaded 0 samples"
**علت**: ساختار اشتباه است (عکس‌ها مستقیم در `data/` بدون subdirectory)

**راه‌حل صحیح**:
```
data/
  class1/
    image.jpg  ✅
  class2/
    image.jpg  ✅
```

**راه‌حل غلط**:
```
data/
  image.jpg  ❌ (مستقیماً در data/)
```

---

## 💡 نکات مهم

### 1. نام‌گذاری
- **نام کلاس**: فقط حروف انگلیسی، اعداد، `_`
- **نام فایل**: هر چیزی OK است
- **Case-sensitive**: `Cat` ≠ `cat`

### 2. Frontend vs Manual
- **Frontend**: خودکار ساختار درست می‌سازد ✅
- **Manual**: باید دقت کنید ساختار درست باشد

### 3. Label Mapping
Frontend خودکار این فایل را می‌سازد:
```json
// projects/your-project-id/labels.json
{
  "cat": 0,
  "dog": 1
}
```

اگر دستی می‌سازید، این فایل را هم بسازید!

---

## 🚀 مثال کامل

### دانلود Dataset نمونه:

```python
# test_data_setup.py
from pathlib import Path
import requests
from PIL import Image
import io

# تست با عکس‌های نمونه
project_dir = Path(r"D:\Project\ModelCreator\projects\test-project")
data_dir = project_dir / "data"

# ساخت ساختار
(data_dir / "cat").mkdir(parents=True, exist_ok=True)
(data_dir / "dog").mkdir(parents=True, exist_ok=True)

print("✅ Data structure created!")
print(f"Now copy images to:")
print(f"  {data_dir / 'cat'}")
print(f"  {data_dir / 'dog'}")
```

---

## ✅ بعد از درست کردن

1. **Restart Backend** (مهم!)
   ```powershell
   # در Terminal Backend: Ctrl+C
   python main.py
   ```

2. **در Frontend**:
   - بروید به همان پروژه
   - Training Config
   - "▶️ شروع آموزش"

3. **باید ببینید**:
   ```
   Loading data...
   Loaded 15 samples for train split
   Loaded 3 samples for val split
   Loaded 2 samples for test split
   ✅ Training started!
   ```

---

**حالا data structure را درست کنید و دوباره test کنید!** 🚀

