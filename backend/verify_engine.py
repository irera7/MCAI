"""
Simple verification script to check if training engine works
This can be run while backend is running to test the real training
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8181"

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/system/health", timeout=3)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        print("\n📝 Please start backend first:")
        print("   cd D:\\Project\\ModelCreator\\backend")
        print("   .\\venv\\Scripts\\activate")
        print("   python main.py")
        return False


def check_projects():
    """Check available projects"""
    try:
        response = requests.get(f"{BASE_URL}/api/project/list", timeout=3)
        if response.status_code == 200:
            projects = response.json()
            print(f"\n✅ Found {len(projects)} project(s):")
            for p in projects:
                print(f"   - {p.get('name', 'Unknown')} (ID: {p.get('id', 'Unknown')})")
            return True, projects
        else:
            print(f"❌ Failed to get projects: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"❌ Error getting projects: {e}")
        return False, []


def start_training_test():
    """Start a test training"""
    project_id = "test-cat-dog"
    
    config = {
        "epochs": 2,  # Very short test
        "batch_size": 4,
        "learning_rate": 0.001,
        "optimizer": "adam",
        "device": "cpu",  # Safe default
        "train_split": 0.7,
        "val_split": 0.15,
        "early_stopping": False,
        "mixed_precision": False
    }
    
    print(f"\n🚀 Starting training test on project: {project_id}")
    print(f"   Config: 2 epochs, batch_size=4, device=cpu")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/training/start/{project_id}",
            json=config,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Training started!")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"\n📊 Monitor training at:")
            print(f"   GET {BASE_URL}/api/training/status/{project_id}")
            return True
        else:
            print(f"❌ Failed to start: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting training: {e}")
        return False


def main():
    print("=" * 70)
    print("MODELCREATOR TRAINING ENGINE - QUICK VERIFICATION")
    print("=" * 70)
    
    # Step 1: Check backend
    if not check_backend():
        return
    
    # Step 2: Check projects
    success, projects = check_projects()
    if not success:
        return
    
    # Step 3: Optionally start test training
    print("\n" + "=" * 70)
    print("READY TO TEST TRAINING")
    print("=" * 70)
    
    user_input = input("\nDo you want to start a test training? (y/n): ")
    
    if user_input.lower() == 'y':
        start_training_test()
        print("\n✅ Test training initiated!")
        print("   Check the frontend UI or use:")
        print("   curl http://127.0.0.1:8181/api/training/status/test-cat-dog")
    else:
        print("\n✅ Verification complete!")
        print("   You can start training from the frontend UI")
    
    print("\n" + "=" * 70)
    print("📚 For full documentation, see: ENGINE_READY_FA.md")
    print("=" * 70)


if __name__ == "__main__":
    main()

