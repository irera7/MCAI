"""
Data Loading Module
Handles loading and preprocessing of datasets for different modalities
"""

import os
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path


class ImageDataset(Dataset):
    """
    Dataset for image classification
    
    Expected structure:
    data_dir/
        class_1/
            img1.jpg
            img2.jpg
        class_2/
            img3.jpg
            img4.jpg
    """
    
    def __init__(self, data_dir: str, label_map: Dict[str, int], 
                 transform: Optional[transforms.Compose] = None,
                 split: str = 'train'):
        """
        Args:
            data_dir: Root directory containing images
            label_map: Mapping from class name to class ID
            transform: Image transformations
            split: 'train', 'val', or 'test'
        """
        self.data_dir = Path(data_dir)
        self.label_map = label_map
        self.split = split
        
        # Default transforms if none provided
        if transform is None:
            if split == 'train':
                self.transform = transforms.Compose([
                    transforms.Resize((256, 256)),
                    transforms.RandomCrop(224),
                    transforms.RandomHorizontalFlip(),
                    transforms.ColorJitter(brightness=0.2, contrast=0.2),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225]
                    )
                ])
            else:
                self.transform = transforms.Compose([
                    transforms.Resize((256, 256)),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225]
                    )
                ])
        else:
            self.transform = transform
        
        self.samples = self._load_samples()
        
    def _load_samples(self) -> List[Tuple[str, int]]:
        """Load all image paths and their labels"""
        samples = []
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
        
        print(f"Loading samples from: {self.data_dir}")
        print(f"Label map: {self.label_map}")
        
        # Check if data_dir exists
        if not self.data_dir.exists():
            print(f"WARNING: Data directory does not exist: {self.data_dir}")
            return samples
        
        # Try to load from subdirectories (one per class)
        found_subdirs = False
        for label_name, label_id in self.label_map.items():
            label_dir = self.data_dir / label_name
            
            if label_dir.exists() and label_dir.is_dir():
                found_subdirs = True
                count = 0
                for img_file in label_dir.iterdir():
                    if img_file.is_file() and img_file.suffix.lower() in valid_extensions:
                        samples.append((str(img_file), label_id))
                        count += 1
                print(f"  Found {count} images in {label_name}/")
        
        # If no subdirectories, try loading all images from data_dir directly
        if not found_subdirs:
            print(f"No subdirectories found, trying to load from {self.data_dir} directly...")
            for img_file in self.data_dir.iterdir():
                if img_file.is_file() and img_file.suffix.lower() in valid_extensions:
                    # Assign to first class by default
                    label_id = list(self.label_map.values())[0] if self.label_map else 0
                    samples.append((str(img_file), label_id))
            print(f"  Found {len(samples)} images in root directory")
        
        if len(samples) == 0:
            print(f"ERROR: No images found!")
            print(f"Expected structure:")
            print(f"  {self.data_dir}/")
            for label_name in self.label_map.keys():
                print(f"    {label_name}/")
                print(f"      image1.jpg")
                print(f"      image2.jpg")
        
        print(f"Loaded {len(samples)} samples for {self.split} split")
        return samples
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        """Get a sample"""
        img_path, label = self.samples[idx]
        
        try:
            # Load image
            image = Image.open(img_path).convert('RGB')
            
            # Apply transforms
            if self.transform:
                image = self.transform(image)
            
            return image, label
            
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            # Return a blank image if loading fails
            image = Image.new('RGB', (224, 224), color='black')
            if self.transform:
                image = self.transform(image)
            return image, label


