# 🔍 Training Dashboard Troubleshooting Guide
# 🔍 راهنمای عیب‌یابی Dashboard آموزش

## 🐛 **مشکلات گزارش شده:**

1. ❌ **Current Epoch از 25 شروع می‌شود و تغییر نمی‌کند**
2. ❌ **چارت‌ها خالی هستند** (فقط محورها نمایش داده می‌شوند)
3. ❌ **متریک‌ها ثابت هستند** (0.1234, 95.67%, 26m 14s)

## 🎯 **علت اصلی:**

**Backend داده‌های Static/Mock را برمی‌گرداند یا Training واقعاً شروع نشده است!**

---

## ✅ **بررسی گام به گام:**

### قدم 1️⃣: بررسی کنید Training واقعاً شروع شده است؟

در UI که نشان می‌دهید:
- `Current Epoch: 25 / 50`
- `Training Loss: 0.1234`
- `Training Accuracy: 95.67%`

**این مقادیر MOCK/DEFAULT هستند** که در XAML تعریف شده‌اند:

```xml
<!-- در TrainingDashboardPage.xaml -->
<TextBlock x:Name="CurrentEpochText"
          Text="25 / 50"  <!-- ❌ مقدار اولیه -->
          .../>

<TextBlock x:Name="TrainLossText"
          Text="0.1234"  <!-- ❌ مقدار اولیه -->
          .../>

<TextBlock x:Name="TrainAccText"
          Text="95.67%"  <!-- ❌ مقدار اولیه -->
          .../>
```

**اگر این مقادیر تغییر نمی‌کنند → Backend داده واقعی نمی‌فرستد!**

---

### قدم 2️⃣: بررسی Backend Logs

وقتی Training Dashboard را باز می‌کنید، Backend باید log هایی مثل این نمایش دهد:

```
[Status Check] Project my_project_id - Epoch: 1, Status: training
[ProgressCallback] Updating epoch 1 metrics...
[ProgressCallback] Updated: Epoch 1/50, Loss: 0.5432, Acc: 0.7856
```

**اگر این log ها را نمی‌بینید:**
- ✅ Backend در حال اجرا است؟
- ✅ Training شروع شده است؟
- ✅ Project ID صحیح است؟

---

### قدم 3️⃣: بررسی API Response

#### روش A: از مرورگر

```
http://127.0.0.1:8181/api/training/status/your_project_id
```

**پاسخ مورد انتظار (اگر Training در حال اجرا نیست):**
```json
{
  "project_id": "your_project_id",
  "status": "not_started",
  "message": "No training in progress"
}
```

**پاسخ مورد انتظار (اگر Training در حال اجرا است):**
```json
{
  "project_id": "your_project_id",
  "status": "training",
  "current_epoch": 3,
  "total_epochs": 50,
  "train_loss": 0.5432,
  "train_acc": 0.7856,
  "val_loss": 0.6123,
  "val_acc": 0.7234,
  "best_val_acc": 0.7856,
  "elapsed_time_str": "2m 15s",
  "eta_str": "38m 45s",
  "message": "Epoch 3/50 - Loss: 0.6123, Acc: 0.7234 - 15.34s/epoch"
}
```

#### روش B: از Terminal

```bash
curl http://127.0.0.1:8181/api/training/status/your_project_id
```

---

### قدم 4️⃣: شروع Training

اگر Training شروع نشده، باید آن را شروع کنید:

#### از UI:
1. به **Create Project** بروید
2. یک پروژه جدید بسازید
3. داده‌ها را آپلود کنید
4. **Start Training** را کلیک کنید
5. به **Training Dashboard** بروید

#### از API مستقیماً:

```bash
curl -X POST "http://127.0.0.1:8181/api/training/start" \
  -H "Content-Type: application/json" \
  -d "{
    \"project_id\": \"test_project_123\",
    \"model_id\": \"resnet18\",
    \"modality\": \"image\",
    \"data_path\": \"D:/Project/ModelCreator/data/sample\",
    \"epochs\": 10,
    \"batch_size\": 32,
    \"learning_rate\": 0.001
  }"
```

---

### قدم 5️⃣: بررسی Project ID صحیح

Dashboard به این صورت ایجاد می‌شود:

```csharp
var dashboard = new TrainingDashboardPage(projectId, projectName);
```

**مطمئن شوید `projectId` با همان ID که Training را شروع کردید مطابقت دارد!**

---

## 🔧 **Debug در Frontend:**

### بررسی Debug Output:

وقتی Dashboard باز است، در **Output** window در Visual Studio باید ببینید:

```
[Charts] Initialized successfully
[Polling] Status: training
[Charts] Added train_loss: 0.5432, Total points: 1
[Charts] Added train_acc: 0.7856, Total points: 1
[Charts] Updated - Loss: 1 points, Acc: 1 points
```

**اگر این log ها را نمی‌بینید:**

1. Output window را باز کنید: **View → Output**
2. از dropdown "Show output from:" گزینه **Debug** را انتخاب کنید
3. Dashboard را Reload کنید

---

## 🧪 **تست کامل:**

### 1️⃣ Backend را Start کنید:

