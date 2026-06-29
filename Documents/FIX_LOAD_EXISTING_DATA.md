# 🔄 رفع مشکل: بارگذاری داده‌های موجود در پروژه

## 🔴 مشکل
وقتی پروژه قبلی را باز می‌کردید:
- ❌ داده‌ها در پوشه `data` موجود بودند
- ❌ اما در UI نمایش داده نمی‌شدند
- ❌ مجبور بودید دوباره فایل‌ها را اضافه کنید

## ✅ راه‌حل

### تغییرات انجام شده

**فایل:** `frontend/ModelCreator.UI/Views/DataImportPage.xaml.cs`

#### 1️⃣ Load کردن خودکار داده‌های موجود

```csharp
public DataImportPage(string projectId, string projectName, string modality)
{
    InitializeComponent();
    
    // ✅ بارگذاری خودکار داده‌های موجود
    LoadExistingData();
    
    // اگر داده موجود بود، پیام متفاوت نمایش داده می‌شود
    if (dataItems.Count > 0)
    {
        MessageBox.Show($"✅ پروژه موجود بارگذاری شد!\n\n" +
                       $"📊 داده‌های موجود:\n" +
                       $"  • {dataItems.Count} فایل\n" +
                       $"  • {labels.Count} لیبل");
    }
}
```

#### 2️⃣ متد LoadExistingData

```csharp
private void LoadExistingData()
{
    // 1. Load labels از labels.json
    // 2. Load فایل‌ها از data/{label}/ directories
    // 3. اضافه کردن به dataItems با لیبل صحیح
    // 4. Update آمار
}
```

#### 3️⃣ بهبود SaveDataToProject

```csharp
private void SaveDataToProject()
{
    // ✅ فقط فایل‌های جدید کپی می‌شوند
    // ✅ فایل‌های موجود Skip می‌شوند
    // ✅ گزارش کامل: copied, skipped, errors
}
```

---

## 🎯 ویژگی‌های جدید

### 1. بارگذاری هوشمند

```
وقتی پروژه را باز می‌کنید:
1. ✅ Labels از labels.json خوانده می‌شوند
2. ✅ فایل‌ها از زیرپوشه‌های data/ بارگذاری می‌شوند
3. ✅ لیبل‌ها به فایل‌ها اختصاص داده می‌شوند
4. ✅ آمار به‌روز می‌شود
```

### 2. Skip کردن فایل‌های موجود

```
وقتی Next می‌زنید:
- فایل جدید → کپی می‌شود ✅
- فایل موجود (همان فایل) → Skip ✅
- فایل موجود (تغییر کرده) → Update می‌شود ✅
```

### 3. پیام‌های واضح

```
پروژه جدید:
"راهنما: ابتدا لیبل‌ها را اضافه کنید..."

پروژه موجود:
"✅ پروژه موجود بارگذاری شد!
📊 داده‌های موجود:
  • 30 فایل
  • 2 لیبل"
```

---

## 🚀 نحوه استفاده

### سناریو 1: باز کردن پروژه test-cat-dog

```
1. Home → Load Project
2. انتخاب "test-cat-dog"
3. ✅ Data Import page باز می‌شود
4. ✅ می‌بینید:
   - Total Samples: 30
   - Labeled: 30
   - Labels: cat (15), dog (15)
5. می‌توانید:
   a) مستقیم Next → Model Selection
   b) یا داده بیشتر اضافه کنید
```

### سناریو 2: اضافه کردن داده به پروژه موجود

```
1. پروژه را باز کنید (مثلاً test-cat-dog با 30 تصویر)
2. ✅ داده‌های موجود نمایش داده می‌شوند
3. داده جدید اضافه کنید:
   - Browse Files → 10 تصویر cat جدید
   - Browse Files → 10 تصویر dog جدید
4. لیبل‌گذاری کنید
5. Next
6. ✅ پیام:
   "✅ ذخیره‌سازی کامل شد!
   📊 خلاصه:
     • 20 فایل جدید کپی شد
     • 30 فایل قبلاً موجود بود
     • کل: 50 فایل"
```

