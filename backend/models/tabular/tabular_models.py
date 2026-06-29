"""
Tabular Data Models
مدل‌های یادگیری ماشین برای داده‌های جدولی

این ماژول از XGBoost و LightGBM برای داده‌های tabular استفاده می‌کند
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import json
import pickle


class TabularModel:
    """
    کلاس پایه برای مدل‌های tabular
    
    Example:
        model = XGBoostClassifier(n_classes=3)
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
    """
    
    def __init__(self, task_type: str = "classification"):
        """
        مقداردهی اولیه
        
        Args:
            task_type: 'classification' یا 'regression'
        """
        self.task_type = task_type
        self.model = None
        self.feature_names = []
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        """آموزش مدل"""
        raise NotImplementedError
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """پیش‌بینی"""
        raise NotImplementedError
    
    def save(self, path: str):
        """ذخیره مدل"""
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'feature_names': self.feature_names,
                'task_type': self.task_type
            }, f)
    
    def load(self, path: str):
        """بارگذاری مدل"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.feature_names = data['feature_names']
            self.task_type = data['task_type']


class XGBoostClassifier(TabularModel):
    """
    XGBoost برای طبقه‌بندی
    
    XGBoost یک gradient boosting framework قدرتمند است
    که برای داده‌های tabular بسیار خوب کار می‌کند
    
    Example:
        model = XGBoostClassifier(n_classes=3, max_depth=6)
        model.fit(X_train, y_train)
        probs = model.predict_proba(X_test)
        preds = model.predict(X_test)
    """
    
    def __init__(
        self,
        n_classes: int = 2,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        n_estimators: int = 100,
        **kwargs
    ):
        """
        مقداردهی اولیه
        
        Args:
            n_classes: تعداد کلاس‌ها
            max_depth: عمق درخت
            learning_rate: نرخ یادگیری
            n_estimators: تعداد درخت‌ها
        """
        super().__init__(task_type="classification")
        
        try:
            import xgboost as xgb
            
            self.model = xgb.XGBClassifier(
                max_depth=max_depth,
                learning_rate=learning_rate,
                n_estimators=n_estimators,
                objective='multi:softprob' if n_classes > 2 else 'binary:logistic',
                num_class=n_classes if n_classes > 2 else None,
                **kwargs
            )
            
            print(f"✅ XGBoostClassifier created (n_classes={n_classes})")
            
        except ImportError:
            print("⚠️ XGBoost not installed. Run: pip install xgboost")
            raise
    
    def fit(self, X: np.ndarray, y: np.ndarray, eval_set: Optional[Tuple] = None):
        """
        آموزش مدل
        
        Args:
            X: features (N, D)
            y: labels (N,)
            eval_set: (X_val, y_val) برای validation
        """
        if eval_set:
            self.model.fit(
                X, y,
                eval_set=[eval_set],
                verbose=False
            )
        else:
            self.model.fit(X, y)
        
        print(f"✅ XGBoost training complete")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """پیش‌بینی کلاس"""
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """پیش‌بینی احتمال"""
        return self.model.predict_proba(X)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """دریافت اهمیت feature‌ها"""
        importance = self.model.feature_importances_
        if self.feature_names:
            return dict(zip(self.feature_names, importance))
        return {f"feature_{i}": imp for i, imp in enumerate(importance)}


class LightGBMClassifier(TabularModel):
    """
    LightGBM برای طبقه‌بندی
    
    LightGBM سریع‌تر از XGBoost است و برای dataset‌های بزرگ مناسب است
    
    Example:
        model = LightGBMClassifier(n_classes=10)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
    """
    
    def __init__(
        self,
        n_classes: int = 2,
        max_depth: int = -1,
        learning_rate: float = 0.1,
        n_estimators: int = 100,
        num_leaves: int = 31,
        **kwargs
    ):
        """مقداردهی اولیه"""
        super().__init__(task_type="classification")
        
        try:
            import lightgbm as lgb
            
            self.model = lgb.LGBMClassifier(
                max_depth=max_depth,
                learning_rate=learning_rate,
                n_estimators=n_estimators,
                num_leaves=num_leaves,
                objective='multiclass' if n_classes > 2 else 'binary',
                num_class=n_classes if n_classes > 2 else None,
                **kwargs
            )
            
            print(f"✅ LightGBMClassifier created (n_classes={n_classes})")
            
        except ImportError:
            print("⚠️ LightGBM not installed. Run: pip install lightgbm")
            raise
    
    def fit(self, X: np.ndarray, y: np.ndarray, eval_set: Optional[Tuple] = None):
        """آموزش مدل"""
        if eval_set:
            self.model.fit(
                X, y,
                eval_set=[eval_set],
                eval_metric='multi_logloss' if self.model.objective == 'multiclass' else 'binary_logloss',
                callbacks=[
                    # EarlyStopping callback
                ]
            )
        else:
            self.model.fit(X, y)
        
        print(f"✅ LightGBM training complete")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """پیش‌بینی"""
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """احتمال"""
        return self.model.predict_proba(X)


class XGBoostRegressor(TabularModel):
    """
    XGBoost برای regression
    
    Example:
        model = XGBoostRegressor()
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
    """
    
    def __init__(
        self,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        n_estimators: int = 100,
        **kwargs
    ):
        """مقداردهی اولیه"""
        super().__init__(task_type="regression")
        
        try:
            import xgboost as xgb
            
            self.model = xgb.XGBRegressor(
                max_depth=max_depth,
                learning_rate=learning_rate,
                n_estimators=n_estimators,
                objective='reg:squarederror',
                **kwargs
            )
            
            print(f"✅ XGBoostRegressor created")
            
        except ImportError:
            print("⚠️ XGBoost not installed")
            raise
    
    def fit(self, X: np.ndarray, y: np.ndarray, eval_set: Optional[Tuple] = None):
        """آموزش"""
        if eval_set:
            self.model.fit(X, y, eval_set=[eval_set], verbose=False)
        else:
            self.model.fit(X, y)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """پیش‌بینی"""
        return self.model.predict(X)


def create_tabular_model(
    model_name: str,
    task_type: str = "classification",
    **kwargs
) -> TabularModel:
    """
    Factory function برای ساخت tabular models
    
    Args:
        model_name: 'xgboost' یا 'lightgbm'
        task_type: 'classification' یا 'regression'
        **kwargs: پارامترهای مدل
        
    Returns:
        TabularModel
        
    Example:
        model = create_tabular_model(
            'xgboost',
            task_type='classification',
            n_classes=3,
            max_depth=6
        )
    """
    if task_type == "classification":
        if model_name.lower() == 'xgboost':
            return XGBoostClassifier(**kwargs)
        elif model_name.lower() == 'lightgbm':
            return LightGBMClassifier(**kwargs)
    elif task_type == "regression":
        if model_name.lower() == 'xgboost':
            return XGBoostRegressor(**kwargs)
        elif model_name.lower() == 'lightgbm':
            # می‌توانید LightGBMRegressor بسازید
            raise NotImplementedError("LightGBMRegressor not yet implemented")
    
    raise ValueError(f"Unsupported model: {model_name} for {task_type}")
