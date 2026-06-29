# 🐛 راهنمای رفع مشکل "همه چیز 0 است" بعد از Import CSV

## 🔴 مشکل
بعد از Import از CSV، آمار همه‌چیز 0 نمایش می‌دهد:
- Total Samples: 0
- Labeled: 0
- کل فایل‌ها در لیست: 0

---

## 🔍 علت‌های احتمالی

### 1️⃣ پوشه اشتباه انتخاب شده
**علامت:**
```
⚠️ X فایل در پوشه انتخابی پیدا نشد!
هیچ فایلی پیدا نشد!
```

**چرا؟**
- فایل CSV می‌گوید: `Image_1.jpg`
- اما شما پوشه‌ای را انتخاب کردید که `Image_1.jpg` در آن نیست!

**راه‌حل:**
```
1. فایل CSV را باز کنید
2. ببینید نام فایل‌ها چیست (مثلاً Image_1.jpg)
3. این فایل‌ها را در کامپیوتر پیدا کنید
4. دوباره Import CSV کنید و پوشه صحیح را انتخاب کنید
```

---

### 2️⃣ نام فایل‌ها مطابقت ندارند

**مثال مشکل:**
```csv
در CSV:       Image_1.jpg
در پوشه:     image_1.jpg  ❌ (حروف کوچک)
              IMG_1.jpg    ❌ (نام متفاوت)
              Image_01.jpg ❌ (فرمت عدد متفاوت)
```

**راه‌حل:**
```bash
# بررسی کنید نام فایل‌ها دقیقاً چیست:
cd D:\Images
dir *.jpg

# مقایسه کنید با CSV
# باید دقیقاً یکسان باشند!
```

---

### 3️⃣ ساختار CSV اشتباه است

**فرمت‌های اشتباه:**
```csv
❌ بدون header و فقط 1 ستون:
Image_1.jpg
Image_2.jpg

❌ با Tab به جای Comma:
Image_1.jpg	Class_A
Image_2.jpg	Class_B

❌ با semicolon:
Image_1.jpg;Class_A
Image_2.jpg;Class_B
```

**فرمت صحیح:**
```csv
✅ با header:
filename,label
Image_1.jpg,Class_A
Image_2.jpg,Class_B

✅ بدون header:
Image_1.jpg,Class_A
Image_2.jpg,Class_B
```

---

## 🔧 راه‌حل گام به گام

### مرحله 1: بررسی Debug Output

1. **Frontend را از Visual Studio اجرا کنید**
2. **View → Output** را باز کنید
3. **Show output from: Debug** را انتخاب کنید
4. دوباره Import CSV کنید
5. به خروجی نگاه کنید:

```
باید ببینید:
✅ Total lines in CSV: 6501
✅ Header detected, skipping first line
✅ Parsed line 2: Image_1.jpg -> SOUTHERN DOGFACE
✅ Parsed line 3: Image_2.jpg -> ADONIS
✅ Parsed 6500 entries from CSV (success: 6500, errors: 0)
✅ Found 75 unique labels: ...
✅ Added new label: SOUTHERN DOGFACE
...
✅ Added new file: Image_1.jpg (D:\...\Image_1.jpg) -> SOUTHERN DOGFACE
...
✅ Files added: 6500
✅ Total items in dataItems: 6500
```

اگر می‌بینید:
```
❌ Files added: 0
❌ Missing files: 6500
❌ File not found: Image_1.jpg
```

→ پوشه اشتباه است!

---

### مرحله 2: بررسی ساختار CSV

```bash
# در Notepad یا VS Code فایل CSV را باز کنید
# خط اول باید باشد:
filename,label

# خط دوم:
Image_1.jpg,SOUTHERN DOGFACE

# NOT:
Image_1.jpg SOUTHERN DOGFACE    ❌ (بدون comma)
Image_1.jpg;SOUTHERN DOGFACE    ❌ (semicolon)
Image_1.jpg	SOUTHERN DOGFACE    ❌ (tab)
```

---

### مرحله 3: پیدا کردن پوشه صحیح

```bash
# روش 1: جستجو در Windows
1. Win + S (Search)
2. نام یکی از فایل‌های CSV را بنویسید: Image_1.jpg
3. پیدا کنید و پوشه آن را یادداشت کنید

# روش 2: از CMD
cd C:\
dir /s Image_1.jpg

# باید مسیر را پیدا کنید، مثلاً:
C:\Users\EPN\Downloads\archive\train\Image_1.jpg
                                  ↑
                                  این پوشه را انتخاب کنید
```

---

### مرحله 4: Import مجدد

