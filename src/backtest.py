"""
Backtest Simulator - Executes trading strategies and calculates performance metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class Trade:
    """Represents a single trade."""
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry_price: float
    exit_price: float
    pnl: float
    return_pct: float


@dataclass
class BacktestResult:
    """Results from a backtest simulation."""
    trades: List[Trade]
    total_return: float
    total_return_pct: float
    max_drawdown: float
    max_drawdown_pct: float
    num_trades: int
    win_rate: float
    avg_return: float
    sharpe_ratio: Optional[float] = None


class BacktestSimulator:
    """Simulator for backtesting trading strategies."""
    
    def __init__(self, initial_capital: float = 100000.0):
        """
        Initialize the backtest simulator.
        
        Args:
            initial_capital: Starting capital (default: 100000)
        """
        self.initial_capital = initial_capital
    
    def run(self, df: pd.DataFrame, signals: pd.DataFrame, 
            entry_price_col: str = "close", exit_price_col: str = "close") -> BacktestResult:
        """
        Run backtest simulation.
        
        Args:
            df: DataFrame with OHLCV data and date index
            signals: DataFrame with 'entry' and 'exit' boolean columns
            entry_price_col: Column to use for entry price (default: "close")
            exit_price_col: Column to use for exit price (default: "close")
            
        Returns:
            BacktestResult with performance metrics
        """
        if entry_price_col not in df.columns:
            raise ValueError(f"Entry price column '{entry_price_col}' not found")
        if exit_price_col not in df.columns:
            raise ValueError(f"Exit price column '{exit_price_col}' not found")
        
        trades = []
        position = None  # None = no position, or dict with entry info
        
        for idx, row in df.iterrows():
            entry_signal = signals.loc[idx, 'entry'] if 'entry' in signals.columns else False
            exit_signal = signals.loc[idx, 'exit'] if 'exit' in signals.columns else False
            
            # Exit existing position first
            if position is not None and exit_signal:
                exit_price = row[exit_price_col]
                entry_price = position['entry_price']
                entry_date = position['entry_date']
                
                pnl = exit_price - entry_price
                return_pct = (pnl / entry_price) * 100
                
                trade = Trade(
                    entry_date=entry_date,
                    exit_date=idx,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    pnl=pnl,
                    return_pct=return_pct
                )
                trades.append(trade)
                position = None
            
            # Enter new position
            if position is None and entry_signal:
                entry_price = row[entry_price_col]
                position = {
                    'entry_date': idx,
                    'entry_price': entry_price
                }
        
        # Close any open position at the end
        if position is not None:
            last_idx = df.index[-1]
            last_row = df.loc[last_idx]
            exit_price = last_row[exit_price_col]
            entry_price = position['entry_price']
            entry_date = position['entry_date']
            
            pnl = exit_price - entry_price
            return_pct = (pnl / entry_price) * 100
            
            trade = Trade(
                entry_date=entry_date,
                exit_date=last_idx,
                entry_price=entry_price,
                exit_price=exit_price,
                pnl=pnl,
                return_pct=return_pct
            )
            trades.append(trade)
        
        # Calculate metrics
        return self._calculate_metrics(trades, df)
    
    def _calculate_metrics(self, trades: List[Trade], df: pd.DataFrame) -> BacktestResult:
        """Calculate performance metrics from trades."""
        if not trades:
            return BacktestResult(
                trades=[],
                total_return=0.0,
                total_return_pct=0.0,
                max_drawdown=0.0,
                max_drawdown_pct=0.0,
                num_trades=0,
                win_rate=0.0,
                avg_return=0.0,
                sharpe_ratio=None
            )
        
        # Calculate returns
        returns = [trade.return_pct for trade in trades]
        total_return_pct = sum(returns)
        total_return = self.initial_capital * (total_return_pct / 100.0)
        
        # Calculate drawdown
        equity_curve = []
        current_equity = self.initial_capital
        
        for trade in trades:
            current_equity *= (1 + trade.return_pct / 100.0)
            equity_curve.append(current_equity)
        
        if equity_curve:
            peak = equity_curve[0]
            max_dd = 0.0
            max_dd_pct = 0.0
            
            for equity in equity_curve:
                if equity > peak:
                    peak = equity
                drawdown = peak - equity
                drawdown_pct = ((peak - equity) / peak) * 100.0
                
                if drawdown > max_dd:
                    max_dd = drawdown
                if drawdown_pct > max_dd_pct:
                    max_dd_pct = drawdown_pct
            
            max_drawdown = max_dd
            max_drawdown_pct = max_dd_pct
        else:
            max_drawdown = 0.0
            max_drawdown_pct = 0.0
        
        # Calculate win rate
        winning_trades = [t for t in trades if t.pnl > 0]
        win_rate = len(winning_trades) / len(trades) if trades else 0.0
        
        # Average return
        avg_return = np.mean(returns) if returns else 0.0
        
        # Sharpe ratio (simplified - assumes daily returns)
        if len(returns) > 1:
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else None
        else:
            sharpe_ratio = None
        
        return BacktestResult(
            trades=trades,
            total_return=total_return,
            total_return_pct=total_return_pct,
            max_drawdown=max_drawdown,
            max_drawdown_pct=max_drawdown_pct,
            num_trades=len(trades),
            win_rate=win_rate,
            avg_return=avg_return,
            sharpe_ratio=sharpe_ratio
        )
    
    def run_with_evaluator(self, df: pd.DataFrame, evaluator: Callable,
                          entry_price_col: str = "close", exit_price_col: str = "close") -> BacktestResult:
        """
        Run backtest with an evaluator function.
        
        Args:
            df: DataFrame with OHLCV data
            evaluator: Function that takes DataFrame and returns signals DataFrame
            entry_price_col: Column for entry price
            exit_price_col: Column for exit price
            
        Returns:
            BacktestResult
        """
        signals = evaluator(df)
        return self.run(df, signals, entry_price_col, exit_price_col)


def run_backtest(df: pd.DataFrame, signals: pd.DataFrame, 
                initial_capital: float = 100000.0) -> BacktestResult:
    """
    Convenience function to run a backtest.
    
    Args:
        df: DataFrame with OHLCV data
        signals: DataFrame with entry/exit signals
        initial_capital: Starting capital
        
    Returns:
        BacktestResult
    """
    simulator = BacktestSimulator(initial_capital=initial_capital)
    return simulator.run(df, signals)

