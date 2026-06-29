# ✅ Training Dashboard Real-Time Updates Fixed
# ✅ به‌روزرسانی Real-Time Dashboard آموزش اصلاح شد

## 🐛 **مشکل گزارش شده:**

Training Dashboard فقط لاگ‌ها را نمایش می‌داد و:
- ❌ چارت‌ها به‌روزرسانی نمی‌شدند
- ❌ متریک‌ها ثابت بودند
- ❌ Progress bar تغییر نمی‌کرد
- ❌ Learning Rate نمایش داده نمی‌شد
- ❌ Batch Speed محاسبه نمی‌شد

**علت:** ObservableCollection به‌روزرسانی می‌شد اما chart‌ها notify نمی‌شدند.

---

## ✅ **تغییرات انجام شده:**

### 1️⃣ **Chart Refresh Mechanism اضافه شد:**

قبلاً:
```csharp
// فقط data اضافه می‌شد
_trainLossData.Add(trainLoss);
_trainAccData.Add(trainAcc);
// ❌ chart به‌روزرسانی نمی‌شد!
```

**حالا:**
```csharp
bool chartsNeedUpdate = false;

// Only add if it's a new value (prevent duplicates)
if (_trainLossData.Count == 0 || 
    Math.Abs(_trainLossData[_trainLossData.Count - 1] - trainLoss) > 0.0001)
{
    _trainLossData.Add(trainLoss);
    chartsNeedUpdate = true;
}

// Force chart refresh by recreating series
if (chartsNeedUpdate)
{
    LossChart.Series = new ISeries[]
    {
        new LineSeries<double>
        {
            Values = _trainLossData,
            Name = "Train Loss",
            Fill = null,
            GeometrySize = 4
        },
        new LineSeries<double>
        {
            Values = _valLossData,
            Name = "Val Loss",
            Fill = null,
            GeometrySize = 4
        }
    };

    AccuracyChart.Series = new ISeries[]
    {
        new LineSeries<double>
        {
            Values = _trainAccData,
            Name = "Train Accuracy",
            Fill = null,
            GeometrySize = 4
        },
        new LineSeries<double>
        {
            Values = _valAccData,
            Name = "Val Accuracy",
            Fill = null,
            GeometrySize = 4
        }
    };
    
    Debug.WriteLine($"[Charts] Updated - Loss: {_trainLossData.Count} points");
}
```

**مزایا:**
- ✅ جلوگیری از duplicate data points
- ✅ Force refresh chart با recreate کردن Series
- ✅ نمایش تعداد نقاط برای debugging

---

### 2️⃣ **Learning Rate نمایش اضافه شد:**

```csharp
// Update Learning Rate
if (status.ContainsKey("learning_rate"))
{
    try
    {
        var lr = Convert.ToDouble(status["learning_rate"]);
        if (LearningRateText != null)
        {
            LearningRateText.Text = lr.ToString("F6");
        }
    }
    catch { }
}
```

---

### 3️⃣ **Batch Speed محاسبه اضافه شد:**

```csharp
// Update Batch Speed
if (status.ContainsKey("samples_per_sec"))
{
    var speed = Convert.ToDouble(status["samples_per_sec"]);
    BatchSpeedText.Text = $"{speed:F1} samples/sec";
}
else if (status.ContainsKey("batch_time"))
{
    var batchTime = Convert.ToDouble(status["batch_time"]);
    var batchSize = status.ContainsKey("batch_size") ? Convert.ToInt32(status["batch_size"]) : 32;
    var speed = batchSize / batchTime;
    BatchSpeedText.Text = $"{speed:F1} samples/sec";
}
```

**محاسبه:**
- اگر `samples_per_sec` موجود باشد → مستقیم استفاده می‌شود
- اگر `batch_time` موجود باشد → `batch_size / batch_time`

---

### 4️⃣ **Progress Updates بهبود یافت:**

```csharp
if (status.ContainsKey("current_epoch") && status.ContainsKey("total_epochs"))
{
    var currentEpoch = Convert.ToInt32(status["current_epoch"]);
    var totalEpochs = Convert.ToInt32(status["total_epochs"]);
    
    CurrentEpochText.Text = $"{currentEpoch} / {totalEpochs}";
    EpochProgressBar.Value = totalEpochs > 0 ? (double)currentEpoch / totalEpochs * 100 : 0;
    
    // Show progress percentage
    if (status.ContainsKey("progress_percent"))
    {
        var progress = Convert.ToInt32(status["progress_percent"]);
        CurrentEpochText.Text = $"{currentEpoch} / {totalEpochs} ({progress}%)";
    }
}
```

---

## 📊 **Backend Status Response:**

Dashboard انتظار دارد backend این فیلدها را برگرداند:

```json
{
  "project_id": "project_123",
  "status": "training",  // training, completed, failed, stopping
  
  // Progress
  "current_epoch": 25,
  "total_epochs": 50,
  "progress_percent": 50,
  
  // Time
  "elapsed_time_str": "15m 30s",
  "eta_str": "15m 20s",
  "epoch_time": "37.5s",
  
  // Metrics
  "train_loss": 0.1234,
  "train_acc": 0.9567,
  "val_loss": 0.1456,
  "val_acc": 0.9432,
  
  // Best Metrics
  "best_val_acc": 0.9654,
  "best_train_loss": 0.0987,
  
  // Training Config
  "learning_rate": 0.001,
  "batch_size": 32,
  "samples_per_sec": 45.2,  // or "batch_time": 0.711
  
  // Log
  "message": "Epoch 25/50 - Loss: 0.1234, Acc: 95.67%"
}
```