class ImageDataLoader:
    """
    DataLoader factory for image datasets
    Handles train/val/test splitting
    """
    
    def __init__(self, project_dir: str, config: dict):
        """
        Args:
            project_dir: Project directory containing data/ subdirectory
            config: Training configuration containing splits, batch_size, etc.
        """
        self.project_dir = Path(project_dir)
        self.data_dir = self.project_dir / "data"
        self.config = config
        
        # Load label mapping
        self.label_map = self._load_label_map()
        self.num_classes = len(self.label_map)
        
    def _load_label_map(self) -> Dict[str, int]:
        """Load or create label mapping"""
        label_file = self.project_dir / "labels.json"
        
        if label_file.exists():
            with open(label_file, 'r', encoding='utf-8') as f:
                label_map = json.load(f)
            print(f"Loaded {len(label_map)} classes: {list(label_map.keys())}")
            return label_map
        
        # Auto-detect labels from directory structure
        label_map = {}
        if self.data_dir.exists():
            for idx, label_dir in enumerate(sorted(self.data_dir.iterdir())):
                if label_dir.is_dir():
                    label_map[label_dir.name] = idx
            
            # If no subdirectories found, check if there are images in root
            if not label_map:
                valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
                images = [f for f in self.data_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_extensions]
                if images:
                    # Create default class
                    label_map["class_0"] = 0
                    print(f"Found {len(images)} images in root directory. Creating default class 'class_0'")
            
            # Save label map
            if label_map:
                with open(label_file, 'w', encoding='utf-8') as f:
                    json.dump(label_map, f, ensure_ascii=False, indent=2)
                print(f"Created label map with {len(label_map)} classes")
        
        return label_map
    
    def create_loaders(self) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """
        Create train, validation, and test data loaders
        
        Returns:
            (train_loader, val_loader, test_loader)
        """
        batch_size = self.config.get('batch_size', 32)
        # Set num_workers=0 on Windows to avoid DataLoader worker crashes
        num_workers = self.config.get('num_workers', 0)
        
        # Create datasets
        train_dataset = ImageDataset(
            str(self.data_dir),
            self.label_map,
            split='train'
        )
        
        val_dataset = ImageDataset(
            str(self.data_dir),
            self.label_map,
            split='val'
        )
        
        test_dataset = ImageDataset(
            str(self.data_dir),
            self.label_map,
            split='test'
        )
        
        # Check if we have any samples
        total_samples = len(train_dataset.samples)
        
        if total_samples == 0:
            # Create a helpful error message
            error_msg = f"No images found in {self.data_dir}!\n\n"
            error_msg += "Please make sure your data is organized properly:\n\n"
            
            if self.label_map:
                error_msg += "Expected structure (with class folders):\n"
                error_msg += f"  {self.data_dir}/\n"
                for label in self.label_map.keys():
                    error_msg += f"    {label}/\n"
                    error_msg += f"      image1.jpg\n"
                    error_msg += f"      image2.jpg\n"
                    error_msg += f"      ...\n"
            else:
                error_msg += "Option 1: Create class folders:\n"
                error_msg += f"  {self.data_dir}/\n"
                error_msg += f"    class1/\n"
                error_msg += f"      image1.jpg\n"
                error_msg += f"      image2.jpg\n"
                error_msg += f"    class2/\n"
                error_msg += f"      image1.jpg\n"
                error_msg += f"      image2.jpg\n\n"
                error_msg += "Option 2: Put images directly in data folder:\n"
                error_msg += f"  {self.data_dir}/\n"
                error_msg += f"    image1.jpg\n"
                error_msg += f"    image2.jpg\n\n"
                error_msg += "Supported formats: .jpg, .jpeg, .png, .bmp, .gif, .webp"
            
            raise ValueError(error_msg)
        
        # Split datasets based on config
        train_split = self.config.get('train_split', 0.7)
        val_split = self.config.get('val_split', 0.15)
        # test_split = 1 - train_split - val_split
        
        # Use all data and split
        all_samples = train_dataset.samples
        
        train_size = int(total_samples * train_split)
        val_size = int(total_samples * val_split)
        test_size = total_samples - train_size - val_size
        
        # Ensure at least 1 sample in each split
        if train_size == 0:
            train_size = max(1, total_samples // 2)
        if val_size == 0:
            val_size = max(1, total_samples // 4)
        if test_size == 0:
            test_size = total_samples - train_size - val_size
        
        print(f"\nSplitting {total_samples} samples:")
        print(f"  Train: {train_size} ({train_split*100:.0f}%)")
        print(f"  Val:   {val_size} ({val_split*100:.0f}%)")
        print(f"  Test:  {test_size} ({(1-train_split-val_split)*100:.0f}%)")
        
        # Random split
        from torch.utils.data import random_split
        generator = torch.Generator().manual_seed(42)
        
        train_dataset, val_dataset, test_dataset = random_split(
            train_dataset,
            [train_size, val_size, test_size],
            generator=generator
        )
        
        # Create data loaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available()
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available()
        )
        
        test_loader = DataLoader(
            test_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available()
        )
        
        print(f"\nCreated data loaders:")
        print(f"  Train: {len(train_dataset)} samples, {len(train_loader)} batches")
        print(f"  Val:   {len(val_dataset)} samples, {len(val_loader)} batches")
        print(f"  Test:  {len(test_dataset)} samples, {len(test_loader)} batches")
        
        return train_loader, val_loader, test_loader


def create_data_loaders(project_dir: str, config: dict) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Convenience function to create data loaders
    
    Args:
        project_dir: Project directory
        config: Training configuration
        
    Returns:
        (train_loader, val_loader, test_loader)
    """
    loader = ImageDataLoader(project_dir, config)
    return loader.create_loaders()


# Test code
if __name__ == "__main__":
    # Test with a sample project
    test_config = {
        'batch_size': 4,
        'num_workers': 0,
        'train_split': 0.7,
        'val_split': 0.15,
    }
    
    # Replace with actual project directory
    project_dir = "../projects/test-project"
    
    if os.path.exists(project_dir):
        try:
            train_loader, val_loader, test_loader = create_data_loaders(
                project_dir,
                test_config
            )
            
            # Test loading a batch
            for images, labels in train_loader:
                print(f"Batch shape: {images.shape}")
                print(f"Labels: {labels}")
                break
                
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Project directory {project_dir} does not exist")
        print("Please create a test project with images first")

