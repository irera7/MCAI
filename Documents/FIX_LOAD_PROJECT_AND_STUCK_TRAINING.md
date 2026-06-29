# 🔧 رفع دو مشکل: باز کردن پروژه + Training متوقف نمی‌شود

## 🎯 مشکلات حل شده

### 1️⃣ امکان باز کردن پروژه‌های قبلی وجود نداشت
### 2️⃣ بعد از خطا، Training متوقف نمی‌شد

---

## ✅ راه‌حل 1: باز کردن پروژه‌های قبلی

### تغییرات انجام شده

**فایل:** `frontend/ModelCreator.UI/Views/ProjectsPage.xaml.cs`

**قبل:**
```csharp
private void Project_Click(object sender, MouseButtonEventArgs e)
{
    MessageBox.Show("Opening project... (Not implemented)");
    // ❌ فقط پیام می‌داد!
}
```

**بعد:**
```csharp
private void Project_Click(object sender, MouseButtonEventArgs e)
{
    if (sender is Border border && border.DataContext is ProjectInfo project)
    {
        // ✅ واقعاً پروژه را باز می‌کند!
        var window = Window.GetWindow(this) as MainWindow;
        window?.MainFrame.Navigate(new DataImportPage(
            project.Id, 
            project.Name, 
            project.Modality
        ));
    }
}
```

### نحوه استفاده

```
1. از صفحه Home روی "Load Project" کلیک کنید
2. لیست پروژه‌های قبلی نمایش داده می‌شود
3. روی هر پروژه کلیک کنید
4. ✅ صفحه Data Import باز می‌شود و می‌توانید:
   - داده‌های بیشتر اضافه کنید
   - به Model Selection بروید
   - به Training بروید
```

---

## ✅ راه‌حل 2: متوقف کردن Training بعد از خطا

### مشکل
وقتی Training با خطا مواجه می‌شد:
- ❌ Session در حافظه باقی می‌ماند
- ❌ نمی‌شد Training جدید شروع کرد
- ❌ باید Backend را Restart می‌کردیم

### تغییرات انجام شده

#### الف) Auto Cleanup بعد از خطا

**فایل:** `backend/api/routes/training.py`

```python
except Exception as e:
    logger.error(f"Error in training: {str(e)}")
    if project_id in active_trainings:
        active_trainings[project_id]["status"] = "failed"
        active_trainings[project_id]["error"] = str(e)
    
    # ✅ پاک‌سازی خودکار بعد از 5 ثانیه
    await asyncio.sleep(5)
    if project_id in active_trainings:
        del active_trainings[project_id]
        logger.info("Cleaned up failed training session")
```

#### ب) Endpoint جدید: Reset Training

```python
@router.post("/reset/{project_id}")
async def reset_training(project_id: str):
    """
    پاک کردن دستی session training
    مفید وقتی training گیر کرده یا failed است
    """
    if project_id in active_trainings:
        del active_trainings[project_id]
        return {"message": "Training session reset successfully"}
```

### نحوه استفاده

#### حالت 1: خطا رخ داد و خودکار پاک می‌شود
```
1. Training شروع می‌شود
2. خطا رخ می‌دهد (مثلاً verbose error)
3. Frontend خطا را نمایش می‌دهد
4. ✅ بعد از 5 ثانیه session خودکار پاک می‌شود
5. می‌توانید Training جدید شروع کنید
```

#### حالت 2: دستی Reset کردن
اگر Training گیر کرد:

```bash
# از Postman یا curl:
curl -X POST http://127.0.0.1:8181/api/training/reset/{project_id}

# پاسخ:
{
  "message": "Training session reset successfully",
  "project_id": "..."
}
```

یا از Frontend می‌توانید دکمه "Reset Training" اضافه کنید.

---

## 🚀 برای استفاده

### مرحله 1: Rebuild Frontend
```bash
cd frontend/ModelCreator.UI
dotnet clean
dotnet build
dotnet run
```

### مرحله 2: Restart Backend
```bash
# Ctrl+C در Terminal Backend
cd backend
python main.py
```

### مرحله 3: تست Load Project
```
1. Frontend را باز کنید
2. Home → Load Project
3. یکی از پروژه‌های قبلی را انتخاب کنید
4. ✅ باید Data Import page باز شود
```

### مرحله 4: تست Training Error Recovery
```
1. یک Training با خطا شروع کنید (مثلاً داده خالی)
2. خطا نمایش داده می‌شود
3. صبر کنید 5 ثانیه
4. دوباره Training را شروع کنید
5. ✅ باید کار کند (session قبلی پاک شده)
```

---

## 📋 تست کامل

### تست 1: Load کردن پروژه موجود

```
Scenario: پروژه test-cat-dog موجود است

1. Home → Load Project
2. پروژه "test-cat-dog" را ببینید
3. روی آن کلیک کنید
4. ✅ Data Import page باز می‌شود
5. Next → Model Selection
6. Next → Training Config
7. Start Training
8. ✅ Training شروع می‌شود با 30 تصویر موجود
```

### تست 2: Recovery از خطا

