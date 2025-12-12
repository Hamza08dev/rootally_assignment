"""
Script to run DSL examples and capture terminal output.
Generates 6-7 example DSL strategies and executes them.
"""

import sys
from pathlib import Path

# Add parent directory to path to allow imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import json
import pandas as pd
from src.dsl_parser import parse_dsl_to_ast
from src.code_generator import generate_code_from_ast
from src.backtest import BacktestSimulator


def print_example_header(num: int, description: str):
    """Print formatted example header."""
    print("\n" + "=" * 80)
    print(f"EXAMPLE {num}: {description}")
    print("=" * 80)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n--- {title} ---")


def run_dsl_example(dsl_text: str, description: str, example_num: int, df: pd.DataFrame):
    """Run a single DSL example and print results."""
    print_example_header(example_num, description)
    
    # Print DSL
    print_section("DSL Code")
    print(dsl_text)
    
    # Parse DSL to AST
    print_section("Parsed AST")
    try:
        ast = parse_dsl_to_ast(dsl_text)
        print(json.dumps(ast, indent=2, default=str))
    except Exception as e:
        print(f"ERROR: {e}")
        return
    
    # Generate evaluator function
    print_section("Code Generation")
    try:
        evaluator = generate_code_from_ast(ast)
        print("[OK] Python evaluator function generated successfully")
    except Exception as e:
        print(f"ERROR: {e}")
        return
    
    # Execute on data
    print_section("Signal Generation")
    try:
        signals = evaluator(df)
        entry_count = signals['entry'].sum()
        exit_count = signals['exit'].sum()
        print(f"[OK] Generated signals:")
        print(f"  - Entry signals: {entry_count} days")
        print(f"  - Exit signals: {exit_count} days")
        
        # Show sample signals
        if entry_count > 0 or exit_count > 0:
            print("\n  Sample signals (first 30 days with any signal):")
            signal_days = signals[(signals['entry']) | (signals['exit'])].head(30)
            if len(signal_days) > 0:
                print(signal_days.to_string())
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Run backtest
    print_section("Backtest Results")
    try:
        simulator = BacktestSimulator(initial_capital=100000.0)
        results = simulator.run(df, signals)
        
        print(f"[OK] Backtest completed:")
        print(f"  - Total Return: ${results.total_return:,.2f} ({results.total_return_pct:.2f}%)")
        print(f"  - Max Drawdown: ${results.max_drawdown:,.2f} ({results.max_drawdown_pct:.2f}%)")
        print(f"  - Number of Trades: {results.num_trades}")
        print(f"  - Win Rate: {results.win_rate * 100:.2f}%")
        print(f"  - Average Return per Trade: {results.avg_return:.2f}%")
        if results.sharpe_ratio:
            print(f"  - Sharpe Ratio: {results.sharpe_ratio:.2f}")
        
        if results.trades and len(results.trades) <= 10:
            print("\n  Trade Log:")
            for i, trade in enumerate(results.trades, 1):
                print(f"    Trade {i}:")
                print(f"      Enter: {trade.entry_date.strftime('%Y-%m-%d')} at ${trade.entry_price:.2f}")
                print(f"      Exit:  {trade.exit_date.strftime('%Y-%m-%d')} at ${trade.exit_price:.2f}")
                print(f"      P&L: ${trade.pnl:.2f} ({trade.return_pct:.2f}%)")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function to run all DSL examples."""
    print("=" * 80)
    print("DSL EXAMPLES - Trading Strategy Execution")
    print("=" * 80)
    
    # Load data
    print("\nLoading sample data...")
    try:
        df = pd.read_csv("data/sample_data.csv", index_col='date', parse_dates=True)
        print(f"[OK] Loaded {len(df)} days of data")
        print(f"  Date range: {df.index[0]} to {df.index[-1]}")
    except Exception as e:
        print(f"ERROR loading data: {e}")
        return
    
    # Define DSL examples
    examples = [
        {
            "description": "Simple Moving Average Crossover",
            "dsl": """ENTRY:
close crosses_above sma(close, 20)

EXIT:
close crosses_below sma(close, 20)"""
        },
        {
            "description": "RSI Oversold Entry with Volume Filter",
            "dsl": """ENTRY:
rsi(close, 14) < 30 AND volume > 1000000

EXIT:
rsi(close, 14) > 70"""
        },
        {
            "description": "Price Above Moving Average with Volume Confirmation",
            "dsl": """ENTRY:
close > sma(close, 50) AND volume > yesterday(volume)

EXIT:
close < sma(close, 50)"""
        },
        {
            "description": "Multiple Conditions with OR Logic",
            "dsl": """ENTRY:
rsi(close, 14) < 30 OR close crosses_above yesterday(high)

EXIT:
rsi(close, 14) > 70 OR close crosses_below yesterday(low)"""
        },
        {
            "description": "Percentage Change Strategy",
            "dsl": """ENTRY:
percent_change(close, 5) > 5

EXIT:
percent_change(close, 3) < -3"""
        },
        {
            "description": "Complex Multi-Condition Entry",
            "dsl": """ENTRY:
close > ema(close, 20) AND volume > 1000000 AND rsi(close, 14) > 50 AND rsi(close, 14) < 70

EXIT:
close < ema(close, 20) OR rsi(close, 14) > 80"""
        },
        {
            "description": "Price Breakout with Volume Spike",
            "dsl": """ENTRY:
close > last_week(high) AND volume > 1500000

EXIT:
close < last_week(low)"""
        }
    ]
    
    # Run each example
    for i, example in enumerate(examples, 1):
        run_dsl_example(example["dsl"], example["description"], i, df)
    
    print("\n" + "=" * 80)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()

