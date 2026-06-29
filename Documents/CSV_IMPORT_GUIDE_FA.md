# 📊 راهنمای Import از CSV برای لیبل‌گذاری خودکار

## 🎯 هدف
این قابلیت به شما اجازه می‌دهد که به جای لیبل‌گذاری دستی هر فایل، از یک فایل CSV برای لیبل‌گذاری خودکار استفاده کنید.

---

## 📝 فرمت فایل CSV

### فرمت پایه
```csv
filename,label
Image_1.jpg,SOUTHERN DOGFACE
Image_2.jpg,ADONIS
Image_3.jpg,BROWN SIPROETA
Image_4.jpg,MONARCH
```

### فرمت با Header (پیشنهادی)
```csv
filename,label
cat_001.jpg,cat
cat_002.jpg,cat
dog_001.jpg,dog
dog_002.jpg,dog
butterfly_01.jpg,butterfly
```

### فرمت بدون Header
```csv
Image_1.jpg,Class_A
Image_2.jpg,Class_B
Image_3.jpg,Class_A
```

⚠️ **مهم:** سیستم به طور خودکار تشخیص می‌دهد که header دارد یا نه!

---

## 🚀 نحوه استفاده

### مرحله 1: آماده‌سازی فایل CSV

#### الف) در Excel یا Google Sheets
```
1. ستون اول: نام فایل
2. ستون دوم: لیبل (Class)
3. Save As → CSV (Comma delimited)
```

#### ب) در Notepad/VS Code
```csv
filename,label
cat_01.jpg,cat
cat_02.jpg,cat
dog_01.jpg,dog
dog_02.jpg,dog
```

⚠️ **نکات مهم:**
- از `,` (کاما) برای جدا کردن ستون‌ها استفاده کنید
- نام فایل‌ها باید دقیقاً مطابق فایل‌های واقعی باشد
- لیبل‌ها می‌توانند فارسی باشند: `گربه,سگ,پرنده`

---

### مرحله 2: Import در Frontend

#### 1️⃣ ایجاد یا Load کردن پروژه
```
- از صفحه Home → Create New Project
- یا Load کردن پروژه موجود
```

#### 2️⃣ رفتن به صفحه Data Import
```
- در فلوی ایجاد پروژه، به صفحه "Data Import" می‌رسید
```

#### 3️⃣ کلیک روی "📊 Import CSV"
```
1. دکمه "📊 Import CSV" را کلیک کنید
2. فایل CSV خود را انتخاب کنید
```

#### 4️⃣ انتخاب پوشه تصاویر
```
1. دیالوگ دوم باز می‌شود
2. یک فایل از داخل پوشه تصاویرتان را انتخاب کنید
   مثال: D:\Images\Butterflies\Image_1.jpg
3. سیستم تمام تصاویر را در آن پوشه جستجو می‌کند
```

#### 5️⃣ بررسی نتیجه
```
✅ پیام موفقیت نمایش داده می‌شود:
   "✅ Import از CSV کامل شد!
   
   📊 آمار:
     • 5 لیبل جدید اضافه شد
     • 100 فایل جدید اضافه شد
     • 100 فایل لیبل‌گذاری شد"
```

---

## 🔍 جزئیات عملکرد

### جستجوی فایل‌ها
سیستم به ترتیب زیر فایل‌ها را جستجو می‌کند:

1. **در پوشه اصلی:**
   ```
   D:\Images\Image_1.jpg
   ```

2. **با نام فایل ساده:**
   ```
   D:\Images\{filename}
   ```

3. **در زیرپوشه‌ها (Recursive):**
   ```
   D:\Images\Folder1\Image_1.jpg
   D:\Images\Folder2\Subfolder\Image_1.jpg
   ```

### اضافه کردن لیبل‌ها
- لیبل‌های جدید به طور خودکار به لیست "Class Labels" اضافه می‌شوند
- لیبل‌های تکراری نادیده گرفته می‌شوند

### لیبل‌گذاری فایل‌ها
- فایل‌هایی که از قبل در لیست هستند، لیبل‌شان به‌روز می‌شود
- فایل‌های جدید با لیبل اضافه می‌شوند

---

## 📋 مثال‌های واقعی

### مثال 1: دیتاست Butterfly Classification

**فایل CSV:** `Training_set.csv`
```csv
filename,label
Image_1.jpg,SOUTHERN DOGFACE
Image_2.jpg,ADONIS
Image_3.jpg,BROWN SIPROETA
Image_4.jpg,MONARCH
Image_5.jpg,GREEN CELLED CATTLEHEART
...
```

**ساختار پوشه:**
```
D:\Datasets\Butterflies\
  Image_1.jpg
  Image_2.jpg
  Image_3.jpg
  ...
```

