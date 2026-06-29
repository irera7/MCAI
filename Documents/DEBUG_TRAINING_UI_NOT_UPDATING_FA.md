# 🐛 راهنمای Debug مشکل عدم بروزرسانی UI در Training

## ❌ مشکل گزارش شده

Training شروع می‌شود اما:
- `current_epoch` تغییر نمیکند
- `train_loss` و `train_acc` بروزرسانی نمیشوند
- فقط لاگ‌های شروع نمایش داده می‌شوند:
  ```
  11:01:23 - 🏗️ Building resnet18 model with 75 classes...
  11:01:25 - 🚀 Training started - 50 epochs on cuda
  ```

## 🔍 تغییرات اعمال شده برای Debug

### 1. اضافه کردن Logging به ProgressCallback

```python
# در backend/engine/callbacks.py
def on_epoch_end(self, epoch: int, metrics: Dict[str, float]):
    try:
        if self.project_id not in self.active_trainings:
            print(f"[ProgressCallback] Project {self.project_id} not in active_trainings")
            return
            
        print(f"[ProgressCallback] Updating epoch {epoch} metrics...")
        
        # ... کد بروزرسانی ...
        
        print(f"[ProgressCallback] Updated: Epoch {epoch}/{total_epochs}, Loss: {val_loss:.4f}, Acc: {val_acc:.4f}")
        
    except Exception as e:
        print(f"[ProgressCallback] Error updating metrics: {e}")
        import traceback
        traceback.print_exc()
```

### 2. بهبود Error Handling در Thread

```python
# در backend/api/routes/training.py
def run_training_sync():
    """Synchronous wrapper for training"""
    try:
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the training
        result = loop.run_until_complete(run_real_training(project_id, config))
        return result
    except Exception as e:
        logger.error(f"Error in training thread: {e}")
        # Update active_trainings with error
        if project_id in active_trainings:
            active_trainings[project_id]["status"] = "failed"
            active_trainings[project_id]["error"] = str(e)
        raise
    finally:
        loop.close()
```

### 3. اضافه کردن Debug Logging به Status Endpoint

```python
@router.get("/status/{project_id}")
async def get_training_status(project_id: str):
    if project_id not in active_trainings:
        logger.debug(f"[Status Check] Project {project_id} not in active_trainings")
        return {
            "project_id": project_id,
            "status": "not_started",
            "message": "No training in progress"
        }
    
    # Get current status
    status_data = active_trainings[project_id].copy()
    logger.debug(f"[Status Check] Project {project_id} - Epoch: {status_data.get('current_epoch', 0)}, Status: {status_data.get('status', 'unknown')}")
    
    return {
        "project_id": project_id,
        **status_data
    }
```

## 🧪 نحوه Debug

### گام 1: بررسی لاگ‌های Backend Terminal

بعد از شروع Training، در Terminal که Backend را اجرا کرده‌اید، باید این لاگ‌ها را ببینید:

**اگر همه چیز درست کار کند:**
```
[ProgressCallback] Updating epoch 1 metrics...
[ProgressCallback] Updated: Epoch 1/50, Loss: 2.3456, Acc: 0.2500
[ProgressCallback] Updating epoch 2 metrics...
[ProgressCallback] Updated: Epoch 2/50, Loss: 1.8901, Acc: 0.4200
...
```

**اگر مشکلی وجود داشته باشد:**
```
[ProgressCallback] Project abc123 not in active_trainings
```
یا
```
[ProgressCallback] Error updating metrics: <error message>
```

### گام 2: تست Manual از طریق curl

در یک Terminal جداگانه، این دستور را اجرا کنید (PROJECT_ID را با ID واقعی جایگزین کنید):

```powershell
# هر 2 ثانیه یکبار status را چک کنید
while ($true) {
    $status = curl -s http://127.0.0.1:8181/api/training/status/YOUR_PROJECT_ID | ConvertFrom-Json
    Write-Host "Epoch: $($status.current_epoch) / $($status.total_epochs) - Loss: $($status.train_loss)" -ForegroundColor Green
    Start-Sleep -Seconds 2
}
```

### گام 3: بررسی Frontend Polling

در DevTools Console (F12) در Frontend، باید این لاگ‌ها را ببینید:

