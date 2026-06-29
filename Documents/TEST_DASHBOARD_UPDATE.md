# 🧪 تست مشکل Dashboard Data Update

## ✅ **تغییرات انجام شده:**

1. **Epoch-based tracking** اضافه شد تا از duplicate updates جلوگیری شود
2. **Enhanced debugging** اضافه شد تا بتوانید دقیقاً ببینید چه داده‌هایی از backend می‌آید
3. **Charts فقط در NEW EPOCH** به‌روزرسانی می‌شوند

---

## 📝 **مراحل تست:**

### 1️⃣ **Build و Run Frontend:**

```powershell
cd D:\Project\ModelCreator\frontend\ModelCreator.UI
dotnet build
dotnet run
```

### 2️⃣ **Backend را در حال اجرا نگه دارید:**

در terminal دیگری (terminal 7 شما):
```powershell
cd D:\Project\ModelCreator\backend
.\venv\Scripts\activate
python main.py
```

✅ مطمئن شوید که می‌بینید:
```
INFO: Uvicorn running on http://127.0.0.1:8181
```

### 3️⃣ **Training را شروع کنید:**

1. در Frontend، پروژه `53569a3d-1248-4b5d-8e8b-be8b75556767` را انتخاب کنید
2. Configure → Start Training
3. Dashboard باز می‌شود

### 4️⃣ **چیزهایی که باید ببینید:**

#### در Dashboard UI:

✅ **Progress Section:**
```
Current Epoch: 1 / 50 (2%)
[████░░░░░░░░░░░░░░░░░░] 2%
ETA: 23m 45s
```

✅ **Metrics Cards:**
```
Training Loss     Training Accuracy
0.7672           80.60%

Best Accuracy    Learning Rate
80.60%          0.001000

Batch Speed
45.2 samples/sec
```

✅ **Loss Chart:**
- باید **خطی** ببینید که با هر epoch پایین می‌آید
- Train Loss (آبی) و Val Loss (نارنجی)

✅ **Accuracy Chart:**
- باید **خطی** ببینید که با هر epoch بالا می‌رود
- Train Accuracy (سبز) و Val Accuracy (بنفش)

✅ **Logs:**
```
16:32:15 - Epoch 1: Loss: 0.7672, Acc: 0.8060 - 34.23s/epoch
16:33:04 - Epoch 2: Loss: 0.5125, Acc: 0.8507 - 32.56s/epoch
16:33:51 - Epoch 3: Loss: 0.4570, Acc: 0.8768 - 34.12s/epoch
```

#### در Visual Studio Debug Output (`Output → Debug`):

✅ **هر 2 ثانیه این را می‌بینید:**

```
========== [Polling] Received Data ==========
Status: training
Epoch: 1
Train Loss: 0.7672
Train Acc: 0.806
Val Loss: 0.7672
Val Acc: 0.806
============================================
```

✅ **زمانی که Epoch تغییر می‌کند:**

```
[Charts] ✅ NEW EPOCH DETECTED: 1
[Charts] ✅ Added train_loss: 0.7672 (Epoch 1), Total points: 1
[Charts] ✅ Added train_acc: 0.806 (Epoch 1), Total points: 1
[Charts] ✅ Added val_loss: 0.7672 (Epoch 1)
[Charts] ✅ Added val_acc: 0.806 (Epoch 1)
[Charts] Series recreated successfully
[Log] ✅ Added: 16:32:15 - Epoch 1: Loss: 0.7672, Acc: 0.8060
```

✅ **زمانی که همان Epoch است (Duplicate Poll):**

```
[Charts] ⏭️ Skipped duplicate poll for Epoch 1 (train_loss: 0.7672)
```

✅ **Epoch بعدی:**

```
[Charts] ✅ NEW EPOCH DETECTED: 2
[Charts] ✅ Added train_loss: 0.5125 (Epoch 2), Total points: 2
[Charts] ✅ Added train_acc: 0.8507 (Epoch 2), Total points: 2
[Log] ✅ Added: 16:33:04 - Epoch 2: Loss: 0.5125, Acc: 0.8507
```

---

## 🔍 **Troubleshooting:**

### مشکل 1: چارت‌ها هنوز به‌روزرسانی نمی‌شوند ❌

**بررسی کنید:**

1. **آیا در Debug Output می‌بینید:**
   ```
   [Charts] ✅ NEW EPOCH DETECTED: X
   ```

   - **اگر نه:** مشکل از backend است، داده‌ها ارسال نمی‌شوند
   - **اگر بله:** مشکل از frontend است، باید بررسی کنید چرا chart refresh نمی‌شود

2. **آیا می‌بینید:**
   ```
   [Charts] Series recreated successfully
   ```

   - **اگر نه:** ممکن است exception رخ داده باشد
   - Debug Output را برای error بررسی کنید

3. **آیا `_trainLossData.Count` بزرگتر از 0 است؟**
   
   در Debug Output باید ببینید:
   ```
   Total points: 1
   Total points: 2
   Total points: 3
   ```

