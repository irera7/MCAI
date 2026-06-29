# ✅ مشکل "داده‌ها ذخیره نمی‌شوند" برطرف شد!

## 🐛 مشکل:

**علائم:**
- ✅ در Frontend: files import شدند
- ✅ در Frontend: labels اختصاص داده شدند
- ✅ کلیک "Next: Select Model →"
- ❌ **در Backend: "No images found!"**
- ❌ **Label map: {}** (خالی!)

## 🔍 علت:

```csharp
private void Next_Click(...)
{
    // Validation... ✅
    
    // Navigate to next page
    NavigationService?.Navigate(new ModelSelectionPage(...));
    
    // ❌ هیچ چیزی ذخیره نشد!
}
```

**Frontend فقط navigate می‌کرد ولی:**
- ❌ فایل‌ها را کپی نمی‌کرد
- ❌ `labels.json` نمی‌ساخت
- ❌ ساختار `data/class1/`, `data/class2/` نمی‌ساخت

## ✅ راه‌حل:

### افزودن `SaveDataToProject()`:

```csharp
private void SaveDataToProject()
{
    // 1. Get project directory
    string projectDir = Path.Combine(projectsDir, projectId);
    string dataDir = Path.Combine(projectDir, "data");
    
    // 2. Create label mapping
    var labelMapping = new Dictionary<string, int>();
    for (int i = 0; i < labels.Count; i++)
    {
        labelMapping[labels[i]] = i;
    }
    
    // 3. Save labels.json
    string labelsJson = JsonSerializer.Serialize(labelMapping);
    File.WriteAllText(Path.Combine(projectDir, "labels.json"), labelsJson);
    
    // 4. Create subdirectories for each label
    foreach (var label in labels)
    {
        Directory.CreateDirectory(Path.Combine(dataDir, label));
    }
    
    // 5. Copy files to their label directories
    foreach (var item in dataItems.Where(d => !string.IsNullOrEmpty(d.Label)))
    {
        string destDir = Path.Combine(dataDir, item.Label);
        string destPath = Path.Combine(destDir, item.FileName);
        File.Copy(item.FilePath, destPath, overwrite: true);
    }
}
```

### فراخوانی در `Next_Click`:

```csharp
private void Next_Click(...)
{
    // Validations...
    
    try
    {
        SaveDataToProject();  // ✅ ذخیره داده‌ها!
        
        NavigationService?.Navigate(new ModelSelectionPage(...));
    }
    catch (Exception ex)
    {
        MessageBox.Show($"خطا در ذخیره داده‌ها: {ex.Message}", ...);
    }
}
```

## 📁 نتیجه:

### قبل: ❌
```
projects/
└── your-project-id/
    ├── project.json
    └── data/
        (خالی!)
```

### بعد: ✅
```
projects/
└── your-project-id/
    ├── project.json
    ├── labels.json          ✅ {"Class_A": 0, "Class_B": 1}
    └── data/
        ├── Class_A/         ✅
        │   ├── image1.jpg
        │   └── image2.jpg
        └── Class_B/         ✅
            ├── image3.jpg
            └── image4.jpg
```

## 🧪 تست کنید!

### 1. Rebuild Frontend

```powershell
cd D:\Project\ModelCreator\frontend\ModelCreator.UI
dotnet clean
dotnet build
dotnet run
```

### 2. Test کامل:

#### Step 1: Create Project
```
Name: test-save-data
Modality: Image Classification
```

#### Step 2: Data Import
1. **Import 2-3 عکس** (Screenshot یا هر چیزی)
2. **Labels پیش‌فرض هستند**: `Class_A`, `Class_B`
3. **Label اول** → `Class_A`
4. **Label دوم** → `Class_B`
5. **Statistics باید نشان دهد**:
   ```
   Total: 2
   Labeled: 2   ✅
   Class_A: 1
   Class_B: 1
   ```

#### Step 3: Next
کلیک **"Next: Select Model →"**

**باید ببینید پیامی مثل:**
```
✅ داده‌ها با موفقیت ذخیره شدند!
Saved 2 files to D:\...\projects\...\data
```

#### Step 4: بررسی دستی (Optional)

```powershell
cd D:\Project\ModelCreator\projects

# پیدا کردن project
dir

# رفتن به project
cd test-save-data-id

# بررسی ساختار
tree /F data

# باید ببینید:
# data/
# ├── Class_A/
# │   └── image1.jpg
# └── Class_B/
#     └── image2.jpg

# بررسی labels.json
type labels.json
# باید ببینید: {"Class_A": 0, "Class_B": 1}
```

### 3. Test Training:

1. **Model Selection** → ResNet-18
2. **Training Config** → کلیک "Start Training"
3. **Backend Log باید نشان دهد**:
   ```
   Loading data for project ...
   Loaded 2 classes: ['Class_A', 'Class_B']  ✅
   Found 1 images in Class_A/                ✅
   Found 1 images in Class_B/                ✅
   Loaded 2 samples                          ✅
   Starting training...                      ✅
   ```

**نه این:**
```
❌ Label map: {}
❌ Found 0 images
❌ No images found!
```

## ✅ نتیجه:

**قبل:**
- Frontend: files را نشان می‌دهد ✅
- Click "Next" → navigate ✅
- Backend: "No images found!" ❌
- Training: fail ❌

**بعد:**
- Frontend: files را نشان می‌دهد ✅
- Click "Next" → **saves data!** ✅
- Backend: "Found X images" ✅
- Training: **starts successfully!** ✅

## 🐛 اگر خطا داشتید:

### خطا: "Access Denied" یا "File in use"

**راه‌حل:**
- فایل‌های source را ببندید
- برنامه‌های دیگر که ممکن است فایل باز کرده باشند را ببندید
- دوباره تلاش کنید

### خطا: "Path not found"

**راه‌حل:**
دستی بررسی کنید:
```powershell
cd D:\Project\ModelCreator
dir projects
# باید پوشه projects وجود داشته باشد
```

اگر نیست:
```powershell
mkdir projects
```

### Backend هنوز "No images" می‌گوید

**بررسی:**
1. **دستی بررسی کنید** که فایل‌ها واقعاً کپی شده‌اند
2. **Restart Backend** (مهم!)
   ```powershell
   # در Terminal Backend: Ctrl+C
   python main.py
   ```
3. دوباره training شروع کنید

## 📊 Debug Logging:

در `SaveDataToProject()` logging اضافه شده:
```csharp
System.Diagnostics.Debug.WriteLine($"Saved {copiedCount} files to {dataDir}");
System.Diagnostics.Debug.WriteLine($"Label mapping: {labelsJson}");
```

**در Output Window (Visual Studio) باید ببینید:**
```
Saved 2 files to D:\...\data
Label mapping: {"Class_A": 0, "Class_B": 1}
```

اگر نمی‌بینید = فایل‌ها کپی نشدند!

## 🚀 بعدش:

1. ✅ **Data Import** - با save!
2. ✅ **Model Selection** - ResNet-18
3. ✅ **Training Config** - شروع آموزش
4. ✅ **Backend finds data** - "Found X images"
5. ✅ **Training starts successfully!** 🔥

---

**الان Rebuild کنید و test کنید!** 🎉

```powershell
dotnet clean
dotnet build
dotnet run
```

