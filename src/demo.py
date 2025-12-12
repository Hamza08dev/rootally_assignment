"""
End-to-End Demonstration Script

Demonstrates the complete pipeline:
Natural Language → Structured JSON → DSL → AST → Python Code → Execution → Results
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to allow imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import json
import pandas as pd
from src.nl_parser import parse_nl_to_json, NLParser
from src.dsl_generator import json_to_dsl
from src.dsl_parser import parse_dsl_to_ast
from src.code_generator import generate_code_from_ast
from src.backtest import BacktestSimulator


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---")


def run_demo(nl_input: str, data_file: str = "data/sample_data.csv", 
             use_llm: bool = True):
    """
    Run the complete end-to-end demonstration.
    
    Args:
        nl_input: Natural language trading rule
        data_file: Path to OHLCV data CSV file
        use_llm: Whether to use LLM for NL parsing (if False, uses fallback)
    """
    print_section("NLP → DSL → Strategy Execution Prototype")
    print(f"\nNatural Language Input:")
    print(f'  "{nl_input}"')
    
    # Step 1: Natural Language → Structured JSON
    print_section("Step 1: Natural Language → Structured JSON")
    try:
        if use_llm:
            structured_json = parse_nl_to_json(nl_input)
        else:
            # Use fallback parser
            parser = NLParser()
            structured_json = parser.parse_with_fallback(nl_input)
        
        print("\nStructured JSON:")
        print(json.dumps(structured_json, indent=2))
    except Exception as e:
        print(f"\nError in NL parsing: {e}")
        print("Trying fallback parser...")
        parser = NLParser()
        structured_json = parser.parse_with_fallback(nl_input)
        print("\nStructured JSON (fallback):")
        print(json.dumps(structured_json, indent=2))
    
    # Step 2: Structured JSON → DSL
    print_section("Step 2: Structured JSON → DSL")
    try:
        dsl_text = json_to_dsl(structured_json)
        print("\nGenerated DSL:")
        print(dsl_text)
    except Exception as e:
        print(f"\nError generating DSL: {e}")
        return
    
    # Step 3: DSL → AST
    print_section("Step 3: DSL → AST")
    try:
        ast = parse_dsl_to_ast(dsl_text)
        print("\nParsed AST:")
        print(json.dumps(ast, indent=2, default=str))
    except Exception as e:
        print(f"\nError parsing DSL: {e}")
        return
    
    # Step 4: AST → Python Code (generate evaluator function)
    print_section("Step 4: AST → Python Code")
    try:
        evaluator = generate_code_from_ast(ast)
        print("\nGenerated Python evaluator function (ready to execute)")
        print("Function signature: evaluator(df: pd.DataFrame) -> pd.DataFrame")
    except Exception as e:
        print(f"\nError generating code: {e}")
        return
    
    # Step 5: Load data
    print_section("Step 5: Load Sample Data")
    try:
        df = pd.read_csv(data_file, index_col='date', parse_dates=True)
        print(f"\nLoaded {len(df)} days of data")
        print(f"Date range: {df.index[0]} to {df.index[-1]}")
        print("\nFirst few rows:")
        print(df.head())
    except Exception as e:
        print(f"\nError loading data: {e}")
        return
    
    # Step 6: Execute generated code
    print_section("Step 6: Execute Generated Code")
    try:
        signals = evaluator(df)
        print("\nGenerated signals:")
        print(f"  Entry signals: {signals['entry'].sum()} days")
        print(f"  Exit signals: {signals['exit'].sum()} days")
        print("\nSample signals (first 20 days):")
        print(signals.head(20))
    except Exception as e:
        print(f"\nError executing code: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 7: Run backtest
    print_section("Step 7: Run Backtest Simulation")
    try:
        simulator = BacktestSimulator(initial_capital=100000.0)
        results = simulator.run(df, signals)
        
        print("\nBacktest Results:")
        print(f"  Total Return: ${results.total_return:,.2f} ({results.total_return_pct:.2f}%)")
        print(f"  Max Drawdown: ${results.max_drawdown:,.2f} ({results.max_drawdown_pct:.2f}%)")
        print(f"  Number of Trades: {results.num_trades}")
        print(f"  Win Rate: {results.win_rate * 100:.2f}%")
        print(f"  Average Return per Trade: {results.avg_return:.2f}%")
        if results.sharpe_ratio:
            print(f"  Sharpe Ratio: {results.sharpe_ratio:.2f}")
        
        if results.trades:
            print("\nTrade Log:")
            for i, trade in enumerate(results.trades, 1):
                print(f"  Trade {i}:")
                print(f"    Enter: {trade.entry_date.strftime('%Y-%m-%d')} at ${trade.entry_price:.2f}")
                print(f"    Exit:  {trade.exit_date.strftime('%Y-%m-%d')} at ${trade.exit_price:.2f}")
                print(f"    P&L: ${trade.pnl:.2f} ({trade.return_pct:.2f}%)")
        else:
            print("\nNo trades executed.")
    except Exception as e:
        print(f"\nError running backtest: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Summary
    print_section("Summary")
    print("\nPipeline completed successfully!")
    print("\nPipeline stages:")
    print("  1. ✓ Natural Language → Structured JSON")
    print("  2. ✓ Structured JSON → DSL")
    print("  3. ✓ DSL → AST")
    print("  4. ✓ AST → Python Code")
    print("  5. ✓ Data Loading")
    print("  6. ✓ Code Execution")
    print("  7. ✓ Backtest Simulation")


def main():
    """Main demo function with example inputs."""
    # Example natural language inputs
    examples = [
        "Buy when the close price is above the 20-day moving average and volume is above 1 million.",
        "Enter when price crosses above yesterday's high.",
        "Exit when RSI(14) is below 30.",
    ]
    
    # Use the first example
    nl_input = examples[0]
    
    # Check if LLM is available
    import os
    use_llm = bool(os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))
    
    if not use_llm:
        print("\n⚠️  Warning: No LLM API key found. Using fallback parser.")
        print("   Set GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY in .env file for full functionality.\n")
    
    # Run demo
    run_demo(nl_input, use_llm=use_llm)


if __name__ == "__main__":
    main()