### مشکل 2: Backend در دسترس نیست ❌

**علائم:**
```
❌ خطا در اتصال
Backend در دسترس نیست!
```

**راه‌حل:**

1. Terminal backend را بررسی کنید (terminal 7)
2. مطمئن شوید که می‌بینید:
   ```
   INFO: Uvicorn running on http://127.0.0.1:8181
   ```

3. اگر backend خاموش است:
   ```powershell
   cd D:\Project\ModelCreator\backend
   .\venv\Scripts\activate
   python main.py
   ```

### مشکل 3: فقط 1 نقطه در chart است ❌

**علت احتمالی:**

1. **Training هنوز شروع نشده:**
   - صبر کنید تا Epoch 1 تمام شود (حدود 34 ثانیه)

2. **Polling کار نمی‌کند:**
   - در Debug Output باید هر 2 ثانیه ببینید:
     ```
     ========== [Polling] Received Data ==========
     ```

3. **Backend همان داده را برمی‌گرداند:**
   - اگر `current_epoch` همیشه 1 است، ممکن است callback کار نکند

### مشکل 4: عدد‌ها hardcoded به نظر می‌رسند ❌

**بررسی کنید:**

1. آیا عدد‌ها تغییر می‌کنند؟
   - برای مثال: `0.7672` → `0.5125` → `0.4570`

2. اگر عدد‌ها تغییر می‌کنند اما chart ثابت است:
   - مشکل از chart rendering است
   - `Series recreated` را در Debug Output بررسی کنید

3. اگر عدد‌ها اصلاً تغییر نمی‌کنند:
   - مشکل از backend است
   - در terminal backend بررسی کنید:
     ```
     [ProgressCallback] Updated: Epoch X/50, Loss: Y, Acc: Z
     ```

---

## ✅ **Success Criteria:**

چارت‌ها زمانی که **درست کار می‌کنند** باید:

1. ✅ هر epoch یک نقطه جدید اضافه شود
2. ✅ Loss Chart به سمت پایین حرکت کند (کاهش یابد)
3. ✅ Accuracy Chart به سمت بالا حرکت کند (افزایش یابد)
4. ✅ بعد از 10 epoch، 10 نقطه در chart باشد
5. ✅ Logs هر epoch به‌روزرسانی شوند
6. ✅ Progress Bar پر شود
7. ✅ ETA محاسبه و نمایش داده شود

---

## 📊 **تایم‌لاین انتظار:**

```
00:00 - Dashboard باز می‌شود
        Status: "⏳ در حال آماده‌سازی..."
        Charts: خالی
        
00:05 - Training شروع می‌شود
        Status: "🔥 در حال آموزش..."
        Epoch: 0 / 50
        
00:34 - Epoch 1 تمام می‌شود
        ✅ Charts: 1 نقطه اضافه می‌شود
        Loss: 0.7672, Acc: 80.60%
        Log: "Epoch 1: Loss: 0.7672, Acc: 0.8060"
        
01:06 - Epoch 2 تمام می‌شود
        ✅ Charts: 2 نقطه
        Loss: 0.5125, Acc: 85.07%
        Log: "Epoch 2: Loss: 0.5125, Acc: 0.8507"
        
01:40 - Epoch 3 تمام می‌شود
        ✅ Charts: 3 نقطه
        Loss: 0.4570, Acc: 87.68%
        Log: "Epoch 3: Loss: 0.4570, Acc: 0.8768"
        
... و الی آخر
        
25:00 - Epoch 50 تمام می‌شود
        ✅ Charts: 50 نقطه
        Status: "✅ آموزش تکمیل شد!"
        → Auto-navigate to Results Page
```

---

## 📹 **ویدیو تست (مراحل):**

1. **Start:**
   - Open Dashboard
   - See "⏳ در حال آماده‌سازی..."

2. **After 5 seconds:**
   - Status changes to "🔥 در حال آموزش..."
   - Progress shows "0 / 50"

3. **After 34 seconds (Epoch 1 done):**
   - **Charts update with 1st point** ✅
   - Log shows "Epoch 1: ..."
   - Progress shows "1 / 50 (2%)"

4. **After 1 minute (Epoch 2 done):**
   - **Charts update with 2nd point** ✅
   - Loss decreases, Accuracy increases
   - Progress shows "2 / 50 (4%)"

5. **Continue watching:**
   - Every ~30 seconds, a new point appears
   - Charts grow progressively
   - Logs update with each epoch

---

## 🎯 **نتیجه‌گیری:**

اگر همه چیز درست کار کند:

✅ Charts به صورت real-time به‌روزرسانی می‌شوند
✅ هر epoch یک نقطه جدید
✅ عدد‌ها دیگر hardcoded نیستند
✅ Dashboard واقعاً "live" است

اگر مشکلی وجود داشت:
1. Debug Output را بررسی کنید
2. Backend terminal را بررسی کنید
3. به بخش Troubleshooting مراجعه کنید

---

**موفق باشید! 🚀**

