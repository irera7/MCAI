# Complete Workflow Analysis: Windows App → Web App

## 🔍 Findings from Windows App Deep Dive

After thoroughly examining the Windows desktop application, here's the **COMPLETE workflow** for each data type:

---

## 📋 Universal Workflow (All Data Types)

### **Step 1: Create Project** → **Step 2: Import Data** → **Step 3: Select Model** → **Step 4: Configure Training** → **Step 5: Train** → **Step 6: Results**

---

## 1️⃣ IMAGE Projects

### Models Available (4 options):
1. **Simple CNN** 🏃
   - Speed: ★★★★★ | Accuracy: ★★★☆☆ | Memory: ★★☆☆☆
   - Training Time: ~5-10 min | Parameters: ~500K
   - **Recommended for:** Quick prototyping

2. **MobileNetV3** 📱 ⭐ **RECOMMENDED**
   - Speed: ★★★★☆ | Accuracy: ★★★★☆ | Memory: ★★☆☆☆
   - Training Time: ~15-20 min | Parameters: ~5.4M
   - **Recommended for:** Mobile deployment, balanced performance

3. **ResNet-50** 🎯
   - Speed: ★★☆☆☆ | Accuracy: ★★★★★ | Memory: ★★★★☆
   - Training Time: ~30-45 min | Parameters: ~25M
   - **Recommended for:** Complex classification, high accuracy

4. **Vision Transformer** ✨
   - Speed: ★☆☆☆☆ | Accuracy: ★★★★★ | Memory: ★★★★★
   - Training Time: ~1-2 hours | Parameters: ~86M
   - **Recommended for:** Large datasets, state-of-the-art accuracy

### Data Import Workflow:
1. **Option A: CSV + Images**
   - Import CSV (filename,label format)
   - Import folder or drag-drop images
   - Auto-label based on CSV mappings
   - Upload to server

2. **Option B: Manual Labeling**
   - Add labels manually
   - Import folder or drag-drop images
   - Assign labels to each image
   - Upload to server

### Training Configuration:
- Epochs: 10-200 (default: 50)
- Batch Size: 8, 16, **32**, 64, 128
- Learning Rate: 0.0001, 0.0005, **0.001**, 0.005, 0.01
- Optimizer: **Adam**, AdamW, SGD, RMSprop
- Train/Val/Test Split: 70/20/10
- Dropout: 0.0-0.5 (default: 0.2)
- Weight Decay: 0, 0.00001, **0.0001**, 0.001
- Data Augmentation: ✅ Enabled
- Early Stopping: ✅ Enabled (patience: 10)
- Mixed Precision: ☐ Optional (FP16, GPU only)

---

## 2️⃣ TEXT Projects

### Models Available (3 options):
1. **TF-IDF + Classifier** 📝
   - Speed: ★★★★★ | Accuracy: ★★★☆☆ | Memory: ★☆☆☆☆
   - Training Time: ~1-2 min | Parameters: ~100K
   - **Recommended for:** Small datasets, quick results

2. **LSTM Network** 🔄 ⭐ **RECOMMENDED**
   - Speed: ★★★☆☆ | Accuracy: ★★★★☆ | Memory: ★★★☆☆
   - Training Time: ~10-15 min | Parameters: ~2M
   - **Recommended for:** Sequence understanding, balanced performance

3. **BERT-Small** 🤖
   - Speed: ★★☆☆☆ | Accuracy: ★★★★★ | Memory: ★★★★☆
   - Training Time: ~20-30 min | Parameters: ~30M
   - **Recommended for:** Best accuracy, contextual understanding

### Data Import Workflow:
- **Formats:** CSV, JSON, TXT
- **CSV:** Must have 'text' and 'label' columns
- **JSON:** Array of objects with 'text' and 'label' fields
- **TXT:** One document per file in class folders

### Training Configuration:
Same as Image projects (epochs, batch size, learning rate, etc.)

---

## 3️⃣ AUDIO Projects

### Models Available (2 options):
1. **Spectrogram CNN** 🎵 ⭐ **RECOMMENDED**
   - Speed: ★★★★☆ | Accuracy: ★★★★☆ | Memory: ★★★☆☆
   - Training Time: ~15-20 min | Parameters: ~3M
   - **Recommended for:** Most audio tasks, excellent performance

2. **Audio Transformer** 🎼
   - Speed: ★★☆☆☆ | Accuracy: ★★★★★ | Memory: ★★★★☆
   - Training Time: ~30-45 min | Parameters: ~12M
   - **Recommended for:** Complex audio patterns, large datasets

