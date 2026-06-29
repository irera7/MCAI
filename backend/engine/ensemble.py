"""
Ensemble Methods Module
ترکیب چند مدل برای accuracy بهتر

این ماژول روش‌های مختلف ensemble را پیاده‌سازی می‌کند
"""

import torch
import torch.nn as nn
from typing import List, Dict, Optional, Tuple
import numpy as np
from pathlib import Path


class VotingEnsemble(nn.Module):
    """
    Voting Ensemble - رأی‌گیری بین مدل‌ها
    
    هر مدل یک پیش‌بینی می‌دهد و با رأی‌گیری نتیجه نهایی مشخص می‌شود
    
    دو نوع voting:
    - Hard Voting: اکثریت آرا
    - Soft Voting: میانگین احتمالات
    
    Example:
        models = [model1, model2, model3]
        ensemble = VotingEnsemble(models, voting='soft')
        output = ensemble(input_data)
    """
    
    def __init__(
        self,
        models: List[nn.Module],
        voting: str = 'soft',  # 'hard' or 'soft'
        weights: Optional[List[float]] = None
    ):
        """
        مقداردهی اولیه
        
        Args:
            models: لیست مدل‌های PyTorch
            voting: نوع رأی‌گیری ('hard' یا 'soft')
            weights: وزن هر مدل (None = وزن یکسان)
        """
        super(VotingEnsemble, self).__init__()
        
        self.models = nn.ModuleList(models)
        self.voting = voting
        self.num_models = len(models)
        
        # تنظیم وزن‌ها
        if weights is None:
            self.weights = [1.0 / self.num_models] * self.num_models
        else:
            assert len(weights) == self.num_models, "تعداد وزن‌ها باید برابر تعداد مدل‌ها باشد"
            # نرمال‌سازی وزن‌ها
            total = sum(weights)
            self.weights = [w / total for w in weights]
        
        print(f"✅ VotingEnsemble با {self.num_models} مدل ({voting} voting)")
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass - ترکیب خروجی مدل‌ها
        
        Args:
            x: ورودی
            
        Returns:
            خروجی ensemble
        """
        # دریافت خروجی تمام مدل‌ها
        outputs = []
        for model in self.models:
            model.eval()  # حالت eval
            with torch.no_grad():
                out = model(x)
            outputs.append(out)
        
        # Stack outputs: (num_models, batch_size, num_classes)
        outputs = torch.stack(outputs)
        
        if self.voting == 'soft':
            # Soft Voting: میانگین وزن‌دار احتمالات
            # اعمال softmax به هر خروجی
            probs = torch.softmax(outputs, dim=2)
            
            # ضرب در وزن‌ها
            weighted_probs = torch.zeros_like(probs[0])
            for i, weight in enumerate(self.weights):
                weighted_probs += weight * probs[i]
            
            return weighted_probs
        
        else:  # hard voting
            # Hard Voting: رأی اکثریت
            # پیدا کردن کلاس با بیشترین امتیاز برای هر مدل
            predictions = torch.argmax(outputs, dim=2)  # (num_models, batch_size)
            
            # رأی‌گیری
            batch_size = predictions.shape[1]
            num_classes = outputs.shape[2]
            final_predictions = torch.zeros(batch_size, num_classes, device=x.device)
            
            for i in range(batch_size):
                votes = predictions[:, i]  # رأی همه مدل‌ها برای sample i
                # شمارش رأی‌ها
                for j, vote in enumerate(votes):
                    final_predictions[i, vote] += self.weights[j]
            
            return final_predictions


class StackingEnsemble(nn.Module):
    """
    Stacking Ensemble - یادگیری ترکیب مدل‌ها
    
    یک مدل meta learner روی خروجی‌های مدل‌های base آموزش می‌بیند
    
    Example:
        base_models = [model1, model2, model3]
        meta_model = SimpleNN(input_dim=3*num_classes, output_dim=num_classes)
        ensemble = StackingEnsemble(base_models, meta_model)
        ensemble.train_meta(train_loader, epochs=10)
    """
    
    def __init__(
        self,
        base_models: List[nn.Module],
        meta_model: nn.Module
    ):
        """
        مقداردهی اولیه
        
        Args:
            base_models: مدل‌های پایه
            meta_model: مدل meta learner
        """
        super(StackingEnsemble, self).__init__()
        
        self.base_models = nn.ModuleList(base_models)
        self.meta_model = meta_model
        self.num_base = len(base_models)
        
        # Freeze کردن base models (فقط meta آموزش می‌بیند)
        for model in self.base_models:
            for param in model.parameters():
                param.requires_grad = False
        
        print(f"✅ StackingEnsemble با {self.num_base} base models")
    
    def get_base_predictions(self, x: torch.Tensor) -> torch.Tensor:
        """
        دریافت پیش‌بینی‌های base models
        
        Args:
            x: ورودی
            
        Returns:
            پیش‌بینی‌های base models
        """
        predictions = []
        for model in self.base_models:
            model.eval()
            with torch.no_grad():
                pred = model(x)
            predictions.append(pred)
        
        # Concatenate: (batch_size, num_base * num_classes)
        return torch.cat(predictions, dim=1)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            x: ورودی
            
        Returns:
            پیش‌بینی نهایی
        """
        # دریافت پیش‌بینی‌های base
        base_preds = self.get_base_predictions(x)
        
        # اعمال meta model
        final_pred = self.meta_model(base_preds)
        
        return final_pred
    
    def train_meta(
        self,
        train_loader: torch.utils.data.DataLoader,
        criterion: nn.Module,
        optimizer: torch.optim.Optimizer,
        epochs: int = 10,
        device: str = 'cpu'
    ):
        """
        آموزش meta model
        
        Args:
            train_loader: DataLoader
            criterion: Loss function
            optimizer: Optimizer
            epochs: تعداد epoch
            device: دستگاه
        """
        device = torch.device(device)
        self.to(device)
        self.meta_model.train()
        
        print(f"\n🎓 آموزش Meta Model ({epochs} epochs)...")
        
        for epoch in range(epochs):
            total_loss = 0.0
            for batch_idx, (data, target) in enumerate(train_loader):
                data, target = data.to(device), target.to(device)
                
                # Forward
                output = self.forward(data)
                loss = criterion(output, target)
                
                # Backward
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / len(train_loader)
            print(f"  Epoch {epoch+1}/{epochs}: Loss = {avg_loss:.4f}")
        
        print("✅ Meta Model آموزش دیده شد")


