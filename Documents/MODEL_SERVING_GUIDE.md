# 🚀 راهنمای Model Serving
## ModelCreator - Production Deployment Guide

---

## 📋 فهرست مطالب
1. [مقدمه](#مقدمه)
2. [نصب و راه‌اندازی](#نصب-و-راه‌اندازی)
3. [Model Registry](#model-registry)
4. [API Endpoints](#api-endpoints)
5. [استفاده از Python](#استفاده-از-python)
6. [استفاده از REST API](#استفاده-از-rest-api)
7. [مثال‌های کاربردی](#مثال‌های-کاربردی)
8. [Production Tips](#production-tips)

---

## 🎯 مقدمه

Model Serving یک infrastructure برای deploy و serve کردن مدل‌های آموزش‌دیده است که شامل:

- ✅ Model Registry: مدیریت مدل‌ها
- ✅ Hot-Reload: بارگذاری/حذف بدون restart
- ✅ Batch Inference: پردازش دسته‌ای
- ✅ Device Management: CUDA/CPU
- ✅ Health Monitoring: بررسی سلامت
- ✅ API Gateway: REST endpoints

---

## 🔧 نصب و راه‌اندازی

### 1. اطمینان از نصب dependencies:

```bash
pip install torch torchvision pillow fastapi uvicorn python-multipart
```

### 2. شروع Backend:

```bash
cd backend
python main.py
```

Server روی `http://127.0.0.1:8181` اجرا می‌شود.

### 3. تست Health Check:

```bash
curl http://127.0.0.1:8181/api/serve/health
```

Output:
```json
{
  "status": "healthy",
  "loaded_models": 0,
  "registered_models": 0,
  "cuda_available": true,
  "timestamp": "2025-11-30T12:00:00"
}
```

---

## 📦 Model Registry

### مفهوم:
Model Registry یک database از مدل‌های ثبت‌شده است که اطلاعات زیر را ذخیره می‌کند:
- مسیر فایل مدل
- نوع مدل (modality)
- Metadata (num_classes, accuracy, etc.)
- تاریخ ثبت

### ساختار Registry:

```json
{
  "model-id-123": {
    "model_path": "projects/abc/best_model.pth",
    "model_type": "image",
    "metadata": {
      "num_classes": 10,
      "model_name": "resnet18",
      "accuracy": 0.95,
      "trained_on": "2025-11-30"
    },
    "registered_at": "2025-11-30T10:00:00",
    "version": "1.0"
  }
}
```

---

## 🌐 API Endpoints

### Model Management:

#### 1. ثبت مدل جدید
```http
POST /api/serve/register
Content-Type: multipart/form-data

model_id: "my-model-v1"
model_path: "projects/abc123/best_model.pth"
model_type: "image"
metadata: '{"num_classes": 10, "model_name": "resnet18"}'
```

**Response**:
```json
{
  "status": "success",
  "message": "Model 'my-model-v1' registered successfully",
  "model_id": "my-model-v1"
}
```

#### 2. بارگذاری مدل در Memory
```http
POST /api/serve/load/my-model-v1?device=cuda
```

**Response**:
```json
{
  "status": "success",
  "message": "Model 'my-model-v1' loaded on cuda",
  "model_id": "my-model-v1",
  "device": "cuda"
}
```

#### 3. حذف مدل از Memory
```http
DELETE /api/serve/unload/my-model-v1
```

#### 4. لیست مدل‌های بارگذاری شده
```http
GET /api/serve/models
```

**Response**:
```json
{
  "status": "success",
  "loaded_models": [
    {
      "model_id": "my-model-v1",
      "loaded": true,
      "device": "cuda",
      "loaded_at": "2025-11-30T10:05:00",
      "metadata": {...}
    }
  ],
  "total": 1
}
```

#### 5. اطلاعات یک مدل
```http
GET /api/serve/models/my-model-v1
```

---

### Inference Endpoints:

#### 1. پیش‌بینی تک تصویر
```http
POST /api/serve/predict/my-model-v1
Content-Type: multipart/form-data

file: [image file]
```

**Response**:
```json
{
  "status": "success",
  "model_id": "my-model-v1",
  "predictions": [5],
  "probabilities": [[0.05, 0.1, 0.05, 0.03, 0.02, 0.7, 0.02, 0.01, 0.01, 0.01]],
  "num_samples": 1
}
```

#### 2. پیش‌بینی Batch
```http
POST /api/serve/predict/batch/my-model-v1
Content-Type: multipart/form-data

files: [image1, image2, image3, ...]
```

**Response**:
```json
{
  "status": "success",
  "model_id": "my-model-v1",
  "predictions": [5, 3, 8],
  "probabilities": [...],
  "num_samples": 3
}
```

---

## 🐍 استفاده از Python

### مثال 1: ثبت و بارگذاری مدل

```python
from backend.engine.model_server import model_server

# ثبت مدل
model_server.register_model(
    model_id="my-classifier",
    model_path="projects/abc123/best_model.pth",
    model_type="image",
    metadata={
        "num_classes": 10,
        "model_name": "resnet18",
        "accuracy": 0.95
    }
)

# بارگذاری در memory
success = model_server.load_model("my-classifier", device="cuda")

if success:
    print("Model loaded successfully!")
```

### مثال 2: Inference

```python
import torch
import asyncio
from backend.engine.model_server import model_server

async def predict_image(image_tensor):
    """پیش‌بینی برای یک تصویر"""
    result = await model_server.predict(
        model_id="my-classifier",
        input_data=image_tensor,
        batch_size=32
    )
    
    if result["status"] == "success":
        print(f"Prediction: {result['predictions'][0]}")
        print(f"Confidence: {max(result['probabilities'][0]):.2%}")
    else:
        print(f"Error: {result['error']}")

# اجرا
image = torch.randn(1, 3, 224, 224)  # مثال
asyncio.run(predict_image(image))
```

### مثال 3: Health Check

```python
from backend.engine.model_server import model_server

# بررسی سلامت
health = model_server.health_check()

print(f"Status: {health['status']}")
print(f"Loaded models: {health['loaded_models']}")
print(f"CUDA available: {health['cuda_available']}")
```

---

## 🌍 استفاده از REST API

### مثال 1: ثبت مدل (cURL)

```bash
curl -X POST "http://127.0.0.1:8181/api/serve/register" \
  -F "model_id=image-classifier-v1" \
  -F "model_path=projects/abc123/best_model.pth" \
  -F "model_type=image" \
  -F 'metadata={"num_classes": 10, "model_name": "resnet18"}'
```

### مثال 2: بارگذاری مدل (cURL)

```bash
curl -X POST "http://127.0.0.1:8181/api/serve/load/image-classifier-v1?device=cuda"
```

### مثال 3: پیش‌بینی (cURL)

```bash
curl -X POST "http://127.0.0.1:8181/api/serve/predict/image-classifier-v1" \
  -F "file=@/path/to/image.jpg"
```

### مثال 4: Python requests

```python
import requests

# ثبت مدل
response = requests.post(
    "http://127.0.0.1:8181/api/serve/register",
    data={
        "model_id": "image-classifier-v1",
        "model_path": "projects/abc123/best_model.pth",
        "model_type": "image",
        "metadata": '{"num_classes": 10}'
    }
)

print(response.json())

# بارگذاری
response = requests.post(
    "http://127.0.0.1:8181/api/serve/load/image-classifier-v1",
    params={"device": "cuda"}
)

print(response.json())

# پیش‌بینی
with open("test_image.jpg", "rb") as f:
    response = requests.post(
        "http://127.0.0.1:8181/api/serve/predict/image-classifier-v1",
        files={"file": f}
    )

result = response.json()
print(f"Prediction: {result['predictions'][0]}")
```

---

## 💡 مثال‌های کاربردی

### Use Case 1: Image Classification API

```python
from fastapi import FastAPI, UploadFile, File
import requests
from PIL import Image
import io

app = FastAPI()

@app.post("/classify")
async def classify_image(file: UploadFile = File(...)):
    """API برای طبقه‌بندی تصویر"""
    
    # ارسال به model server
    files = {"file": (file.filename, await file.read(), file.content_type)}
    response = requests.post(
        "http://127.0.0.1:8181/api/serve/predict/image-classifier-v1",
        files=files
    )
    
    result = response.json()
    
    # Map prediction به label
    class_names = ["cat", "dog", "bird", ...]
    predicted_class = class_names[result["predictions"][0]]
    confidence = max(result["probabilities"][0])
    
    return {
        "class": predicted_class,
        "confidence": confidence
    }
```

### Use Case 2: Batch Processing Script

```python
import asyncio
from pathlib import Path
from backend.engine.model_server import model_server
from torchvision import transforms
from PIL import Image
import torch

async def process_directory(image_dir: str):
    """پردازش تمام تصاویر در یک پوشه"""
    
    # بارگذاری مدل
    model_server.load_model("image-classifier-v1", device="cuda")
    
    # Transform
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    # خواندن تصاویر
    images = []
    image_paths = list(Path(image_dir).glob("*.jpg"))
    
    for img_path in image_paths:
        img = Image.open(img_path).convert('RGB')
        img_tensor = transform(img)
        images.append(img_tensor)
    
    # Batch inference
    batch = torch.stack(images)
    result = await model_server.predict(
        model_id="image-classifier-v1",
        input_data=batch,
        batch_size=32
    )
    
    # نتایج
    for img_path, pred in zip(image_paths, result["predictions"]):
        print(f"{img_path.name}: Class {pred}")

# اجرا
asyncio.run(process_directory("test_images/"))
```

### Use Case 3: A/B Testing

```python
from backend.engine.model_server import model_server
import numpy as np

async def ab_test_models(image_tensor):
    """مقایسه دو مدل"""
    
    # بارگذاری هر دو مدل
    model_server.load_model("model-v1", device="cuda")
    model_server.load_model("model-v2", device="cuda")
    
    # پیش‌بینی با model v1
    result_v1 = await model_server.predict("model-v1", image_tensor)
    
    # پیش‌بینی با model v2
    result_v2 = await model_server.predict("model-v2", image_tensor)
    
    # مقایسه
    print(f"Model V1: Class {result_v1['predictions'][0]}")
    print(f"Model V2: Class {result_v2['predictions'][0]}")
    
    # انتخاب model با confidence بیشتر
    conf_v1 = max(result_v1['probabilities'][0])
    conf_v2 = max(result_v2['probabilities'][0])
    
    if conf_v1 > conf_v2:
        print("V1 wins!")
        return result_v1
    else:
        print("V2 wins!")
        return result_v2
```

---

## 🚀 Production Tips

### 1. Performance Optimization

```python
# استفاده از batch inference
# ❌ Bad: تک‌تک process کردن
for image in images:
    result = await model_server.predict(model_id, image)

# ✅ Good: batch processing
batch = torch.stack(images)
result = await model_server.predict(model_id, batch, batch_size=32)
```

### 2. Memory Management

```python
# Unload کردن مدل‌های استفاده نشده
model_server.unload_model("old-model")

# پاک کردن CUDA cache
import torch
torch.cuda.empty_cache()
```

### 3. Error Handling

```python
async def safe_predict(model_id, input_data):
    """پیش‌بینی با error handling"""
    try:
        result = await model_server.predict(model_id, input_data)
        
        if result["status"] == "error":
            print(f"Prediction error: {result['error']}")
            return None
        
        return result
    
    except Exception as e:
        print(f"Exception: {e}")
        return None
```

### 4. Load Balancing

```python
# استفاده از چند instance
models = ["model-gpu-1", "model-gpu-2", "model-gpu-3"]
current_model = 0

async def predict_with_lb(input_data):
    """پیش‌بینی با load balancing"""
    global current_model
    
    model_id = models[current_model]
    current_model = (current_model + 1) % len(models)
    
    return await model_server.predict(model_id, input_data)
```

### 5. Monitoring

```python
import time
from collections import defaultdict

# آمار performance
stats = defaultdict(list)

async def predict_with_monitoring(model_id, input_data):
    """پیش‌بینی با monitoring"""
    start_time = time.time()
    
    result = await model_server.predict(model_id, input_data)
    
    duration = time.time() - start_time
    stats[model_id].append(duration)
    
    # محاسبه میانگین
    avg_time = sum(stats[model_id]) / len(stats[model_id])
    print(f"Avg inference time for {model_id}: {avg_time:.3f}s")
    
    return result
```

### 6. Caching

```python
from functools import lru_cache
import hashlib

# Cache برای inputs تکراری
@lru_cache(maxsize=1000)
async def cached_predict(model_id, input_hash):
    """پیش‌بینی با caching"""
    # توجه: این یک مثال ساده است
    # در production باید cache persistence داشته باشید
    pass
```

---

## 📊 Benchmarking

### مقایسه Performance:

```python
import time
import numpy as np

async def benchmark_model(model_id, num_samples=100):
    """benchmark یک مدل"""
    
    # بارگذاری
    model_server.load_model(model_id, device="cuda")
    
    # تولید dummy data
    batch = torch.randn(num_samples, 3, 224, 224)
    
    # Warmup
    _ = await model_server.predict(model_id, batch[:10])
    
    # Benchmark
    start = time.time()
    result = await model_server.predict(model_id, batch, batch_size=32)
    duration = time.time() - start
    
    print(f"Model: {model_id}")
    print(f"Samples: {num_samples}")
    print(f"Total time: {duration:.3f}s")
    print(f"Throughput: {num_samples/duration:.1f} samples/sec")
```

---

## 🔒 Security Notes

1. **Authentication**: در production باید authentication اضافه کنید
2. **Rate Limiting**: محدودیت تعداد درخواست‌ها
3. **Input Validation**: اعتبارسنجی ورودی‌ها
4. **HTTPS**: استفاده از SSL/TLS

---

## ✅ Checklist برای Production

- [ ] Authentication & Authorization
- [ ] Rate limiting
- [ ] Input validation
- [ ] Error handling
- [ ] Logging & Monitoring
- [ ] Load balancing
- [ ] Caching strategy
- [ ] Backup & Recovery
- [ ] Health checks
- [ ] Documentation

---

**تاریخ**: 30 نوامبر 2025  
**نسخه**: 1.0  
**وضعیت**: Production Ready ✅

