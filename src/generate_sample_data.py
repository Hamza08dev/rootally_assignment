"""
Generate sample OHLCV data for testing and demonstration.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_sample_data(start_date: str = "2023-01-01", 
                        end_date: str = "2023-12-31",
                        initial_price: float = 100.0,
                        output_file: str = "data/sample_data.csv") -> pd.DataFrame:
    """
    Generate synthetic OHLCV data with realistic price movements.
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        initial_price: Starting price
        output_file: Output CSV file path
        
    Returns:
        DataFrame with OHLCV data
    """
    # Create date range (trading days only - exclude weekends)
    date_range = pd.bdate_range(start=start_date, end=end_date)
    n_days = len(date_range)
    
    # Generate price movements using random walk with trend
    np.random.seed(42)  # For reproducibility
    
    # Daily returns (normal distribution with slight upward bias)
    daily_returns = np.random.normal(0.0005, 0.02, n_days)  # ~0.05% daily return, 2% volatility
    
    # Add some trend and volatility clusters
    trend = np.linspace(0, 0.001, n_days)  # Gradual trend increase
    volatility_cluster = np.random.choice([0.015, 0.025], size=n_days)  # Varying volatility
    
    # Adjust returns
    daily_returns = daily_returns * (volatility_cluster / 0.02) + trend
    
    # Generate close prices
    close_prices = [initial_price]
    for ret in daily_returns[1:]:
        close_prices.append(close_prices[-1] * (1 + ret))
    
    # Generate OHLC from close prices
    data = []
    for i, (date, close) in enumerate(zip(date_range, close_prices)):
        # High/Low range around close (typically 1-3% range)
        daily_range_pct = np.random.uniform(0.01, 0.03)
        
        high = close * (1 + daily_range_pct / 2)
        low = close * (1 - daily_range_pct / 2)
        
        # Open is typically close to previous close with some gap
        if i == 0:
            open_price = close * np.random.uniform(0.99, 1.01)
        else:
            gap = np.random.uniform(-0.005, 0.005)
            open_price = close_prices[i-1] * (1 + gap)
            # Ensure open is within high/low
            open_price = max(low, min(high, open_price))
        
        # Volume (base volume with some randomness and correlation to price movement)
        base_volume = 1000000
        volume_multiplier = 1 + abs(daily_returns[i]) * 10  # Higher volume on big moves
        volume = int(base_volume * volume_multiplier * np.random.uniform(0.7, 1.3))
        
        data.append({
            'date': date,
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    
    # Save to CSV
    df.to_csv(output_file)
    print(f"Generated {len(df)} days of sample data and saved to {output_file}")
    
    return df


if __name__ == "__main__":
    # Generate sample data
    df = generate_sample_data()
    print(f"\nFirst few rows:")
    print(df.head())
    print(f"\nLast few rows:")
    print(df.tail())
    print(f"\nStatistics:")
    print(df.describe())

