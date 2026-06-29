"""
Time Series Data Loader with Advanced Preprocessing
بارگذاری و پیش‌پردازش داده‌های سری زمانی
"""

import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any, Union
from sklearn.preprocessing import StandardScaler, MinMaxScaler


class TimeSeriesDataset(Dataset):
    """
    Dataset برای داده‌های سری زمانی
    
    Supports:
    - Univariate & Multivariate time series
    - Sliding window approach
    - Multiple preprocessing techniques
    - Classification & Forecasting tasks
    """
    
    def __init__(
        self,
        data_path: str,
        sequence_length: int = 50,
        forecast_horizon: int = 1,
        target_column: Optional[str] = None,  # None for forecasting
        stride: int = 1,
        scaling: str = 'standard',  # 'standard', 'minmax', 'none'
        differencing: bool = False,  # Remove trend
        detrend: bool = False,  # Linear detrend
        remove_seasonality: bool = False,
        task: str = 'classification'  # 'classification' or 'forecasting'
    ):
        """
        Args:
            data_path: مسیر CSV file
            sequence_length: طول هر sequence
            forecast_horizon: تعداد timestep برای پیش‌بینی (forecasting)
            target_column: ستون هدف (برای classification)
            stride: فاصله بین windows
            scaling: روش scaling
            differencing: استفاده از differencing
            detrend: حذف trend خطی
            remove_seasonality: حذف seasonality
            task: نوع task
        """
        self.data_path = Path(data_path)
        self.sequence_length = sequence_length
        self.forecast_horizon = forecast_horizon
        self.target_column = target_column
        self.stride = stride
        self.scaling = scaling
        self.differencing = differencing
        self.detrend = detrend
        self.remove_seasonality = remove_seasonality
        self.task = task
        
        # بارگذاری داده
        self.df = pd.read_csv(data_path)
        self._preprocess()
        
        print(f"✅ TimeSeriesDataset loaded: {len(self)} sequences")
        print(f"   Sequence length: {self.sequence_length}")
        print(f"   Features: {self.X.shape[2]}")
        if self.task == 'classification':
            print(f"   Classes: {len(np.unique(self.y))}")
    
    def _preprocess(self):
        """پیش‌پردازش سری زمانی"""
        df = self.df.copy()
        
        # 1. جدا کردن features و target
        if self.task == 'classification':
            if self.target_column not in df.columns:
                raise ValueError(f"Target column '{self.target_column}' not found!")
            X = df.drop(columns=[self.target_column])
            y = df[self.target_column].values
        else:
            X = df
            y = None
        
        # 2. تبدیل به numpy
        data = X.values.astype(np.float32)
        
        # 3. Handle missing values
        if np.isnan(data).any():
            # Forward fill then backward fill
            df_temp = pd.DataFrame(data)
            df_temp = df_temp.fillna(method='ffill').fillna(method='bfill')
            data = df_temp.values
        
        # 4. Detrending
        if self.detrend:
            data = self._detrend_data(data)
        
        # 5. Remove seasonality
        if self.remove_seasonality:
            data = self._remove_seasonality(data)
        
        # 6. Differencing
        if self.differencing:
            data = np.diff(data, axis=0)
            if y is not None:
                y = y[1:]  # adjust target
        
        # 7. Scaling
        if self.scaling == 'standard':
            self.scaler = StandardScaler()
            data = self.scaler.fit_transform(data)
        elif self.scaling == 'minmax':
            self.scaler = MinMaxScaler()
            data = self.scaler.fit_transform(data)
        
        # 8. Create sequences با sliding window
        self.X, self.y = self._create_sequences(data, y)
    
    def _detrend_data(self, data: np.ndarray) -> np.ndarray:
        """حذف trend خطی"""
        from scipy import signal
        detrended = np.zeros_like(data)
        for i in range(data.shape[1]):
            detrended[:, i] = signal.detrend(data[:, i])
        return detrended
    
    def _remove_seasonality(self, data: np.ndarray, period: int = 12) -> np.ndarray:
        """حذف seasonality"""
        deseasonalized = data.copy()
        for i in range(data.shape[1]):
            if len(data) >= period * 2:
                # محاسبه seasonal component
                seasonal = pd.Series(data[:, i]).rolling(window=period, center=True).mean()
                seasonal = seasonal.fillna(method='bfill').fillna(method='ffill')
                deseasonalized[:, i] = data[:, i] - seasonal.values
        return deseasonalized
    
    def _create_sequences(
        self, 
        data: np.ndarray, 
        labels: Optional[np.ndarray]
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        ایجاد sequences با sliding window
        """
        X_sequences = []
        y_sequences = []
        
        if self.task == 'classification':
            # برای classification: هر sequence یک label دارد
            for i in range(0, len(data) - self.sequence_length + 1, self.stride):
                X_sequences.append(data[i:i + self.sequence_length])
                # استفاده از label آخرین timestep
                y_sequences.append(labels[i + self.sequence_length - 1])
            
            X = np.array(X_sequences)
            y = np.array(y_sequences)
            
        else:
            # برای forecasting: predict کردن چند timestep بعدی
            for i in range(0, len(data) - self.sequence_length - self.forecast_horizon + 1, self.stride):
                X_sequences.append(data[i:i + self.sequence_length])
                # Target = timesteps بعدی
                y_sequences.append(data[i + self.sequence_length:i + self.sequence_length + self.forecast_horizon])
            
            X = np.array(X_sequences)
            y = np.array(y_sequences)
        
        self.X_array = X
        self.y_array = y
        
        # تبدیل به tensor
        self.X = torch.FloatTensor(X)
        if self.task == 'classification':
            self.y = torch.LongTensor(y)
        else:
            self.y = torch.FloatTensor(y)
        
        return self.X, self.y
    
    def __len__(self) -> int:
        return len(self.X)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, Union[int, torch.Tensor]]:
        if self.task == 'classification':
            return self.X[idx], self.y[idx].item()
        else:
            return self.X[idx], self.y[idx]
    
    def inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """بازگرداندن scaling"""
        if hasattr(self, 'scaler'):
            return self.scaler.inverse_transform(data)
        return data


def create_timeseries_loaders(
    project_dir: str,
    config: Dict[str, Any]
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    ایجاد DataLoader برای time series
    """
    import json
    
    project_file = Path(project_dir) / "project.json"
    with open(project_file, 'r') as f:
        project_info = json.load(f)
    
    data_file = Path(project_dir) / "data" / "timeseries.csv"
    
    # Time series settings
    sequence_length = config.get('sequence_length', 50)
    forecast_horizon = config.get('forecast_horizon', 1)
    target_column = config.get('target_column', None)
    stride = config.get('stride', 1)
    scaling = config.get('scaling', 'standard')
    differencing = config.get('differencing', False)
    detrend = config.get('detrend', False)
    remove_seasonality = config.get('remove_seasonality', False)
    task = config.get('task', 'classification')
    
    # ایجاد dataset
    full_dataset = TimeSeriesDataset(
        data_path=str(data_file),
        sequence_length=sequence_length,
        forecast_horizon=forecast_horizon,
        target_column=target_column,
        stride=stride,
        scaling=scaling,
        differencing=differencing,
        detrend=detrend,
        remove_seasonality=remove_seasonality,
        task=task
    )
    
    # تقسیم به train/val/test (time-based split)
    total_size = len(full_dataset)
    train_size = int(config.get('train_split', 0.7) * total_size)
    val_size = int(config.get('val_split', 0.15) * total_size)
    test_size = total_size - train_size - val_size
    
    # Split بدون shuffle (برای time series)
    train_dataset = torch.utils.data.Subset(full_dataset, range(train_size))
    val_dataset = torch.utils.data.Subset(full_dataset, range(train_size, train_size + val_size))
    test_dataset = torch.utils.data.Subset(full_dataset, range(train_size + val_size, total_size))
    
    batch_size = config.get('batch_size', 32)
    num_workers = config.get('num_workers', 2)
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=False,  # Don't shuffle time series!
        num_workers=num_workers
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers
    )
    
    print(f"✅ Time Series DataLoaders created:")
    print(f"   Train: {len(train_dataset)} sequences")
    print(f"   Val: {len(val_dataset)} sequences")
    print(f"   Test: {len(test_dataset)} sequences")
    
    return train_loader, val_loader, test_loader


