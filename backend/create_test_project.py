# 🧪 Quick Test Script - ساخت داده تستی

import os
import json
from pathlib import Path
import urllib.request
from PIL import Image
import io

def setup_test_project():
    """
    ساخت یک پروژه تستی با داده‌های نمونه
    """
    print("=" * 60)
    print("Test Project Setup")
    print("=" * 60)
    
    # Project directory
    projects_dir = Path("../projects")
    projects_dir.mkdir(exist_ok=True)
    
    test_project = projects_dir / "test-cat-dog"
    data_dir = test_project / "data"
    
    # ساخت ساختار
    (data_dir / "cat").mkdir(parents=True, exist_ok=True)
    (data_dir / "dog").mkdir(parents=True, exist_ok=True)
    
    print(f"\n[OK] Created directories:")
    print(f"  {data_dir / 'cat'}")
    print(f"  {data_dir / 'dog'}")
    
    # ساخت label mapping
    labels = {"cat": 0, "dog": 1}
    labels_file = test_project / "labels.json"
    with open(labels_file, 'w', encoding='utf-8') as f:
        json.dump(labels, f, ensure_ascii=False, indent=2)
    
    print(f"\n[OK] Created labels.json:")
    print(f"  {labels}")
    
    # ساخت عکس‌های dummy (رنگی)
    print(f"\n[...] Creating sample images...")
    
    # Cat images (blue)
    for i in range(15):
        img = Image.new('RGB', (224, 224), color=(100, 150, 255))  # Blue
        img.save(data_dir / "cat" / f"cat_{i+1:02d}.jpg")
    
    # Dog images (orange)
    for i in range(15):
        img = Image.new('RGB', (224, 224), color=(255, 150, 100))  # Orange
        img.save(data_dir / "dog" / f"dog_{i+1:02d}.jpg")
    
    print(f"  [OK] Created 15 cat images (blue)")
    print(f"  [OK] Created 15 dog images (orange)")
    
    # بررسی نهایی
    print(f"\n[INFO] Final check:")
    cat_count = len(list((data_dir / "cat").glob("*.jpg")))
    dog_count = len(list((data_dir / "dog").glob("*.jpg")))
    
    print(f"  Cat images: {cat_count}")
    print(f"  Dog images: {dog_count}")
    print(f"  Total: {cat_count + dog_count}")
    
    print(f"\n" + "=" * 60)
    print(f"[OK] Test project ready!")
    print(f"=" * 60)
    print(f"\nProject ID: test-cat-dog")
    print(f"Location: {test_project.absolute()}")
    print(f"\n[NEXT] Now you can:")
    print(f"  1. Restart Backend")
    print(f"  2. In Frontend open project: test-cat-dog")
    print(f"  3. Start training!")
    
    return str(test_project)

if __name__ == "__main__":
    try:
        project_path = setup_test_project()
        
        print(f"\n\n[TEST] Quick Test:")
        print(f"Run this to verify:")
        print(f'  python -c "from engine import create_data_loaders; '
              f'train, val, test = create_data_loaders(r\'{project_path}\', {{\'batch_size\': 4}}); '
              f'print(f\'Train: {{len(train.dataset)}} samples\')"')
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

