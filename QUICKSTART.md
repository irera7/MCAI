# AI Model Builder - Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### 1. Start the Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
Backend will run at `http://127.0.0.1:8181`

### 2. Start the Frontend
```bash
cd frontend
dotnet run --project ModelCreator.UI
```

### 3. Create Your First Model

1. Click "Create New Project"
2. Enter project name: "My First Model"
3. Select data type: "Image Classification"
4. Drag & drop images into folders by class
5. Select model: "MobileNetV3" (fast and accurate)
6. Click "Start Training"
7. Watch live progress in dashboard
8. Export model when complete

## 📋 System Check

Before starting, ensure you have:
- ✅ Python 3.10+
- ✅ .NET 8.0 SDK
- ✅ 8+ GB RAM
- ✅ (Optional) NVIDIA GPU for faster training

## 🎯 Example Projects

### Image Classifier (Cats vs Dogs)
```
/data
  /cats
    cat1.jpg
    cat2.jpg
  /dogs
    dog1.jpg
    dog2.jpg
```

### Text Classifier (Sentiment Analysis)
```csv
text,label
"Great product!",positive
"Terrible experience",negative
```

### Audio Classifier (Music Genres)
```
/data
  /rock
    song1.wav
  /jazz
    song2.wav
```

## 🔧 Troubleshooting

**Backend won't start?**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**Frontend build error?**
```bash
dotnet clean
dotnet restore
dotnet build
```

**CUDA not detected?**
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

## 📚 Next Steps

- Read `PROJECT_DOCUMENTATION.md` for complete guide
- Check `/docs` API documentation
- Try example datasets in `/examples`
- Join community forum for support

## 🎓 Training Tips

1. **Start Small**: Use 50-100 images per class initially
2. **Balance Data**: Equal samples per class works best
3. **Try Augmentation**: Enable for small datasets
4. **Monitor Validation**: Watch for overfitting
5. **Save Checkpoints**: Save best models during training

## 📞 Support

- 📖 Documentation: `PROJECT_DOCUMENTATION.md`
- 🐛 Issues: GitHub Issues
- 💬 Community: Discord/Forum
- 📧 Email: support@aimodelbuilder.com

---

**Ready to build AI models? Let's go! 🚀**

