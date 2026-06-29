"""
Tabular Data Loader with Feature Engineering
بارگذاری و feature engineering برای داده‌های جدولی
"""

import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif


class TabularDataset(Dataset):
    """
    Dataset برای داده‌های جدولی با feature engineering
    """
    
    def __init__(
        self,
        data_path: str,
        target_column: str,
        feature_engineering: bool = True,
        scaling: str = 'standard',  # 'standard', 'minmax', 'none'
        handle_missing: str = 'mean',  # 'mean', 'median', 'drop'
        feature_selection: Optional[int] = None,  # top k features
        categorical_encoding: str = 'onehot'  # 'onehot', 'label'
    ):
        """
        Args:
            data_path: مسیر فایل CSV
            target_column: نام ستون هدف
            feature_engineering: فعال‌سازی feature engineering
            scaling: روش scaling features
            handle_missing: نحوه برخورد با missing values
            feature_selection: تعداد بهترین features (None = همه)
            categorical_encoding: روش encode کردن categorical features
        """
        self.data_path = Path(data_path)
        self.target_column = target_column
        self.feature_engineering = feature_engineering
        self.scaling = scaling
        self.handle_missing = handle_missing
        self.feature_selection_k = feature_selection
        self.categorical_encoding = categorical_encoding
        
        # بارگذاری و پیش‌پردازش داده
        self.df = pd.read_csv(data_path)
        self._preprocess()
        
        print(f"✅ TabularDataset loaded: {len(self.df)} samples")
        print(f"   Features: {self.X.shape[1]}")
        print(f"   Classes: {len(np.unique(self.y))}")
    
    def _preprocess(self):
        """پیش‌پردازش داده"""
        df = self.df.copy()
        
        # 1. جدا کردن features و target
        if self.target_column not in df.columns:
            raise ValueError(f"Target column '{self.target_column}' not found!")
        
        X = df.drop(columns=[self.target_column])
        y = df[self.target_column]
        
        # 2. Encode کردن target
        self.label_encoder = LabelEncoder()
        y = self.label_encoder.fit_transform(y)
        
        # 3. شناسایی categorical و numerical columns
        self.categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
        self.numerical_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        
        print(f"   Numerical features: {len(self.numerical_cols)}")
        print(f"   Categorical features: {len(self.categorical_cols)}")
        
        # 4. Handle missing values
        if self.handle_missing == 'drop':
            X = X.dropna()
            y = y[X.index]
        else:
            # Numerical columns
            if self.numerical_cols:
                imputer_num = SimpleImputer(strategy=self.handle_missing)
                X[self.numerical_cols] = imputer_num.fit_transform(X[self.numerical_cols])
            
            # Categorical columns
            if self.categorical_cols:
                imputer_cat = SimpleImputer(strategy='most_frequent')
                X[self.categorical_cols] = imputer_cat.fit_transform(X[self.categorical_cols])
        
        # 5. Encode categorical features
        if self.categorical_cols:
            if self.categorical_encoding == 'onehot':
                # One-hot encoding
                X = pd.get_dummies(X, columns=self.categorical_cols, drop_first=True)
            else:
                # Label encoding
                for col in self.categorical_cols:
                    le = LabelEncoder()
                    X[col] = le.fit_transform(X[col].astype(str))
        
        # 6. Feature Engineering
        if self.feature_engineering:
            X = self._engineer_features(X)
        
        # 7. Feature Selection
        if self.feature_selection_k and self.feature_selection_k < X.shape[1]:
            selector = SelectKBest(mutual_info_classif, k=self.feature_selection_k)
            X_array = selector.fit_transform(X.values, y)
            selected_features = X.columns[selector.get_support()].tolist()
            X = pd.DataFrame(X_array, columns=selected_features)
            print(f"   Selected top {self.feature_selection_k} features")
        
        # 8. Scaling
        if self.scaling == 'standard':
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X.values)
            X = pd.DataFrame(X_scaled, columns=X.columns)
        elif self.scaling == 'minmax':
            from sklearn.preprocessing import MinMaxScaler
            self.scaler = MinMaxScaler()
            X_scaled = self.scaler.fit_transform(X.values)
            X = pd.DataFrame(X_scaled, columns=X.columns)
        
        self.X = torch.FloatTensor(X.values)
        self.y = torch.LongTensor(y)
        self.feature_names = X.columns.tolist()
    
    def _engineer_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Feature engineering خودکار
        """
        X_new = X.copy()
        
        # فقط برای numerical columns
        num_cols = X_new.select_dtypes(include=[np.number]).columns
        
        if len(num_cols) >= 2:
            # Polynomial features (degree 2) برای 2 feature اول
            for i, col1 in enumerate(num_cols[:2]):
                for col2 in num_cols[i+1:3]:
                    # ضرب
                    X_new[f'{col1}_x_{col2}'] = X_new[col1] * X_new[col2]
                    # تقسیم (با جلوگیری از division by zero)
                    X_new[f'{col1}_div_{col2}'] = X_new[col1] / (X_new[col2] + 1e-8)
            
            # تجمیع آماری
            X_new['sum_all'] = X_new[num_cols].sum(axis=1)
            X_new['mean_all'] = X_new[num_cols].mean(axis=1)
            X_new['std_all'] = X_new[num_cols].std(axis=1)
            X_new['max_all'] = X_new[num_cols].max(axis=1)
            X_new['min_all'] = X_new[num_cols].min(axis=1)
        
        print(f"   Engineered features: {X_new.shape[1] - X.shape[1]} new features")
        return X_new
    
    def __len__(self) -> int:
        return len(self.X)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        return self.X[idx], self.y[idx].item()
    
    def get_feature_importance(self, model: torch.nn.Module) -> pd.DataFrame:
        """
        محاسبه feature importance
        """
        if hasattr(model, 'fc') and hasattr(model.fc[0], 'weight'):
            weights = model.fc[0].weight.data.abs().mean(dim=0).cpu().numpy()
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': weights
            }).sort_values('importance', ascending=False)
            return importance_df
        return pd.DataFrame()


def create_tabular_loaders(
    project_dir: str,
    config: Dict[str, Any]
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    ایجاد DataLoader برای tabular data
    """
    import json
    
    project_file = Path(project_dir) / "project.json"
    with open(project_file, 'r') as f:
        project_info = json.load(f)
    
    data_file = Path(project_dir) / "data" / "data.csv"
    target_column = config.get('target_column', 'target')
    
    # Feature engineering settings
    feature_engineering = config.get('feature_engineering', True)
    scaling = config.get('scaling', 'standard')
    handle_missing = config.get('handle_missing', 'mean')
    feature_selection = config.get('feature_selection', None)
    
    # ایجاد dataset
    full_dataset = TabularDataset(
        data_path=str(data_file),
        target_column=target_column,
        feature_engineering=feature_engineering,
        scaling=scaling,
        handle_missing=handle_missing,
        feature_selection=feature_selection
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
    
    batch_size = config.get('batch_size', 64)
    num_workers = config.get('num_workers', 2)
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
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
    
    print(f"✅ Tabular DataLoaders created:")
    print(f"   Train: {len(train_dataset)} samples")
    print(f"   Val: {len(val_dataset)} samples")
    print(f"   Test: {len(test_dataset)} samples")
    
    return train_loader, val_loader, test_loader


if __name__ == "__main__":
    # تست با یک dataset نمونه
    print("Testing TabularDataset with feature engineering...")
    
    # ساخت یک CSV نمونه
    test_data = pd.DataFrame({
        'age': [25, 30, 35, 40, 45, 50, 55, 60],
        'income': [30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000],
        'education': ['high school', 'bachelor', 'bachelor', 'master', 'master', 'phd', 'phd', 'phd'],
        'city': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B'],
        'target': [0, 0, 1, 1, 1, 1, 0, 1]
    })
    
    test_file = Path('test_tabular.csv')
    test_data.to_csv(test_file, index=False)
    
    try:
        dataset = TabularDataset(
            data_path=str(test_file),
            target_column='target',
            feature_engineering=True,
            scaling='standard',
            handle_missing='mean',
            feature_selection=None
        )
        
        print(f"\nDataset created successfully!")
        print(f"Feature names: {dataset.feature_names[:10]}...")  # Show first 10
        print(f"Sample shape: {dataset.X[0].shape}")
        
        # تست DataLoader
        loader = DataLoader(dataset, batch_size=4, shuffle=True)
        for batch_X, batch_y in loader:
            print(f"Batch X shape: {batch_X.shape}")
            print(f"Batch y shape: {batch_y.shape}")
            break
    
    finally:
        # پاک کردن فایل تست
        if test_file.exists():
            test_file.unlink()

