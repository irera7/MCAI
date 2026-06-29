# 🔄 دستور Restart سریع

## Backend را Restart کنید:

در Terminal که Backend دارد اجرا می‌شود:

1. فشار دهید: **Ctrl + C** (توقف Backend)
2. دوباره اجرا کنید:

```bash
python main.py
```

یا اگر Terminal بسته شد:

```powershell
cd D:\Project\ModelCreator\backend
.\venv\Scripts\activate
python main.py
```

---

## ✅ بعد از Restart:

Frontend را **نیازی به Restart ندارد!** 

فقط:
1. یک پروژه **جدید** بسازید
2. Import Data
3. Select Model  
4. Training Config → **"▶️ شروع آموزش"**

**حالا باید ببینید:**
- ⏳ "در حال آماده‌سازی..." (2 ثانیه)
- 🔥 "در حال آموزش..." (شروع Epoch ها)
- 📊 نمودارها Update می‌شوند
- 📈 Loss کم می‌شود، Accuracy زیاد می‌شود

---

## 🎯 Mock Training:

- هر Epoch: **2-5 ثانیه**
- برای 10 Epoch: **~30 ثانیه**
- برای 50 Epoch: **~3 دقیقه**

**Loss**: شروع از ~2.0 → کم می‌شود به ~0.1
**Accuracy**: شروع از ~50% → زیاد می‌شود به ~95%

---

**Backend را Restart کنید و دوباره تست کنید!** 🚀

