# 📚 راهنمای کامل آموزش مدل

## 🎯 گردش کار صحیح

### مراحل شروع آموزش:

```
1. ایجاد پروژه (Create Project)
   ↓
2. وارد کردن داده (Import Data) + لیبل‌گذاری
   ↓
3. انتخاب مدل (Select Model)
   ↓
4. تنظیم پارامترهای آموزش (Training Config)
   ↓
5. کلیک روی دکمه "▶️ شروع آموزش" (Start Training)
   ↓
6. منتظر بمانید تا "⏳ در حال شروع آموزش..." نمایش داده شود
   ↓
7. به طور خودکار به صفحه Training Dashboard می‌رود
   ↓
8. مشاهده آموزش لحظه‌ای (Live Training Monitor)
```

---

## ⚠️ نکات مهم

### 1. قبل از شروع آموزش:
✅ **حتماً Backend را اجرا کنید:**
```powershell
cd D:\Project\ModelCreator\backend
.\venv\Scripts\activate
python main.py
```

✅ **منتظر این پیام بمانید:**
```
INFO:     Uvicorn running on http://127.0.0.1:8181
```

---

### 2. در هنگام شروع آموزش:

**دکمه "Start Training" چکار می‌کند؟**

1. ✅ پارامترهای آموزش را می‌فرستد
2. ⏳ درخواست شروع آموزش می‌دهد
3. ⏳ 1 ثانیه صبر می‌کند (برای Initialize شدن WebSocket)
4. ➡️ به صفحه Training Dashboard می‌رود

**اگر خطا گرفتید:**
- بررسی کنید Backend در حال اجرا باشد
- مطمئن شوید Port 8181 باز است
- لاگ‌های Backend را بررسی کنید

---

### 3. در صفحه Training Dashboard:

**چه چیزهایی می‌بینید؟**
- 📊 **نمودارهای لحظه‌ای** (Loss & Accuracy)
- 📈 **پیشرفت Epoch** (Current/Total)
- 📝 **لاگ‌های آموزش** (Training Logs)
- ⏱️ **زمان سپری‌شده** (Elapsed Time)

**اگر خطای WebSocket دریافت کردید:**

```
خطا در اتصال به سرور آموزش:
WebSocket connection failed: Unable to connect to the remote server
```

**دلایل احتمالی:**

#### 1️⃣ Backend در حال اجرا نیست
**راه‌حل:**
```powershell
# Terminal جداگانه باز کنید
cd D:\Project\ModelCreator\backend
.\venv\Scripts\activate
python main.py
```

#### 2️⃣ آموزش هنوز شروع نشده
**راه‌حل:**
- به صفحه قبل (Training Config) برگردید
- دکمه "▶️ شروع آموزش" را بزنید
- صبر کنید تا دکمه به "⏳ در حال شروع آموزش..." تغییر کند
- خودکار به Dashboard می‌رود

#### 3️⃣ Port 8181 مسدود است
**راه‌حل:**
```powershell
# بررسی Port
Test-NetConnection -ComputerName 127.0.0.1 -Port 8181

# اگر TcpTestSucceeded: False بود، Firewall را بررسی کنید
```

---

## 🔍 عیب‌یابی (Troubleshooting)

### خطای "Unable to connect"

**1. بررسی Backend:**
```powershell
# آیا Backend در حال اجرا است؟
curl http://127.0.0.1:8181/api/health

# پاسخ باید باشد:
# {"status":"healthy"}
```

**2. بررسی WebSocket Endpoint:**
```powershell
# در Terminal Backend، باید این لاگ را ببینید:
INFO:     WebSocket connected for project <project_id>
```

**3. بررسی Firewall:**
```powershell
# Windows Firewall
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*8181*"}
```

---

### دکمه "Start Training" کار نمی‌کند

**علائم:**
- دکمه disable می‌شود
- متن "⏳ در حال شروع آموزش..." نمایش داده می‌شود
- هیچ اتفاقی نمی‌افتد

**راه‌حل:**

