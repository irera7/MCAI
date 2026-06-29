# 🎮 راهنمای تشخیص و رفع مشکل GPU

## مشکل: GPU شناسایی نمی‌شود

### ✅ راه‌حل‌ها به ترتیب اولویت:

## 1️⃣ تست Backend

ابتدا مطمئن شوید Backend در حال اجرا است:

```powershell
cd backend
.\venv\Scripts\activate
python main.py
```

Backend باید روی `http://127.0.0.1:8181` اجرا شود.

## 2️⃣ تست GPU در Python

اسکریپت تست را اجرا کنید:

```powershell
cd backend
.\venv\Scripts\activate
python test_gpu.py
```

این اسکریپت اطلاعات کامل GPU را نمایش می‌دهد.

### یا به صورت دستی:

```powershell
python -c "import torch; print('CUDA Available:', torch.cuda.is_available()); print('GPU Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU')"
```

## 3️⃣ بررسی نصب NVIDIA

### چک کردن GPU و Driver:

```powershell
nvidia-smi
```

این دستور باید اطلاعات GPU و نسخه driver را نشان دهد.

اگر خطا داد:
- NVIDIA Driver نصب نیست
- GPU شما NVIDIA نیست (AMD یا Intel کار نمی‌کند)

### نصب NVIDIA Driver:

1. به سایت NVIDIA بروید: https://www.nvidia.com/download/index.aspx
2. مدل GPU خود را پیدا کنید
3. آخرین driver را دانلود و نصب کنید
4. کامپیوتر را Restart کنید

## 4️⃣ بررسی نصب CUDA

### چک کردن CUDA:

```powershell
nvcc --version
```

اگر CUDA نصب نیست:

1. از سایت NVIDIA دانلود کنید: https://developer.nvidia.com/cuda-downloads
2. CUDA Toolkit 11.8 یا 12.1 را نصب کنید
3. Restart کنید

## 5️⃣ نصب مجدد PyTorch با CUDA

اگر PyTorch بدون CUDA نصب شده:

```powershell
cd backend
.\venv\Scripts\activate

# حذف PyTorch قبلی
pip uninstall torch torchvision torchaudio

# نصب PyTorch با CUDA 11.8
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# یا برای CUDA 12.1
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

برای انتخاب نسخه مناسب: https://pytorch.org/get-started/locally/

## 6️⃣ تست نهایی

بعد از نصب، دوباره تست کنید:

```powershell
cd backend
.\venv\Scripts\activate
python test_gpu.py
```

باید پیام `✅ GPU is available and working!` را ببینید.

## 🔍 عیب‌یابی پیشرفته

### مشکل 1: PyTorch GPU را نمی‌بیند ولی nvidia-smi کار می‌کند

**علت:** نسخه CUDA در PyTorch با نسخه Driver سازگار نیست

**راه‌حل:**
```powershell
# چک کردن نسخه CUDA Driver
nvidia-smi  # خط اول نسخه CUDA را نشان می‌دهد

# نصب PyTorch با نسخه مناسب
# اگر CUDA 11.x دارید:
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# اگر CUDA 12.x دارید:
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### مشکل 2: "CUDA out of memory"

**علت:** حافظه GPU پر است

**راه‌حل:**
1. Batch Size را کوچک‌تر کنید (مثلاً از 64 به 32 یا 16)
2. برنامه‌های دیگری که از GPU استفاده می‌کنند را ببندید
3. کامپیوتر را Restart کنید

### مشکل 3: GPU خیلی کند است

**علت:** GPU مناسب Deep Learning نیست (مثل GPU های Laptop)

**راه‌حل:**
- از CPU استفاده کنید (برای dataset های کوچک قابل قبول است)
- Mixed Precision را غیرفعال کنید
- Batch Size را کاهش دهید

## 📊 GPU های پشتیبانی شده

### ✅ پشتیبانی کامل:
- NVIDIA GeForce RTX 40xx (4090, 4080, etc.)
- NVIDIA GeForce RTX 30xx (3090, 3080, 3070, 3060, etc.)
- NVIDIA GeForce RTX 20xx (2080 Ti, 2070, etc.)
- NVIDIA GeForce GTX 16xx (1660 Ti, 1650, etc.)
- NVIDIA Tesla (T4, V100, A100, etc.)

### ⚠️ پشتیبانی محدود:
- NVIDIA GeForce GTX 10xx (1080 Ti, 1070, 1060)
- NVIDIA GeForce GTX 9xx (980, 970)

### ❌ بدون پشتیبانی:
- AMD GPUs (تنها NVIDIA پشتیبانی می‌شود)
- Intel GPUs (integrated graphics)
- GPU های قدیمی‌تر از GTX 9xx

## 💡 نکات مهم

1. **برای آموزش Deep Learning:**
   - حداقل 4GB VRAM نیاز است
   - 6GB+ توصیه می‌شود
   - 8GB+ برای مدل‌های بزرگ

2. **بدون GPU:**
   - هنوز می‌توانید از برنامه استفاده کنید
   - فقط آموزش کندتر است (5-10x)
   - برای dataset های کوچک (<1000 نمونه) قابل قبول است

3. **Cloud Training:**
   - اگر GPU ندارید، از Google Colab استفاده کنید (رایگان)
   - یا از خدمات AWS/Azure/GCP

## 📞 دریافت کمک

اگر باز هم مشکل دارید:

1. خروجی `test_gpu.py` را ذخیره کنید
2. خروجی `nvidia-smi` را ذخیره کنید
3. نسخه PyTorch را چک کنید: `pip show torch`
4. یک Issue در GitHub ایجاد کنید

---

**به یاد داشته باشید:** بدون GPU هم می‌توانید از برنامه استفاده کنید! 
فقط آموزش کمی بیشتر طول می‌کشد. ✅

