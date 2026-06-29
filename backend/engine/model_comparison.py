"""
Model Comparison Engine
مقایسه و تحلیل چندین مدل آموزش دیده

این ماژول امکان مقایسه بین مدل‌های مختلف را فراهم می‌کند
تا بتوانید بهترین مدل را انتخاب کنید
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import torch
import matplotlib.pyplot as plt
import seaborn as sns


class TrainingRun:
    """
    اطلاعات یک دوره آموزش
    
    این کلاس تمام اطلاعات یک training run را نگه می‌دارد
    """
    
    def __init__(
        self,
        run_id: str,
        project_id: str,
        model_name: str,
        modality: str,
        hyperparameters: Dict[str, Any],
        history: Dict[str, List[float]],
        metrics: Dict[str, float],
        timestamp: str,
        duration: float = 0.0,
        device: str = 'cpu',
        **kwargs
    ):
        """
        مقداردهی اولیه
        
        Args:
            run_id: شناسه یکتای این run
            project_id: شناسه پروژه
            model_name: نام مدل (مثلاً 'resnet18')
            modality: نوع داده ('image', 'text', 'audio')
            hyperparameters: تنظیمات (learning_rate, batch_size, etc.)
            history: تاریخچه training (train_loss, val_acc, etc.)
            metrics: نتایج نهایی (best_val_acc, best_val_loss, etc.)
            timestamp: زمان شروع training
            duration: مدت زمان training (ثانیه)
            device: دستگاه محاسباتی
            **kwargs: اطلاعات اضافی
        """
        self.run_id = run_id
        self.project_id = project_id
        self.model_name = model_name
        self.modality = modality
        self.hyperparameters = hyperparameters
        self.history = history
        self.metrics = metrics
        self.timestamp = timestamp
        self.duration = duration
        self.device = device
        self.extra_info = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """
        تبدیل به dictionary برای ذخیره
        
        Returns:
            دیکشنری شامل تمام اطلاعات
        """
        return {
            'run_id': self.run_id,
            'project_id': self.project_id,
            'model_name': self.model_name,
            'modality': self.modality,
            'hyperparameters': self.hyperparameters,
            'history': self.history,
            'metrics': self.metrics,
            'timestamp': self.timestamp,
            'duration': self.duration,
            'device': self.device,
            **self.extra_info
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrainingRun':
        """
        ساخت TrainingRun از dictionary
        
        Args:
            data: دیکشنری اطلاعات
            
        Returns:
            شیء TrainingRun
        """
        # جدا کردن فیلدهای اصلی از extra
        main_fields = {
            'run_id', 'project_id', 'model_name', 'modality',
            'hyperparameters', 'history', 'metrics', 'timestamp',
            'duration', 'device'
        }
        
        main_data = {k: v for k, v in data.items() if k in main_fields}
        extra = {k: v for k, v in data.items() if k not in main_fields}
        
        return cls(**main_data, **extra)
    
    def get_best_metric(self, metric_name: str) -> float:
        """
        دریافت بهترین مقدار یک metric
        
        Args:
            metric_name: نام metric (مثلاً 'val_acc')
            
        Returns:
            بهترین مقدار
        """
        if metric_name in self.history:
            # برای accuracy → max، برای loss → min
            if 'acc' in metric_name.lower():
                return max(self.history[metric_name])
            else:
                return min(self.history[metric_name])
        return 0.0


class ModelComparison:
    """
    موتور مقایسه مدل‌ها
    
    این کلاس امکان ذخیره، بارگذاری و مقایسه مدل‌های مختلف را فراهم می‌کند
    
    Example:
        comparison = ModelComparison('projects/my-project')
        
        # ذخیره یک run
        comparison.save_run(run_id='run1', model_name='resnet18', ...)
        
        # مقایسه همه run‌ها
        results = comparison.compare_all()
        
        # رسم نمودار
        comparison.plot_comparison('val_acc')
    """
    
    def __init__(self, project_dir: str):
        """
        مقداردهی اولیه
        
        Args:
            project_dir: مسیر پروژه
        """
        self.project_dir = Path(project_dir)
        self.runs_dir = self.project_dir / "runs"
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        
        # لیست تمام run‌ها
        self.runs: Dict[str, TrainingRun] = {}
        self._load_all_runs()
    
    def _load_all_runs(self):
        """
        بارگذاری تمام run‌های ذخیره شده
        """
        # خواندن تمام فایل‌های JSON در پوشه runs
        for run_file in self.runs_dir.glob("*.json"):
            try:
                with open(run_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    run = TrainingRun.from_dict(data)
                    self.runs[run.run_id] = run
            except Exception as e:
                print(f"⚠️ خطا در خواندن {run_file}: {e}")
        
        print(f"📂 {len(self.runs)} run بارگذاری شد")
    
    def save_run(
        self,
        run_id: str,
        project_id: str,
        model_name: str,
        modality: str,
        hyperparameters: Dict[str, Any],
        history: Dict[str, List[float]],
        duration: float = 0.0,
        device: str = 'cpu',
        **kwargs
    ) -> TrainingRun:
        """
        ذخیره یک training run
        
        این تابع اطلاعات training را ذخیره می‌کند تا بعداً بتوان مقایسه کرد
        
        Args:
            run_id: شناسه یکتا (می‌تواند خودکار باشد)
            project_id: شناسه پروژه
            model_name: نام مدل
            modality: نوع داده
            hyperparameters: تنظیمات
            history: تاریخچه training
            duration: مدت زمان (ثانیه)
            device: دستگاه
            **kwargs: اطلاعات اضافی
            
        Returns:
            شیء TrainingRun ذخیره شده
        """
        # محاسبه metrics نهایی از history
        metrics = {}
        for key in history.keys():
            if 'acc' in key.lower():
                metrics[f'best_{key}'] = max(history[key])
            elif 'loss' in key.lower():
                metrics[f'best_{key}'] = min(history[key])
        
        # ایجاد TrainingRun
        run = TrainingRun(
            run_id=run_id,
            project_id=project_id,
            model_name=model_name,
            modality=modality,
            hyperparameters=hyperparameters,
            history=history,
            metrics=metrics,
            timestamp=datetime.now().isoformat(),
            duration=duration,
            device=device,
            **kwargs
        )
        
        # ذخیره در حافظه
        self.runs[run_id] = run
        
        # ذخیره در فایل
        run_file = self.runs_dir / f"{run_id}.json"
        with open(run_file, 'w', encoding='utf-8') as f:
            json.dump(run.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"✅ Run '{run_id}' ذخیره شد")
        return run
    
    def get_run(self, run_id: str) -> Optional[TrainingRun]:
        """
        دریافت یک run خاص
        
        Args:
            run_id: شناسه run
            
        Returns:
            TrainingRun یا None
        """
        return self.runs.get(run_id)
    
    def get_all_runs(self) -> List[TrainingRun]:
        """
        دریافت تمام run‌ها
        
        Returns:
            لیست تمام TrainingRun‌ها
        """
        return list(self.runs.values())
    
    def compare_runs(
        self,
        run_ids: Optional[List[str]] = None,
        metric: str = 'val_acc'
    ) -> pd.DataFrame:
        """
        مقایسه چند run با یکدیگر
        
        Args:
            run_ids: لیست شناسه‌های run (None = همه)
            metric: metric برای مقایسه
            
        Returns:
            DataFrame مقایسه
        """
        # اگر run_ids داده نشد، همه را مقایسه کن
        if run_ids is None:
            runs_to_compare = self.get_all_runs()
        else:
            runs_to_compare = [self.runs[rid] for rid in run_ids if rid in self.runs]
        
        if not runs_to_compare:
            print("⚠️ هیچ run برای مقایسه وجود ندارد")
            return pd.DataFrame()
        
        # ساخت DataFrame
        data = []
        for run in runs_to_compare:
            row = {
                'run_id': run.run_id,
                'model': run.model_name,
                'modality': run.modality,
                'timestamp': run.timestamp,
                'duration': f"{run.duration:.2f}s",
                'device': run.device,
            }
            
            # اضافه کردن hyperparameters
            for key, value in run.hyperparameters.items():
                row[f'hp_{key}'] = value
            
            # اضافه کردن metrics
            row.update(run.metrics)
            
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # مرتب‌سازی بر اساس metric (اگر موجود باشد)
        best_metric = f'best_{metric}'
        if best_metric in df.columns:
            # برای accuracy: نزولی، برای loss: صعودی
            ascending = 'loss' in metric.lower()
            df = df.sort_values(best_metric, ascending=ascending)
        
        return df
    
    def get_best_run(self, metric: str = 'val_acc') -> Optional[TrainingRun]:
        """
        پیدا کردن بهترین run بر اساس یک metric
        
        Args:
            metric: metric برای مقایسه
            
        Returns:
            بهترین TrainingRun یا None
        """
        runs = self.get_all_runs()
        if not runs:
            return None
        
        # برای accuracy → max، برای loss → min
        reverse = 'acc' in metric.lower()
        
        best_run = max(
            runs,
            key=lambda r: r.get_best_metric(metric) if reverse else -r.get_best_metric(metric)
        )
        
        return best_run
    
    def plot_comparison(
        self,
        metric: str = 'val_acc',
        run_ids: Optional[List[str]] = None,
        save_path: Optional[str] = None
    ):
        """
        رسم نمودار مقایسه
        
        Args:
            metric: metric برای رسم
            run_ids: لیست run‌ها (None = همه)
            save_path: مسیر ذخیره (None = نمایش)
        """
        # دریافت run‌ها
        if run_ids is None:
            runs_to_plot = self.get_all_runs()
        else:
            runs_to_plot = [self.runs[rid] for rid in run_ids if rid in self.runs]
        
        if not runs_to_plot:
            print("⚠️ هیچ run برای رسم وجود ندارد")
            return
        
        # ایجاد figure
        plt.figure(figsize=(12, 6))
        
        # رسم هر run
        for run in runs_to_plot:
            if metric in run.history:
                epochs = range(1, len(run.history[metric]) + 1)
                label = f"{run.model_name} ({run.run_id})"
                plt.plot(epochs, run.history[metric], marker='o', label=label)
        
        plt.xlabel('Epoch')
        plt.ylabel(metric.replace('_', ' ').title())
        plt.title(f'Model Comparison - {metric}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"📊 نمودار در {save_path} ذخیره شد")
        else:
            plt.show()
        
        plt.close()
    
    def generate_report(
        self,
        output_file: Optional[str] = None
    ) -> str:
        """
        ایجاد گزارش کامل مقایسه
        
        Args:
            output_file: مسیر فایل خروجی (None = فقط return)
            
        Returns:
            متن گزارش
        """
        report_lines = []
        report_lines.append("="*70)
        report_lines.append("MODEL COMPARISON REPORT")
        report_lines.append("="*70)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Project: {self.project_dir.name}")
        report_lines.append(f"Total Runs: {len(self.runs)}")
        report_lines.append("")
        
        if not self.runs:
            report_lines.append("⚠️ No training runs found")
            report = "\n".join(report_lines)
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
            return report
        
        # بهترین run‌ها
        report_lines.append("BEST MODELS")
        report_lines.append("-"*70)
        
        for metric in ['val_acc', 'val_loss', 'train_acc']:
            best_run = self.get_best_run(metric)
            if best_run:
                best_value = best_run.get_best_metric(metric)
                report_lines.append(
                    f"Best {metric}: {best_run.model_name} "
                    f"({best_run.run_id}) = {best_value:.4f}"
                )
        
        report_lines.append("")
        
        # جدول مقایسه
        report_lines.append("COMPARISON TABLE")
        report_lines.append("-"*70)
        
        df = self.compare_runs()
        if not df.empty:
            report_lines.append(df.to_string())
        
        report_lines.append("")
        report_lines.append("="*70)
        
        report = "\n".join(report_lines)
        
        # ذخیره در فایل
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 گزارش در {output_file} ذخیره شد")
        
        return report
    
    def export_to_csv(self, output_file: str):
        """
        Export مقایسه به CSV
        
        Args:
            output_file: مسیر فایل CSV
        """
        df = self.compare_runs()
        if not df.empty:
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"📊 CSV در {output_file} ذخیره شد")
        else:
            print("⚠️ هیچ داده‌ای برای export وجود ندارد")
    
    def delete_run(self, run_id: str) -> bool:
        """
        حذف یک run
        
        Args:
            run_id: شناسه run
            
        Returns:
            True اگر حذف شد
        """
        if run_id in self.runs:
            # حذف از حافظه
            del self.runs[run_id]
            
            # حذف فایل
            run_file = self.runs_dir / f"{run_id}.json"
            if run_file.exists():
                run_file.unlink()
            
            print(f"✅ Run '{run_id}' حذف شد")
            return True
        
        print(f"⚠️ Run '{run_id}' پیدا نشد")
        return False


def compare_models(
    project_dir: str,
    metric: str = 'val_acc',
    plot: bool = True
) -> pd.DataFrame:
    """
    تابع کمکی برای مقایسه سریع مدل‌ها
    
    Args:
        project_dir: مسیر پروژه
        metric: metric برای مقایسه
        plot: آیا نمودار رسم شود؟
        
    Returns:
        DataFrame مقایسه
        
    Example:
        df = compare_models('projects/my-project', metric='val_acc', plot=True)
        print(df)
    """
    comparison = ModelComparison(project_dir)
    df = comparison.compare_runs(metric=metric)
    
    if plot and not df.empty:
        comparison.plot_comparison(metric=metric)
    
    return df