1. **بررسی لاگ Backend:**
```
# در Terminal که Backend اجرا کرده‌اید:
INFO:     POST /api/training/start/{project_id}
```

2. **بررسی Response:**
- اگر 200 OK دریافت شد → آموزش شروع شده
- اگر 500 Error → مشکل در Backend
- اگر Connection Error → Backend در دسترس نیست

3. **دوباره تلاش کنید:**
- Frontend را ببندید (Close)
- Backend را Restart کنید
- Frontend را دوباره اجرا کنید

---

### نمودارها خالی هستند

**دلایل:**
- آموزش تازه شروع شده (Epoch 0)
- داده هنوز ارسال نشده
- WebSocket disconnected

**راه‌حل:**
- چند ثانیه صبر کنید
- بررسی کنید "StatusText" چیزی نمایش می‌دهد:
  - ✅ "متصل به جلسه آموزش" → OK
  - ❌ "خطا در اتصال" → WebSocket problem

---

## 📖 مثال کامل

### سناریو: آموزش یک مدل Classification

```powershell
# Step 1: Start Backend
cd D:\Project\ModelCreator\backend
.\venv\Scripts\activate
python main.py

# منتظر بمانید:
# INFO:     Uvicorn running on http://127.0.0.1:8181
```

```powershell
# Step 2: Start Frontend (Terminal جدید)
cd D:\Project\ModelCreator\frontend
dotnet run --project ModelCreator.UI
```

**در Frontend:**

1. **Create Project:**
   - Name: `my_image_classifier`
   - Modality: `Image Classification`

2. **Import Data:**
   - Upload images
   - Add labels: `cat`, `dog`
   - Assign labels to each image

3. **Select Model:**
   - Choose: `ResNet-50`

4. **Configure Training:**
   - Epochs: `50`
   - Batch Size: `32`
   - Learning Rate: `0.001`
   - Optimizer: `Adam`
   - Click "▶️ شروع آموزش"

5. **Training Dashboard:**
   - منتظر بمانید دکمه به "⏳ در حال شروع آموزش..." تغییر کند
   - خودکار به Dashboard می‌رود
   - نمودارها شروع به Update شدن می‌کنند

---

## 🎓 نکات پیشرفته

### 1. Multi-GPU Training
اگر چند GPU دارید، در Training Config:
- Backend به طور خودکار همه GPUها را detect می‌کند
- آموزش parallel اجرا می‌شود

### 2. Resume Training
اگر آموزش قطع شد:
- پروژه را دوباره باز کنید
- به Training Config بروید
- دکمه "Resume Training" را بزنید

### 3. Early Stopping
اگر Early Stopping فعال باشد:
- آموزش خودکار متوقف می‌شود اگر Validation Loss بهبود نیافت
- بهترین مدل ذخیره می‌شود

---

## 📞 کمک بیشتر

**مستندات:**
- `PERSIAN_README.md` - راهنمای کامل
- `QUICK_START_FA.md` - شروع سریع
- `GPU_TROUBLESHOOTING_FA.md` - مشکلات GPU
- `WEBSOCKET_ERROR_FA.md` - مشکلات WebSocket
- `COMMON_ERRORS_FA.md` - خطاهای رایج

**لاگ‌ها:**
```powershell
# Backend logs
cd backend
python main.py
# تمام لاگ‌ها در Terminal نمایش داده می‌شوند

# Frontend logs
# در صفحه Training Dashboard → "Logs" tab
```

---

## ✅ چک‌لیست قبل از آموزش

- [ ] Backend در حال اجرا است
- [ ] Port 8181 باز است (Test-NetConnection)
- [ ] داده‌ها import شده‌اند
- [ ] لیبل‌ها به همه داده‌ها assign شده‌اند
- [ ] مدل انتخاب شده
- [ ] پارامترهای آموزش تنظیم شده‌اند
- [ ] GPU detect شده (اختیاری)
- [ ] فضای دیسک کافی وجود دارد

---

**🎉 حالا آماده‌اید! دکمه "▶️ شروع آموزش" را بزنید!**