### سناریو 3: تغییر لیبل‌ها در پروژه موجود

```
1. پروژه را باز کنید
2. ✅ فایل‌های موجود با لیبل‌های فعلی نمایش داده می‌شوند
3. لیبل بعضی فایل‌ها را تغییر دهید
4. Next
5. ✅ فایل‌ها به پوشه‌های جدید منتقل می‌شوند
```

---

## 🧪 تست

### تست 1: Load کردن پروژه موجود

```bash
# Prerequisite: پروژه test-cat-dog موجود است
# با 15 cat و 15 dog

1. Frontend را اجرا کنید
2. Home → Load Project
3. test-cat-dog را انتخاب کنید
4. بررسی کنید:
   ✅ Total Samples: 30
   ✅ Labeled: 30
   ✅ cat: 15, dog: 15
   ✅ فایل‌ها در لیست نمایش داده می‌شوند
```

### تست 2: اضافه کردن داده جدید

```bash
1. پروژه test-cat-dog را باز کنید (30 تصویر موجود)
2. Browse Files → 5 تصویر cat جدید
3. لیبل‌گذاری: cat
4. Next
5. بررسی پیام:
   ✅ "5 فایل جدید کپی شد"
   ✅ "30 فایل قبلاً موجود بود"
   ✅ "کل: 35 فایل"
```

### تست 3: هیچ تغییری ایجاد نکردن

```bash
1. پروژه test-cat-dog را باز کنید
2. هیچ فایل جدید اضافه نکنید
3. Next
4. بررسی پیام:
   ✅ "همه فایل‌ها (30) قبلاً موجود بودند"
   ✅ "تغییری در فایل‌ها ایجاد نشد"
```

---

## 📊 جزئیات فنی

### ساختار پوشه پروژه

```
projects/
  {project_id}/
    data/
      cat/              ← لیبل 1
        cat_01.jpg
        cat_02.jpg
        ...
      dog/              ← لیبل 2
        dog_01.jpg
        dog_02.jpg
        ...
    labels.json         ← {"cat": 0, "dog": 1}
    project.json
```

### فرآیند LoadExistingData

```
1. خواندن labels.json:
   {"cat": 0, "dog": 1}
   → labels = ["cat", "dog"]

2. خواندن data/cat/:
   → 15 فایل با label = "cat"

3. خواندن data/dog/:
   → 15 فایل با label = "dog"

4. نتیجه:
   dataItems.Count = 30
   labels.Count = 2
```

### منطق Skip کردن فایل‌ها

```csharp
if (File.Exists(destPath))
{
    if (item.FilePath == destPath)
    {
        // همان فایل است → Skip
        skippedCount++;
    }
    else
    {
        // فایل متفاوت → بررسی تاریخ و سایز
        if (نسخه جدیدتر یا سایز متفاوت)
        {
            // Update
            File.Copy(overwrite: true);
            copiedCount++;
        }
        else
        {
            // Skip
            skippedCount++;
        }
    }
}
else
{
    // فایل وجود ندارد → Copy
    File.Copy(overwrite: false);
    copiedCount++;
}
```

---

## 🐛 مشکلات احتمالی و راه‌حل

### مشکل 1: فایل‌ها Load نمی‌شوند

**علامت:**
```
Total Samples: 0
اما پوشه data/ پر است
```

**علت:** مسیر پروژه اشتباه است

**Debug:**
```csharp
// در Output Window ببینید:
Loading existing data from: D:\...\projects\{id}\data
Loaded X files from cat/
Loaded Y files from dog/
```

**راه‌حل:**
```bash
# بررسی کنید پوشه درست است:
cd D:\Project\ModelCreator\projects\{project_id}\data
dir

# باید ببینید:
# cat\
# dog\
```

---

