#!/usr/bin/env python3
"""Check what backend is returning for training status"""
import requests
import json
import time

project_id = "53569a3d-1248-4b5d-8e8b-be8b75556767"
url = f"http://127.0.0.1:8181/api/training/status/{project_id}"

print("=" * 70)
print("🔍 CHECKING BACKEND TRAINING STATUS")
print("=" * 70)

try:
    response = requests.get(url, timeout=5)
    print(f"\n✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📊 Backend Response:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        print(f"\n📈 Key Metrics:")
        print(f"   Status: {data.get('status', 'N/A')}")
        print(f"   Current Epoch: {data.get('current_epoch', 'N/A')}")
        print(f"   Total Epochs: {data.get('total_epochs', 'N/A')}")
        print(f"   Train Loss: {data.get('train_loss', 'N/A')}")
        print(f"   Train Acc: {data.get('train_acc', 'N/A')}")
        print(f"   Val Loss: {data.get('val_loss', 'N/A')}")
        print(f"   Val Acc: {data.get('val_acc', 'N/A')}")
        print(f"   Message: {data.get('message', 'N/A')}")
        
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
        print(response.text)
        
except requests.Timeout:
    print("\n❌ Request timed out - Backend may be blocked")
except requests.ConnectionError:
    print("\n❌ Could not connect to backend on port 8181")
    print("   Make sure backend is running: python main.py")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 70)

