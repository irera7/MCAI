# 📋 راهنمای سریع - من داده ندارم!

## 🎯 مشکل: هیچ عکسی ندارم برای تست!

**نگران نباشید!** 3 راه حل داریم:

---

## ✅ راه حل 1: ساخت خودکار (توصیه می‌شود!)

### استفاده از Script ما:

```powershell
cd D:\Project\ModelCreator\backend
.\venv\Scripts\activate
python create_test_project.py
```

**این کار می‌کند:**
- ✅ یک پروژه `test-cat-dog` می‌سازد
- ✅ 15 عکس dummy cat (آبی)
- ✅ 15 عکس dummy dog (نارنجی)
- ✅ فایل `labels.json`
- ✅ ساختار کامل

**بعدش:**
1. Restart Backend
2. در Frontend باز کنید project با ID: `test-cat-dog`
3. Training Config → Start Training!

---

## ✅ راه حل 2: دانلود Dataset رایگان

### 1. CIFAR-10 (محبوب):
```python
import torchvision.datasets as datasets

# دانلود CIFAR-10
cifar = datasets.CIFAR10(root='./data', download=True, train=True)

# نمونه: 10 کلاس (airplane, car, bird, cat, deer, dog, frog, horse, ship, truck)
```

### 2. از Kaggle:
- [Dogs vs Cats](https://www.kaggle.com/c/dogs-vs-cats/data)
- [Animals-10](https://www.kaggle.com/datasets/alessiocorrado99/animals10)
- [Food-101](https://www.kaggle.com/dansbecker/food-101)

**دانلود:**
```bash
# نصب Kaggle CLI
pip install kaggle

# دانلود dataset
kaggle datasets download -d dataset-name
```

### 3. از Internet:
- Google Images: سرچ کنید و 20 تا عکس download
- Unsplash.com: عکس‌های رایگان با کیفیت بالا
- Pixabay.com: رایگان برای استفاده تجاری

---

## ✅ راه حل 3: استفاده از عکس‌های خودتان

### دارید:
- عکس‌های خودتان روی گوشی/کامپیوتر
- ذخیره‌های اینترنت
- اسکرین‌شات‌ها
- هر چیزی!

### ساختار:

```powershell
# 1. یک پوشه بسازید
mkdir D:\MyImages

# 2. دسته‌بندی کنید
mkdir D:\MyImages\category1
mkdir D:\MyImages\category2

# 3. عکس‌ها را کپی کنید
copy phone_photos\*.jpg D:\MyImages\category1\
copy computer_pics\*.jpg D:\MyImages\category2\

# 4. کپی به project
cd D:\Project\ModelCreator\projects

# ایجاد project directory
mkdir test-my-images
mkdir test-my-images\data

# کپی
xcopy /E D:\MyImages\* test-my-images\data\

# 5. ساخت labels.json
cd test-my-images
echo {"category1": 0, "category2": 1} > labels.json
```

---

## 🎨 مثال‌های خلاقانه

### 1. تشخیص Emoji
- پوشه 1: 😊 happy
- پوشه 2: 😢 sad
- پوشه 3: 😠 angry

Screenshot از emoji ها!

### 2. تشخیص رنگ
- پوشه 1: red (عکس‌های قرمز)
- پوشه 2: blue (عکس‌های آبی)
- پوشه 3: green (عکس‌های سبز)

### 3. تشخیص شکل
- پوشه 1: circle (دایره‌ها)
- پوشه 2: square (مربع‌ها)
- پوشه 3: triangle (مثلث‌ها)

Paint باز کنید و بکشید!

### 4. تشخیص متن
- پوشه 1: english (متن انگلیسی)
- پوشه 2: persian (متن فارسی)
- پوشه 3: arabic (متن عربی)

Screenshot از متن‌ها!

---

## 💡 حداقل نیاز

**برای تست سریع:**
- 2 کلاس
- 10 عکس per class
- مجموع 20 عکس
- فرمت JPG یا PNG

**مثال سریع:**
```
test-project/data/
  ├── class1/
  │   ├── 1.jpg
  │   ├── 2.jpg
  │   ├── 3.jpg
  │   ├── 4.jpg
  │   ├── 5.jpg
  │   ├── 6.jpg
  │   ├── 7.jpg
  │   ├── 8.jpg
  │   ├── 9.jpg
  │   └── 10.jpg
  └── class2/
      ├── 1.jpg
      ├── 2.jpg
      ├── 3.jpg
      ├── 4.jpg
      ├── 5.jpg
      ├── 6.jpg
      ├── 7.jpg
      ├── 8.jpg
      ├── 9.jpg
      └── 10.jpg
```

**Training time:** ~2 minutes on CPU!

---

## 🚀 سریع‌ترین راه

```powershell
# 1. Run test script
cd D:\Project\ModelCreator\backend
.\venv\Scripts\activate
python create_test_project.py

# 2. صبر کنید تا ببینید:
# ✅ Test project ready!
# Project ID: test-cat-dog

# 3. Restart Backend
# Ctrl+C
python main.py

# 4. Frontend:
# - بروید Projects
# - باید یک project به نام "test-cat-dog" ببینید
# - Open → Training Config → Start!
```

**2 دقیقه بعد:** مدل trained شماست! ✅

---

## 📞 هنوز مشکل دارید?

**Option A: Run the test script!**
```bash
python create_test_project.py
```

**Option B: Google "sample image dataset"**
- MNIST: اعداد دست‌نویس
- CIFAR-10: اشیا عمومی
- Fashion-MNIST: لباس‌ها

**Option C: بسازید خودتان!**
- Paint باز کنید
- 10 تا دایره بکشید → save as circle_1.jpg, circle_2.jpg, ...
- 10 تا مربع بکشید → save as square_1.jpg, square_2.jpg, ...
- Done! 🎨

---

**الان test script را run کنید!** 🚀

```powershell
cd D:\Project\ModelCreator\backend
python create_test_project.py
```

