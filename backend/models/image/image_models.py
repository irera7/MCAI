"""
Image classification models
Includes CNN, MobileNetV3, and Vision Transformer architectures
"""
import torch
import torch.nn as nn
import torchvision.models as models
from typing import Optional

class SimpleCNN(nn.Module):
    """
    Simple Convolutional Neural Network for image classification
    Suitable for simple image classification tasks
    """
    def __init__(self, num_classes: int = 10, input_channels: int = 3):
        super(SimpleCNN, self).__init__()
        
        # Convolutional layers
        self.conv_layers = nn.Sequential(
            # First conv block
            nn.Conv2d(input_channels, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # Second conv block
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # Third conv block
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # Fourth conv block
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        
        # Fully connected layers
        self.fc_layers = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(256, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        """Forward pass"""
        x = self.conv_layers(x)
        x = torch.flatten(x, 1)
        x = self.fc_layers(x)
        return x


class MobileNetV3Classifier(nn.Module):
    """
    MobileNetV3 based classifier using transfer learning
    Efficient for deployment on resource-constrained devices
    """
    def __init__(self, num_classes: int = 10, pretrained: bool = True, variant: str = 'small'):
        super(MobileNetV3Classifier, self).__init__()
        
        # Load pretrained MobileNetV3
        if variant == 'small':
            self.backbone = models.mobilenet_v3_small(pretrained=pretrained)
            in_features = self.backbone.classifier[0].in_features
        else:
            self.backbone = models.mobilenet_v3_large(pretrained=pretrained)
            in_features = self.backbone.classifier[0].in_features
        
        # Replace classifier head
        self.backbone.classifier = nn.Sequential(
            nn.Linear(in_features, 1024),
            nn.Hardswish(inplace=True),
            nn.Dropout(p=0.2, inplace=True),
            nn.Linear(1024, num_classes)
        )
    
    def forward(self, x):
        """Forward pass"""
        return self.backbone(x)


class VisionTransformerClassifier(nn.Module):
    """
    Vision Transformer (ViT) for image classification
    Uses attention mechanism instead of convolutions
    """
    def __init__(self, num_classes: int = 10, pretrained: bool = True, variant: str = 'b_16'):
        super(VisionTransformerClassifier, self).__init__()
        
        # Load pretrained ViT
        if variant == 'b_16':
            self.backbone = models.vit_b_16(pretrained=pretrained)
        elif variant == 'b_32':
            self.backbone = models.vit_b_32(pretrained=pretrained)
        else:
            self.backbone = models.vit_l_16(pretrained=pretrained)
        
        # Replace classification head
        in_features = self.backbone.heads.head.in_features
        self.backbone.heads.head = nn.Linear(in_features, num_classes)
    
    def forward(self, x):
        """Forward pass"""
        return self.backbone(x)


def create_image_model(
    model_type: str,
    num_classes: int,
    pretrained: bool = True,
    input_channels: int = 3
) -> nn.Module:
    """
    Factory function to create image classification models
    
    Args:
        model_type: Type of model ('cnn', 'mobilenetv3', 'vit')
        num_classes: Number of output classes
        pretrained: Whether to use pretrained weights
        input_channels: Number of input channels (3 for RGB)
        
    Returns:
        PyTorch model instance
    """
    if model_type.lower() == 'cnn':
        return SimpleCNN(num_classes=num_classes, input_channels=input_channels)
    
    elif model_type.lower() == 'mobilenetv3':
        return MobileNetV3Classifier(num_classes=num_classes, pretrained=pretrained)
    
    elif model_type.lower() == 'vit':
        return VisionTransformerClassifier(num_classes=num_classes, pretrained=pretrained)
    
    else:
        raise ValueError(f"Unknown model type: {model_type}")


# Model configurations for easy reference
MODEL_CONFIGS = {
    'cnn': {
        'name': 'Simple CNN',
        'description': 'Lightweight convolutional network',
        'params': '~1M',
        'speed': 'Fast',
        'accuracy': 'Medium'
    },
    'mobilenetv3': {
        'name': 'MobileNetV3',
        'description': 'Efficient mobile architecture',
        'params': '~5M',
        'speed': 'Fast',
        'accuracy': 'High'
    },
    'vit': {
        'name': 'Vision Transformer',
        'description': 'Transformer-based vision model',
        'params': '~86M',
        'speed': 'Medium',
        'accuracy': 'Very High'
    }
}

