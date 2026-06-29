# 📤 راهنمای آپلود داده و رفع مشکل "No Images Found"

## 🔴 مشکل رایج: "No images found in data directory"

این خطا زمانی رخ می‌دهد که:
- پوشه `data` در پروژه خالی است
- فایل‌ها انتخاب شده‌اند اما به Backend کپی نشده‌اند
- مسیر پروژه اشتباه است

---

## ✅ راه حل قدم به قدم

### مرحله 1: ایجاد پروژه جدید
```
1. از صفحه Home کلیک کنید: "Create New Project"
2. نام پروژه را وارد کنید (مثال: "cat-dog-classifier")
3. نوع داده را انتخاب کنید: "image"
4. روی "Create" کلیک کنید
```

### مرحله 2: آپلود و لیبل‌گذاری داده‌ها

#### الف) اضافه کردن لیبل‌ها (Class Labels)
```
1. در صفحه "Data Import"، سمت راست را ببینید
2. در قسمت "Class Labels"، لیبل‌های خود را اضافه کنید
   مثال:
   - cat
   - dog
3. روی دکمه "Add Label" کلیک کنید
4. حداقل 2 لیبل نیاز است
```

#### ب) Import کردن فایل‌ها
```
روش 1: Browse Files
- روی "Browse Files" کلیک کنید
- فایل‌های مورد نظر را انتخاب کنید (Ctrl+A برای انتخاب همه)
- OK کنید

روش 2: Browse Folder
- روی "Browse Folder" کلیک کنید
- یک فایل در داخل پوشه را انتخاب کنید
- تمام فایل‌های پوشه import می‌شوند

روش 3: Drag & Drop
- فایل‌ها یا پوشه را از File Explorer بکشید
- در ناحیه Drop Zone رها کنید
```

#### ج) لیبل‌گذاری فایل‌ها
```
1. در لیست فایل‌ها، برای هر فایل منوی کشویی (Combo Box) را باز کنید
2. لیبل مناسب را انتخاب کنید
3. برای همه فایل‌ها این کار را تکرار کنید

⚠️ مهم: حداقل 50% فایل‌ها باید لیبل داشته باشند
✅ توصیه: همه فایل‌ها را لیبل‌گذاری کنید
```

#### د) ذخیره و بررسی
```
1. روی دکمه "Next" کلیک کنید
2. فایل‌ها به پوشه زیر کپی می‌شوند:
   D:\Project\ModelCreator\projects\{project_id}\data\

3. ساختار پوشه:
   projects/
     {project_id}/
       data/
         cat/
           cat_001.jpg
           cat_002.jpg
           ...
         dog/
           dog_001.jpg
           dog_002.jpg
           ...
       labels.json
       project.json
```

---

## 🔍 بررسی موفقیت آپلود

### روش 1: از طریق File Explorer
```
1. پوشه پروژه را باز کنید:
   D:\Project\ModelCreator\projects\{project_id}\

2. وارد پوشه data شوید

3. باید زیرپوشه‌هایی به نام لیبل‌ها ببینید:
   data/
     cat/       ← باید تصاویر گربه اینجا باشند
     dog/       ← باید تصاویر سگ اینجا باشند

4. اگر پوشه data خالی است:
   ❌ فایل‌ها کپی نشده‌اند!
   ✅ به "مشکلات رایج" بروید
```

### روش 2: از طریق Backend API
```bash
# در Terminal جدید:
curl http://127.0.0.1:8181/api/data/stats/{project_id}
```

پاسخ باید شامل این باشد:
```json
{
  "total_files": 30,
  "num_classes": 2,
  "ready_for_training": true,
  "classes": {
    "cat": {"count": 15},
    "dog": {"count": 15}
  }
}
```

اگر `total_files: 0` است:
❌ فایل‌ها آپلود نشده‌اند!

---

## 🐛 مشکلات رایج و راه حل

### 1️⃣ فایل‌ها کپی نمی‌شوند

**علت:** مسیر پروژه اشتباه است

**راه حل:**
```csharp
// در DataImportPage.xaml.cs بررسی کنید:
System.Diagnostics.Debug.WriteLine($"Data directory: {dataDir}");

// باید چاپ شود:
// D:\Project\ModelCreator\projects\{project_id}\data
```

اگر مسیر اشتباه است:
- Frontend را Rebuild کنید
- یا مسیر را manual تنظیم کنید

### 2️⃣ خطا: "Project directory not found"

**راه حل:**
```
1. مطمئن شوید Backend اجرا شده و پروژه ایجاد شده است
2. بررسی کنید پوشه وجود دارد:
   D:\Project\ModelCreator\projects\{project_id}\

3. اگر وجود ندارد، پروژه را دوباره ایجاد کنید از Frontend
```

### 3️⃣ فایل‌ها قبلاً کپی شده‌اند اما Training کار نمی‌کند

**بررسی:**
```bash
# 1. بررسی ساختار پوشه
cd D:\Project\ModelCreator\projects\{project_id}\data
dir

# باید ببینید:
# cat/
# dog/

# 2. بررسی تعداد فایل‌ها
cd cat
dir *.jpg /b | find /c ".jpg"

# باید عدد > 0 باشد
```

