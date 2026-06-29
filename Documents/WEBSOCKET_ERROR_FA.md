# ⚠️ خطا: WebSocket connection failed

## مشکل
```
Failed to connect to training: WebSocket connection failed
Unable to connect to the remote server
```

## علت
Backend در حال اجرا نیست یا روی port 8181 در دسترس نیست.

## ✅ راه‌حل (گام‌به‌گام):

### قدم 1: بررسی Backend

**باز کردن یک Terminal جدید:**
```powershell
# رفتن به پوشه backend
cd D:\Project\ModelCreator\backend

# فعال کردن محیط مجازی
.\venv\Scripts\activate

# اجرای Backend
python main.py
```

**باید این پیام را ببینید:**
```
INFO:     Uvicorn running on http://127.0.0.1:8181
INFO:     Application startup complete
```

### قدم 2: تست Backend

در مرورگر این آدرس را باز کنید:
```
http://127.0.0.1:8181
```

باید یک JSON ببینید:
```json
{
  "message": "AI Model Builder API",
  "status": "running",
  "version": "1.0.0"
}
```

### قدم 3: اجرای Frontend

**در Terminal دیگر:**
```powershell
cd D:\Project\ModelCreator\frontend
dotnet run --project ModelCreator.UI
```

---

## 🔍 عیب‌یابی

### مشکل 1: Port 8181 قبلاً استفاده می‌شود

```powershell
# پیدا کردن process روی port 8181
netstat -ano | findstr :8181

# اگر چیزی پیدا شد، PID را یادداشت کنید و kill کنید:
Stop-Process -Id [PID] -Force
```

### مشکل 2: Backend خطا می‌دهد

```powershell
# بررسی نصب dependencies
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt

# اجرای دوباره
python main.py
```

### مشکل 3: Firewall مسدود می‌کند

1. Windows Firewall را باز کنید
2. "Allow an app through firewall" را انتخاب کنید
3. Python را پیدا کنید و اجازه دهید

---

## 📋 Checklist

قبل از اجرای Frontend، مطمئن شوید:

- [ ] Backend در حال اجرا است
- [ ] `http://127.0.0.1:8181` در مرورگر کار می‌کند
- [ ] خطایی در console Backend نیست
- [ ] Port 8181 آزاد است

---

## 🎯 دستور سریع (همه یکجا)

**Terminal 1 - Backend:**
```powershell
cd D:\Project\ModelCreator\backend; .\venv\Scripts\activate; python main.py
```

**Terminal 2 - Frontend (بعد از اینکه Backend اجرا شد):**
```powershell
cd D:\Project\ModelCreator\frontend; dotnet run --project ModelCreator.UI
```

---

## ⚡ نکات مهم

1. **همیشه ابتدا Backend را اجرا کنید**
2. منتظر بمانید تا پیام "Uvicorn running" را ببینید
3. سپس Frontend را اجرا کنید
4. هر دو Terminal باید باز بمانند

---

## 🐛 اگر باز هم کار نکرد

خروجی کامل Backend را بررسی کنید:
```powershell
cd backend
.\venv\Scripts\activate
python main.py
# خطاها را بخوانید
```

خطاهای رایج:
- `ModuleNotFoundError` → `pip install -r requirements.txt`
- `Address already in use` → Port 8181 را آزاد کنید
- `Permission denied` → با Admin اجرا کنید

---

**به یاد داشته باشید: Backend باید همیشه در حال اجرا باشد!** 🚀

