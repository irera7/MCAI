# 🔍 تست قطعی: آیا Dashboard واقعاً اجرا شده؟

## ⚠️ مشکل احتمالی

از توضیحات شما به نظر می‌رسد که **داده‌های mock** می‌بینید:
- Current Epoch: 25 / 50
- Training Loss: 0.1234  
- Training Accuracy: 95.67%
- Estimated Time: 15m 23s

اما از لاگ Backend مشخص است که:
- Current Epoch: **12 / 30** (نه 25/50!)
- Training Loss: **0.2403** (نه 0.1234!)
- Training Accuracy: **92.83%** (نه 95.67%!)

---

## 🎯 این یعنی چه؟

### احتمال 1️⃣: شما در حال نگاه کردن به Designer View هستید

در Visual Studio، وقتی یک XAML file را باز می‌کنید، یک **Preview/Designer** نمایش داده می‌شود که داده‌های mock را نشان می‌دهد.

**این برنامه واقعی نیست!** این فقط پیش‌نمایش طراحی است!

### احتمال 2️⃣: برنامه Run نشده یا Crash کرده

اگر برنامه را Run کردید اما بلافاصله crash کرد، ممکن است فقط پنجره خالی یا با داده‌های اولیه ببینید.

### احتمال 3️⃣: شما Screenshot یک Mockup را نگاه می‌کنید

اگر از اینترنت یا یک مستندات screenshot دیدید، آن یک mockup طراحی بوده نه برنامه واقعی!

---

## ✅ تست قطعی: چگونه بفهمیم برنامه اجرا شده؟

### روش 1: بررسی Title Bar پنجره

**برنامه واقعی:**
```
ModelCreator - Training Dashboard
```

**Designer View:**
```
TrainingDashboardPage.xaml - Microsoft Visual Studio
```

---

### روش 2: بررسی Output Console

اگر برنامه واقعاً Run شده باشد، در **Output Console** (Debug) باید این لاگ‌ها را ببینید:

```
[Dashboard] Initialized with Project ID: 5107dfd9-3ac2-4a98-b99d-a7710c30c4cf
[Dashboard] ProjectNameText updated
[Charts] Initialized successfully
[Polling @ 14:25:12] Received Data
Status: training
Epoch: 12
Train Loss: 0.2403
```

**اگر هیچ چیز نمی‌بینید** → برنامه Run نشده!

---

### روش 3: تست با کلیک روی دکمه‌ها

در برنامه واقعی:
- کلیک روی **"⏹ Stop"** → باید یک action رخ بدهد
- کلیک روی **"💾 Save"** → باید یک پیام نمایش داده شود

در Designer View:
- کلیک روی دکمه‌ها → **هیچ اتفاقی نمی‌افتد**

---

### روش 4: بررسی Task Manager

**Windows:**
1. باز کنید Task Manager (Ctrl+Shift+Esc)
2. تب **"Details"** را انتخاب کنید
3. به دنبال **"ModelCreator.UI.exe"** بگردید

**اگر پیدا نکردید** → برنامه در حال اجرا نیست!

---

## 🚀 مراحل صحیح برای اجرای برنامه

### مرحله 1: بستن همه پنجره‌های Visual Studio

اگر Visual Studio باز است، آن را ببندید تا Designer View نبینید.

### مرحله 2: اجرا از Terminal/CMD

```bash
# باز کنید Terminal جدید (خارج از Visual Studio)
cd D:\Project\ModelCreator\frontend
dotnet run --project ModelCreator.UI
```

**منتظر بمانید تا ببینید:**
```
info: Microsoft.Hosting.Lifetime[0]
      Application started.
```

### مرحله 3: باز شدن پنجره برنامه

یک پنجره WPF باید باز شود با:
- Title: **"AI Model Builder"** یا **"ModelCreator"**
- صفحه Home با لیست پروژه‌ها

### مرحله 4: پیدا کردن پروژه فعال

در صفحه Home یا Projects:
- به دنبال پروژه‌ای با نام **"My Model"** بگردید
- یا پروژه‌ای که الان در حال training است
- Project ID: `5107dfd9-3ac2-4a98-b99d-a7710c30c4cf`

### مرحله 5: باز کردن Dashboard

کلیک کنید روی:
- **"View Training Dashboard"**
- یا **"Monitor Training"**
- یا **"Training Status"**

### مرحله 6: بررسی داده‌ها

**اگر برنامه واقعاً کار کند، باید ببینید:**
- **Current Epoch**: 12 / 30 (و هر 30 ثانیه یکبار +1)
- **Training Loss**: 0.2403 (و در حال تغییر)
- **Training Accuracy**: 92.83% (و در حال تغییر)
- **Training Logs**: پیام‌های متنی در حال اضافه شدن