**نتیجه:**
- 75 کلاس مختلف پروانه شناسایی می‌شود
- 6500 تصویر لیبل‌گذاری می‌شود
- آماده برای Training!

---

### مثال 2: دیتاست Cat vs Dog

**فایل CSV:** `labels.csv`
```csv
filename,label
cat_001.jpg,cat
cat_002.jpg,cat
cat_003.jpg,cat
dog_001.jpg,dog
dog_002.jpg,dog
dog_003.jpg,dog
```

**ساختار پوشه:**
```
D:\Datasets\Animals\
  cats\
    cat_001.jpg
    cat_002.jpg
    cat_003.jpg
  dogs\
    dog_001.jpg
    dog_002.jpg
    dog_003.jpg
```

**نتیجه:**
- 2 کلاس (cat, dog)
- 6 تصویر لیبل‌گذاری می‌شود
- حتی اگر در زیرپوشه باشند پیدا می‌شوند!

---

### مثال 3: دیتاست با نام‌های فارسی

**فایل CSV:** `labels_fa.csv`
```csv
filename,label
گل_رز_01.jpg,گل رز
گل_رز_02.jpg,گل رز
گل_مریم_01.jpg,گل مریم
گل_نرگس_01.jpg,گل نرگس
```

**نتیجه:**
✅ کاملاً پشتیبانی می‌شود!
- لیبل‌های فارسی: گل رز، گل مریم، گل نرگس
- نام فایل‌های فارسی نیز پشتیبانی می‌شوند

---

## ⚠️ مشکلات رایج و راه‌حل

### 1️⃣ خطا: "فایل‌ها پیدا نشدند"

**علت:**
- نام فایل‌ها در CSV با نام واقعی مطابقت ندارند
- پوشه اشتباه انتخاب شده است

**راه‌حل:**
```bash
# بررسی کنید نام فایل‌ها دقیقاً مطابقت دارند:

در CSV:      Image_1.jpg
در پوشه:    Image_1.JPG  ❌ (حروف بزرگ/کوچک)
             Image_1.jpg  ✅

در CSV:      cat.jpg
در پوشه:    cat (1).jpg  ❌
             cat.jpg      ✅
```

### 2️⃣ پیام: "X فایل پیدا نشد"

**نرمال است!** 
اگر تعداد کمی فایل گم شده:
- ممکن است آن فایل‌ها وجود نداشته باشند
- یا نام آنها در CSV اشتباه باشد

**بررسی:**
```
پیام نمایش می‌دهد:
⚠️ 5 فایل پیدا نشد!

فایل‌های گم شده:
  • Image_999.jpg
  • Image_1000.jpg
  ...
```

### 3️⃣ خطا: "فایل CSV خالی است"

**علت:**
- فایل CSV واقعاً خالی است
- یا فرمت آن اشتباه است

**راه‌حل:**
```csv
# حتماً حداقل یک سطر داده داشته باشید:
filename,label
Image_1.jpg,Class_A
```

### 4️⃣ لیبل‌ها اضافه می‌شوند اما فایل‌ها نه

**علت:**
- پوشه تصاویر اشتباه انتخاب شده

**راه‌حل:**
1. دوباره "Import CSV" کنید
2. این بار پوشه درست را انتخاب کنید
3. فایل‌هایی که قبلاً اضافه شده‌اند، لیبل‌شان به‌روز می‌شود

---

## 🎨 ویژگی‌های پیشرفته

### 1️⃣ Import مجدد برای به‌روزرسانی

می‌توانید چندبار CSV import کنید:
- بار اول: فایل‌های جدید اضافه می‌شوند
- بارهای بعد: لیبل‌های موجود به‌روز می‌شوند

```
بار اول:   100 فایل اضافه شد
بار دوم:   0 فایل اضافه شد، 100 فایل به‌روز شد
```

### 2️⃣ Merge کردن CSV‌های مختلف

```bash
# می‌توانید از چند CSV استفاده کنید:
1. Import train.csv  → 80 تصویر
2. Import test.csv   → 20 تصویر
3. مجموع: 100 تصویر در لیست
```

### 3️⃣ ترکیب Import دستی و CSV

```
1. Import CSV → 50 تصویر خودکار لیبل می‌شوند
2. Browse Files → 10 تصویر دیگر اضافه کنید
3. لیبل‌گذاری دستی برای 10 تصویر جدید
```

---

## 📊 مقایسه روش‌ها