---

## 🔧 **به‌روزرسانی Backend (اختیاری):**

برای اطمینان از ارسال کامل data، در `backend/api/routes/training.py`:

```python
@router.get("/status/{project_id}")
async def get_training_status(project_id: str):
    if project_id not in active_trainings:
        return {
            "project_id": project_id,
            "status": "not_started",
            "message": "No training in progress"
        }
    
    status_data = active_trainings[project_id].copy()
    
    # محاسبه samples_per_sec اگر موجود نباشد
    if "samples_per_sec" not in status_data and "batch_time" in status_data:
        batch_time = status_data["batch_time"]
        batch_size = status_data.get("batch_size", 32)
        status_data["samples_per_sec"] = batch_size / batch_time if batch_time > 0 else 0
    
    # محاسبه progress_percent
    if "current_epoch" in status_data and "total_epochs" in status_data:
        current = status_data["current_epoch"]
        total = status_data["total_epochs"]
        status_data["progress_percent"] = int((current / total) * 100) if total > 0 else 0
    
    return {
        "project_id": project_id,
        **status_data
    }
```

---

## 🧪 **تست Dashboard:**

### قدم 1: Backend را اجرا کنید

```bash
cd D:\Project\ModelCreator\backend
.\venv\Scripts\activate
python main.py
```

منتظر بمانید تا ببینید:
```
INFO: Uvicorn running on http://127.0.0.1:8181
```

### قدم 2: یک Training شروع کنید

از Frontend یا مستقیماً از API:

```bash
curl -X POST "http://127.0.0.1:8181/api/training/start" \
  -H "Content-Type: application/json" \
  -d "{\"project_id\": \"test_project\", \"epochs\": 10}"
```

### قدم 3: Training Dashboard را باز کنید

```bash
cd D:\Project\ModelCreator\frontend
dotnet run --project ModelCreator.UI
```

Navigate to **Training Dashboard**

### ✅ **انتظار می‌رود:**

1. **Charts:**
   - ✅ Loss Chart به صورت Real-time به‌روزرسانی می‌شود
   - ✅ Accuracy Chart به صورت Real-time به‌روزرسانی می‌شود
   - ✅ هر 2 ثانیه data point جدید اضافه می‌شود

2. **Progress:**
   - ✅ Current Epoch: `25 / 50 (50%)`
   - ✅ Progress Bar پر می‌شود
   - ✅ ETA به‌روزرسانی می‌شود

3. **Metrics:**
   - ✅ Training Loss: `0.1234`
   - ✅ Training Accuracy: `95.67%`
   - ✅ Best Accuracy: `96.54%`
   - ✅ Learning Rate: `0.001000`
   - ✅ Batch Speed: `45.2 samples/sec`

4. **Logs:**
   - ✅ لاگ‌های جدید به صورت Real-time اضافه می‌شوند
   - ✅ Auto-scroll به آخرین لاگ

---

## 🎯 **Polling Mechanism:**

Dashboard هر **2 ثانیه** یک بار `/api/training/status/{project_id}` را poll می‌کند:

```csharp
private async Task PollTrainingStatus()
{
    while (true)
    {
        try
        {
            var status = await apiService.GetAsync<Dictionary<string, object>>(
                $"/api/training/status/{_projectId}"
            );
            
            if (status != null)
            {
                Dispatcher.Invoke(() =>
                {
                    // Update all UI elements
                    UpdateProgress(status);
                    UpdateMetrics(status);
                    UpdateCharts(status);  // ✅ Charts are now updated!
                    UpdateLogs(status);
                });
            }
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[Polling] Network error: {ex.Message}");
        }
        
        await Task.Delay(2000);  // Poll every 2 seconds
    }
}
```

---

## 📝 **Debug Output:**

در Debug Console می‌بینید:

```
[Polling] Status: training
[Polling] Epoch parse error: ... (if any)
[Charts] Updated - Loss: 25 points, Acc: 25 points
[Polling] Network error: ... (if backend not running)
```

---

## ✅ **Build Status:**

```bash
cd D:\Project\ModelCreator\frontend
dotnet build ModelCreator.UI
```

**✅ Build: Succeeded**  
**✅ 0 Errors**  
**✅ 0 Warnings**

---

## 🚀 **همه چیز آماده است!**

**Dashboard حالا به صورت Real-time:**
- ✅ چارت‌ها را به‌روزرسانی می‌کند
- ✅ متریک‌ها را نمایش می‌دهد
- ✅ Progress را track می‌کند
- ✅ Learning Rate و Batch Speed را نشان می‌دهد

**اکنون می‌توانید آموزش را مانیتور کنید و نتایج real-time را ببینید! 🎉**

---

## 📖 **اسناد مرتبط:**

- `QUICKSTART.md` - راهنمای سریع شروع
- `TRAINING_GUIDE_FA.md` - راهنمای کامل آموزش
- `UI_UX_OPTIMIZATION.md` - بهینه‌سازی‌های UI/UX

