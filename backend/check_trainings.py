#!/usr/bin/env python3
"""Check active_trainings dictionary"""
import sys
sys.path.insert(0, '.')

from api.routes.training import active_trainings

print("=" * 70)
print("🔍 ACTIVE TRAININGS STATUS")
print("=" * 70)

if not active_trainings:
    print("❌ No active trainings found!")
    print("   Training has either completed or not started.")
else:
    print(f"✅ Found {len(active_trainings)} active training(s):\n")
    for project_id, info in active_trainings.items():
        print(f"📦 Project: {project_id[:20]}...")
        print(f"   Status: {info.get('status', 'unknown')}")
        print(f"   Epoch: {info.get('current_epoch', 0)}/{info.get('total_epochs', 0)}")
        print(f"   Train Loss: {info.get('train_loss', 0):.4f}")
        print(f"   Train Acc: {info.get('train_acc', 0):.4f}")
        print(f"   Message: {info.get('message', 'N/A')}")
        print()

print("=" * 70)