| روش | سرعت | دقت | مناسب برای |
|-----|------|-----|-----------|
| **لیبل‌گذاری دستی** | 🐌 کند | ✅ دقیق | < 50 تصویر |
| **Import CSV** | ⚡ خیلی سریع | ✅ دقیق | > 50 تصویر |
| **Browse Folder با ساختار** | ⚡ سریع | ✅ خودکار | پوشه‌های سازمان‌یافته |

### زمان صرف شده (مثال):

**1000 تصویر:**
- لیبل‌گذاری دستی: **~2 ساعت** 🐌
- Import CSV: **~2 دقیقه** ⚡
- صرفه‌جویی: **98% سریع‌تر!**

---

## ✅ Checklist قبل از Import CSV

قبل از استفاده، مطمئن شوید:

- [ ] فایل CSV آماده است
- [ ] فرمت: `filename,label`
- [ ] نام فایل‌ها دقیقاً مطابق فایل‌های واقعی است
- [ ] تصاویر در یک پوشه هستند (یا زیرپوشه‌ها)
- [ ] لیبل‌ها معنی‌دار و واضح هستند
- [ ] حداقل 2 کلاس/لیبل مختلف دارید
- [ ] حداقل 10 تصویر برای هر کلاس دارید

---

## 🧪 تست

### تست سریع با دیتاست نمونه:

#### 1. ایجاد CSV تست
```csv
filename,label
test1.jpg,A
test2.jpg,A
test3.jpg,B
test4.jpg,B
```

#### 2. آماده کردن تصاویر
```
D:\Test\
  test1.jpg
  test2.jpg
  test3.jpg
  test4.jpg
```

#### 3. Import در Frontend
```
1. Create New Project
2. Data Import
3. Import CSV → انتخاب CSV
4. انتخاب پوشه D:\Test\
5. باید 4 تصویر با 2 لیبل import شود
```

#### 4. بررسی
```
✅ Total Samples: 4
✅ Labeled: 4
✅ Labels: A (2), B (2)
```

---

## 💡 نکات و ترفندها

### 1️⃣ تولید CSV از ساختار پوشه

اگر فایل‌هایتان در پوشه‌های جداگانه هستند:

```bash
# در Windows PowerShell:
Get-ChildItem -Recurse -Include *.jpg | 
  Select-Object Name, @{Name="Label";Expression={$_.Directory.Name}} |
  Export-Csv -Path labels.csv -NoTypeInformation
```

خروجی:
```csv
Name,Label
cat_01.jpg,cats
cat_02.jpg,cats
dog_01.jpg,dogs
```

### 2️⃣ ویرایش سریع در Excel

```
1. Open CSV in Excel
2. Sort by Label
3. Fill Down برای لیبل‌های مشابه
4. Save As CSV
```

### 3️⃣ استفاده از Python برای تولید CSV

```python
import os
import pandas as pd

# تولید خودکار CSV از ساختار پوشه
data = []
base_dir = "D:/Datasets/Animals"

for label in os.listdir(base_dir):
    label_dir = os.path.join(base_dir, label)
    if os.path.isdir(label_dir):
        for filename in os.listdir(label_dir):
            if filename.endswith(('.jpg', '.png')):
                data.append({'filename': filename, 'label': label})

df = pd.DataFrame(data)
df.to_csv('labels.csv', index=False)
print(f"Created CSV with {len(df)} entries")
```

---

## 📞 دریافت کمک

### مشکل دارید?

1. **بررسی Debug Output:**
   ```
   Visual Studio → Output Window → Debug
   نگاه کنید به:
   - "Parsed X entries from CSV"
   - "Found X unique labels"
   - "Added/Updated: filename -> label"
   - "File not found: filename"
   ```

2. **فرمت CSV را بررسی کنید:**
   ```
   - آیا comma دارد؟
   - آیا header دارد؟
   - آیا کاراکترهای خاص دارد؟
   ```

3. **مسیر فایل‌ها را چک کنید:**
   ```bash
   dir D:\Images\*.jpg
   ```

---

## 🎯 خلاصه

| مرحله | توضیح |
|-------|--------|
| 1️⃣ | CSV آماده کنید (filename,label) |
| 2️⃣ | دکمه "📊 Import CSV" |
| 3️⃣ | فایل CSV را انتخاب کنید |
| 4️⃣ | پوشه تصاویر را انتخاب کنید |
| 5️⃣ | پیام موفقیت را ببینید |
| 6️⃣ | روی "Next" برای ذخیره کلیک کنید |

**⚡ سریع‌تر از لیبل‌گذاری دستی!**  
**✅ دقیق‌تر از روش‌های خودکار!**  
**🚀 مناسب برای دیتاست‌های بزرگ!**

---

**آخرین بروزرسانی:** 2025-11-26  
**نسخه:** 1.0  
**وضعیت:** ✅ آماده استفاده

