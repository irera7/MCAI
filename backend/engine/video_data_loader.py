"""
Video Data Loader
بارگذاری و پیش‌پردازش داده‌های ویدئویی
"""

import torch
from torch.utils.data import Dataset, DataLoader
import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any
import os


class VideoDataset(Dataset):
    """
    Dataset برای ویدئوهای طبقه‌بندی شده
    
    ساختار پوشه:
    data/
      class1/
        video1.mp4
        video2.avi
      class2/
        video1.mp4
    """
    
    def __init__(
        self,
        data_dir: str,
        label_map: Dict[str, int],
        num_frames: int = 16,
        frame_size: Tuple[int, int] = (112, 112),
        temporal_stride: int = 1,
        transform=None
    ):
        """
        Args:
            data_dir: مسیر پوشه داده
            label_map: dict از label name به label id
            num_frames: تعداد frame برای استخراج از هر ویدئو
            frame_size: اندازه هر frame (H, W)
            temporal_stride: فاصله بین frame‌ها
            transform: تبدیلات اضافی
        """
        self.data_dir = Path(data_dir)
        self.label_map = label_map
        self.num_frames = num_frames
        self.frame_size = frame_size
        self.temporal_stride = temporal_stride
        self.transform = transform
        
        # بارگذاری لیست ویدئوها
        self.samples = self._load_samples()
        
        print(f"✅ VideoDataset loaded: {len(self.samples)} videos")
        print(f"   Classes: {len(self.label_map)}")
        print(f"   Frames per video: {self.num_frames}")
    
    def _load_samples(self) -> List[Tuple[Path, int]]:
        """بارگذاری لیست ویدئوها"""
        samples = []
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv']
        
        for label_name, label_id in self.label_map.items():
            label_dir = self.data_dir / label_name
            if not label_dir.exists():
                continue
            
            for video_file in label_dir.iterdir():
                if video_file.suffix.lower() in video_extensions:
                    samples.append((video_file, label_id))
        
        return samples
    
    def _extract_frames(self, video_path: Path) -> Optional[np.ndarray]:
        """
        استخراج frame‌ها از ویدئو
        
        Returns:
            frames: (num_frames, H, W, C) یا None در صورت خطا
        """
        try:
            cap = cv2.VideoCapture(str(video_path))
            
            # دریافت تعداد کل frame‌ها
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames < self.num_frames:
                # اگر ویدئو کوتاه است، frame‌ها را تکرار می‌کنیم
                frame_indices = np.linspace(0, total_frames - 1, self.num_frames, dtype=int)
            else:
                # انتخاب frame‌های یکنواخت
                frame_indices = np.linspace(
                    0, 
                    total_frames - 1, 
                    self.num_frames * self.temporal_stride,
                    dtype=int
                )[::self.temporal_stride][:self.num_frames]
            
            frames = []
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                
                if ret:
                    # تبدیل BGR به RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # تغییر اندازه
                    frame = cv2.resize(frame, self.frame_size)
                    frames.append(frame)
            
            cap.release()
            
            if len(frames) == self.num_frames:
                return np.array(frames)
            
            return None
            
        except Exception as e:
            print(f"Error loading video {video_path}: {e}")
            return None
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        video_path, label = self.samples[idx]
        
        # استخراج frame‌ها
        frames = self._extract_frames(video_path)
        
        if frames is None:
            # در صورت خطا، یک ویدئوی خالی برمی‌گردانیم
            frames = np.zeros((self.num_frames, *self.frame_size, 3), dtype=np.uint8)
        
        # نرمال‌سازی به [0, 1]
        frames = frames.astype(np.float32) / 255.0
        
        # تبدیل به tensor: (T, H, W, C) -> (C, T, H, W)
        frames = torch.from_numpy(frames).permute(3, 0, 1, 2)
        
        # Normalize با ImageNet stats
        mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1, 1)
        frames = (frames - mean) / std
        
        if self.transform:
            frames = self.transform(frames)
        
        return frames, label


def create_video_loaders(
    project_dir: str,
    config: Dict[str, Any]
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    ایجاد DataLoader برای train, validation, test
    
    Args:
        project_dir: مسیر پروژه
        config: تنظیمات
        
    Returns:
        train_loader, val_loader, test_loader
    """
    import json
    
    # خواندن اطلاعات پروژه
    project_file = Path(project_dir) / "project.json"
    with open(project_file, 'r') as f:
        project_info = json.load(f)
    
    data_dir = Path(project_dir) / "data"
    label_map = project_info.get('label_map', {})
    
    # پارامترهای video
    num_frames = config.get('num_frames', 16)
    frame_size = config.get('frame_size', (112, 112))
    temporal_stride = config.get('temporal_stride', 1)
    
    # ایجاد dataset کامل
    full_dataset = VideoDataset(
        data_dir=str(data_dir),
        label_map=label_map,
        num_frames=num_frames,
        frame_size=frame_size,
        temporal_stride=temporal_stride
    )
    
    # تقسیم به train/val/test
    total_size = len(full_dataset)
    train_size = int(config.get('train_split', 0.7) * total_size)
    val_size = int(config.get('val_split', 0.15) * total_size)
    test_size = total_size - train_size - val_size
    
    train_dataset, val_dataset, test_dataset = torch.utils.data.random_split(
        full_dataset,
        [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(42)
    )
    
    # ایجاد DataLoader
    batch_size = config.get('batch_size', 4)  # batch size کمتر برای video
    num_workers = config.get('num_workers', 2)
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    print(f"✅ Video DataLoaders created:")
    print(f"   Train: {len(train_dataset)} videos")
    print(f"   Val: {len(val_dataset)} videos")
    print(f"   Test: {len(test_dataset)} videos")
    
    return train_loader, val_loader, test_loader


# Helper function برای preview
def preview_video(video_path: str, num_frames: int = 16):
    """نمایش چند frame از یک ویدئو"""
    import matplotlib.pyplot as plt
    
    dataset = VideoDataset(
        data_dir=str(Path(video_path).parent.parent),
        label_map={"class": 0},
        num_frames=num_frames
    )
    
    frames, _ = dataset[0]
    frames = frames.permute(1, 2, 3, 0)  # (C, T, H, W) -> (T, H, W, C)
    
    # نمایش 8 frame اول
    fig, axes = plt.subplots(2, 4, figsize=(12, 6))
    for i, ax in enumerate(axes.flat):
        if i < num_frames:
            # Denormalize
            frame = frames[i].numpy()
            frame = frame * np.array([0.229, 0.224, 0.225]) + np.array([0.485, 0.456, 0.406])
            frame = np.clip(frame, 0, 1)
            ax.imshow(frame)
            ax.set_title(f"Frame {i+1}")
            ax.axis('off')
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # تست
    print("Testing VideoDataset...")
    
    # فرض: پوشه test با ویدئوهای نمونه
    test_dir = Path("../projects/test-video/data")
    if test_dir.exists():
        label_map = {d.name: i for i, d in enumerate(test_dir.iterdir()) if d.is_dir()}
        
        dataset = VideoDataset(
            data_dir=str(test_dir),
            label_map=label_map,
            num_frames=16
        )
        
        print(f"Dataset size: {len(dataset)}")
        
        if len(dataset) > 0:
            video, label = dataset[0]
            print(f"Video shape: {video.shape}")  # Should be (3, 16, 112, 112)
            print(f"Label: {label}")