### Data Import Workflow:
- **Formats:** WAV, MP3, FLAC
- **Recommended:** 16kHz or 22kHz sample rate
- **Organization:** By class folders or named with class labels

### Training Configuration:
Same as Image projects + Audio-specific preprocessing

---

## 4️⃣ VIDEO Projects

### Models Available (1 option):
1. **3D CNN** 🎬 ⭐ **RECOMMENDED**
   - Speed: ★★☆☆☆ | Accuracy: ★★★★☆ | Memory: ★★★★★
   - Training Time: ~1-2 hours | Parameters: ~10M
   - **Recommended for:** Action recognition, spatiotemporal processing

### Data Import Workflow:
- **Formats:** MP4, AVI, MOV
- **Organization:** By class folders
- **Preprocessing:** Frame extraction, temporal sampling

---

## 5️⃣ TABULAR Projects

### Models Available (3 options):
1. **Multi-Layer Perceptron (MLP)** 📊
   - Speed: ★★★★★ | Accuracy: ★★★☆☆ | Memory: ★☆☆☆☆
   - Training Time: ~2-5 min | Parameters: ~50K
   - **Recommended for:** Starting point, simple patterns

2. **XGBoost** 🚀 ⭐ **RECOMMENDED**
   - Speed: ★★★★☆ | Accuracy: ★★★★★ | Memory: ★★☆☆☆
   - Training Time: ~5-10 min | Parameters: Variable
   - **Recommended for:** Industry-standard, excellent accuracy

3. **Random Forest** 🌲
   - Speed: ★★★☆☆ | Accuracy: ★★★★☆ | Memory: ★★☆☆☆
   - Training Time: ~3-8 min | Parameters: Variable
   - **Recommended for:** Interpretability, feature importance

### Data Import Workflow:
- **Formats:** CSV, XLSX, XLS
- **Requirements:** Header row with column names, target column

### Preprocessing Options:
- **Scaling:** Standard Scaling, Min-Max, Robust, None
- **Missing Values:** Mean Imputation, Median, Mode, Drop
- **Encoding:** One-Hot, Label Encoding, Target Encoding
- **Feature Selection:** Optional (top N features)

### Training Configuration (XGBoost/Random Forest specific):
- **N Estimators (Trees):** 50-1000 (default: 100)
- **Max Depth:** 3-20 (default: 6)
- **Learning Rate:** 0.01-0.3 (default: 0.1)
- **Subsample:** 0.5-1.0 (default: 0.8)
- Train/Val Split: 70/30 or 80/20
- Early Stopping: ✅ Enabled

---

## 6️⃣ TIME SERIES Projects

### Models Available (3 options):
1. **LSTM** 📈 ⭐ **RECOMMENDED**
   - Speed: ★★★☆☆ | Accuracy: ★★★★☆ | Memory: ★★★☆☆
   - Training Time: ~15-20 min | Parameters: ~1.5M
   - **Recommended for:** Temporal dependencies, most use cases

2. **Temporal CNN** ⚡
   - Speed: ★★★★☆ | Accuracy: ★★★☆☆ | Memory: ★★☆☆☆
   - Training Time: ~10-15 min | Parameters: ~800K
   - **Recommended for:** Fast inference, pattern recognition

3. **Transformer** 🔮
   - Speed: ★★☆☆☆ | Accuracy: ★★★★★ | Memory: ★★★★☆
   - Training Time: ~30-40 min | Parameters: ~8M
   - **Recommended for:** Complex patterns, long sequences

### Data Import Workflow:
- **Formats:** CSV, TSV
- **Requirements:** Timestamp column, value columns, optional target

### Preprocessing Options:
- **Normalization:** Z-score, Min-Max, None
- **Window Size:** Sequence length for training
- **Stride:** Step size for sliding window
- **Missing Values:** Interpolation, Forward Fill, Drop

---

## 7️⃣ MEDICAL Projects

### Models Available (2 options):
1. **Medical CNN** 🏥 ⭐ **RECOMMENDED**
   - Speed: ★★★☆☆ | Accuracy: ★★★★☆ | Memory: ★★★☆☆
   - Training Time: ~20-30 min | Parameters: ~5M
   - **Recommended for:** Medical images (MRI, CT, X-ray)

2. **Signal 1D CNN** 💓
   - Speed: ★★★★☆ | Accuracy: ★★★★☆ | Memory: ★★☆☆☆
   - Training Time: ~15-20 min | Parameters: ~2M
   - **Recommended for:** ECG, EEG, time-series medical data

