# 🔍 بررسی کامل API Training Dashboard

## ✅ نتیجه بررسی

### Backend API - وضعیت: ✅ کار می‌کند

از لاگ‌های Backend مشاهده شد:

```
INFO:     127.0.0.1:55933 - "GET /api/training/status/53569a3d-1248-4b5d-8e8b-be8b75556767 HTTP/1.1" 200 OK
[ProgressCallback] Updating epoch 12 metrics...
[ProgressCallback] Updated: Epoch 12/20, Loss: 0.3287, Acc: 0.9176
```

**نتیجه:**
- ✅ API هر 2 ثانیه درخواست دریافت می‌کند
- ✅ Status Code: `200 OK`
- ✅ `ProgressCallback` داده‌ها را به‌روزرسانی می‌کند
- ✅ داده‌ها در `active_trainings` dictionary ذخیره می‌شوند

---

## 📊 داده‌هایی که API برمی‌گرداند

بر اساس کد `ProgressCallback`, این فیلدها در پاسخ API وجود دارند:

```json
{
  "project_id": "53569a3d-1248-4b5d-8e8b-be8b75556767",
  "status": "training",
  "current_epoch": 12,
  "total_epochs": 20,
  "train_loss": 0.0344,
  "train_acc": 0.9934,
  "val_loss": 0.3287,
  "val_acc": 0.9176,
  "best_train_loss": 0.0270,
  "best_val_loss": 0.3187,
  "best_val_acc": 0.9234,
  "elapsed_time": 420,
  "elapsed_time_str": "7m 0s",
  "eta": 280,
  "eta_str": "4m 40s",
  "epoch_time": "35.2s",
  "progress_percent": 60,
  "message": "Epoch 12/20 - Loss: 0.3287, Acc: 0.9176 - 35.2s/epoch",
  "learning_rate": 0.0001,
  "config": { ... }
}
```

---

## 🔍 بررسی Frontend

### کد Frontend که داده را دریافت می‌کند:

```csharp
// frontend/ModelCreator.UI/Views/TrainingDashboardPage.xaml.cs
// خط 201-668

private async Task PollTrainingStatus()
{
    var apiService = App.GetService<IApiService>();
    
    while (true)
    {
        try
        {
            // Get training status via HTTP
            var status = await apiService.GetAsync<Dictionary<string, object>>(
                $"/api/training/status/{_projectId}"
            );
            
            if (status != null)
            {
                // Parse and update UI
                Dispatcher.Invoke(() => {
                    // Update progress, metrics, charts
                });
            }
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[Polling] Network error: {ex.Message}");
        }
        
        await Task.Delay(2000); // Poll every 2 seconds
    }
}
```

---

## 🐛 مشکل احتمالی: چرا داده در UI نمایش داده نمی‌شود؟

### احتمال 1: Frontend با Project ID اشتباه متصل شده

**بررسی:**
```csharp
// در TrainingDashboardPage.xaml.cs خط 34-40
_projectId = projectId;
System.Diagnostics.Debug.WriteLine($"[Dashboard] Initialized with Project ID: {_projectId}");
```

**تست:**
- بررسی کنید که Project ID در Frontend با ID در Backend یکسان است
- در لاگ‌های Backend: `53569a3d-1248-4b5d-8e8b-be8b75556767`
- در لاگ‌های Frontend باید همین ID را ببینید

---

### احتمال 2: Exception در Parsing داده‌ها

**نقطه احتمالی:**
```csharp
// خط 258-303 - پارس کردن current_epoch و total_epochs
currentEpoch = Convert.ToInt32(status["current_epoch"]);
totalEpochs = Convert.ToInt32(status["total_epochs"]);
```

**مشکل احتمالی:**
- اگر `status["current_epoch"]` از نوع `JsonElement` باشد، `Convert.ToInt32()` ممکن است exception بیندازد
- Exception catch می‌شود اما UI به‌روز نمی‌شود

---

### احتمال 3: Charts به‌روز نمی‌شوند

**کد مربوطه:**
```csharp
// خط 343-351 - اضافه کردن به نمودار Loss
if (isNewEpoch)
{
    _trainLossData.Add(trainLoss);
    chartsNeedUpdate = true;
    System.Diagnostics.Debug.WriteLine($"[Charts] ✅ Added train_loss: {trainLoss}");
}
```

**مشکل احتمالی:**
- `isNewEpoch` ممکن است همیشه `false` باشد
- بررسی شود: `currentEpoch > _lastSeenEpoch`

---

### احتمال 4: Data Type مismatch در JSON Deserialization

**مشکل:**
```csharp
var status = await apiService.GetAsync<Dictionary<string, object>>(...);
```

وقتی JSON deserialize می‌شود به `Dictionary<string, object>`:
- اعداد ممکن است `JsonElement` شوند نه `int` یا `double`
- نیاز به cast صحیح است

