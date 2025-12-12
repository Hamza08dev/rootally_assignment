"""
Technical indicators and helper functions for time-series analysis.
"""

import pandas as pd
import numpy as np
from typing import Union


def sma(series: pd.Series, period: int) -> pd.Series:
    """
    Calculate Simple Moving Average.
    
    Args:
        series: Price series (e.g., close prices)
        period: Number of periods for moving average
        
    Returns:
        Series with SMA values
    """
    return series.rolling(window=period, min_periods=1).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average.
    
    Args:
        series: Price series
        period: Number of periods for EMA
        
    Returns:
        Series with EMA values
    """
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        series: Price series (typically close prices)
        period: Number of periods (default: 14)
        
    Returns:
        Series with RSI values (0-100)
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()
    
    rs = gain / loss
    rsi_values = 100 - (100 / (1 + rs))
    
    return rsi_values.fillna(50)  # Fill NaN with neutral RSI value


def yesterday(series: pd.Series) -> pd.Series:
    """
    Get value from previous trading day.
    
    Args:
        series: Price series
        
    Returns:
        Series with yesterday's values
    """
    return series.shift(1)


def last_week(series: pd.Series) -> pd.Series:
    """
    Get value from 7 trading days ago.
    
    Args:
        series: Price series
        
    Returns:
        Series with values from last week
    """
    return series.shift(7)


def n_days_ago(series: pd.Series, n: int) -> pd.Series:
    """
    Get value from n trading days ago.
    
    Args:
        series: Price series
        n: Number of days to look back
        
    Returns:
        Series with values from n days ago
    """
    return series.shift(n)


def change(series: pd.Series, n: int = 1) -> pd.Series:
    """
    Calculate absolute change over n periods.
    
    Args:
        series: Price series
        n: Number of periods
        
    Returns:
        Series with absolute changes
    """
    return series - series.shift(n)


def percent_change(series: pd.Series, n: int = 1) -> pd.Series:
    """
    Calculate percentage change over n periods.
    
    Args:
        series: Price series
        n: Number of periods
        
    Returns:
        Series with percentage changes
    """
    return ((series - series.shift(n)) / series.shift(n)) * 100


def crosses_above(series1: pd.Series, series2: Union[pd.Series, float]) -> pd.Series:
    """
    Detect when series1 crosses above series2.
    
    A crossover occurs when:
    - Current period: series1 > series2
    - Previous period: series1 <= series2
    
    Args:
        series1: First series (typically price)
        series2: Second series or constant value
        
    Returns:
        Boolean series indicating crossover points
    """
    if isinstance(series2, (int, float)):
        series2 = pd.Series(series2, index=series1.index)
    
    current_above = series1 > series2
    prev_below = series1.shift(1) <= series2.shift(1)
    
    return current_above & prev_below


def crosses_below(series1: pd.Series, series2: Union[pd.Series, float]) -> pd.Series:
    """
    Detect when series1 crosses below series2.
    
    A crossover occurs when:
    - Current period: series1 < series2
    - Previous period: series1 >= series2
    
    Args:
        series1: First series (typically price)
        series2: Second series or constant value
        
    Returns:
        Boolean series indicating crossover points
    """
    if isinstance(series2, (int, float)):
        series2 = pd.Series(series2, index=series1.index)
    
    current_below = series1 < series2
    prev_above = series1.shift(1) >= series2.shift(1)
    
    return current_below & prev_above


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pre-calculate common indicators for a DataFrame.
    This is optional but can improve performance.
    
    Args:
        df: DataFrame with OHLCV columns
        
    Returns:
        DataFrame with additional indicator columns
    """
    result = df.copy()
    
    # Common SMA periods
    for period in [20, 50, 200]:
        result[f'sma_{period}'] = sma(result['close'], period)
    
    # Common RSI periods
    result['rsi_14'] = rsi(result['close'], 14)
    
    # Common EMA periods
    for period in [20, 50]:
        result[f'ema_{period}'] = ema(result['close'], period)
    
    return result

