# 🔧 رفع خطای اتصال Frontend به Backend

## 🔴 خطا
```
خطا در اتصال به سرور

Backend در دسترس نیست! لطفاً اطمینان حاصل کنید Backend اجرا شده است:
cd backend
python main.py
```

**اما Backend در حال اجرا است!** 🤔

---

## ✅ راه‌حل‌های احتمالی

### راه‌حل 1: Restart کردن Backend و Frontend

#### مرحله 1: Backend را Restart کنید
```bash
# در Terminal Backend:
Ctrl + C  (برای توقف)

# دوباره اجرا:
cd backend
.venv\Scripts\activate  # (اگر فعال نیست)
python main.py

# باید ببینید:
INFO: Uvicorn running on http://127.0.0.1:8181 (Press CTRL+C to quit)
INFO: Started server process [XXXX]
INFO: Waiting for application startup.
2025-11-26 XX:XX:XX - main - INFO - Starting AI Model Builder Backend...
INFO: Application startup complete.
```

#### مرحله 2: Frontend را Restart کنید
```bash
# در Terminal Frontend:
Ctrl + C  (اگر اجرا است)

# دوباره اجرا:
cd frontend/ModelCreator.UI
dotnet run

# یا از Visual Studio:
# Stop → Start (F5)
```

---

### راه‌حل 2: بررسی Port

ممکن است Backend روی port دیگری اجرا شده باشد.

#### بررسی:
```bash
# در CMD/PowerShell:
netstat -ano | findstr :8181

# یا
netstat -ano | findstr :8000
```

اگر Backend روی port 8000 است:
```bash
# در Terminal Backend ببینید:
# Uvicorn running on http://127.0.0.1:8000  ← اگر 8000 است

# باید ApiService را تغییر دهید:
```

---

### راه‌حل 3: تغییر BaseUrl در Frontend

اگر Backend روی port دیگری است:

**فایل:** `frontend/ModelCreator.UI/Services/ApiService.cs`

```csharp
// خط 31 - تغییر دهید:
public string BaseUrl { get; set; } = "http://127.0.0.1:8000";  // اگر Backend روی 8000 است
// یا
public string BaseUrl { get; set; } = "http://localhost:8181";  // localhost به جای 127.0.0.1
```

---

### راه‌حل 4: Firewall یا Antivirus

#### بررسی Firewall:
```
1. Windows Settings → Privacy & Security → Windows Security
2. Firewall & network protection
3. Allow an app through firewall
4. بررسی کنید:
   - Python.exe ✅
   - ModelCreator.UI.exe ✅
```

#### موقتاً غیرفعال کردن (برای تست):
```
Control Panel → Windows Defender Firewall → Turn off (NOT RECOMMENDED for production)
```

---

### راه‌حل 5: تست دستی اتصال

#### تست 1: از Browser
```
1. مرورگر را باز کنید
2. آدرس را بزنید:
   http://127.0.0.1:8181/api/system/info

3. باید ببینید:
   {
     "status": "ok",
     "gpu_available": true,
     ...
   }
```

#### تست 2: از PowerShell/CMD
```bash
curl http://127.0.0.1:8181/api/system/info

# یا
Invoke-WebRequest -Uri "http://127.0.0.1:8181/api/system/info"
```

اگر این تست‌ها کار کرد → مشکل از Frontend است  
اگر کار نکرد → مشکل از Backend است

---

### راه‌حل 6: بررسی CORS در Backend

**فایل:** `backend/main.py`

بررسی کنید خطوط CORS وجود دارند:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # یا ["http://localhost:*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### راه‌حل 7: Backend روی localhost به جای 127.0.0.1

اگر Backend روی `localhost` اجرا شده:

**تغییر در main.py:**
```python
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",  # ← مطمئن شوید 127.0.0.1 است نه 0.0.0.0
        port=8181,
        reload=True
    )
```

---

## 🧪 Debug گام به گام

### گام 1: بررسی Backend
```bash
# Terminal Backend را ببینید
# باید ببینید:
INFO: Uvicorn running on http://127.0.0.1:8181

# اگر می‌بینید:
INFO: Uvicorn running on http://0.0.0.0:8181
→ مشکل اینجاست! باید 127.0.0.1 باشد
```

### گام 2: تست API از Browser
```
http://127.0.0.1:8181/api/system/info
```

اگر کار کرد → Frontend مشکل دارد  
اگر کار نکرد → Backend مشکل دارد

### گام 3: بررسی Frontend Debug Output
```
Visual Studio → Output Window → Debug

باید ببینید:
GET: http://127.0.0.1:8181/api/system/info
POST: http://127.0.0.1:8181/api/training/start/...
```

اگر می‌بینید:
```
POST Error: Unable to connect...
API request failed: ...
```
→ مشکل اتصال است

---

## 💡 راه‌حل سریع (توصیه شده)

### روش 1: Restart همه چیز
```bash
# 1. Backend را ببندید (Ctrl+C)
# 2. Frontend را ببندید
# 3. Backend را دوباره اجرا کنید
cd backend
python main.py

# 4. صبر کنید تا ببینید:
INFO: Application startup complete.

# 5. Frontend را دوباره اجرا کنید
cd frontend/ModelCreator.UI
dotnet run

# 6. تست کنید
```

### روش 2: از Test Project استفاده کنید
```
1. Backend اجرا است
2. Frontend: Home → Load Project
3. test-cat-dog را انتخاب کنید
4. اگر لیست پروژه‌ها نمایش داده شد → اتصال OK است
5. اگر خطا داد → به راه‌حل‌های بالا برگردید
```

---

## 🔍 اطلاعات Debug

برای کمک بیشتر، این اطلاعات را بفرستید:

### 1. Backend Output
```bash
# آخرین 20 خط Terminal Backend:
(کپی کنید)
```

### 2. Frontend Error
```bash
# پیام کامل خطا از MessageBox:
(کپی کنید)
```

### 3. Test Browser
```bash
# نتیجه این آدرس در Browser:
http://127.0.0.1:8181/api/system/info
```

### 4. Port Check
```bash
# نتیجه این دستور:
netstat -ano | findstr :8181
```

---

## ✅ علامت‌های اتصال موفق

### Backend
```
INFO: Uvicorn running on http://127.0.0.1:8181 ✅
INFO: Started server process [XXXX] ✅
INFO: Application startup complete. ✅
```

### Frontend
```
# در Output Window:
GET: http://127.0.0.1:8181/api/system/info ✅
Response: {"status":"ok",...} ✅
```

### Browser
```
http://127.0.0.1:8181/api/system/info
→ JSON response نمایش داده می‌شود ✅
```

---

## 🎯 خلاصه

| مشکل | راه‌حل |
|------|--------|
| Backend اجرا نیست | `cd backend && python main.py` |
| Port اشتباه است | بررسی و تغییر BaseUrl |
| Firewall مسدود کرده | Allow کردن Python/App |
| CORS مشکل دارد | بررسی main.py |
| Cache مشکل ساز است | Restart همه چیز |

---

**توصیه:** ابتدا Backend و Frontend را Restart کنید! 90% مواقع مشکل حل می‌شود! ✅

---

**تاریخ:** 2025-11-26  
**نسخه:** 1.0

