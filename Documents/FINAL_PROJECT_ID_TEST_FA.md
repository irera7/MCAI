# 🔍 تست نهایی: بررسی Project ID در Dashboard

## ✅ تغییرات جدید

من کد را تغییر دادم تا **Project ID را به صورت بسیار واضح** نمایش دهد:

### 1. در بالای صفحه (Project Name):
```
Project: TEstt2 (ID: 7e0bbe13-3299...)
```

### 2. در پایین صفحه (Status Bar):
```
🔍 DEBUG: Monitoring Project ID: 7e0bbe13-3299-4337-a651-422ba9377a4d
```

---

## 🧪 مراحل تست

### مرحله 1: بستن برنامه فعلی
```
کلیک روی X
```

### مرحله 2: اجرای نسخه جدید
```bash
cd D:\Project\ModelCreator\frontend
dotnet run --project ModelCreator.UI
```

### مرحله 3: باز کردن Dashboard

1. Home → Projects
2. **هر پروژه‌ای** را باز کنید
3. اگر training دارد → Dashboard باز می‌شود

### مرحله 4: بررسی Project ID

**نگاه کنید به**:
- ✅ **بالای صفحه** (زیر "Training Dashboard")
- ✅ **پایین صفحه** (Status Bar)

**باید ببینید**:
```
🔍 DEBUG: Monitoring Project ID: 7e0bbe13-3299-4337-a651-422ba9377a4d
```

---

## 🎯 مقایسه با Backend

### در Backend Logs:
```
INFO: ... "GET /api/training/status/7e0bbe13-3299-4337-a651-422ba9377a4d HTTP/1.1" 200 OK
```

### در Dashboard باید ببینید:
```
🔍 DEBUG: Monitoring Project ID: 7e0bbe13-3299-4337-a651-422ba9377a4d
```

**اگر IDs یکسان هستند** ✅ → Project صحیح است!

**اگر IDs متفاوت هستند** ❌ → Bug در کد است!

---

## 📊 سناریوهای مختلف

### سناریو A: IDs یکسان هستند
```
Dashboard: 7e0bbe13-3299...
Backend:   7e0bbe13-3299...  ← یکسان ✅
```

**یعنی**: Project صحیح است، اما مشکل در Dispatcher یا Polling است.

---

### سناریو B: IDs متفاوت هستند
```
Dashboard: abc123...
Backend:   7e0bbe13-3299...  ← متفاوت ❌
```

**یعنی**: Dashboard برای پروژه اشتباه باز شده! Bug در navigation است.

---

### سناریو C: Backend هیچ request برای Project ID در Dashboard دریافت نمی‌کند

```
Dashboard: 7e0bbe13-3299...
Backend:   [هیچ لاگی برای این ID] ❌
```

**یعنی**: Polling اصلاً به Backend متصل نمی‌شود!

---

## 🐛 اگر IDs متفاوت هستند

اگر Project IDs یکسان نیستند، یعنی bug در یکی از این جاهاست:

### 1. ProjectsPage.xaml.cs
```csharp
window?.MainFrame.Navigate(new TrainingDashboardPage(
    project.Id,  ← آیا این ID صحیح است?
    project.Name
));
```

### 2. HomePage یا navigation دیگر
```csharp
// آیا جای دیگری Dashboard با ID hardcoded باز می‌شود?
```

### 3. TrainingDashboardPage Constructor
```csharp
_projectId = projectId;  ← آیا parameter صحیح دریافت می‌شود?
```

---

## 🎯 چک‌لیست تست

- [ ] برنامه را Restart کردم
- [ ] یک پروژه که training دارد را باز کردم
- [ ] Dashboard باز شد
- [ ] در **بالای صفحه** Project ID را می‌بینم
- [ ] در **پایین صفحه** Project ID را می‌بینم
- [ ] Project ID با Backend logs **یکسان است**
- [ ] اگر یکسان نیست → Screenshot بفرستم

---

## 📸 چه چیزی باید ببینید

```
┌─────────────────────────────────────────────────┐
│ Training Dashboard                              │
│ Project: TEstt2 (ID: 7e0bbe13-3299...)    ← بالا
├─────────────────────────────────────────────────┤
│ Current Epoch: ...                              │
│ Training Loss: ...                              │
│ ...                                             │
├─────────────────────────────────────────────────┤
│ 🔍 DEBUG: Monitoring Project ID:                │
│    7e0bbe13-3299-4337-a651-422ba9377a4d   ← پایین
└─────────────────────────────────────────────────┘
```

---

## ✅ اقدام بعدی

**لطفاً**:

1. Restart کنید برنامه
2. Dashboard را باز کنید
3. Screenshot بگیرید که **کل صفحه** را نشان دهد (با Project ID در بالا و پایین)
4. به من بگویید: **Project ID در Dashboard چیست?**
5. من آن را با Backend logs مقایسه می‌کنم

---

**این تست قطعی است!** با این روش دقیقاً می‌فهمیم مشکل از کجاست! 🎯

