# ModelCreator User Manual

## Complete Guide to Building AI Models Without Code

---

<p align="center">
  <strong>Version 1.2.0</strong><br>
  <em>Your Journey from Data to Deployed AI Model</em>
</p>

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Understanding the Interface](#2-understanding-the-interface)
3. [Creating Your First Project](#3-creating-your-first-project)
4. [Importing Data](#4-importing-data)
5. [Selecting a Model](#5-selecting-a-model)
6. [Configuring Training](#6-configuring-training)
7. [Training Your Model](#7-training-your-model)
8. [Evaluating Results](#8-evaluating-results)
9. [Exporting Your Model](#9-exporting-your-model)
10. [Testing with Inference Playground](#10-testing-with-inference-playground)
11. [Advanced Features](#11-advanced-features)
12. [Troubleshooting](#12-troubleshooting)
13. [Keyboard Shortcuts](#13-keyboard-shortcuts)
14. [Glossary](#14-glossary)

---

## 1. Getting Started

### 1.1 System Requirements

Before installing ModelCreator, ensure your system meets these requirements:

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Operating System | Windows 10 (64-bit) | Windows 11 (64-bit) |
| Processor | Intel Core i5 | Intel Core i7 / AMD Ryzen 7 |
| Memory | 8 GB RAM | 16 GB RAM |
| Storage | 10 GB free space | 50 GB SSD |
| Graphics | Integrated | NVIDIA GPU with 6GB+ VRAM |
| Display | 1280 × 720 | 1920 × 1080 |

> 💡 **Tip**: Having an NVIDIA GPU significantly speeds up training. Without a GPU, training will use your CPU (slower but still works).

### 1.2 Installation

#### Step 1: Install the Backend

1. Open **Command Prompt** or **PowerShell**
2. Navigate to the ModelCreator folder:
   ```bash
   cd D:\Project\ModelCreator\backend
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
4. Activate the virtual environment:
   ```bash
   venv\Scripts\activate
   ```
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

#### Step 2: Install the Frontend

1. Open a new terminal
2. Navigate to the frontend folder:
   ```bash
   cd D:\Project\ModelCreator\frontend
   ```
3. Restore packages:
   ```bash
   dotnet restore
   ```

### 1.3 Starting the Application

#### Start the Backend Server

```bash
cd D:\Project\ModelCreator\backend
venv\Scripts\activate
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8181
```

#### Start the Frontend Application

```bash
cd D:\Project\ModelCreator\frontend
dotnet run --project ModelCreator.UI
```

Or open `ModelCreator.sln` in Visual Studio and press **F5**.

---

## 2. Understanding the Interface

### 2.1 Main Window Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  [Logo]  ModelCreator              [Theme Toggle] [Settings]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐                                               │
│  │              │                                               │
│  │   SIDEBAR    │           MAIN CONTENT AREA                   │
│  │              │                                               │
│  │  • Home      │     Displays the current page content         │
│  │  • Projects  │     (Project creation, training, etc.)        │
│  │  • Training  │                                               │
│  │  • Results   │                                               │
│  │  • Export    │                                               │
│  │  • Settings  │                                               │
│  │              │                                               │
│  └──────────────┘                                               │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  Status Bar: Connection Status | GPU Status | Current Project   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Navigation

| Icon | Page | Description |
|------|------|-------------|
| 🏠 | Home | Welcome screen, recent projects |
| 📁 | Projects | View and manage all projects |
| ➕ | Create Project | Start a new AI project |
| 📊 | Training | Monitor active training |
| 📈 | Results | View training results |
| 📤 | Export | Export trained models |
| ⚙️ | Settings | Application settings |

### 2.3 Theme Options

ModelCreator supports two themes:

- **Dark Theme** (Default): Easy on the eyes, recommended for extended use
- **Light Theme**: High contrast, good for bright environments

Toggle between themes using the theme button in the top-right corner.

---

## 3. Creating Your First Project

### 3.1 Step-by-Step Project Creation

1. **Click "Create New Project"** on the Home page

2. **Enter Project Details**:
   - **Project Name**: Give your project a descriptive name (e.g., "Cat vs Dog Classifier")
   - **Description** (Optional): Add notes about your project

3. **Select Data Type**:

   | Data Type | Use For |
   |-----------|---------|
   | 🖼️ Image | Photos, pictures, visual content |
   | 📝 Text | Documents, reviews, messages |
   | 🎵 Audio | Sound recordings, voice, music |
   | 🎬 Video | Video clips, recordings |
   | 📊 Tabular | CSV files, spreadsheets |
   | 📈 Time Series | Sequential data, trends |
   | 🏥 Medical | MRI, CT scans, ECG signals |
   | 🧬 Genomic | DNA sequences, genes |

4. **Click "Create"**

### 3.2 Project Structure

When you create a project, ModelCreator creates this folder structure:

```
projects/
└── your-project-id/
    ├── project.json      # Project configuration
    ├── data/             # Your training data
    ├── models/           # Saved model checkpoints
    ├── exports/          # Exported models
    ├── logs/             # Training logs
    └── tensorboard/      # TensorBoard files
```

---

## 4. Importing Data

### 4.1 Data Import Methods

#### Method 1: Drag and Drop
1. Open the **Data Import** page
2. Drag files or folders directly onto the drop zone
3. Files will be automatically organized

#### Method 2: Browse Files
1. Click **"Browse Files"** button
2. Select individual files to import
3. Click **"Open"**

#### Method 3: Browse Folder
1. Click **"Browse Folder"** button
2. Select a folder containing your data
3. All supported files will be imported

### 4.2 Data Organization by Type

#### 🖼️ Image Classification

Organize your images in folders by class:

```
data/
├── cats/
│   ├── cat1.jpg
│   ├── cat2.jpg
│   └── cat3.jpg
├── dogs/
│   ├── dog1.jpg
│   ├── dog2.jpg
│   └── dog3.jpg
└── birds/
    ├── bird1.jpg
    └── bird2.jpg
```

**Supported formats**: JPG, JPEG, PNG, BMP, TIFF

#### 📝 Text Classification

Create a CSV file with two columns:

```csv
text,label
"I love this product!",positive
"Terrible experience",negative
"It's okay I guess",neutral
```

Or organize text files in folders:

```
data/
├── positive/
│   ├── review1.txt
│   └── review2.txt
└── negative/
    ├── review1.txt
    └── review2.txt
```

#### 🎵 Audio Classification

Organize audio files in folders by class:

```
data/
├── music/
│   └── song1.wav
├── speech/
│   └── talk1.wav
└── noise/
    └── static1.wav
```

**Supported formats**: WAV, MP3, FLAC

#### 📊 Tabular Data

Prepare a CSV file with features and a target column:

```csv
age,income,education,purchased
25,50000,Bachelor,yes
35,75000,Master,yes
22,30000,High School,no
```

### 4.3 Creating and Managing Labels

1. **View Labels**: See all detected classes in the Labels panel
2. **Add Label**: Click "+" to create a new class
3. **Rename Label**: Double-click a label to rename it
4. **Delete Label**: Select label and click "Delete"
5. **Assign Data**: Drag files to labels to assign them

### 4.4 Data Preview

Before training, preview your data:

1. Click on any sample in the data list
2. View the preview in the right panel
3. Check that labels are correctly assigned
4. Verify data quality

### 4.5 Data Statistics

The statistics panel shows:

| Statistic | Description |
|-----------|-------------|
| Total Samples | Number of data points |
| Classes | Number of unique labels |
| Distribution | Samples per class |
| Split Preview | Train/Val/Test distribution |

> ⚠️ **Warning**: Imbalanced data (very different class sizes) may affect model performance. Try to have similar amounts of data for each class.

---

## 5. Selecting a Model

### 5.1 Model Selection Page

After importing data, you'll choose a model architecture. Each model has different characteristics:

### 5.2 Image Models

| Model | Speed | Accuracy | Best For |
|-------|-------|----------|----------|
| **ResNet-18** ⭐ | Fast | Good | General use, quick experiments |
| **ResNet-50** | Medium | Very Good | Production models |
| **EfficientNet-B0** | Fast | Very Good | Balance of speed and accuracy |
| **MobileNetV3** | Very Fast | Good | Mobile/edge deployment |
| **Vision Transformer** | Slow | Excellent | Best accuracy, needs more data |

> 💡 **Recommendation**: Start with **ResNet-18** for quick experiments, then try **EfficientNet-B0** for better accuracy.

### 5.3 Text Models

| Model | Speed | Accuracy | Best For |
|-------|-------|----------|----------|
| **LSTM** ⭐ | Fast | Good | Simple text, quick training |
| **GRU** | Fast | Good | Similar to LSTM, slightly faster |
| **Transformer** | Medium | Very Good | Complex patterns |
| **BERT** | Slow | Excellent | Best accuracy, needs GPU |

> 💡 **Recommendation**: Start with **LSTM** for small datasets, use **BERT** for best results with larger datasets.

### 5.4 Specialized Models

| Modality | Model | Description |
|----------|-------|-------------|
| Audio | Spectrogram CNN | Converts audio to images, then classifies |
| Video | 3D CNN | Processes video frames together |
| Medical | MRI CNN | Optimized for medical images |
| Medical | ECG CNN | Processes heart signals |
| Genomic | DNA CNN | Analyzes DNA sequences |
| Tabular | XGBoost | Gradient boosting for tables |
| Time Series | LSTM | Sequential pattern recognition |

### 5.5 Model Information Cards

Each model card shows:

- **Model Name**: Architecture name
- **Parameters**: Model size (smaller = faster)
- **Speed Rating**: Training and inference speed
- **Pretrained**: Whether pretrained weights are available
- **Recommended**: Badge for suggested models

---

## 6. Configuring Training

### 6.1 Basic Settings

#### Epochs
- **What it means**: How many times the model sees all your data
- **Range**: 1 - 1000
- **Default**: 50
- **Tip**: Start with 50, increase if model is still improving

#### Batch Size
- **What it means**: How many samples to process at once
- **Options**: 8, 16, 32, 64, 128
- **Default**: 32
- **Tip**: Reduce if you get "out of memory" errors

#### Learning Rate
- **What it means**: How fast the model learns
- **Range**: 0.0001 - 0.01
- **Default**: 0.001
- **Tip**: Lower values = slower but more stable training

#### Optimizer
- **Options**:
  - **Adam** (Recommended): Works well for most cases
  - **SGD**: Classic option, may need tuning
  - **AdamW**: Adam with better regularization
  - **RMSProp**: Good for recurrent networks

### 6.2 Advanced Settings

#### Data Split
Configure how your data is divided:

| Split | Purpose | Default |
|-------|---------|---------|
| Training | Model learns from this | 80% |
| Validation | Monitor during training | 10% |
| Test | Final evaluation | 10% |

#### Regularization

| Setting | Purpose | Default |
|---------|---------|---------|
| Dropout | Prevents overfitting | 0.2 |
| Weight Decay | L2 regularization | 0.0001 |

#### Data Augmentation
Enable to artificially increase your dataset variety:

- **For Images**: Rotation, flipping, cropping, color changes
- **For Audio**: Noise addition, pitch shifting
- **For Text**: (Not applicable)

> 💡 **Tip**: Enable augmentation when you have limited data.

#### Early Stopping
Automatically stops training when the model stops improving:

| Setting | Description | Default |
|---------|-------------|---------|
| Enable | Turn on/off | Yes |
| Patience | Epochs to wait | 10 |

### 6.3 Hardware Settings

#### Device Selection
- **CUDA (GPU)**: Much faster, requires NVIDIA GPU
- **CPU**: Slower but always available

#### Mixed Precision
- **Enable**: Faster training, less memory usage
- **Requires**: Modern NVIDIA GPU (RTX series)

### 6.4 Recommended Configurations

#### Quick Experiment
```
Epochs: 20
Batch Size: 32
Learning Rate: 0.001
Optimizer: Adam
Early Stopping: Yes (patience: 5)
```

#### Production Model
```
Epochs: 100
Batch Size: 32
Learning Rate: 0.001
Optimizer: AdamW
Dropout: 0.3
Weight Decay: 0.0001
Early Stopping: Yes (patience: 15)
Data Augmentation: Yes
```

#### Limited GPU Memory
```
Batch Size: 8 or 16
Mixed Precision: Yes
Model: MobileNetV3 or EfficientNet-B0
```

---

## 7. Training Your Model

### 7.1 Starting Training

1. Review your configuration
2. Click **"Start Training"**
3. The training dashboard will open automatically

### 7.2 Training Dashboard

The dashboard shows real-time training progress:

```
┌─────────────────────────────────────────────────────────────────┐
│  Training Progress                                              │
│  ═══════════════════════════════════════════════════════════   │
│                                                                  │
│  Epoch: 25/50                    Progress: 50%                  │
│  ████████████████████░░░░░░░░░░░░░░░░░░░░                       │
│                                                                  │
│  Elapsed: 5m 30s                 ETA: 5m 30s                    │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Loss Chart                      Accuracy Chart                 │
│  ┌─────────────────┐            ┌─────────────────┐            │
│  │    ╲            │            │            ╱    │            │
│  │     ╲___        │            │        ___╱     │            │
│  │         ╲___    │            │    ___╱         │            │
│  │             ╲   │            │   ╱             │            │
│  └─────────────────┘            └─────────────────┘            │
│  — Train Loss  — Val Loss       — Train Acc  — Val Acc         │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  Current Metrics                                                │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │
│  │ Train Loss   │ Val Loss     │ Train Acc    │ Val Acc      │ │
│  │ 0.2534       │ 0.3012       │ 92.5%        │ 89.3%        │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
│                                                                  │
│  Best Val Accuracy: 91.2% (Epoch 22)                           │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  [Stop Training]  [Save Checkpoint]  [View TensorBoard]        │
└─────────────────────────────────────────────────────────────────┘
```

### 7.3 Understanding the Charts

#### Loss Chart
- **Training Loss** (solid line): Should decrease over time
- **Validation Loss** (dashed line): Should decrease, then stabilize

#### Accuracy Chart
- **Training Accuracy**: Should increase over time
- **Validation Accuracy**: Should increase, then stabilize

### 7.4 Warning Signs During Training

| Sign | Meaning | Solution |
|------|---------|----------|
| Val loss increasing while train loss decreasing | Overfitting | Enable dropout, add data, use augmentation |
| Both losses not decreasing | Learning rate too low/high | Adjust learning rate |
| Training very slow | Batch size too small or CPU training | Increase batch size, use GPU |
| Out of memory error | Batch size too large | Reduce batch size |

### 7.5 Training Controls

| Button | Action |
|--------|--------|
| **Stop Training** | Immediately stop (saves current state) |
| **Save Checkpoint** | Save current model without stopping |
| **View TensorBoard** | Open detailed visualization |

### 7.6 Using TensorBoard

For detailed training visualization:

1. Click **"View TensorBoard"** or run manually:
   ```bash
   cd D:\Project\ModelCreator\projects\{your-project-id}
   tensorboard --logdir tensorboard
   ```
2. Open browser to `http://localhost:6006`
3. View detailed charts, histograms, and more

---

## 8. Evaluating Results

### 8.1 Results Page

After training completes, view your results:

```
┌─────────────────────────────────────────────────────────────────┐
│  Training Results                                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Final Metrics                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │  Accuracy: 94.5%    │  Loss: 0.1823    │  F1 Score: 0.943 ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Training Summary                                               │
│  • Total Epochs: 50                                             │
│  • Training Time: 15 minutes                                    │
│  • Best Epoch: 45                                               │
│  • Early Stopping: Triggered at epoch 50                        │
│                                                                  │
│  Confusion Matrix                                               │
│  ┌─────────────────────────────────┐                           │
│  │           Predicted             │                           │
│  │         Cat    Dog    Bird      │                           │
│  │  Cat    95     3      2         │                           │
│  │  Dog    4      92     4         │                           │
│  │  Bird   1      5      94        │                           │
│  └─────────────────────────────────┘                           │
│                                                                  │
│  Per-Class Performance                                          │
│  • Cat:  Precision: 95%, Recall: 95%, F1: 95%                  │
│  • Dog:  Precision: 92%, Recall: 92%, F1: 92%                  │
│  • Bird: Precision: 94%, Recall: 94%, F1: 94%                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Understanding Metrics

| Metric | What It Means | Good Value |
|--------|---------------|------------|
| **Accuracy** | Overall correct predictions | > 90% |
| **Loss** | Model error (lower is better) | < 0.3 |
| **Precision** | Of predicted positives, how many were correct | > 90% |
| **Recall** | Of actual positives, how many were found | > 90% |
| **F1 Score** | Balance of precision and recall | > 90% |

### 8.3 Reading the Confusion Matrix

The confusion matrix shows:
- **Diagonal** (top-left to bottom-right): Correct predictions
- **Off-diagonal**: Mistakes (misclassifications)

Example interpretation:
- "95 cats were correctly identified as cats"
- "3 cats were incorrectly identified as dogs"

### 8.4 When to Retrain

Consider retraining if:
- Accuracy is below your target
- One class has much lower performance than others
- Confusion matrix shows consistent misclassifications

**Improvement strategies**:
1. Add more training data
2. Enable data augmentation
3. Try a different model architecture
4. Adjust hyperparameters
5. Use AutoML for automatic optimization

---

## 9. Exporting Your Model

### 9.1 Export Formats

| Format | File Extension | Best For |
|--------|----------------|----------|
| **PyTorch** | .pt, .pth | Python applications |
| **ONNX** | .onnx | Cross-platform deployment |
| **TorchScript** | .pt | Optimized PyTorch |
| **TensorFlow Lite** | .tflite | Mobile apps (Android/iOS) |

### 9.2 How to Export

1. Go to the **Export** page
2. Select your trained model
3. Choose export format(s)
4. Click **"Export"**
5. Find exported files in `projects/{id}/exports/`

### 9.3 Export Package Contents

Each export includes:

```
exports/
├── model.pt              # Model weights
├── model.onnx            # ONNX format (if selected)
├── metadata.json         # Configuration and labels
├── instructions.txt      # How to use the model
└── sample_code.py        # Example inference code
```

### 9.4 Using Exported Models

#### PyTorch
```python
import torch

# Load model
checkpoint = torch.load('model.pt')
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

# Make prediction
with torch.no_grad():
    output = model(input_tensor)
    prediction = torch.argmax(output, dim=1)
```

#### ONNX
```python
import onnxruntime as ort

# Load model
session = ort.InferenceSession('model.onnx')

# Make prediction
input_name = session.get_inputs()[0].name
output = session.run(None, {input_name: input_data})
```

---

## 10. Testing with Inference Playground

### 10.1 Accessing the Playground

1. After training, click **"Test Model"** or
2. Go to **Inference Playground** from the sidebar

### 10.2 Making Predictions

#### For Images
1. Click **"Upload Image"** or drag an image
2. Click **"Predict"**
3. View results with confidence scores

#### For Text
1. Type or paste text in the input box
2. Click **"Predict"**
3. View classification result

#### For Audio
1. Upload an audio file or record
2. Click **"Predict"**
3. View classification result

### 10.3 Understanding Results

```
┌─────────────────────────────────────────────────────────────────┐
│  Prediction Results                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Image Preview]                                                │
│                                                                  │
│  Predicted Class: Cat                                           │
│  Confidence: 94.5%                                              │
│                                                                  │
│  All Predictions:                                               │
│  ┌────────────────────────────────────────┐                    │
│  │ Cat   ████████████████████████ 94.5%  │                    │
│  │ Dog   ███                      4.2%   │                    │
│  │ Bird  █                        1.3%   │                    │
│  └────────────────────────────────────────┘                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 10.4 Batch Predictions

1. Enable **"Batch Mode"**
2. Upload multiple files
3. Click **"Predict All"**
4. Export results to CSV

---

## 11. Advanced Features

### 11.1 AutoML (Automatic Hyperparameter Optimization)

AutoML automatically finds the best settings for your model.

#### How to Use
1. Go to **AutoML** page
2. Select your project
3. Configure:
   - **Number of Trials**: How many configurations to try (default: 50)
   - **Timeout**: Maximum time in minutes (optional)
4. Click **"Start Optimization"**

#### What AutoML Optimizes
- Learning rate
- Batch size
- Optimizer type
- Dropout rate
- Weight decay
- Model-specific parameters

#### Viewing Results
After completion:
- Best parameters are displayed
- Optimization history chart
- Parameter importance analysis

### 11.2 Model Comparison

Compare multiple models on the same dataset:

1. Go to **Model Comparison** page
2. Select models to compare
3. Click **"Compare"**
4. View side-by-side results

### 11.3 Ensemble Methods

Combine multiple models for better accuracy:

#### Voting Ensemble
- **Hard Voting**: Majority vote wins
- **Soft Voting**: Average probabilities (usually better)

#### How to Create
1. Go to **Ensemble Methods** page
2. Select trained models to combine
3. Choose ensemble type
4. Click **"Create Ensemble"**

### 11.4 Model Serving

Deploy your model as an API:

1. Go to **Model Serving** page
2. Select a trained model
3. Click **"Load Model"**
4. Use the API endpoint for predictions

#### API Usage
```bash
curl -X POST "http://localhost:8181/api/inference/predict/{project_id}" \
     -H "Content-Type: application/json" \
     -d '{"data": "your input data"}'
```

### 11.5 TensorBoard Integration

For detailed training analysis:

1. During or after training, click **"View TensorBoard"**
2. Or manually run:
   ```bash
   tensorboard --logdir projects/{project_id}/tensorboard
   ```
3. Open `http://localhost:6006` in your browser

TensorBoard shows:
- Training/validation curves
- Learning rate changes
- Model graph
- Histograms of weights

---

## 12. Troubleshooting

### 12.1 Common Issues and Solutions

#### "Backend not connected"
**Cause**: Backend server is not running

**Solution**:
1. Open terminal
2. Navigate to backend folder
3. Activate virtual environment
4. Run `python main.py`

#### "CUDA out of memory"
**Cause**: GPU memory is full

**Solutions**:
1. Reduce batch size (try 8 or 16)
2. Use a smaller model (MobileNetV3)
3. Enable mixed precision training
4. Close other GPU applications

#### "No samples found"
**Cause**: Data not organized correctly

**Solution**: Ensure data is in class folders:
```
data/
├── class1/
│   └── files...
└── class2/
    └── files...
```

#### Training is very slow
**Causes & Solutions**:
- Using CPU instead of GPU → Check GPU is detected
- Batch size too small → Increase batch size
- Too many workers → Reduce num_workers to 2-4

#### Model accuracy is low
**Solutions**:
1. Add more training data
2. Enable data augmentation
3. Train for more epochs
4. Try a different model
5. Use AutoML to find better hyperparameters

#### "Module not found" error
**Solution**:
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### 12.2 Checking System Status

#### Verify GPU is Available
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU name: {torch.cuda.get_device_name(0)}")
```

#### Check Backend Health
```bash
curl http://localhost:8181/health
```

Expected response:
```json
{
  "status": "healthy",
  "api_version": "1.0.0",
  "torch_available": true
}
```

### 12.3 Getting Help

1. Check the **API Documentation**: `http://localhost:8181/docs`
2. Review training logs in `projects/{id}/logs/`
3. Check TensorBoard for detailed metrics

---

## 13. Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + N` | New Project |
| `Ctrl + O` | Open Project |
| `Ctrl + S` | Save Project |
| `Ctrl + Shift + S` | Save Checkpoint |
| `F5` | Start Training |
| `Shift + F5` | Stop Training |
| `Ctrl + E` | Export Model |
| `Ctrl + T` | Open TensorBoard |
| `Ctrl + ,` | Settings |
| `F1` | Help |
| `Ctrl + D` | Toggle Dark/Light Theme |

---

## 14. Glossary

| Term | Definition |
|------|------------|
| **Accuracy** | Percentage of correct predictions |
| **Augmentation** | Artificially increasing dataset variety |
| **Batch** | Group of samples processed together |
| **Batch Size** | Number of samples in each batch |
| **Checkpoint** | Saved state of model during training |
| **Classification** | Categorizing data into predefined classes |
| **CNN** | Convolutional Neural Network (for images) |
| **CUDA** | NVIDIA's GPU computing platform |
| **Dropout** | Regularization technique to prevent overfitting |
| **Epoch** | One complete pass through all training data |
| **Early Stopping** | Stopping training when improvement stops |
| **F1 Score** | Harmonic mean of precision and recall |
| **GPU** | Graphics Processing Unit (accelerates training) |
| **Hyperparameter** | Settings that control training (learning rate, etc.) |
| **Inference** | Using trained model to make predictions |
| **Learning Rate** | How fast the model updates its weights |
| **Loss** | Measure of model error (lower is better) |
| **LSTM** | Long Short-Term Memory (for sequences) |
| **Model** | The AI algorithm that learns from data |
| **ONNX** | Open Neural Network Exchange format |
| **Optimizer** | Algorithm that updates model weights |
| **Overfitting** | Model memorizes training data, performs poorly on new data |
| **Precision** | Of positive predictions, how many were correct |
| **Pretrained** | Model already trained on large dataset |
| **Recall** | Of actual positives, how many were found |
| **Regularization** | Techniques to prevent overfitting |
| **TensorBoard** | Tool for visualizing training metrics |
| **Training** | Process of teaching model from data |
| **Validation** | Data used to monitor training progress |
| **Weight Decay** | L2 regularization strength |

---

## Quick Reference Card

### Workflow Summary

```
1. CREATE PROJECT     →  Choose name and data type
        ↓
2. IMPORT DATA        →  Drag & drop or browse files
        ↓
3. SELECT MODEL       →  Choose architecture (start with recommended)
        ↓
4. CONFIGURE          →  Set epochs, batch size, learning rate
        ↓
5. TRAIN              →  Click Start, monitor progress
        ↓
6. EVALUATE           →  Check accuracy, confusion matrix
        ↓
7. EXPORT             →  Save model in desired format
        ↓
8. DEPLOY             →  Use model in your application
```

### Recommended Starting Settings

| Setting | Value |
|---------|-------|
| Epochs | 50 |
| Batch Size | 32 |
| Learning Rate | 0.001 |
| Optimizer | Adam |
| Early Stopping | Yes (patience: 10) |
| Data Augmentation | Yes |

---

**Need more help?** Check the API documentation at `http://localhost:8181/docs` when the backend is running.

---

<p align="center">
  <strong>ModelCreator v1.2.0</strong><br>
  <em>Making AI Accessible to Everyone</em><br><br>
  © 2025 ModelCreator. All Rights Reserved.
</p>


