# 🔍 Training Dashboard Troubleshooting - عیب‌یابی Dashboard

## 🐛 **مشکل:**

Training Dashboard details نمایش داده نمی‌شوند:
- ❌ Charts خالی هستند
- ❌ Current Epoch تغییر نمی‌کند
- ❌ Metrics update نمی‌شوند

---

## ✅ **راه‌حل: Debug Tool**

یک صفحه Debug اضافه کردیم که دقیقاً API response را نشان می‌دهد.

### 📍 **استفاده:**

#### 1️⃣ از Frontend:

```csharp
// در HomePage.xaml.cs اضافه شد:
private void DashboardDebug_Click(object sender, RoutedEventArgs e)
{
    var window = Window.GetWindow(this) as MainWindow;
    window?.MainFrame.Navigate(new DashboardDebugPage());
}
```

یا مستقیماً:
```csharp
NavigationService?.Navigate(new DashboardDebugPage("your_project_id"));
```

#### 2️⃣ صفحه Debug:

```
┌─────────────────────────────────────────┐
│  Training Dashboard Debug Tool          │
├─────────────────────────────────────────┤
│  Project ID:                            │
│  [53569a3d-1248-4b5d-8e8b-be8b75556767]│
│  [🔄 Test API]                          │
├─────────────────────────────────────────┤
│  Status:    training                    │
│  Epoch:     15                          │
│  Loss:      0.0226                      │
│  Accuracy:  99.43%                      │
├─────────────────────────────────────────┤
│  📄 API Response (JSON)                 │
│  {                                      │
│    "status": "training",                │
│    "current_epoch": 15,                 │
│    "total_epochs": 50,                  │
│    "train_loss": 0.0226,                │
│    "train_acc": 0.9943                  │
│  }                                      │
└─────────────────────────────────────────┘
```

---

## 🧪 **تست مراحل:**

### قدم 1: Backend را Check کنید

```bash
cd D:\Project\ModelCreator\backend
.\venv\Scripts\activate
python main.py
```

منتظر بمانید تا:
```
INFO: Uvicorn running on http://127.0.0.1:8181
```

### قدم 2: Project ID را پیدا کنید

از Backend logs:
```
INFO: 127.0.0.1:60897 - "GET /api/training/status/53569a3d-1248-4b5d-8e8b-be8b75556767 HTTP/1.1" 200 OK
[ProgressCallback] Updated: Epoch 15/50, Loss: 0.2981, Acc: 0.9246
```

**Project ID:** `53569a3d-1248-4b5d-8e8b-be8b75556767`

### قدم 3: Frontend را Run کنید

```bash
cd D:\Project\ModelCreator\frontend
dotnet run --project ModelCreator.UI
```

### قدم 4: Debug Page را باز کنید

- از code:
  ```csharp
  new DashboardDebugPage("53569a3d-1248-4b5d-8e8b-be8b75556767")
  ```

- Project ID را paste کنید
- دکمه **Test API** را کلیک کنید

---

## 📊 **تفسیر نتایج:**

### ✅ **حالت موفق:**

```json
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
  "message": "Epoch 15/50 - Loss: 0.2981, Acc: 0.9246"
}
```

**✅ API کار می‌کند! → مشکل در TrainingDashboardPage است**

---

### ❌ **حالت 1: not_started**

```json
{
  "project_id": "your_project_id",
  "status": "not_started",
  "message": "No training in progress"
}
```

**مشکل:** Project ID اشتباه است یا Training شروع نشده

**راه‌حل:**
1. Project ID صحیح را از Backend logs پیدا کنید
2. یا Training جدید شروع کنید

---

### ❌ **حالت 2: Network Error**

```
❌ خطا: Unable to connect...
```

**مشکل:** Backend در حال اجرا نیست

**راه‌حل:**
```bash
cd D:\Project\ModelCreator\backend
.\venv\Scripts\activate
python main.py
```

---

## 🔧 **اگر API کار می‌کند اما Dashboard نه:**

### مشکل در TrainingDashboardPage

بیایید بررسی کنیم:

#### 1️⃣ بررسی Project ID:

```csharp
// در TrainingDashboardPage constructor
public TrainingDashboardPage(string projectId, string projectName = "")
{
    InitializeComponent();
    _projectId = projectId;
    
    // ✅ اضافه کنید:
    System.Diagnostics.Debug.WriteLine($"[Dashboard] Project ID: {_projectId}");
    
    if (ProjectNameText != null)
    {
        // ✅ نمایش Project ID برای debug
        ProjectNameText.Text = $"Project: {_projectName}\nID: {_projectId}";
    }
}
```

