"""
Time Series Models
مدل‌های پیش‌بینی سری‌های زمانی

این ماژول مدل‌های LSTM، Prophet و ARIMA برای time series فراهم می‌کند
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Tuple, Optional, List
import pandas as pd


class TimeSeriesLSTM(nn.Module):
    """
    LSTM برای پیش‌بینی سری زمانی
    
    این مدل از LSTM برای یادگیری الگوهای زمانی استفاده می‌کند
    
    ورودی: (batch, sequence_length, input_dim)
    خروجی: (batch, output_dim) یا (batch, forecast_horizon, output_dim)
    
    Example:
        model = TimeSeriesLSTM(
            input_dim=1,
            hidden_dim=64,
            num_layers=2,
            output_dim=1,
            forecast_horizon=10
        )
        
        # ورودی: 100 timestep گذشته
        x = torch.randn(32, 100, 1)
        # پیش‌بینی: 10 timestep آینده
        output = model(x)  # (32, 10, 1)
    """
    
    def __init__(
        self,
        input_dim: int = 1,
        hidden_dim: int = 64,
        num_layers: int = 2,
        output_dim: int = 1,
        forecast_horizon: int = 1,
        dropout: float = 0.2,
        bidirectional: bool = False
    ):
        """
        مقداردهی اولیه
        
        Args:
            input_dim: تعداد feature‌های ورودی
            hidden_dim: اندازه hidden state
            num_layers: تعداد لایه‌های LSTM
            output_dim: تعداد feature‌های خروجی
            forecast_horizon: چند timestep آینده پیش‌بینی شود
            dropout: نرخ dropout
            bidirectional: استفاده از LSTM دوطرفه
        """
        super(TimeSeriesLSTM, self).__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.output_dim = output_dim
        self.forecast_horizon = forecast_horizon
        self.bidirectional = bidirectional
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True,
            bidirectional=bidirectional
        )
        
        # تعداد جهت‌ها (1 یا 2)
        num_directions = 2 if bidirectional else 1
        
        # Fully connected layer برای هر timestep آینده
        self.fc = nn.Linear(hidden_dim * num_directions, output_dim * forecast_horizon)
        
        print(f"✅ TimeSeriesLSTM created")
        print(f"   Input: (batch, seq_len, {input_dim})")
        print(f"   Output: (batch, {forecast_horizon}, {output_dim})")
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            x: (batch, sequence_length, input_dim)
            
        Returns:
            (batch, forecast_horizon, output_dim)
        """
        # LSTM forward
        lstm_out, (h_n, c_n) = self.lstm(x)
        
        # استفاده از آخرین hidden state
        # h_n: (num_layers * num_directions, batch, hidden_dim)
        
        if self.bidirectional:
            # Concatenate forward and backward hidden states
            h_forward = h_n[-2, :, :]
            h_backward = h_n[-1, :, :]
            last_hidden = torch.cat([h_forward, h_backward], dim=1)
        else:
            last_hidden = h_n[-1, :, :]
        
        # پیش‌بینی
        output = self.fc(last_hidden)
        
        # Reshape به (batch, forecast_horizon, output_dim)
        output = output.view(-1, self.forecast_horizon, self.output_dim)
        
        return output