if __name__ == "__main__":
    # تست
    print("Testing TimeSeriesDataset...")
    
    # ساخت یک سری زمانی نمونه
    np.random.seed(42)
    t = np.linspace(0, 100, 1000)
    # Trend + Seasonality + Noise
    trend = 0.05 * t
    seasonal = 10 * np.sin(2 * np.pi * t / 50)
    noise = np.random.randn(1000) * 2
    
    data = pd.DataFrame({
        'value': trend + seasonal + noise,
        'feature2': np.random.randn(1000),
        'target': (trend + seasonal + noise > 10).astype(int)
    })
    
    test_file = Path('test_timeseries.csv')
    data.to_csv(test_file, index=False)
    
    try:
        # Test classification
        dataset = TimeSeriesDataset(
            data_path=str(test_file),
            sequence_length=50,
            target_column='target',
            scaling='standard',
            detrend=True,
            remove_seasonality=True,
            task='classification'
        )
        
        print(f"Dataset created: {len(dataset)} sequences")
        print(f"Sequence shape: {dataset.X[0].shape}")
        
        # Test DataLoader
        loader = DataLoader(dataset, batch_size=16, shuffle=False)
        for batch_X, batch_y in loader:
            print(f"Batch X: {batch_X.shape}")
            print(f"Batch y: {batch_y.shape}")
            break
    
    finally:
        if test_file.exists():
            test_file.unlink()