#### 2️⃣ بررسی Polling:

در `PollTrainingStatus()`:

```csharp
private async Task PollTrainingStatus()
{
    while (true)
    {
        try
        {
            // ✅ Log URL
            var url = $"/api/training/status/{_projectId}";
            System.Diagnostics.Debug.WriteLine($"[Polling] GET {url}");
            
            var status = await apiService.GetAsync<Dictionary<string, object>>(url);
            
            // ✅ Log response
            if (status != null)
            {
                System.Diagnostics.Debug.WriteLine($"[Polling] Response: {string.Join(", ", status.Keys)}");
                var statusValue = status.ContainsKey("status") ? status["status"].ToString() : "unknown";
                System.Diagnostics.Debug.WriteLine($"[Polling] Status: {statusValue}");
            }
            else
            {
                System.Diagnostics.Debug.WriteLine($"[Polling] Response is NULL!");
            }
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"[Polling] ERROR: {ex.Message}");
        }
        
        await Task.Delay(2000);
    }
}
```

#### 3️⃣ بررسی Debug Output:

در Visual Studio:
1. **View → Output**
2. Select "**Debug**" from dropdown
3. Run Frontend
4. Navigate to Training Dashboard
5. بررسی کنید:

```
[Dashboard] Project ID: 53569a3d-1248-4b5d-8e8b-be8b75556767
[Polling] GET /api/training/status/53569a3d-1248-4b5d-8e8b-be8b75556767
[Polling] Response: project_id, status, current_epoch, ...
[Polling] Status: training
[Charts] Added train_loss: 0.0226, Total points: 15
[Charts] Updated - Loss: 15 points, Acc: 15 points
```

---

## 🎯 **سناریوهای ممکن:**

### سناریو 1: API OK, Charts خالی

**علت:** `ObservableCollection` update نمی‌شود یا chart نمی‌تواند render کند

**راه‌حل:**
- بررسی کنید `_trainLossData.Count` > 0
- بررسی کنید `LossChart.Series` set شده است
- LiveCharts package نصب است؟

### سناریو 2: API OK, UI freeze

**علت:** Dispatcher.Invoke blocking است

**راه‌حل:**
- استفاده از `Dispatcher.InvokeAsync`
- Try-Catch در Dispatcher.Invoke

### سناریو 3: API OK, Current Epoch ثابت

**علت:** `CurrentEpochText` update نمی‌شود

**راه‌حل:**
```csharp
if (status.ContainsKey("current_epoch"))
{
    var epoch = Convert.ToInt32(status["current_epoch"]);
    System.Diagnostics.Debug.WriteLine($"[Update] Current Epoch: {epoch}");
    
    Dispatcher.Invoke(() => {
        if (CurrentEpochText != null)
        {
            CurrentEpochText.Text = $"{epoch} / {total}";
            System.Diagnostics.Debug.WriteLine($"[UI] Updated CurrentEpochText");
        }
        else
        {
            System.Diagnostics.Debug.WriteLine($"[UI] CurrentEpochText is NULL!");
        }
    });
}
```

---

## 📝 **Quick Fix Checklist:**

- [ ] Backend در حال اجرا است
- [ ] Training شروع شده است
- [ ] Project ID صحیح است
- [ ] Debug Tool response کامل نشان می‌دهد
- [ ] Frontend Debug Output فعال است
- [ ] Polling logs نمایش داده می‌شوند
- [ ] `_trainLossData.Count` > 0 است
- [ ] Charts Series تنظیم شده است

---

## 🚀 **نتیجه:**

1. ✅ **Debug Tool** اضافه شد → می‌توانید دقیقاً API response را ببینید
2. ✅ **Debug Logging** اضافه شد → می‌توانید flow را track کنید
3. ✅ **Quick Fixes** → رایج‌ترین مشکلات

**حالا بیایید با Debug Tool مشکل دقیق را پیدا کنیم! 🔍**

---

## 📞 **برای Debug بیشتر:**

لطفاً موارد زیر را ارسال کنید:

1. **Screenshot** از Debug Tool با JSON response
2. **Debug Output** از Visual Studio Output window
3. **Backend Logs** در زمان Polling
4. **چه چیزی را می‌بینید؟** (Static values یا خالی یا error)

با این اطلاعات می‌توانیم مشکل دقیق را شناسایی کنیم! 🎯