```bash
cd D:\Project\ModelCreator\backend
.\venv\Scripts\activate
python main.py
```

منتظر بمانید تا ببینید:
```
INFO: Uvicorn running on http://127.0.0.1:8181
```

### 2️⃣ Training شروع کنید (از Terminal):

```bash
curl -X POST "http://127.0.0.1:8181/api/training/start" \
  -H "Content-Type: application/json" \
  -d "{
    \"project_id\": \"dashboard_test\",
    \"model_id\": \"resnet18\",
    \"modality\": \"image\",
    \"data_path\": \"D:/Project/ModelCreator/data/sample\",
    \"epochs\": 10,
    \"batch_size\": 16,
    \"learning_rate\": 0.001
  }"
```

**Backend باید نمایش دهد:**
```
[Training] Starting training for project dashboard_test
Building resnet18 model...
Training started - 10 epochs on cuda
```

### 3️⃣ Status را بررسی کنید:

```bash
curl http://127.0.0.1:8181/api/training/status/dashboard_test
```

**باید JSON با current_epoch, train_loss, etc. برگرداند**

### 4️⃣ Frontend را Start کنید:

```bash
cd D:\Project\ModelCreator\frontend
dotnet run --project ModelCreator.UI
```

### 5️⃣ Dashboard را باز کنید:

- از Home به **Training Dashboard** بروید
- یا مستقیماً navigate کنید با `project_id = "dashboard_test"`

### ✅ **انتظار:**

- ✅ **Current Epoch** از 0 شروع می‌شود و هر چند ثانیه increase می‌شود: `1 / 10 → 2 / 10 → ...`
- ✅ **Training Loss** تغییر می‌کند: `2.3456 → 1.8765 → 1.2345 → ...`
- ✅ **Training Accuracy** افزایش می‌یابد: `25.34% → 45.67% → 68.92% → ...`
- ✅ **چارت Loss** خط نزولی نمایش می‌دهد
- ✅ **چارت Accuracy** خط صعودی نمایش می‌دهد
- ✅ **Progress Bar** پر می‌شود
- ✅ **ETA** کاهش می‌یابد: `15m 30s → 12m 45s → 10m 20s → ...`
- ✅ **Logs** real-time اضافه می‌شوند

---

## 🚨 **مشکلات احتمالی:**

### مشکل 1: Backend در دسترس نیست

**علامت:**
```
[Polling] Network error: ...
❌ خطا در اتصال به سرور
```

**راه‌حل:**
```bash
cd D:\Project\ModelCreator\backend
.\venv\Scripts\activate
python main.py
```

### مشکل 2: Training شروع نشده

**علامت:**
```json
{
  "status": "not_started",
  "message": "No training in progress"
}
```

**راه‌حل:**
- Training را از UI یا API شروع کنید

### مشکل 3: Project ID اشتباه است

**علامت:**
- همیشه status "not_started" است
- اما می‌دانید Training در حال اجرا است

**راه‌حل:**
- Project ID صحیح را بررسی کنید
- از همان ID استفاده کنید که برای `/api/training/start` استفاده کردید

### مشکل 4: Data Path اشتباه است

**علامت:**
```
Training failed: No such file or directory: 'D:/...'
```

**راه‌حل:**
- مسیر داده‌ها را بررسی کنید
- مطمئن شوید پوشه شامل زیرپوشه‌های class است:
  ```
  data/
    class_a/
      img1.jpg
      img2.jpg
    class_b/
      img3.jpg
      img4.jpg
  ```

---

## 📝 **چک‌لیست عیب‌یابی:**

- [ ] Backend در حال اجرا است (`http://127.0.0.1:8181`)
- [ ] Training شروع شده است (از UI یا API)
- [ ] `/api/training/status/{project_id}` داده‌های واقعی برمی‌گرداند (نه Mock)
- [ ] Project ID در Dashboard با Training ID مطابقت دارد
- [ ] Data path صحیح است و داده‌ها موجود هستند
- [ ] Frontend Debug Output را نمایش می‌دهد
- [ ] Backend Logs را نمایش می‌دهد

---

## 🎯 **نتیجه‌گیری:**

**مشکل اصلی** این نیست که چارت‌ها update نمی‌شوند، بلکه:

1. **Training شروع نشده است** → Current Epoch ثابت می‌ماند
2. **Backend داده Mock برمی‌گرداند** → متریک‌ها تغییر نمی‌کنند
3. **Project ID اشتباه است** → `/api/training/status` می‌گوید "not_started"

**راه‌حل:**
1. Training را **واقعاً** شروع کنید
2. Project ID **صحیح** را در Dashboard استفاده کنید
3. Backend logs و API response را **بررسی** کنید

**بعد از شروع Training واقعی، همه چیز به صورت real-time به‌روزرسانی می‌شود! ✅**

---

## 📞 **برای کمک بیشتر:**

لطفاً موارد زیر را ارسال کنید:
1. Backend logs (output از `python main.py`)
2. API response از `/api/training/status/{project_id}`
3. Frontend Debug output (از Visual Studio Output window)
4. چطور Training را شروع کردید؟

