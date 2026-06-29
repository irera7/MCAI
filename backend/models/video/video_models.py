"""
Video Classification Models
مدل‌های طبقه‌بندی ویدئو

این ماژول مدل‌های deep learning برای طبقه‌بندی ویدئو را فراهم می‌کند
"""

import torch
import torch.nn as nn
from typing import Tuple, Optional


class CNN3D(nn.Module):
    """
    3D CNN برای طبقه‌بندی ویدئو
    
    این مدل از convolution های 3D برای extract کردن feature از ویدئو استفاده می‌کند
    
    ورودی: (batch, channels, frames, height, width)
    مثلاً: (32, 3, 16, 112, 112) = 32 video با 16 frame
    
    Example:
        model = CNN3D(num_classes=10, num_frames=16)
        video = torch.randn(4, 3, 16, 112, 112)  # 4 videos
        output = model(video)  # (4, 10)
    """
    
    def __init__(
        self,
        num_classes: int = 10,
        num_frames: int = 16,
        dropout: float = 0.5
    ):
        """
        مقداردهی اولیه
        
        Args:
            num_classes: تعداد کلاس‌ها
            num_frames: تعداد frame در هر video
            dropout: نرخ dropout
        """
        super(CNN3D, self).__init__()
        
        # Conv3D layers
        self.features = nn.Sequential(
            # Conv block 1
            nn.Conv3d(3, 64, kernel_size=(3, 3, 3), padding=(1, 1, 1)),
            nn.BatchNorm3d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(1, 2, 2), stride=(1, 2, 2)),
            
            # Conv block 2
            nn.Conv3d(64, 128, kernel_size=(3, 3, 3), padding=(1, 1, 1)),
            nn.BatchNorm3d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(2, 2, 2), stride=(2, 2, 2)),
            
            # Conv block 3
            nn.Conv3d(128, 256, kernel_size=(3, 3, 3), padding=(1, 1, 1)),
            nn.BatchNorm3d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(2, 2, 2), stride=(2, 2, 2)),
            
            # Conv block 4
            nn.Conv3d(256, 512, kernel_size=(3, 3, 3), padding=(1, 1, 1)),
            nn.BatchNorm3d(512),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(2, 2, 2), stride=(2, 2, 2))
        )
        
        # Classifier
        self.avgpool = nn.AdaptiveAvgPool3d((1, 1, 1))
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(256, num_classes)
        )
        
        print(f"✅ CNN3D created (num_classes={num_classes}, frames={num_frames})")
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            x: (batch, 3, frames, H, W)
            
        Returns:
            (batch, num_classes)
        """
        x = self.features(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x


class R2Plus1D(nn.Module):
    """
    R(2+1)D: مدل video classification از Facebook
    
    این مدل 3D convolution را به (2D spatial + 1D temporal) تجزیه می‌کند
    که باعث کاهش پارامترها و بهبود performance می‌شود
    
    Example:
        model = R2Plus1D(num_classes=10)
        video = torch.randn(4, 3, 16, 112, 112)
        output = model(video)
    """
    
    def __init__(
        self,
        num_classes: int = 10,
        dropout: float = 0.5
    ):
        """
        مقداردهی اولیه
        
        Args:
            num_classes: تعداد کلاس‌ها
            dropout: نرخ dropout
        """
        super(R2Plus1D, self).__init__()
        
        # استفاده از pre-trained R2Plus1D از torchvision
        try:
            import torchvision.models.video as video_models
            
            # بارگذاری مدل pre-trained
            self.base_model = video_models.r2plus1d_18(pretrained=True)
            
            # تغییر classifier برای num_classes ما
            in_features = self.base_model.fc.in_features
            self.base_model.fc = nn.Sequential(
                nn.Dropout(dropout),
                nn.Linear(in_features, num_classes)
            )
            
            print(f"✅ R2Plus1D created (pretrained, num_classes={num_classes})")
            
        except Exception as e:
            print(f"⚠️ Could not load pretrained R2Plus1D: {e}")
            print("Using custom implementation...")
            
            # پیاده‌سازی ساده R2Plus1D
            self.base_model = self._build_custom_r2plus1d(num_classes, dropout)
    
    def _build_custom_r2plus1d(self, num_classes: int, dropout: float):
        """پیاده‌سازی ساده R2Plus1D"""
        class R2Plus1DBlock(nn.Module):
            def __init__(self, in_channels, out_channels):
                super().__init__()
                # Spatial convolution (2D)
                self.spatial = nn.Conv3d(
                    in_channels, out_channels,
                    kernel_size=(1, 3, 3),
                    padding=(0, 1, 1)
                )
                # Temporal convolution (1D)
                self.temporal = nn.Conv3d(
                    out_channels, out_channels,
                    kernel_size=(3, 1, 1),
                    padding=(1, 0, 0)
                )
                self.bn = nn.BatchNorm3d(out_channels)
                self.relu = nn.ReLU(inplace=True)
            
            def forward(self, x):
                x = self.spatial(x)
                x = self.temporal(x)
                x = self.bn(x)
                x = self.relu(x)
                return x
        
        return nn.Sequential(
            R2Plus1DBlock(3, 64),
            nn.MaxPool3d((1, 2, 2)),
            R2Plus1DBlock(64, 128),
            nn.MaxPool3d((2, 2, 2)),
            R2Plus1DBlock(128, 256),
            nn.MaxPool3d((2, 2, 2)),
            nn.AdaptiveAvgPool3d((1, 1, 1)),
            nn.Flatten(),
            nn.Dropout(dropout),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        return self.base_model(x)


class SlowFast(nn.Module):
    """
    SlowFast Networks: مدل دو مسیره برای video
    
    این مدل از دو pathway استفاده می‌کند:
    - Slow pathway: frame rate پایین، spatial detail بالا
    - Fast pathway: frame rate بالا، spatial detail پایین
    
    Example:
        model = SlowFast(num_classes=10)
        # Slow: 4 frames, Fast: 32 frames
        slow = torch.randn(2, 3, 4, 224, 224)
        fast = torch.randn(2, 3, 32, 56, 56)
        output = model(slow, fast)
    """
    
    def __init__(
        self,
        num_classes: int = 10,
        dropout: float = 0.5
    ):
        """
        مقداردهی اولیه
        
        Args:
            num_classes: تعداد کلاس‌ها
            dropout: نرخ dropout
        """
        super(SlowFast, self).__init__()
        
        # Slow pathway (high spatial resolution, low temporal resolution)
        self.slow_pathway = nn.Sequential(
            nn.Conv3d(3, 64, kernel_size=(1, 7, 7), stride=(1, 2, 2), padding=(0, 3, 3)),
            nn.BatchNorm3d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(1, 3, 3), stride=(1, 2, 2), padding=(0, 1, 1)),
            
            nn.Conv3d(64, 128, kernel_size=(3, 3, 3), padding=(1, 1, 1)),
            nn.BatchNorm3d(128),
            nn.ReLU(inplace=True)
        )
        
        # Fast pathway (low spatial resolution, high temporal resolution)
        self.fast_pathway = nn.Sequential(
            nn.Conv3d(3, 16, kernel_size=(5, 7, 7), stride=(1, 2, 2), padding=(2, 3, 3)),
            nn.BatchNorm3d(16),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(1, 3, 3), stride=(1, 2, 2), padding=(0, 1, 1)),
            
            nn.Conv3d(16, 32, kernel_size=(3, 3, 3), padding=(1, 1, 1)),
            nn.BatchNorm3d(32),
            nn.ReLU(inplace=True)
        )
        
        # Fusion and classification
        self.fusion = nn.Conv3d(128 + 32, 256, kernel_size=1)
        self.avgpool = nn.AdaptiveAvgPool3d((1, 1, 1))
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(256, num_classes)
        )
        
        print(f"✅ SlowFast created (num_classes={num_classes})")
    
    def forward(self, slow_input: torch.Tensor, fast_input: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            slow_input: (batch, 3, T_slow, H, W)
            fast_input: (batch, 3, T_fast, H_fast, W_fast)
            
        Returns:
            (batch, num_classes)
        """
        slow = self.slow_pathway(slow_input)
        fast = self.fast_pathway(fast_input)
        
        # Resize fast to match slow
        if fast.shape[2:] != slow.shape[2:]:
            import torch.nn.functional as F
            fast = F.interpolate(
                fast,
                size=slow.shape[2:],
                mode='trilinear',
                align_corners=False
            )
        
        # Concatenate pathways
        x = torch.cat([slow, fast], dim=1)
        
        # Fusion
        x = self.fusion(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        
        return x


def create_video_model(
    model_name: str,
    num_classes: int,
    **kwargs
) -> nn.Module:
    """
    Factory function برای ساخت video models
    
    Args:
        model_name: 'cnn3d', 'r2plus1d', یا 'slowfast'
        num_classes: تعداد کلاس‌ها
        **kwargs: پارامترهای اضافی
        
    Returns:
        Video classification model
        
    Example:
        model = create_video_model('cnn3d', num_classes=10, num_frames=16)
        model = create_video_model('r2plus1d', num_classes=101)  # UCF-101
    """
    models = {
        'cnn3d': CNN3D,
        'r2plus1d': R2Plus1D,
        'slowfast': SlowFast
    }
    
    if model_name.lower() not in models:
        raise ValueError(f"Unsupported video model: {model_name}. Choose from: {list(models.keys())}")
    
    return models[model_name.lower()](num_classes=num_classes, **kwargs)
