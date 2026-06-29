# ✅ Debug Button اضافه شد!

## 🔍 **دسترسی به صفحه Debug:**

### روش 1️⃣: از Navigation Bar (ساده‌ترین)

```
┌──────────────────────────────────────────────────┐
│ 🏠 Home  📁 Projects  📊 Data Types  🚀 Features │
│                          ❓ Help  🔍 Debug       │
└──────────────────────────────────────────────────┘
```

**فقط روی دکمه `🔍 Debug` کلیک کنید!** (رنگ طلایی)

---

### روش 2️⃣: از کد

```csharp
// در هر جایی از برنامه:
NavigationService?.Navigate(new DashboardDebugPage());

// یا با Project ID:
NavigationService?.Navigate(new DashboardDebugPage("your_project_id"));
```

---

## 🧪 **استفاده از Debug Tool:**

### قدم 1: کلیک روی `🔍 Debug` در Navigation Bar

### قدم 2: Project ID را وارد کنید

از Backend logs کپی کنید:
```
INFO: GET /api/training/status/53569a3d-1248-4b5d-8e8b-be8b75556767
```

**Project ID:** `53569a3d-1248-4b5d-8e8b-be8b75556767`

### قدم 3: کلیک روی `🔄 Test API`

### قدم 4: بررسی نتیجه

#### ✅ **موفق:**
```json
{
  "status": "training",
  "current_epoch": 15,
  "total_epochs": 50,
  "train_loss": 0.0226,
  "train_acc": 0.9943
}
```

**→ API کار می‌کند! مشکل در TrainingDashboardPage است**

#### ❌ **not_started:**
```json
{
  "status": "not_started",
  "message": "No training in progress"
}
```

**→ Project ID اشتباه است یا Training شروع نشده**

#### ❌ **Network Error:**
```
❌ خطا: Unable to connect...
```

**→ Backend در حال اجرا نیست**

---

## 🎯 **سناریوهای ممکن:**

### سناریو 1: API موفق، Dashboard کار نمی‌کند

**علت:** مشکل در UI update یا data binding

**راه‌حل:**
1. Visual Studio Debug Output را بررسی کنید
2. بررسی کنید `_projectId` در Dashboard درست است
3. بررسی کنید Polling logs نمایش داده می‌شوند

### سناریو 2: Project ID اشتباه

**راه‌حل:**
1. Backend logs را باز کنید
2. Project ID صحیح را کپی کنید:
   ```
   [ProgressCallback] Updated: Epoch 15/50...
   ```
3. در Debug Tool paste کنید

### سناریو 3: Backend نیست

**راه‌حل:**
```bash
cd D:\Project\ModelCreator\backend
.\venv\Scripts\activate
python main.py
```

منتظر بمانید تا:
```
INFO: Uvicorn running on http://127.0.0.1:8181
```

---

## 📊 **مثال واقعی:**

### Backend در حال Training:

```
Epoch 15 [Train]: 100%|████████| 143/143 [00:12<00:00]
Epoch 15 [Val]:   100%|████████| 41/41 [00:08<00:00]

Epoch 15/50 Summary:
  Train Loss: 0.0226 | Train Acc: 0.9943
  Val Loss:   0.2981 | Val Acc:   0.9246

[ProgressCallback] Updated: Epoch 15/50, Loss: 0.2981, Acc: 0.9246
INFO: GET /api/training/status/53569a3d-1248-4b5d-8e8b-be8b75556767 HTTP/1.1" 200
```

### Debug Tool Test:

1. **Project ID:** `53569a3d-1248-4b5d-8e8b-be8b75556767`
2. **کلیک Test API**
3. **نتیجه:**

```
✅ Status: 200 OK

Status:    training
Epoch:     15
Loss:      0.0226
Accuracy:  99.43%

📄 API Response (JSON):
{
  "project_id": "53569a3d-1248-4b5d-8e8b-be8b75556767",
  "status": "training",
  "current_epoch": 15,
  "total_epochs": 50,
  "train_loss": 0.0226,
  "train_acc": 0.9943,
  "val_loss": 0.2981,
  "val_acc": 0.9246,
  "best_val_acc": 0.9246,
  "elapsed_time_str": "3m 45s",
  "eta_str": "8m 30s",
  "message": "Epoch 15/50 - Loss: 0.2981, Acc: 0.9246 - 12.34s/epoch"
}
```

**✅ API کامل کار می‌کند!**

---

## 🔧 **اگر Dashboard هنوز کار نمی‌کند:**

### بررسی 1: Project ID در Dashboard

در `TrainingDashboardPage.xaml`، Project Name را ببینید:

```
Project: My Model
ID: 53569a3d-1248-4b5d-8e8b-be8b75556767
```

**آیا ID مطابقت دارد؟**

### بررسی 2: Visual Studio Output

**View → Output → Debug**

باید ببینید:
```
[Dashboard] Project ID: 53569a3d-1248-4b5d-8e8b-be8b75556767
[Polling] GET /api/training/status/53569a3d-1248-4b5d-8e8b-be8b75556767
[Polling] Status: training
[Charts] Added train_loss: 0.0226, Total points: 15
```

### بررسی 3: Charts

```csharp
System.Diagnostics.Debug.WriteLine($"[Charts] Data Count: Loss={_trainLossData.Count}, Acc={_trainAccData.Count}");
```

**باید > 0 باشد**

---

## 🚀 **Build موفق:**

```bash
cd D:\Project\ModelCreator\frontend
dotnet build ModelCreator.UI
```

**✅ Build: Succeeded**  
**✅ Debug Button اضافه شد**

---

## 📝 **مراحل بعدی:**

1. ✅ Frontend را Run کنید
2. ✅ روی `🔍 Debug` کلیک کنید
3. ✅ Project ID را paste کنید
4. ✅ Test API کنید
5. ✅ JSON response را به من نشان دهید

**با این اطلاعات می‌توانیم مشکل دقیق Dashboard را پیدا کنیم! 🔍**

