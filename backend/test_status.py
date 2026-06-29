#!/usr/bin/env python3
"""Test script to check training status"""
import requests
import json

project_id = "53569a3d-1248-4b5d-8e8b-be8b75556767"
url = f"http://127.0.0.1:8181/api/training/status/{project_id}"

try:
    response = requests.get(url, timeout=5)
    print(f"✅ Status Code: {response.status_code}")
    print(f"📊 Response:")
    print(json.dumps(response.json(), indent=2))
except requests.Timeout:
    print("❌ Request timed out after 5 seconds")
except requests.ConnectionError:
    print("❌ Could not connect to backend")
except Exception as e:
    print(f"❌ Error: {e}")