```
[Polling] Status: training
[Polling] Epoch: 1/50
[Polling] Train Loss: 2.3456
[Polling] Train Acc: 0.2500
```

## 🔧 مشکلات احتمالی و راه‌حل‌ها

### مشکل 1: ProgressCallback اصلاً فراخوانی نمیشود

**علائم:**
- هیچ لاگ `[ProgressCallback]` در Terminal Backend نیست

**راه‌حل:**
- بررسی کنید که `callbacks` لیست به Trainer پاس داده می‌شود
- بررسی کنید که `trainer.fit()` به درستی اجرا می‌شود

### مشکل 2: project_id در active_trainings نیست

**علائم:**
- لاگ: `[ProgressCallback] Project abc123 not in active_trainings`

**راه‌حل:**
- مشکل threading: `active_trainings` dictionary به Thread دیگر منتقل نشده
- راه‌حل موقت: استفاده از یک global dictionary یا shared memory

### مشکل 3: Metrics در active_trainings هست اما Frontend دریافت نمیکند

**علائم:**
- لاگ‌های `[ProgressCallback]` نشان می‌دهند که metrics بروزرسانی می‌شوند
- اما UI تغییری نمیکند

**راه‌حل:**
- بررسی کنید که Frontend polling کار می‌کند
- بررسی کنید که هیچ exception در Frontend Console نیست
- بررسی کنید که `project_id` در Frontend و Backend یکسان است

### مشکل 4: Training خیلی سریع Crash می‌کند

**علائم:**
- فقط 2 لاگ اول نمایش داده می‌شود
- هیچ لاگ `[ProgressCallback]` نیست

**راه‌حل:**
- بررسی Backend Terminal برای Stack Trace
- احتمالاً مشکل در data loading یا model building است
- بررسی کنید که GPU memory کافی است

## 📊 نمونه Output مورد انتظار

### Backend Terminal (هر Epoch):
```
Starting training for 50 epochs
Device: cuda
Model: ResNet
Optimizer: Adam
Mixed Precision: True
======================================================================

Epoch 1/50 - Train: 100%|██████████| 25/25 [00:23<00:00,  1.06it/s]
Epoch 1/50 - Val: 100%|██████████| 7/7 [00:01<00:00,  5.12it/s]

Epoch 1/50 Summary:
  Train Loss: 2.3456 | Train Acc: 0.2500
  Val Loss:   2.4123 | Val Acc:   0.2300
  Learning Rate: 0.001000

[ProgressCallback] Updating epoch 1 metrics...
[ProgressCallback] Updated: Epoch 1/50, Loss: 2.4123, Acc: 0.2300
```

### Frontend Console:
```
[Polling] Status: training
[Polling] Epoch: 1/50
[Polling] Train Loss: 2.3456
[Polling] Train Acc: 0.2500
```

### Frontend UI:
```
Current Epoch: 1 / 50 (2%)
Training Loss: 2.3456
Training Accuracy: 25.00%
Estimated Time: 20m 15s

Training Logs:
11:01:25 - 🚀 Training started - 50 epochs on cuda
11:01:50 - Epoch 1/50 - Loss: 2.4123, Acc: 0.2300 - 25.3s/epoch
```

## 🎯 اقدامات بعدی

1. **Backend را Restart کنید** (تغییرات اعمال شده)
2. **Training را شروع کنید**
3. **Backend Terminal را بررسی کنید** - آیا لاگ‌های `[ProgressCallback]` را میبینید؟
4. **اگر لاگ‌ها را میبینید**: مشکل در Frontend polling است
5. **اگر لاگ‌ها را نمیبینید**: مشکل در Backend/Trainer/Callback است

## 📞 گزارش مشکل

اگر مشکل همچنان وجود دارد، لطفاً این اطلاعات را ارائه دهید:

1. **لاگ‌های Backend Terminal** (از زمان شروع Training تا حالا)
2. **Frontend Console Logs** (F12 -> Console)
3. **Screenshot از UI Training Dashboard**
4. **نتیجه curl به `/api/training/status/PROJECT_ID`**

با این اطلاعات می‌توانم مشکل را دقیق‌تر تشخیص دهم!

