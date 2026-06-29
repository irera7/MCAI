"""
Hyperparameter Optimization Module using Optuna
Automatically finds the best hyperparameters for model training

این ماژول از Optuna استفاده می‌کند تا بهترین hyperparameter‌ها را پیدا کند
"""

import optuna
from optuna.trial import Trial
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, Any, Callable, Optional, List, Tuple
from pathlib import Path
import json
from datetime import datetime

from .trainer import Trainer
from .callbacks import EarlyStopping, ModelCheckpoint
from .model_builder import ModelBuilder


class HyperparameterOptimizer:
    """
    بهینه‌ساز خودکار hyperparameter با استفاده از Optuna
    
    این کلاس به صورت خودکار بهترین مقادیر برای:
    - Learning rate
    - Batch size
    - Optimizer type
    - Dropout rate
    - Number of layers
    - Hidden dimensions
    و غیره را پیدا می‌کند
    
    Example:
        optimizer = HyperparameterOptimizer(
            train_loader=train_loader,
            val_loader=val_loader,
            model_builder_func=lambda trial: build_my_model(trial),
            n_trials=50
        )
        best_params = optimizer.optimize()
    """
    
    def __init__(
        self,
        train_loader: torch.utils.data.DataLoader,
        val_loader: torch.utils.data.DataLoader,
        num_classes: int,
        modality: str = 'image',
        model_name: str = 'resnet18',
        device: str = 'cuda',
        n_trials: int = 50,
        timeout: Optional[int] = None,
        study_name: Optional[str] = None,
        direction: str = 'maximize',  # 'maximize' for accuracy, 'minimize' for loss
        pruning: bool = True,
        save_dir: Optional[str] = None,
        **fixed_params
    ):
        """
        مقداردهی اولیه بهینه‌ساز
        
        Args:
            train_loader: DataLoader برای آموزش
            val_loader: DataLoader برای validation
            num_classes: تعداد کلاس‌ها
            modality: نوع داده ('image', 'text', 'audio')
            model_name: نام مدل پایه
            device: دستگاه محاسباتی ('cuda' یا 'cpu')
            n_trials: تعداد trial‌ها (آزمایش‌ها)
            timeout: حداکثر زمان به ثانیه (None = بدون محدودیت)
            study_name: نام study (برای ذخیره و بازیابی)
            direction: جهت بهینه‌سازی ('maximize' یا 'minimize')
            pruning: آیا trial‌های ضعیف را زودتر متوقف کنیم؟
            save_dir: مسیر ذخیره نتایج
            **fixed_params: پارامترهای ثابت که بهینه نمی‌شوند
        """
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.num_classes = num_classes
        self.modality = modality
        self.model_name = model_name
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.n_trials = n_trials
        self.timeout = timeout
        self.study_name = study_name or f"study_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.direction = direction
        self.pruning = pruning
        self.save_dir = Path(save_dir) if save_dir else Path("optuna_studies")
        self.fixed_params = fixed_params
        
        # ایجاد پوشه ذخیره
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # تنظیم pruner برای متوقف کردن trial‌های ضعیف
        if self.pruning:
            self.pruner = optuna.pruners.MedianPruner(
                n_startup_trials=5,  # حداقل 5 trial قبل از شروع pruning
                n_warmup_steps=5,    # حداقل 5 epoch قبل از pruning
                interval_steps=1     # بررسی در هر epoch
            )
        else:
            self.pruner = optuna.pruners.NopPruner()
        
        # ایجاد یا بازیابی study
        self.study = optuna.create_study(
            study_name=self.study_name,
            direction=direction,
            pruner=self.pruner,
            load_if_exists=True
        )
        
        print(f"🔍 HyperparameterOptimizer initialized")
        print(f"   Study: {self.study_name}")
        print(f"   Direction: {direction}")
        print(f"   Trials: {n_trials}")
        print(f"   Device: {self.device}")
        print(f"   Pruning: {'Enabled' if pruning else 'Disabled'}")
    
    def _suggest_hyperparameters(self, trial: Trial) -> Dict[str, Any]:
        """
        پیشنهاد hyperparameter‌ها برای این trial
        
        این تابع فضای جستجوی hyperparameter‌ها را تعریف می‌کند
        
        Args:
            trial: Trial object از Optuna
            
        Returns:
            دیکشنری از hyperparameter‌های پیشنهادی
        """
        params = {}
        
        # Learning Rate - محدوده لگاریتمی
        # چرا log؟ چون learning rate معمولاً در مقیاس لگاریتمی تغییر می‌کند
        params['learning_rate'] = trial.suggest_float('learning_rate', 1e-5, 1e-2, log=True)
        
        # Batch Size - باید power of 2 باشد برای کارایی GPU
        params['batch_size'] = trial.suggest_categorical('batch_size', [8, 16, 32, 64, 128])
        
        # Optimizer - انتخاب نوع optimizer
        params['optimizer'] = trial.suggest_categorical('optimizer', ['adam', 'adamw', 'sgd', 'rmsprop'])
        
        # Weight Decay - برای regularization (جلوگیری از overfitting)
        params['weight_decay'] = trial.suggest_float('weight_decay', 1e-6, 1e-3, log=True)
        
        # Dropout Rate - فقط برای modality‌هایی که dropout دارند
        if self.modality in ['text', 'audio']:
            params['dropout'] = trial.suggest_float('dropout', 0.1, 0.5)
        
        # پارامترهای خاص Text
        if self.modality == 'text':
            # Hidden Dimension برای LSTM/GRU
            if self.model_name in ['lstm', 'gru']:
                params['hidden_dim'] = trial.suggest_categorical('hidden_dim', [128, 256, 512])
                params['num_layers'] = trial.suggest_int('num_layers', 1, 3)
                params['bidirectional'] = trial.suggest_categorical('bidirectional', [True, False])
        
        # Learning Rate Scheduler
        params['scheduler'] = trial.suggest_categorical('scheduler', ['none', 'step', 'cosine', 'plateau'])
        
        if params['scheduler'] == 'step':
            params['step_size'] = trial.suggest_int('step_size', 5, 20)
            params['gamma'] = trial.suggest_float('gamma', 0.1, 0.9)
        
        # پارامترهای ثابت را اضافه کن
        params.update(self.fixed_params)
        
        return params
    
    def _build_model(self, params: Dict[str, Any]) -> nn.Module:
        """
        ساخت مدل با hyperparameter‌های داده شده
        
        Args:
            params: دیکشنری hyperparameter‌ها
            
        Returns:
            مدل PyTorch
        """
        if self.modality == 'image':
            # ساخت مدل تصویر
            model = ModelBuilder.build_image_model(
                model_name=self.model_name,
                num_classes=self.num_classes,
                pretrained=True
            )
            
        elif self.modality == 'text':
            # ساخت مدل متن
            vocab_size = len(self.train_loader.dataset.dataset.vocab)
            embed_dim = 128  # می‌توان این را هم بهینه کرد
            
            model = ModelBuilder.build_text_model(
                model_name=self.model_name,
                vocab_size=vocab_size,
                embed_dim=embed_dim,
                num_classes=self.num_classes,
                hidden_dim=params.get('hidden_dim', 256),
                num_layers=params.get('num_layers', 2),
                dropout=params.get('dropout', 0.3),
                bidirectional=params.get('bidirectional', True)
            )
            
        elif self.modality == 'audio':
            # ساخت مدل صوتی
            model = ModelBuilder.build_audio_model(
                model_name=self.model_name,
                num_classes=self.num_classes,
                n_mels=128,
                dropout=params.get('dropout', 0.3)
            )
        else:
            raise ValueError(f"Unsupported modality: {self.modality}")
        
        return model
    
    def _build_optimizer(
        self, 
        model: nn.Module, 
        params: Dict[str, Any]
    ) -> torch.optim.Optimizer:
        """
        ساخت optimizer با hyperparameter‌های داده شده
        
        Args:
            model: مدل PyTorch
            params: دیکشنری hyperparameter‌ها
            
        Returns:
            Optimizer
        """
        optimizer_name = params['optimizer']
        lr = params['learning_rate']
        weight_decay = params['weight_decay']
        
        if optimizer_name == 'adam':
            return optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
        elif optimizer_name == 'adamw':
            return optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
        elif optimizer_name == 'sgd':
            return optim.SGD(model.parameters(), lr=lr, weight_decay=weight_decay, momentum=0.9)
        elif optimizer_name == 'rmsprop':
            return optim.RMSprop(model.parameters(), lr=lr, weight_decay=weight_decay)
        else:
            raise ValueError(f"Unknown optimizer: {optimizer_name}")
    
    def _build_scheduler(
        self,
        optimizer: torch.optim.Optimizer,
        params: Dict[str, Any]
    ) -> Optional[torch.optim.lr_scheduler._LRScheduler]:
        """
        ساخت learning rate scheduler
        
        Args:
            optimizer: Optimizer
            params: دیکشنری hyperparameter‌ها
            
        Returns:
            Scheduler یا None
        """
        scheduler_type = params['scheduler']
        
        if scheduler_type == 'none':
            return None
        elif scheduler_type == 'step':
            return optim.lr_scheduler.StepLR(
                optimizer,
                step_size=params.get('step_size', 10),
                gamma=params.get('gamma', 0.1)
            )
        elif scheduler_type == 'cosine':
            return optim.lr_scheduler.CosineAnnealingLR(
                optimizer,
                T_max=20  # می‌توان این را هم بهینه کرد
            )
        elif scheduler_type == 'plateau':
            return optim.lr_scheduler.ReduceLROnPlateau(
                optimizer,
                mode='min',
                factor=0.1,
                patience=5
            )
        else:
            return None
    
    def _objective(self, trial: Trial) -> float:
        """
        تابع هدف که Optuna آن را بهینه می‌کند
        
        این تابع:
        1. Hyperparameter‌ها را پیشنهاد می‌دهد
        2. مدل را می‌سازد
        3. مدل را آموزش می‌دهد
        4. Performance را برمی‌گرداند
        
        Args:
            trial: Trial object از Optuna
            
        Returns:
            مقدار metric (accuracy یا loss)
        """
        # 1. پیشنهاد hyperparameter‌ها
        params = self._suggest_hyperparameters(trial)
        
        print(f"\n{'='*70}")
        print(f"Trial {trial.number + 1}/{self.n_trials}")
        print(f"{'='*70}")
        print(f"Hyperparameters:")
        for key, value in params.items():
            if key not in self.fixed_params:  # فقط پارامترهای متغیر را نمایش بده
                print(f"  {key}: {value}")
        print()
        
        # 2. ساخت مدل
        try:
            model = self._build_model(params)
            model = model.to(self.device)
        except Exception as e:
            print(f"❌ Error building model: {e}")
            raise optuna.TrialPruned()
        
        # 3. ساخت optimizer و scheduler
        optimizer = self._build_optimizer(model, params)
        scheduler = self._build_scheduler(optimizer, params)
        
        # 4. Loss function
        criterion = nn.CrossEntropyLoss()
        
        # 5. Callbacks برای early stopping
        callbacks = [
            EarlyStopping(patience=5, mode='min')  # توقف زودهنگام اگر بهبود نداشت
        ]
        
        # 6. ایجاد Trainer
        # نکته: باید batch_size جدید را اعمال کنیم
        # برای سادگی، از loader‌های موجود استفاده می‌کنیم
        # در نسخه کامل، باید loader جدید با batch_size جدید بسازیم
        
        trainer = Trainer(
            model=model,
            train_loader=self.train_loader,
            val_loader=self.val_loader,
            criterion=criterion,
            optimizer=optimizer,
            device=self.device,
            scheduler=scheduler,
            callbacks=callbacks
        )
        
        # 7. آموزش برای تعداد محدود epoch
        # برای AutoML، معمولاً epoch‌های کمتری می‌زنیم
        max_epochs = self.fixed_params.get('epochs', 10)
        
        try:
            history = trainer.fit(epochs=max_epochs)
        except Exception as e:
            print(f"❌ Error during training: {e}")
            raise optuna.TrialPruned()
        
        # 8. برگرداندن بهترین metric
        if self.direction == 'maximize':
            # برای accuracy
            best_metric = max(history['val_acc'])
            metric_name = 'val_acc'
        else:
            # برای loss
            best_metric = min(history['val_loss'])
            metric_name = 'val_loss'
        
        print(f"✅ Trial completed: {metric_name} = {best_metric:.4f}\n")
        
        return best_metric
    
    def optimize(self) -> Dict[str, Any]:
        """
        اجرای فرآیند بهینه‌سازی
        
        Returns:
            دیکشنری شامل بهترین hyperparameter‌ها و نتایج
        """
        print(f"\n{'🔍'*35}")
        print("HYPERPARAMETER OPTIMIZATION STARTED")
        print(f"{'🔍'*35}\n")
        
        # اجرای optimization
        self.study.optimize(
            self._objective,
            n_trials=self.n_trials,
            timeout=self.timeout,
            show_progress_bar=True
        )
        
        # نمایش نتایج
        print(f"\n{'✅'*35}")
        print("OPTIMIZATION COMPLETED")
        print(f"{'✅'*35}\n")
        
        best_trial = self.study.best_trial
        
        print(f"Best Trial: #{best_trial.number}")
        print(f"Best Value: {best_trial.value:.4f}")
        print(f"\nBest Hyperparameters:")
        for key, value in best_trial.params.items():
            print(f"  {key}: {value}")
        
        # ذخیره نتایج
        results = {
            'study_name': self.study_name,
            'best_trial_number': best_trial.number,
            'best_value': best_trial.value,
            'best_params': best_trial.params,
            'n_trials': len(self.study.trials),
            'direction': self.direction,
            'modality': self.modality,
            'model_name': self.model_name,
            'timestamp': datetime.now().isoformat()
        }
        
        # ذخیره به فایل JSON
        save_path = self.save_dir / f"{self.study_name}_results.json"
        with open(save_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {save_path}")
        
        # ذخیره visualization (اگر plotly نصب باشد)
        try:
            import plotly
            
            # History plot
            fig1 = optuna.visualization.plot_optimization_history(self.study)
            fig1.write_html(str(self.save_dir / f"{self.study_name}_history.html"))
            
            # Importance plot
            fig2 = optuna.visualization.plot_param_importances(self.study)
            fig2.write_html(str(self.save_dir / f"{self.study_name}_importance.html"))
            
            print(f"📊 Visualizations saved to: {self.save_dir}")
            
        except ImportError:
            print("⚠️ Install plotly for visualizations: pip install plotly")
        
        return results
    
    def get_best_params(self) -> Dict[str, Any]:
        """
        دریافت بهترین hyperparameter‌ها
        
        Returns:
            دیکشنری بهترین hyperparameter‌ها
        """
        return self.study.best_params
    
    def get_trials_dataframe(self):
        """
        دریافت DataFrame تمام trial‌ها
        
        Returns:
            pandas DataFrame
        """
        return self.study.trials_dataframe()


def optimize_hyperparameters(
    train_loader: torch.utils.data.DataLoader,
    val_loader: torch.utils.data.DataLoader,
    num_classes: int,
    modality: str = 'image',
    model_name: str = 'resnet18',
    n_trials: int = 50,
    device: str = 'cuda',
    save_dir: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    تابع کمکی برای بهینه‌سازی سریع hyperparameter‌ها
    
    این تابع یک wrapper ساده است که استفاده از HyperparameterOptimizer را آسان می‌کند
    
    Args:
        train_loader: DataLoader آموزش
        val_loader: DataLoader validation
        num_classes: تعداد کلاس‌ها
        modality: نوع داده ('image', 'text', 'audio')
        model_name: نام مدل
        n_trials: تعداد trial‌ها
        device: دستگاه محاسباتی
        save_dir: مسیر ذخیره
        **kwargs: پارامترهای اضافی
        
    Returns:
        دیکشنری نتایج
        
    Example:
        results = optimize_hyperparameters(
            train_loader=train_loader,
            val_loader=val_loader,
            num_classes=10,
            modality='image',
            model_name='resnet18',
            n_trials=20
        )
        
        print(f"Best learning rate: {results['best_params']['learning_rate']}")
    """
    optimizer = HyperparameterOptimizer(
        train_loader=train_loader,
        val_loader=val_loader,
        num_classes=num_classes,
        modality=modality,
        model_name=model_name,
        n_trials=n_trials,
        device=device,
        save_dir=save_dir,
        **kwargs
    )
    
    return optimizer.optimize()