**اگر همچنان می‌بینید 25/50, 0.1234, 95.67%**:
→ این Designer View است، نه برنامه واقعی!

---

## 🎬 ویدیوی راهنما (مراحل دقیق)

### 1. بستن Visual Studio

```
File → Close Solution
یا
Alt+F4
```

### 2. باز کردن Terminal

```
Windows Key + R
نوشتن: cmd
Enter
```

### 3. اجرای برنامه

```cmd
cd /d D:\Project\ModelCreator\frontend
dotnet run --project ModelCreator.UI
```

### 4. منتظر ماندن

```
منتظر بمانید 5-10 ثانیه تا برنامه شروع شود
یک پنجره WPF باید ظاهر شود
```

### 5. باز کردن Dashboard

```
Home → Projects → پروژه "My Model" → View Training Dashboard
```

### 6. بررسی اعداد

```
آیا Epoch = 12/30 است؟
آیا Loss = 0.2403 است؟
آیا هر چند ثانیه تغییر می‌کند؟
```

---

## 🐛 اگر برنامه Crash کرد

### خطای رایج 1: Port در حال استفاده است

```
Error: Address already in use
```

**راه حل:**
```bash
# بستن process قبلی
taskkill /F /IM ModelCreator.UI.exe
```

### خطای رایج 2: Backend در دسترس نیست

```
Connection refused to http://127.0.0.1:8181
```

**راه حل:**
```bash
# Terminal جدید
cd D:\Project\ModelCreator\backend
python main.py
```

### خطای رایج 3: Missing DLL

```
System.IO.FileNotFoundException: Could not load file or assembly
```

**راه حل:**
```bash
cd frontend
dotnet restore
dotnet build
dotnet run --project ModelCreator.UI
```

---

## ✅ چک‌لیست نهایی

قبل از اینکه بگویید "داده‌های mock نمایش داده می‌شوند":

- [ ] Visual Studio را بستم (Designer View را ندارم)
- [ ] برنامه را از Terminal با `dotnet run` اجرا کردم
- [ ] یک پنجره WPF واقعی باز شد (نه یک tab در Visual Studio)
- [ ] صفحه Home را دیدم
- [ ] پروژه را پیدا کردم و Dashboard را باز کردم
- [ ] در Task Manager، `ModelCreator.UI.exe` را می‌بینم
- [ ] Backend هم در حال اجرا است (`python main.py`)
- [ ] در Dashboard، اعداد **25/50, 0.1234** را می‌بینم (نه 12/30, 0.2403)

**اگر همه چک‌لیست‌ها ✅ هستند و باز هم mock می‌بینید:**
→ لطفاً یک **screenshot از کل صفحه** (با Title Bar) بفرستید تا ببینم دقیقاً چه چیزی نمایش داده می‌شود!

---

## 📸 مثال: برنامه واقعی vs Designer View

### ❌ Designer View (Mock Data)
```
┌─────────────────────────────────────────────────────┐
│ TrainingDashboardPage.xaml - Visual Studio         │ ← Title
├─────────────────────────────────────────────────────┤
│ [Design] [XAML] [Split]                           │ ← Tabs
│                                                     │
│  Training Dashboard                                 │
│  Project: My Model                                  │
│                                                     │
│  Current Epoch    Training Loss    ...             │
│     25 / 50          0.1234                        │ ← Mock
│  ▓▓▓▓▓▓▓▓░░░░                                      │
└─────────────────────────────────────────────────────┘
```

### ✅ برنامه واقعی (Live Data)
```
┌─────────────────────────────────────────────────────┐
│ AI Model Builder                                    │ ← Title
├─────────────────────────────────────────────────────┤
│                                                     │
│  Training Dashboard                                 │
│  Project: My Model                                  │
│                                                     │
│  Current Epoch    Training Loss    ...             │
│     12 / 30          0.2403                        │ ← Live
│  ▓▓▓▓░░░░░░░░░░                                    │
│                                                     │
│  Training Logs                                      │
│  14:25:12 - 🔄 اتصال به سیستم...                  │ ← Logs
│  14:25:13 - ✅ اتصال برقرار شد!                    │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 نتیجه

**لطفاً مطمئن شوید که:**
1. ✅ Visual Studio را بسته‌اید
2. ✅ برنامه را از Terminal اجرا کرده‌اید
3. ✅ یک پنجره WPF واقعی باز شده (نه Designer)
4. ✅ Backend در حال اجرا است
5. ✅ Dashboard را از داخل برنامه واقعی باز کرده‌اید

**اگر همچنان مشکل دارید**, لطفاً:
- Screenshot از **کل صفحه** (با Title Bar و Task Bar)
- یا Output Console (Debug) را کپی کنید و بفرستید

تا بتوانم ببینم دقیقاً چه اتفاقی دارد می‌افتد! 🔍