### مشکل 2: لیبل‌ها Load می‌شوند اما فایل‌ها نه

**علامت:**
```
Labels: 2 (cat, dog)
Total Samples: 0
```

**علت:** پسوند فایل‌ها مطابقت ندارد

**بررسی:**
```csharp
// GetFileExtensions() چه می‌گوید؟
// image: .jpg, .jpeg, .png, .bmp, .gif, .tiff

// آیا فایل‌های شما این پسوندها را دارند؟
```

**راه‌حل:**
اگر فایل‌ها پسوند دیگری دارند (مثلاً .webp):
```csharp
// در GetFileExtensions() اضافه کنید:
"image" => new[] { ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp" },
```

---

### مشکل 3: فایل‌ها دوبار کپی می‌شوند

**علامت:**
```
Error: File already exists
```

**علت:** منطق Skip کار نمی‌کند

**راه‌حل:**
این مشکل با تغییرات جدید رفع شد:
```csharp
// فایل‌های موجود Skip می‌شوند
// فقط فایل‌های جدید کپی می‌شوند
```

---

## 💡 نکات مهم

### 1. فایل‌های Source تغییر نمی‌کنند

```
وقتی پروژه را Load می‌کنید:
- فایل‌های اصلی در data/ هستند
- هیچ تغییری در آنها ایجاد نمی‌شود
- فقط در UI نمایش داده می‌شوند
```

### 2. می‌توانید فایل جدید اضافه کنید

```
پروژه موجود: 30 فایل
+ Browse 10 فایل جدید
= 40 فایل در لیست

Next → فقط 10 فایل جدید کپی می‌شود
```

### 3. تغییر لیبل باعث Move نمی‌شود

```
در حال حاضر:
- تغییر لیبل در UI → فقط در حافظه
- Next → فایل به پوشه جدید کپی می‌شود
- فایل قدیمی باقی می‌ماند

آینده:
- می‌توانیم Delete کردن فایل قدیمی را اضافه کنیم
```

---

## 🎯 خلاصه

| قبل | بعد |
|-----|-----|
| ❌ فایل‌های موجود نمایش نمی‌شوند | ✅ خودکار Load می‌شوند |
| ❌ باید دوباره Import کنید | ✅ بلافاصله نمایش داده می‌شوند |
| ❌ لیبل‌ها گم می‌شوند | ✅ از labels.json خوانده می‌شوند |
| ❌ فایل‌ها دوبار کپی می‌شوند | ✅ فایل‌های موجود Skip می‌شوند |

---

## 📈 بهبودهای آینده

### کوتاه‌مدت
- [ ] نمایش تصویر thumbnail در لیست
- [ ] فیلتر بر اساس لیبل
- [ ] جستجوی فایل
- [ ] Sort کردن لیست

### میان‌مدت
- [ ] Delete کردن فایل از پروژه
- [ ] Move کردن فایل بین لیبل‌ها
- [ ] Rename کردن فایل
- [ ] Bulk operations

### بلند‌مدت
- [ ] Lazy loading برای پروژه‌های بزرگ
- [ ] Cache کردن thumbnails
- [ ] Virtual scrolling
- [ ] Incremental loading

---

**تاریخ:** 2025-11-26  
**نسخه:** 2.2  
**وضعیت:** ✅ رفع شد و آماده استفاده

---

## 🎓 دستورالعمل استفاده

### برای استفاده کامل:

```
1. Rebuild Frontend:
   cd frontend/ModelCreator.UI
   dotnet clean
   dotnet build
   dotnet run

2. باز کردن پروژه موجود:
   Home → Load Project → انتخاب پروژه
   ✅ داده‌ها خودکار Load می‌شوند

3. اضافه کردن داده جدید (اختیاری):
   Browse Files → انتخاب فایل‌ها
   لیبل‌گذاری
   Next

4. ادامه به Training:
   Model Selection → Training Config → Start!
```

**همه چیز آماده است!** 🎉

