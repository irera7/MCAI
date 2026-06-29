"""
Download and prepare CIFAR-10 dataset for ModelCreator
Creates a project structure with 60,000 images organized by class
"""

import torchvision
import torchvision.transforms as transforms
from pathlib import Path
import json
from tqdm import tqdm

def download_cifar10(output_dir='../projects/cifar10-project', max_images=None):
    """
    Download CIFAR-10 and organize into project structure
    
    Args:
        output_dir: Directory to create project
        max_images: Max images per class (None for all)
    """
    print("=" * 70)
    print("CIFAR-10 Dataset Download and Setup")
    print("=" * 70)
    
    output_dir = Path(output_dir)
    data_dir = output_dir / 'data'
    
    # Download CIFAR-10
    print("\n1. Downloading CIFAR-10 dataset...")
    train_dataset = torchvision.datasets.CIFAR10(
        root='./temp/cifar10_raw',
        train=True,
        download=True
    )
    
    test_dataset = torchvision.datasets.CIFAR10(
        root='./temp/cifar10_raw',
        train=False,
        download=True
    )
    
    # Class names
    classes = ['airplane', 'automobile', 'bird', 'cat', 'deer',
               'dog', 'frog', 'horse', 'ship', 'truck']
    
    print(f"\n2. Creating project structure at: {output_dir}")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create class folders
    for cls in classes:
        (data_dir / cls).mkdir(exist_ok=True)
    
    # Count images per class
    class_counts = {cls: 0 for cls in classes}
    
    # Save training images
    print("\n3. Saving training images...")
    for idx, (img, label) in enumerate(tqdm(train_dataset, desc="Train")):
        class_name = classes[label]
        
        # Skip if reached max
        if max_images and class_counts[class_name] >= max_images:
            continue
        
        # Save image
        filename = f'{class_name}_train_{class_counts[class_name]:05d}.png'
        img.save(data_dir / class_name / filename)
        class_counts[class_name] += 1
    
    # Save test images
    print("\n4. Saving test images...")
    test_counts = {cls: 0 for cls in classes}
    for idx, (img, label) in enumerate(tqdm(test_dataset, desc="Test")):
        class_name = classes[label]
        
        # Limit test images to 20% of train
        max_test = max_images // 5 if max_images else 1000
        if test_counts[class_name] >= max_test:
            continue
        
        # Save image
        filename = f'{class_name}_test_{test_counts[class_name]:05d}.png'
        img.save(data_dir / class_name / filename)
        test_counts[class_name] += 1
        class_counts[class_name] += 1
    
    # Create labels.json
    print("\n5. Creating labels.json...")
    labels = {name: idx for idx, name in enumerate(classes)}
    with open(output_dir / 'labels.json', 'w') as f:
        json.dump(labels, f, indent=2)
    
    # Create project.json
    print("\n6. Creating project.json...")
    project_info = {
        "id": "cifar10-project",
        "name": "CIFAR-10 Classification",
        "modality": "image",
        "description": "10-class image classification dataset",
        "created_at": "2025-11-30",
        "num_classes": 10,
        "total_images": sum(class_counts.values())
    }
    
    with open(output_dir / 'project.json', 'w') as f:
        json.dump(project_info, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 70)
    print("✅ CIFAR-10 Dataset Ready!")
    print("=" * 70)
    print(f"\nLocation: {output_dir.absolute()}")
    print(f"\nImages per class:")
    for cls in classes:
        print(f"  {cls:12s}: {class_counts[cls]:,} images")
    print(f"\nTotal:        {sum(class_counts.values()):,} images")
    
    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print("1. Open ModelCreator UI")
    print("2. Load this project")
    print("3. Select a model (ResNet-18 recommended)")
    print("4. Configure training:")
    print("   - Epochs: 50-100")
    print("   - Batch Size: 64-128")
    print("   - Learning Rate: 0.001")
    print("   - Optimizer: Adam")
    print("   - Early Stopping: Yes (patience=10)")
    print("5. Start Training!")
    print("\nExpected Results:")
    print("  - Training time: ~30-60 mins (GPU)")
    print("  - Final Accuracy: ~85-92%")
    print("  - TensorBoard: projects/cifar10-project/tensorboard")
    print("=" * 70)


def download_quick_test(max_per_class=100):
    """
    Download small subset for quick testing
    Args:
        max_per_class: Images per class
    """
    print("\n🚀 Quick Test Mode: Creating small dataset...")
    download_cifar10(
        output_dir='../projects/cifar10-quick-test',
        max_images=max_per_class
    )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        # Quick test with 100 images per class
        download_quick_test(100)
    elif len(sys.argv) > 1 and sys.argv[1] == 'tiny':
        # Tiny test with 20 images per class
        download_quick_test(20)
    else:
        # Full dataset
        print("\n⚠️  Full CIFAR-10 has 60,000 images!")
        print("   This will take several minutes and ~200MB disk space.")
        print("\nOptions:")
        print("  python download_cifar10.py        - Full dataset")
        print("  python download_cifar10.py quick  - 1,000 images (100/class)")
        print("  python download_cifar10.py tiny   - 200 images (20/class)")
        
        choice = input("\nContinue with full dataset? (y/n): ")
        if choice.lower() == 'y':
            download_cifar10()
        else:
            print("\n💡 Tip: Run 'python download_cifar10.py quick' for faster setup")