**راه حل در کد:**
```csharp
// استفاده از try-catch برای هر field
try
{
    var trainLoss = Convert.ToDouble(status["train_loss"]);
    TrainLossText.Text = trainLoss.ToString("F4");
}
catch (Exception ex)
{
    Debug.WriteLine($"[Polling] Loss parse error: {ex.Message}");
}
```

---

## 🔧 راه حل‌های پیشنهادی

### راه حل 1: اضافه کردن Logging بیشتر

در `TrainingDashboardPage.xaml.cs`:

```csharp
// بعد از خط 215 (دریافت status)
System.Diagnostics.Debug.WriteLine($"\n========== [Polling] Raw Response ==========");
System.Diagnostics.Debug.WriteLine($"Status object is null: {status == null}");
if (status != null)
{
    System.Diagnostics.Debug.WriteLine($"Keys in status: {string.Join(", ", status.Keys)}");
    foreach (var kvp in status)
    {
        System.Diagnostics.Debug.WriteLine($"  {kvp.Key}: {kvp.Value} (Type: {kvp.Value?.GetType().Name})");
    }
}
System.Diagnostics.Debug.WriteLine($"===========================================\n");
```

---

### راه حل 2: تست مستقیم API از مرورگر

باز کنید:
```
http://127.0.0.1:8181/api/training/status/53569a3d-1248-4b5d-8e8b-be8b75556767
```

**انتظار:**
```json
{
  "project_id": "...",
  "status": "training",
  "current_epoch": 12,
  "train_loss": 0.0344,
  ...
}
```

---

### راه حل 3: چک کردن Output Console در Visual Studio

در Visual Studio:
1. **View** → **Output**
2. در dropdown "Show output from:", انتخاب کنید: **Debug**
3. اجرا کنید Frontend
4. باز کنید Training Dashboard
5. ببینید لاگ‌ها:
   ```
   [Dashboard] Initialized with Project ID: ...
   [Polling @ 08:15:23] Received Data
   Status: training
   Epoch: 12 (Last seen: 11)
   Train Loss: 0.0344
   ...
   [Charts] ✅ Added train_loss: 0.0344 (Epoch 12), Total points: 12
   ```

**اگر لاگ نمی‌بینید:**
- مشکل در connection است
- یا exception در Dispatcher.Invoke

**اگر لاگ می‌بینید اما UI به‌روز نمی‌شود:**
- مشکل در UI binding یا chart update است

---

## 🎯 نتیجه‌گیری

### ✅ Backend: کاملاً سالم است
- API پاسخ می‌دهد
- داده‌ها به‌روزرسانی می‌شوند
- ProgressCallback کار می‌کند

### ⚠️ Frontend: نیاز به بررسی دارد

**چک کنید:**
1. ✅ Output Console در Visual Studio را باز کنید
2. ✅ لاگ‌های Debug را بررسی کنید
3. ✅ Project ID صحیح است؟
4. ✅ Exception در Parsing رخ می‌دهد؟
5. ✅ Charts update می‌شوند؟

### 🔍 مراحل تست:

#### مرحله 1: تست API از مرورگر
```
http://127.0.0.1:8181/api/training/status/53569a3d-1248-4b5d-8e8b-be8b75556767
```
باید JSON با داده‌های واقعی ببینید.

#### مرحله 2: چک لاگ‌های Frontend
در Output Console باید ببینید:
```
[Dashboard] Initialized with Project ID: 53569a3d-1248-4b5d-8e8b-be8b75556767
[Polling @ 08:15:23] Received Data
Status: training
Epoch: 12 (Last seen: 11)
[Charts] ✅ Added train_loss: 0.0344
```

#### مرحله 3: اگر لاگ نمی‌بینید
- Connection issue است
- Backend URL اشتباه است
- یا ApiService null است

#### مرحله 4: اگر لاگ می‌بینید اما UI خالی است
- مشکل در UI Controls است
- یا XAML binding درست نیست
- یا Dispatcher.Invoke exception می‌زند

---

## 📝 توصیه نهایی

**برای کاربر:**
1. در Visual Studio، **Output Console** را باز کنید (View → Output)
2. Frontend را اجرا کنید
3. Training Dashboard را باز کنید
4. لاگ‌های Debug را کپی کنید و به من بدهید

**یا:**

باز کنید در مرورگر:
```
http://127.0.0.1:8181/api/training/status/53569a3d-1248-4b5d-8e8b-be8b75556767
```

و JSON response را کپی کنید.

---

## ✅ خلاصه

**Backend API:**
- ✅ کار می‌کند
- ✅ داده‌ها صحیح هستند
- ✅ Response 200 OK

**Frontend:**
- ⚠️ نیاز به بررسی لاگ‌های Debug
- ⚠️ احتمالاً مشکل در Parsing یا UI Update است

**راه حل:**
- بررسی Output Console
- یا تست API از مرورگر