class TimeSeriesGRU(nn.Module):
    """
    GRU برای پیش‌بینی سری زمانی
    
    مشابه LSTM اما با پارامترهای کمتر
    
    Example:
        model = TimeSeriesGRU(
            input_dim=5,
            hidden_dim=128,
            forecast_horizon=24  # پیش‌بینی 24 ساعت آینده
        )
    """
    
    def __init__(
        self,
        input_dim: int = 1,
        hidden_dim: int = 64,
        num_layers: int = 2,
        output_dim: int = 1,
        forecast_horizon: int = 1,
        dropout: float = 0.2
    ):
        """مقداردهی اولیه"""
        super(TimeSeriesGRU, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.forecast_horizon = forecast_horizon
        self.output_dim = output_dim
        
        # GRU layers
        self.gru = nn.GRU(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        # Output layer
        self.fc = nn.Linear(hidden_dim, output_dim * forecast_horizon)
        
        print(f"✅ TimeSeriesGRU created (forecast_horizon={forecast_horizon})")
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        gru_out, h_n = self.gru(x)
        
        # آخرین hidden state
        last_hidden = h_n[-1, :, :]
        
        # پیش‌بینی
        output = self.fc(last_hidden)
        output = output.view(-1, self.forecast_horizon, self.output_dim)
        
        return output


class AttentionLSTM(nn.Module):
    """
    LSTM با Attention mechanism
    
    این مدل از attention برای تمرکز روی timestep‌های مهم استفاده می‌کند
    
    Example:
        model = AttentionLSTM(
            input_dim=10,
            hidden_dim=128,
            forecast_horizon=5
        )
    """
    
    def __init__(
        self,
        input_dim: int = 1,
        hidden_dim: int = 64,
        num_layers: int = 2,
        output_dim: int = 1,
        forecast_horizon: int = 1,
        dropout: float = 0.2
    ):
        """مقداردهی اولیه"""
        super(AttentionLSTM, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.forecast_horizon = forecast_horizon
        self.output_dim = output_dim
        
        # LSTM
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        # Attention layer
        self.attention = nn.Linear(hidden_dim, 1)
        
        # Output layer
        self.fc = nn.Linear(hidden_dim, output_dim * forecast_horizon)
        
        print(f"✅ AttentionLSTM created with attention mechanism")
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with attention"""
        # LSTM
        lstm_out, _ = self.lstm(x)
        # lstm_out: (batch, seq_len, hidden_dim)
        
        # محاسبه attention weights
        attention_scores = self.attention(lstm_out)
        # (batch, seq_len, 1)
        
        attention_weights = torch.softmax(attention_scores, dim=1)
        
        # Apply attention
        context = torch.sum(attention_weights * lstm_out, dim=1)
        # (batch, hidden_dim)
        
        # پیش‌بینی
        output = self.fc(context)
        output = output.view(-1, self.forecast_horizon, self.output_dim)
        
        return output


class ProphetWrapper:
    """
    Wrapper برای Facebook Prophet
    
    Prophet یک کتابخانه پیش‌بینی time series است که برای
    داده‌های تجاری با روندهای فصلی مناسب است
    
    Example:
        from datetime import datetime, timedelta
        
        # ساخت داده
        dates = pd.date_range('2020-01-01', periods=365)
        values = np.random.randn(365).cumsum()
        df = pd.DataFrame({'ds': dates, 'y': values})
        
        # آموزش
        prophet = ProphetWrapper()
        prophet.fit(df)
        
        # پیش‌بینی 30 روز آینده
        future = prophet.predict(periods=30)
        print(future[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])
    """
    
    def __init__(
        self,
        growth: str = 'linear',
        seasonality_mode: str = 'additive',
        daily_seasonality: bool = True,
        weekly_seasonality: bool = True,
        yearly_seasonality: bool = True
    ):
        """
        مقداردهی اولیه
        
        Args:
            growth: 'linear' یا 'logistic'
            seasonality_mode: 'additive' یا 'multiplicative'
            daily_seasonality: فصلی بودن روزانه
            weekly_seasonality: فصلی بودن هفتگی
            yearly_seasonality: فصلی بودن سالانه
        """
        try:
            from prophet import Prophet
            
            self.model = Prophet(
                growth=growth,
                seasonality_mode=seasonality_mode,
                daily_seasonality=daily_seasonality,
                weekly_seasonality=weekly_seasonality,
                yearly_seasonality=yearly_seasonality
            )
            
            print(f"✅ Prophet model created")
            
        except ImportError:
            print("⚠️ Prophet not installed. Run: pip install prophet")
            raise
    
    def fit(self, df: pd.DataFrame):
        """
        آموزش مدل
        
        Args:
            df: DataFrame با ستون‌های 'ds' (تاریخ) و 'y' (مقدار)
        """
        self.model.fit(df)
        print(f"✅ Prophet training complete")
    
    def predict(self, periods: int = 30, freq: str = 'D') -> pd.DataFrame:
        """
        پیش‌بینی
        
        Args:
            periods: چند دوره آینده
            freq: فرکانس ('D' for daily, 'H' for hourly, etc.)
            
        Returns:
            DataFrame با پیش‌بینی‌ها
        """
        future = self.model.make_future_dataframe(periods=periods, freq=freq)
        forecast = self.model.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    
    def plot(self):
        """رسم نمودار"""
        try:
            import matplotlib.pyplot as plt
            fig = self.model.plot(self.model.predict(self.model.make_future_dataframe(30)))
            plt.show()
        except Exception as e:
            print(f"⚠️ Could not plot: {e}")


def create_timeseries_model(
    model_name: str,
    **kwargs
):
    """
    Factory function برای ساخت time series models
    
    Args:
        model_name: 'lstm', 'gru', 'attention_lstm', 'prophet'
        **kwargs: پارامترهای مدل
        
    Returns:
        Time series model
        
    Example:
        # PyTorch models
        model = create_timeseries_model(
            'lstm',
            input_dim=5,
            hidden_dim=128,
            forecast_horizon=24
        )
        
        # Prophet
        model = create_timeseries_model('prophet')
    """
    models = {
        'lstm': TimeSeriesLSTM,
        'gru': TimeSeriesGRU,
        'attention_lstm': AttentionLSTM,
        'prophet': ProphetWrapper
    }
    
    if model_name.lower() not in models:
        raise ValueError(f"Unsupported model: {model_name}. Choose from: {list(models.keys())}")
    
    return models[model_name.lower()](**kwargs)