**اگر فایل‌ها هستند اما training کار نمی‌کند:**
```
1. بررسی کنید labels.json وجود دارد:
   D:\Project\ModelCreator\projects\{project_id}\labels.json

2. محتوای آن باید باشد:
   {
     "cat": 0,
     "dog": 1
   }

3. اگر وجود ندارد، دوباره از Frontend "Next" را بزنید
```

### 4️⃣ خطا: "Permission Denied" هنگام کپی

**راه حل:**
```
1. Frontend را با Admin اجرا کنید (Run as Administrator)
2. یا فایل‌ها را به پوشه دیگری کپی کنید
3. یا مجوزهای پوشه projects را بررسی کنید
```

---

## 📊 حداقل نیازمندی‌های داده

برای Training موفق:

| مورد | حداقل | توصیه شده |
|------|------|-----------|
| تعداد کلاس‌ها | 2 | 2-10 |
| تعداد تصاویر هر کلاس | 10 | 100+ |
| سایز تصویر | هر سایزی | 224x224+ |
| فرمت | JPG, PNG | JPG |
| تعداد کل تصاویر | 20 | 500+ |

⚠️ **هشدار:**
- کمتر از 10 تصویر → Overfitting قطعی
- کمتر از 50 تصویر → نتایج ضعیف
- 100-500 تصویر → نتایج قابل قبول
- 500+ تصویر → نتایج خوب

---

## 🧪 تست سریع

برای تست کامل سیستم:

### 1. استفاده از پروژه test-cat-dog
```bash
# این پروژه از قبل آماده است
cd D:\Project\ModelCreator\projects\test-cat-dog\

# بررسی ساختار
dir data

# باید ببینید:
# cat\ (15 تصویر)
# dog\ (15 تصویر)
```

### 2. Training با پروژه تست
```
1. Backend را اجرا کنید
2. از Frontend روی Load Project کلیک کنید
3. پروژه "test-cat-dog" را انتخاب کنید
4. مستقیم به Model Selection بروید
5. Training را شروع کنید
```

اگر training شروع شد → سیستم درست کار می‌کند ✅  
اگر همان خطا آمد → مشکل از Backend است ❌

---

## 🔧 Debug کردن مشکل

### روش 1: فعال کردن Debug Logging

در Frontend:
```csharp
// در DataImportPage.xaml.cs، خط 574
System.Diagnostics.Debug.WriteLine($"Copied: {item.FileName} -> {destPath}");
```

خروجی را در Visual Studio Output Window ببینید:
```
View → Output → Show output from: Debug
```

### روش 2: بررسی Backend Logs

```bash
cd backend
python main.py

# وقتی Training شروع می‌کنید، باید ببینید:
# Loading samples from: D:\Project\ModelCreator\projects\{id}\data
# Found X images in class_name/
# Loaded X samples for train split
```

اگر می‌بینید:
```
Found 0 images in root directory
ERROR: No images found!
```

→ فایل‌ها کپی نشده‌اند!

---

## 📝 Checklist قبل از Training

- [ ] Backend روی http://127.0.0.1:8181 اجرا است
- [ ] پروژه ایجاد شده است
- [ ] فایل‌ها import شده‌اند (در Frontend لیست می‌بینید)
- [ ] همه فایل‌ها لیبل‌گذاری شده‌اند (80%+)
- [ ] روی Next کلیک کردید
- [ ] پیام "✅ با موفقیت X فایل ذخیره شد" را دیدید
- [ ] پوشه `data` را بررسی کردید و فایل‌ها را دیدید
- [ ] `labels.json` وجود دارد
- [ ] حداقل 10 تصویر برای هر کلاس دارید

اگر همه ✅ هستند → می‌توانید Training را شروع کنید! 🚀

---

## 🆘 همچنان کار نمی‌کند؟

### گام 1: Backend را Restart کنید
```bash
# Ctrl+C برای توقف
cd backend
python main.py
```

### گام 2: Frontend را Rebuild کنید
```bash
cd frontend/ModelCreator.UI
dotnet clean
dotnet build
```

### گام 3: پروژه جدید بسازید
```
1. پروژه قدیمی را پاک کنید
2. یک پروژه جدید ایجاد کنید
3. دوباره فایل‌ها را import کنید
```

### گام 4: با Test Project تست کنید
```
از پروژه test-cat-dog که آماده است استفاده کنید
```

### گام 5: مستندات بیشتر
```
- TRAINING_GUIDE_FA.md
- COMMON_ERRORS_FA.md
- QUICK_START_FA.md
```

---

## 💡 نکات مهم

1. **همیشه روی Next کلیک کنید:** این دکمه فایل‌ها را کپی می‌کند!

2. **بررسی کنید فایل‌ها کپی شده‌اند:** از File Explorer پوشه data را چک کنید

3. **حداقل 10 تصویر برای هر کلاس:** کمتر → نتایج بد

4. **Backend باید اجرا باشد:** وگرنه پروژه ایجاد نمی‌شود

5. **مسیر درست را استفاده کنید:** D:\Project\ModelCreator\projects\

---

## 📞 دریافت کمک

اگر مشکل حل نشد:

1. Screenshot از خطا بگیرید
2. محتوای پوشه data را بررسی کنید
3. Backend logs را کپی کنید
4. در GitHub Issue بسازید

---

**آخرین بروزرسانی:** 2025-11-26  
**نسخه:** 1.0