```
1. دوباره "Import CSV" کلیک کنید
2. همان فایل CSV را انتخاب کنید
3. این بار پوشه صحیح را انتخاب کنید:
   مثلاً: C:\Users\EPN\Downloads\archive\train\
4. باید پیام موفقیت ببینید:
   ✅ 6500 فایل جدید اضافه شد
   ✅ کل فایل‌ها در لیست: 6500
```

---

## 📋 Checklist Debug

- [ ] فایل CSV با فرمت صحیح است (filename,label)
- [ ] CSV حداقل 1 سطر داده دارد (غیر از header)
- [ ] فایل‌های تصویر واقعاً در کامپیوتر وجود دارند
- [ ] نام فایل‌ها در CSV دقیقاً با نام واقعی مطابقت دارد
- [ ] پوشه‌ای که فایل‌ها در آن هستند را انتخاب کرده‌اید
- [ ] Debug Output را بررسی کرده‌اید
- [ ] پیام موفقیت دیده‌اید (نه 0 فایل!)

---

## 🧪 تست سریع

### ایجاد یک تست ساده:

#### 1. ایجاد پوشه تست
```bash
mkdir C:\Test\Images
```

#### 2. کپی کردن 4 تصویر
```
کپی کنید:
- cat.jpg
- dog.jpg  
- bird.jpg
- fish.jpg

به پوشه: C:\Test\Images\
```

#### 3. ایجاد CSV تست
فایل: `C:\Test\test.csv`
```csv
filename,label
cat.jpg,cat
dog.jpg,dog
bird.jpg,bird
fish.jpg,fish
```

#### 4. Import در Frontend
```
1. Import CSV
2. انتخاب: C:\Test\test.csv
3. انتخاب پوشه: C:\Test\Images\
4. باید ببینید:
   ✅ 4 فایل جدید اضافه شد
   ✅ کل فایل‌ها در لیست: 4
   ✅ فایل‌های لیبل‌شده: 4
```

اگر این کار کرد → سیستم درست کار می‌کند!  
اگر 0 نمایش داد → پوشه اشتباه انتخاب کردید!

---

## 💡 نکات مهم

### 1. حتماً پوشه‌ای که فایل‌ها در آن هستند را انتخاب کنید

```
❌ اشتباه:
CSV: C:\Data\labels.csv
انتخاب پوشه: C:\Data\  ← فایل‌ها اینجا نیستند!

✅ درست:
CSV: C:\Data\labels.csv
فایل‌ها: C:\Data\Images\Image_1.jpg
انتخاب پوشه: C:\Data\Images\  ← اینجا را انتخاب کنید!
```

### 2. سیستم در زیرپوشه‌ها هم جستجو می‌کند

```
اگر ساختار این باشد:
C:\Data\
  Images\
    Train\
      Class_A\
        Image_1.jpg
      Class_B\
        Image_2.jpg

می‌توانید:
- پوشه C:\Data\Images\ را انتخاب کنید
- یا حتی C:\Data\ را انتخاب کنید
سیستم در همه زیرپوشه‌ها جستجو می‌کند!
```

### 3. مطمئن شوید CSV درست Parse شده

```
در Debug Output باید ببینید:
✅ Parsed 6500 entries from CSV (success: 6500, errors: 0)

اگر می‌بینید:
❌ Parsed 0 entries from CSV (success: 0, errors: 6500)
→ فرمت CSV اشتباه است!
```

---

## 📞 همچنان کار نمی‌کند؟

### اطلاعات لازم برای Debug:

1. **محتوای 5 خط اول CSV:**
   ```
   (کپی کنید و بفرستید)
   ```

2. **مسیر پوشه تصاویر:**
   ```
   (مثلاً: C:\Users\EPN\Downloads\archive\train\)
   ```

3. **نام 5 فایل اول در پوشه:**
   ```bash
   cd "C:\Users\EPN\Downloads\archive\train"
   dir *.jpg /b | head -5
   ```

4. **Debug Output:**
   ```
   (کپی کنید Output Window را)
   ```

با این اطلاعات می‌توانیم مشکل دقیق را پیدا کنیم!

---

## ✅ علامت موفقیت

بعد از Import صحیح، باید ببینید:

```
پیام:
✅ Import از CSV کامل شد!

📊 آمار:
  • تعداد کل در CSV: 6500 ردیف
  • 75 لیبل جدید اضافه شد
  • 6500 فایل جدید اضافه شد
  • 6500 فایل لیبل‌گذاری شد

📂 وضعیت فعلی:
  • کل فایل‌ها در لیست: 6500
  • فایل‌های لیبل‌شده: 6500
  • کل لیبل‌ها: 75
```

و در صفحه:
```
Total Samples: 6500  ✅
Labeled: 6500        ✅
Unlabeled: 0         ✅
```

---

**آخرین بروزرسانی:** 2025-11-26  
**نسخه:** 1.1 (با Debug بهتر)

