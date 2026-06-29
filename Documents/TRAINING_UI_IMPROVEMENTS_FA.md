# 📊 بهبودهای رابط کاربری Training Dashboard

## ✅ مشکل حل شده

قبلاً UI فقط لاگ‌های ساده مانند "Training started" را نمایش می‌داد و اطلاعات کافی در مورد پیشرفت، زمان و معیارها نداشت.

## 🎯 بهبودهای اعمال شده

### 1️⃣ نمایش اطلاعات زمان
- **زمان سپری شده (Elapsed Time)**: زمان کل از شروع Training
- **زمان تخمینی (ETA - Estimated Time Remaining)**: زمان باقی‌مانده تا پایان Training
- **زمان هر Epoch**: مدت زمان اجرای هر Epoch

### 2️⃣ نمایش معیارهای بهتر
- **Train Loss**: مقدار Loss در Training
- **Train Accuracy**: دقت مدل در Training
- **Validation Loss**: مقدار Loss در Validation
- **Validation Accuracy**: دقت مدل در Validation
- **Best Accuracy**: بهترین دقت به دست آمده تا کنون
- **Best Loss**: کمترین Loss به دست آمده تا کنون

### 3️⃣ نمایش پیشرفت Training
- **Epoch Progress**: نمایش تعداد Epoch فعلی و کل (مثلاً: 25 / 50)
- **Progress Percentage**: درصد پیشرفت Training (مثلاً: 50%)
- **Progress Bar**: نوار پیشرفت گرافیکی

### 4️⃣ لاگ‌های بهتر
قبلاً:
```
10:53:50 - Training started
10:53:52 - Training started
```

حالا:
```
10:53:50 - Training started
10:54:15 - Epoch 1/50 - Loss: 2.3456, Acc: 0.2500 - 25.3s/epoch
10:54:40 - Epoch 2/50 - Loss: 1.8901, Acc: 0.4200 - 25.1s/epoch
10:55:05 - Epoch 3/50 - Loss: 1.5432, Acc: 0.5800 - 24.8s/epoch
```

## 📝 تغییرات فایل‌ها

### Backend: `backend/engine/callbacks.py`
- **ProgressCallback بهبود یافت**:
  - محاسبه زمان سپری شده (elapsed time)
  - محاسبه ETA (زمان تخمینی)
  - محاسبه زمان هر Epoch
  - ذخیره بهترین مقادیر (best metrics)
  - فرمت‌بندی زمان به فرمت انسان‌خوانده (1h 15m 30s)
  - محاسبه درصد پیشرفت

### Frontend: `frontend/ModelCreator.UI/Views/TrainingDashboardPage.xaml.cs`
- **بروزرسانی UI با اطلاعات جدید**:
  - نمایش ETA
  - نمایش زمان سپری شده
  - نمایش درصد پیشرفت
  - نمایش Best Accuracy
  - نمایش Validation metrics در نمودارها
  - لاگ‌های غنی‌تر با اطلاعات بیشتر

## 🔍 ساختار داده‌های ارسالی از Backend

```python
{
    'current_epoch': 25,                    # Epoch فعلی
    'total_epochs': 50,                     # کل Epoch‌ها
    'train_loss': 0.1234,                   # Train Loss
    'train_acc': 0.9567,                    # Train Accuracy
    'val_loss': 0.1456,                     # Validation Loss
    'val_acc': 0.9421,                      # Validation Accuracy
    'best_train_loss': 0.1100,              # بهترین Train Loss
    'best_val_loss': 0.1250,                # بهترین Val Loss
    'best_val_acc': 0.9500,                 # بهترین Val Accuracy
    'elapsed_time': 1523,                   # زمان سپری شده (ثانیه)
    'elapsed_time_str': '25m 23s',          # زمان سپری شده (فرمت شده)
    'eta': 1477,                            # زمان تخمینی (ثانیه)
    'eta_str': '24m 37s',                   # زمان تخمینی (فرمت شده)
    'epoch_time': '25.3s',                  # زمان هر Epoch
    'progress_percent': 50,                 # درصد پیشرفت
    'message': 'Epoch 25/50 - Loss: 0.1234, Acc: 0.9567 - 25.3s/epoch',
    'status': 'training'                    # وضعیت
}
```

## 🎨 نمایش در UI

### قسمت بالای Dashboard
```
┌─────────────────────────────────────────────────────────────┐
│  Current Epoch  │  Training Loss  │  Training Acc  │   ETA   │
│    25 / 50      │     0.1234      │    95.67%      │ 24m 37s │
│   [▓▓▓▓▓▓▓░░░]  │                 │                │         │
│      50%        │                 │                │         │
└─────────────────────────────────────────────────────────────┘
```

### قسمت لاگ‌ها
```
Training Logs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
10:53:50 - Training started
10:54:15 - Epoch 1/50 - Loss: 2.3456, Acc: 0.2500 - 25.3s/epoch
10:54:40 - Epoch 2/50 - Loss: 1.8901, Acc: 0.4200 - 25.1s/epoch
10:55:05 - Epoch 3/50 - Loss: 1.5432, Acc: 0.5800 - 24.8s/epoch
...
```

### Status Bar
```
🔥 در حال آموزش... (زمان: 25m 23s)
```

## 🧪 تست کردن

1. یک پروژه جدید بسازید
2. داده‌های Training را آپلود کنید
3. Training را شروع کنید
4. مشاهده کنید:
   - ✅ نوار پیشرفت به درستی پر می‌شود
   - ✅ زمان سپری شده و ETA نمایش داده می‌شود
   - ✅ معیارها (Loss, Accuracy) به‌روزرسانی می‌شوند
   - ✅ لاگ‌ها اطلاعات کامل دارند
   - ✅ Best Accuracy نمایش داده می‌شود
   - ✅ نمودارها به‌روزرسانی می‌شوند

## 📚 توضیحات فنی

### محاسبه ETA
```python
# میانگین زمان هر Epoch
avg_epoch_time = elapsed_time / current_epoch

# تعداد Epoch‌های باقیمانده
remaining_epochs = total_epochs - current_epoch

# زمان تخمینی
eta = avg_epoch_time * remaining_epochs
```

### فرمت زمان
```python
def _format_time(seconds):
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}m {secs}s"
    else:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h {mins}m"
```

## ⚠️ نکات مهم

1. **Polling Interval**: UI هر 1 ثانیه یک بار از Backend وضعیت را می‌خواهد
2. **Data Limit**: فقط آخرین 100 نقطه در نمودارها نمایش داده می‌شود
3. **Async Updates**: همه بروزرسانی‌های UI در `Dispatcher.Invoke` انجام می‌شود
4. **Error Handling**: تمام conversions (string to int/double) داخل try-catch هستند

## 🎉 نتیجه

حالا UI اطلاعات کامل و واضحی از Training نمایش می‌دهد و کاربر می‌تواند به راحتی پیشرفت مدل را رصد کند!

