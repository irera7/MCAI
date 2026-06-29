# CSV Auto-Labeling Guide

## 🎯 Overview

The web app now supports **CSV-based auto-labeling**, matching the Windows desktop app workflow. This allows you to prepare labels in a CSV file and automatically apply them when importing images.

---

## 📝 CSV Format

### Structure
```csv
filename,label
image1.jpg,cat
image2.jpg,cat
image3.jpg,dog
image4.jpg,dog
```

### Rules
1. **Header (Optional):** First line can be header with "filename,label" or similar
2. **Format:** Each line: `filename,label`
3. **Filename:** Exact filename of the image (e.g., "cat001.jpg")
4. **Label:** Class/category name (e.g., "cat", "dog", "bird")
5. **Encoding:** UTF-8 (supports international characters)

---

## 🚀 Workflow

### Method 1: CSV Auto-Labeling (Recommended)

**Step 1: Prepare CSV File**
```csv
filename,label
cat1.jpg,cat
cat2.jpg,cat
dog1.jpg,dog
dog2.jpg,dog
```

**Step 2: In Web App**
1. Go to Step 2 (Import & Label Data)
2. Click "Import CSV (Auto-label)"
3. Select your CSV file
4. Labels are automatically created!

**Step 3: Import Images**
1. Drag & drop all your images
2. Files with matching names are auto-labeled! ✨
3. Click "Upload X Labeled Files"
4. Done! 🎉

### Method 2: Manual Labeling

**Alternative workflow:**
1. Add labels manually in right panel
2. Import images
3. Select label for each file manually
4. Upload

---

## 📊 Example Workflow

### Your Dataset
```
my_images/
├── cat1.jpg
├── cat2.jpg
├── dog1.jpg
├── dog2.jpg
```

### Create CSV (labels.csv)
```csv
filename,label
cat1.jpg,cat
cat2.jpg,cat
dog1.jpg,dog
dog2.jpg,dog
```

### In Web App
1. **Import CSV:** Click "Import CSV" → Select labels.csv
   - Result: Labels "cat" and "dog" created automatically
   
2. **Import Images:** Drag & drop all 4 images
   - Result: All files auto-labeled based on CSV!
   - cat1.jpg → labeled as "cat" ✅
   - cat2.jpg → labeled as "cat" ✅
   - dog1.jpg → labeled as "dog" ✅
   - dog2.jpg → labeled as "dog" ✅

3. **Upload:** Click "Upload 4 Labeled Files"
   - Done! All images uploaded with correct labels

---

## 💡 Tips & Tricks

### 1. Generate CSV from Folder Structure

If you have organized folders:
```
dataset/
├── cat/
│   ├── img1.jpg
│   └── img2.jpg
└── dog/
    ├── img1.jpg
    └── img2.jpg
```

Generate CSV:
```python
import os
import csv

with open('labels.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['filename', 'label'])
    
    for label in os.listdir('dataset'):
        folder = os.path.join('dataset', label)
        if os.path.isdir(folder):
            for filename in os.listdir(folder):
                if filename.endswith(('.jpg', '.png', '.jpeg')):
                    writer.writerow([filename, label])
```

### 2. CSV with Excel

1. Open Excel
2. Create columns: filename | label
3. Fill in data
4. Save As → CSV (UTF-8)

### 3. Bulk Rename Files

If files have prefixes:
```csv
filename,label
cat_001.jpg,cat
cat_002.jpg,cat
dog_001.jpg,dog
dog_002.jpg,dog
```

### 4. Handle Special Characters

CSV supports international names:
```csv
filename,label
gato1.jpg,gato
chien1.jpg,chien
猫1.jpg,猫
```

---

## ⚠️ Common Issues

### Issue 1: Files Not Auto-Labeled

**Problem:** Imported images but labels not applied

**Solution:** 
- Check filename spelling in CSV matches exactly
- Filenames are case-sensitive: "cat1.jpg" ≠ "Cat1.jpg"
- Check for extra spaces in CSV

### Issue 2: CSV Not Reading

**Problem:** CSV import fails

**Solution:**
- Ensure format is: `filename,label`
- Check file is actually .csv (not .txt renamed)
- Use UTF-8 encoding
- Remove empty lines at end

### Issue 3: Some Files Not Matching

**Problem:** Some files auto-labeled, others not

**Solution:**
- Only files with exact filename match are labeled
- Files without matches can be labeled manually
- Check CSV for typos in filenames

---

## 🎓 Advanced: Python Script for Auto-CSV Generation

```python
#!/usr/bin/env python3
"""
Auto-generate labels.csv from organized folder structure
"""
import os
import csv
from pathlib import Path

def generate_labels_csv(dataset_dir, output_csv='labels.csv'):
    """
    Generate CSV from folder structure:
    dataset/
      cat/
        img1.jpg
      dog/
        img1.jpg
    """
    labels = []
    
    for label_dir in Path(dataset_dir).iterdir():
        if not label_dir.is_dir():
            continue
            
        label_name = label_dir.name
        
        for img_file in label_dir.iterdir():
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                labels.append({
                    'filename': img_file.name,
                    'label': label_name
                })
    
    # Write CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['filename', 'label'])
        writer.writeheader()
        writer.writerows(labels)
    
    print(f"✅ Generated {output_csv} with {len(labels)} entries")
    print(f"📊 Labels found: {set(row['label'] for row in labels)}")

if __name__ == '__main__':
    generate_labels_csv('path/to/your/dataset')
```

Usage:
```bash
python generate_csv.py
# Creates labels.csv
```

---

## 📦 Sample CSV Download

Download sample CSV: [sample_labels.csv](http://localhost:3333/sample_labels.csv)

---

## ✅ Checklist

Before uploading:
- [ ] CSV file created with correct format
- [ ] Filenames in CSV match actual image files
- [ ] No typos or extra spaces
- [ ] Images ready to import
- [ ] At least 2 different labels

Ready to go! 🚀