### Data Import Workflow:
- **Formats:** 
  - Images: DICOM, PNG, JPG
  - Signals: CSV, EDF
- **Organization:** By diagnosis/class folders

### Preprocessing Options:
- **DICOM:** Window/Level adjustment, HU normalization
- **Signals:** Filtering, baseline correction, artifact removal

---

## 8️⃣ GENOMIC Projects

### Models Available (2 options):
1. **DNA CNN** 🧬 ⭐ **RECOMMENDED**
   - Speed: ★★★☆☆ | Accuracy: ★★★★☆ | Memory: ★★★☆☆
   - Training Time: ~15-25 min | Parameters: ~3M
   - **Recommended for:** DNA sequence analysis, motif detection

2. **Sequence Embedding** 🔬
   - Speed: ★★☆☆☆ | Accuracy: ★★★★☆ | Memory: ★★★★☆
   - Training Time: ~20-30 min | Parameters: ~5M
   - **Recommended for:** Variable-length sequences, embeddings

### Data Import Workflow:
- **Formats:** FASTA, FASTQ, CSV
- **Requirements:** Sequence data with labels

### Preprocessing Options:
- **Encoding:** One-hot encoding (built-in)
- **K-mer:** Optional k-mer feature extraction
- **Sequence Length:** Fixed or variable

---

## 🎯 What's Missing in Web App?

### ❌ Currently MISSING:
1. **Model Selection Page** - Choose from 2-4 architectures per data type
2. **Training Configuration Page** - Detailed hyperparameter settings
3. **Model-specific UI** for each data type
4. **Preprocessing options** (especially for Tabular, TimeSeries, Medical)

### ✅ Currently HAVE:
1. Data Import pages (basic, being improved)
2. Training Dashboard (real-time monitoring)
3. Results Page
4. AutoML, Model Serving, Cloud Training

---

## 📊 Implementation Priority

### HIGH PRIORITY (Must Have):
1. ✅ **ModelSelectionPage** - Universal for all data types
2. ✅ **TrainingConfigPage** - Universal training settings
3. ✅ **Image models** - 4 architectures
4. ✅ **Text models** - 3 architectures
5. ✅ **Tabular models** - 3 architectures with preprocessing

### MEDIUM PRIORITY:
6. ✅ **Audio models** - 2 architectures
7. ✅ **TimeSeries models** - 3 architectures with preprocessing
8. ✅ **Medical models** - 2 architectures with DICOM support

### LOW PRIORITY:
9. ✅ **Video models** - 1 architecture
10. ✅ **Genomic models** - 2 architectures

---

## 🚀 Next Steps

1. Create `ModelSelectionPage.tsx` with all model architectures
2. Create `TrainingConfigPage.tsx` with comprehensive settings
3. Update routing in `App.tsx` to include these pages
4. Connect pages: `ImageProjectPage` → `ModelSelectionPage` → `TrainingConfigPage` → `TrainingDashboardPage`
5. Repeat for all 8 data types

---

## 📁 File Structure (New Pages)

```
web/src/pages/
├── ModelSelectionPage.tsx      ← NEW (Universal)
├── TrainingConfigPage.tsx      ← NEW (Universal)
├── ImageProjectPage.tsx        ← UPDATE (add "Next" button)
├── TextProjectPage.tsx         ← UPDATE
├── TabularProjectPage.tsx      ← UPDATE
├── AudioProjectPage.tsx        ← UPDATE
├── VideoProjectPage.tsx        ← UPDATE
├── TimeSeriesProjectPage.tsx   ← UPDATE
├── MedicalProjectPage.tsx      ← UPDATE
└── GenomicProjectPage.tsx      ← UPDATE
```

---

## 🎨 UI Design Notes

### Model Selection Cards:
- 2-column grid layout
- Each card shows:
  - Icon + Name + Category
  - Description
  - Speed/Accuracy/Memory bars (1-5 stars)
  - Training Time + Parameters
  - "⭐ Recommended" badge
- Click to select (highlight selected)
- "Back" and "Next: Configure Training →" buttons

### Training Config Page:
- **Left Panel:** Configuration forms
  - Basic Settings (Epochs, Batch Size, Learning Rate, Optimizer)
  - Advanced Settings (Data Split, Dropout, Weight Decay, Checkboxes)
- **Right Panel:** Summary + Actions
  - Configuration summary
  - Estimated training time
  - System info (GPU, RAM)
  - "🚀 Start Training" button

---

## ✨ Status: READY TO IMPLEMENT

All information gathered. Ready to build ModelSelectionPage and TrainingConfigPage!