```
Scenario: Training با خطا متوقف می‌شود

1. یک پروژه جدید بسازید (بدون داده)
2. به Training Config بروید
3. Start Training
4. ✅ خطا نمایش داده می‌شود:
   "No images found in data directory..."
5. صبر کنید 5 ثانیه
6. به Data Import برگردید
7. داده آپلود کنید
8. دوباره Training را شروع کنید
9. ✅ این بار کار می‌کند!
```

### تست 3: Manual Reset

```
Scenario: Training گیر کرده

1. از Postman:
   POST http://127.0.0.1:8181/api/training/reset/{project_id}

2. یا از Frontend:
   (اگر دکمه Reset اضافه کردید)

3. ✅ Session پاک می‌شود
4. می‌توانید Training جدید شروع کنید
```

---

## 🐛 مشکلات احتمالی و راه‌حل

### مشکل 1: لیست پروژه‌ها خالی است

**علت:** Backend اجرا نیست

**راه‌حل:**
```bash
cd backend
python main.py
```

بررسی کنید:
```bash
curl http://127.0.0.1:8181/api/project/list

# باید لیست پروژه‌ها را ببینید
```

---

### مشکل 2: کلیک روی پروژه کار نمی‌کند

**علت:** Frontend rebuild نشده

**راه‌حل:**
```bash
cd frontend/ModelCreator.UI
dotnet clean
dotnet build
```

---

### مشکل 3: Training هنوز گیر می‌کند

**راه‌حل سریع:**

#### روش 1: از API
```bash
# Reset کردن training
curl -X POST http://127.0.0.1:8181/api/training/reset/{project_id}
```

#### روش 2: Restart Backend
```bash
# در Terminal Backend:
Ctrl + C
python main.py
```

#### روش 3: از Python Console
```python
# اگر دسترسی به Backend دارید:
from backend.api.routes.training import active_trainings
active_trainings.clear()
print("All training sessions cleared!")
```

---

## 💡 نکات مهم

### 1. Session Cleanup Timing
```
خطا رخ می‌دهد → 5 ثانیه صبر → پاک‌سازی خودکار
```
چرا 5 ثانیه؟
- Frontend وقت دارد خطا را نمایش دهد
- کاربر وقت دارد خطا را بخواند
- بعد session پاک می‌شود

### 2. Load Project Navigation
```
فعلاً: همیشه به Data Import می‌رود
آینده: بر اساس status پروژه:
  - status: "new" → Data Import
  - status: "data_imported" → Model Selection
  - status: "configured" → Training Config
  - status: "trained" → Results
```

### 3. Multiple Training Sessions
```
Backend از چند training همزمان پشتیبانی می‌کند:
- پروژه A → Training
- پروژه B → Training
- ✅ هر دو می‌توانند همزمان اجرا شوند
```

---

## 📈 بهبودهای آینده

### کوتاه‌مدت
- [ ] دکمه "Reset Training" در Frontend
- [ ] نمایش لیست Training های فعال
- [ ] Progress bar برای Load Project
- [ ] Cache کردن لیست پروژه‌ها

### میان‌مدت
- [ ] Navigation هوشمند بر اساس status پروژه
- [ ] Resume کردن Training از checkpoint
- [ ] History/logs Training قبلی
- [ ] Compare کردن نتایج چند training

### بلند‌مدت
- [ ] Multi-user support (هر کاربر پروژه‌های خودش)
- [ ] Cloud storage برای پروژه‌ها
- [ ] Collaboration (چند نفر روی یک پروژه)
- [ ] Version control برای پروژه‌ها

---

## ✅ خلاصه

| قبل | بعد |
|-----|-----|
| ❌ نمی‌شد پروژه باز کرد | ✅ کلیک → باز می‌شود |
| ❌ Training گیر می‌کرد بعد از خطا | ✅ خودکار پاک می‌شود |
| ❌ باید Backend restart می‌شد | ✅ نیازی نیست |
| ❌ Session دستی پاک نمی‌شد | ✅ Endpoint Reset |

---

## 🎓 دستورالعمل استفاده کامل

### سناریو 1: ادامه پروژه قبلی

```
1. Frontend: Home → Load Project
2. انتخاب پروژه (مثلاً test-cat-dog)
3. ✅ Data Import page → می‌بینید 30 تصویر موجود است
4. می‌توانید:
   a) داده بیشتر اضافه کنید
   b) Next → Model Selection
   c) Next → Training Config
   d) Start Training
```

### سناریو 2: Training با خطا

```
1. Training شروع می‌شود
2. خطا رخ می‌دهد
3. Frontend: پیام خطا نمایش داده می‌شود
4. صبر کنید 5 ثانیه
5. ✅ Session پاک می‌شود
6. مشکل را رفع کنید (داده آپلود کنید)
7. دوباره Training شروع کنید
```

### سناریو 3: Training گیر کرد

```
1. Backend Terminal: بررسی logs
2. اگر stuck است:
   curl -X POST http://127.0.0.1:8181/api/training/reset/{project_id}
3. ✅ Session پاک شد
4. Training جدید شروع کنید
```

---

**تاریخ:** 2025-11-26  
**نسخه:** 2.1  
**وضعیت:** ✅ رفع شد و آماده استفاده