class BaggingEnsemble(nn.Module):
    """
    Bagging Ensemble - Bootstrap Aggregating
    
    چند مدل مشابه روی subset‌های مختلف data آموزش می‌بینند
    
    نکته: این کلاس فقط inference می‌کند
    مدل‌ها باید قبلاً روی subset‌های مختلف آموزش دیده باشند
    
    Example:
        # آموزش چند مدل روی bootstrap samples
        models = train_multiple_models_with_bootstrap(base_model, data, n=5)
        ensemble = BaggingEnsemble(models)
        output = ensemble(input_data)
    """
    
    def __init__(self, models: List[nn.Module]):
        """
        مقداردهی اولیه
        
        Args:
            models: لیست مدل‌های آموزش دیده
        """
        super(BaggingEnsemble, self).__init__()
        
        self.models = nn.ModuleList(models)
        self.num_models = len(models)
        
        print(f"✅ BaggingEnsemble با {self.num_models} مدل")
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass - میانگین خروجی‌ها
        
        Args:
            x: ورودی
            
        Returns:
            خروجی ensemble
        """
        outputs = []
        for model in self.models:
            model.eval()
            with torch.no_grad():
                out = model(x)
            outputs.append(out)
        
        # Stack و میانگین
        outputs = torch.stack(outputs)
        
        # میانگین
        avg_output = torch.mean(outputs, dim=0)
        
        return avg_output


def create_voting_ensemble(
    model_paths: List[str],
    model_builder_func,
    num_classes: int,
    voting: str = 'soft',
    device: str = 'cpu'
) -> VotingEnsemble:
    """
    ایجاد Voting Ensemble از مدل‌های ذخیره شده
    
    Args:
        model_paths: مسیرهای فایل‌های مدل
        model_builder_func: تابع برای ساخت مدل
        num_classes: تعداد کلاس‌ها
        voting: نوع رأی‌گیری
        device: دستگاه
        
    Returns:
        VotingEnsemble
        
    Example:
        def build_model():
            return ModelBuilder.build_image_model('resnet18', 10)
        
        ensemble = create_voting_ensemble(
            ['model1.pt', 'model2.pt', 'model3.pt'],
            build_model,
            num_classes=10
        )
    """
    models = []
    device = torch.device(device)
    
    for path in model_paths:
        # ساخت مدل
        model = model_builder_func(num_classes)
        
        # لود کردن weights
        checkpoint = torch.load(path, map_location=device)
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint)
        
        model.to(device)
        model.eval()
        models.append(model)
    
    ensemble = VotingEnsemble(models, voting=voting)
    return ensemble


def evaluate_ensemble(
    ensemble: nn.Module,
    test_loader: torch.utils.data.DataLoader,
    device: str = 'cpu'
) -> Dict[str, float]:
    """
    ارزیابی ensemble
    
    Args:
        ensemble: مدل ensemble
        test_loader: DataLoader تست
        device: دستگاه
        
    Returns:
        دیکشنری metrics
    """
    device = torch.device(device)
    ensemble.to(device)
    ensemble.eval()
    
    correct = 0
    total = 0
    
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            
            output = ensemble(data)
            pred = torch.argmax(output, dim=1)
            
            correct += (pred == target).sum().item()
            total += target.size(0)
    
    accuracy = 100.0 * correct / total
    
    return {
        'accuracy': accuracy,
        'correct': correct,
        'total': total
    }


# تابع کمکی برای ساخت سریع ensemble
def quick_ensemble(
    models: List[nn.Module],
    ensemble_type: str = 'voting',
    **kwargs
) -> nn.Module:
    """
    ساخت سریع ensemble
    
    Args:
        models: لیست مدل‌ها
        ensemble_type: 'voting', 'stacking', یا 'bagging'
        **kwargs: پارامترهای اضافی
        
    Returns:
        مدل ensemble
    """
    if ensemble_type == 'voting':
        return VotingEnsemble(models, **kwargs)
    elif ensemble_type == 'bagging':
        return BaggingEnsemble(models)
    elif ensemble_type == 'stacking':
        meta_model = kwargs.get('meta_model')
        if meta_model is None:
            raise ValueError("meta_model باید برای stacking داده شود")
        return StackingEnsemble(models, meta_model)
    else:
        raise ValueError(f"نوع ensemble نامعتبر: {ensemble_type}")

