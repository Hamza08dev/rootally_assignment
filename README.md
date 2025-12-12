# NLP → DSL → Strategy Execution Prototype

A complete pipeline for converting natural language trading rules into executable Python strategies with backtesting capabilities.

## Overview

This project implements a research-engineering prototype that demonstrates:

1. **Natural Language Parsing**: Converts English trading instructions into structured JSON
2. **DSL Design**: A domain-specific language for expressing trading strategies
3. **DSL Parsing**: Parses DSL text into an Abstract Syntax Tree (AST)
4. **Code Generation**: Converts AST into executable Python code
5. **Backtesting**: Simulates strategy execution and calculates performance metrics

## Architecture

```
Natural Language Input 
    ↓
NL Parser (LLM-based)
    ↓
Structured JSON
    ↓
DSL Generator
    ↓
DSL Text
    ↓
DSL Parser (Lark)
    ↓
AST (Abstract Syntax Tree)
    ↓
Code Generator
    ↓
Python Evaluation Function
    ↓
Backtest Simulator
    ↓
Performance Metrics
```

## Project Structure

```
rootally/
├── src/
│   ├── __init__.py
│   ├── nl_parser.py              # Natural language → structured JSON
│   ├── dsl_generator.py          # Structured JSON → DSL text
│   ├── dsl_parser.py             # DSL text → AST (using Lark)
│   ├── code_generator.py         # AST → Python code
│   ├── indicators.py             # Technical indicators (SMA, RSI, etc.)
│   ├── backtest.py               # Strategy execution simulator
│   ├── demo.py                   # End-to-end demonstration script
│   └── generate_sample_data.py   # Sample data generator
├── data/
│   └── sample_data.csv           # Sample OHLCV data
├── docs/
│   └── dsl_specification.md      # DSL design document
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure LLM API (optional but recommended):
   
   **Option A: Using Google Gemini (Recommended)**
   - Create a `.env` file in the project root (copy from `.env.example`)
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your-actual-api-key-here
     GEMINI_MODEL=gemini-2.5-flash
     LLM_PROVIDER=gemini
     ```
   
   **Option B: Using OpenAI**
   - Create a `.env` file in the project root
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=sk-your-actual-api-key-here
     LLM_PROVIDER=openai
     ```
   
   **Option C: Using Anthropic**
   - Create a `.env` file in the project root
   - Add your Anthropic API key:
     ```
     ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here
     LLM_PROVIDER=anthropic
     ```
   
   **Quick Setup:**
   ```bash
   # Copy the example file
   copy .env.example .env
   
   # Then edit .env and replace "your_openai_api_key_here" with your actual key
   ```
   
   **Note**: The system includes a fallback parser that works without an LLM API key, but it has limited functionality. For full natural language parsing capabilities, an API key is required.
   
   **Getting API Keys:**
   - **Gemini**: https://aistudio.google.com/app/apikey (Get free API key)
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/
   
   **Detailed Setup:** See `SETUP_API_KEY.md` for step-by-step instructions.

## Usage

### Quick Start

**Run the demo:**
```bash
python src/demo.py
```

**Run DSL examples:**
```bash
python src/run_dsl_examples.py
```

This runs 7 example DSL strategies and saves output to `dsl_examples_output.txt`.

### Programmatic Usage

#### 1. Parse Natural Language

```python
from src.nl_parser import parse_nl_to_json

nl_text = "Buy when close is above 20-day moving average and volume > 1M"
structured_json = parse_nl_to_json(nl_text)
print(structured_json)
```

#### 2. Generate DSL

```python
from src.dsl_generator import json_to_dsl

dsl_text = json_to_dsl(structured_json)
print(dsl_text)
```

#### 3. Parse DSL to AST

```python
from src.dsl_parser import parse_dsl_to_ast

ast = parse_dsl_to_ast(dsl_text)
print(ast)
```

#### 4. Generate Python Code

```python
from src.code_generator import generate_code_from_ast
import pandas as pd

evaluator = generate_code_from_ast(ast)
df = pd.read_csv("data/sample_data.csv", index_col='date', parse_dates=True)
signals = evaluator(df)
```

#### 5. Run Backtest

```python
from src.backtest import BacktestSimulator

simulator = BacktestSimulator(initial_capital=100000.0)
results = simulator.run(df, signals)

print(f"Total Return: {results.total_return_pct:.2f}%")
print(f"Number of Trades: {results.num_trades}")
print(f"Win Rate: {results.win_rate * 100:.2f}%")
```

### Generate Sample Data

Generate synthetic OHLCV data for testing:

```bash
python src/generate_sample_data.py
```

This creates `data/sample_data.csv` with 260 trading days of data.

## DSL Specification

The DSL supports:

- **Entry/Exit Rules**: Separate sections for entry and exit conditions
- **Boolean Logic**: AND/OR operators
- **Comparisons**: `>`, `<`, `>=`, `<=`, `==`, `!=`
- **Series**: `open`, `high`, `low`, `close`, `volume`
- **Indicators**: `sma(series, period)`, `rsi(series, period)`, `ema(series, period)`
- **Time Functions**: `yesterday(series)`, `last_week(series)`, `n_days_ago(series, n)`
- **Cross Functions**: `crosses_above(series1, series2)`, `crosses_below(series1, series2)`
- **Change Functions**: `change(series, n)`, `percent_change(series, n)`

### Example DSL

```
ENTRY:
close > sma(close, 20) AND volume > 1000000

EXIT:
rsi(close, 14) < 30
```

See `docs/dsl_specification.md` for complete documentation.

## Natural Language Examples

The system can parse various natural language patterns:

- "Buy when the close price is above the 20-day moving average and volume is above 1 million."
- "Enter when price crosses above yesterday's high."
- "Exit when RSI(14) is below 30."
- "Trigger entry when volume increases by more than 30 percent compared to last week."

## Backtest Metrics

The backtest simulator calculates:

- **Total Return**: Absolute and percentage return
- **Max Drawdown**: Maximum peak-to-trough decline
- **Number of Trades**: Total trades executed
- **Win Rate**: Percentage of profitable trades
- **Average Return**: Average return per trade
- **Sharpe Ratio**: Risk-adjusted return metric

## Testing

**Run DSL examples:**
```bash
python src/run_dsl_examples.py
```

**Run demo:**
```bash
python src/demo.py
```

**Test individual components:**
```python
from src.dsl_parser import parse_dsl_to_ast
from src.indicators import sma, rsi
import pandas as pd

# Test DSL parser
ast = parse_dsl_to_ast("ENTRY:\nclose > sma(close, 20)")

# Test indicators
df = pd.read_csv("data/sample_data.csv", index_col='date', parse_dates=True)
sma_values = sma(df['close'], 20)
rsi_values = rsi(df['close'], 14)
```

## Design Decisions

1. **Modular Architecture**: Each component (parser, generator, simulator) is separate for maintainability
2. **AST as Intermediate Representation**: Enables validation and easier code generation
3. **Pandas-based Execution**: Leverages vectorized operations for performance
4. **LLM for NL Parsing**: Uses GPT-4o-mini or Claude Haiku for cost-effective natural language understanding
5. **Lark for DSL Parsing**: Provides robust parsing with clear error messages
6. **Extensible Design**: Easy to add new indicators or DSL features

## Limitations

- Natural language parsing relies on LLM API (with basic fallback)
- DSL supports a limited set of indicators (SMA, RSI, EMA)
- Backtest simulator is simplified (no transaction costs, slippage, etc.)
- Time functions assume trading days (weekends/holidays excluded)

## Future Enhancements

- Support for more technical indicators (MACD, Bollinger Bands, etc.)
- More sophisticated backtesting (transaction costs, slippage, position sizing)
- Support for multiple timeframes
- Strategy optimization capabilities
- Real-time data integration
- More robust natural language parsing patterns

## Dependencies

- `pandas`: Data manipulation and analysis
- `lark`: DSL parsing
- `openai` or `anthropic`: LLM API client (optional)
- `python-dotenv`: Environment variable management
- `numpy`: Numerical operations

## License

This is a prototype implementation for evaluation purposes.

## Author

Created as a take-home assignment demonstrating NLP, DSL design, parsing, code generation, and backtesting capabilities.

## Railway Deployment

This project is designed to work with Railway deployment. Ensure:

1. Environment variables are set in Railway dashboard
2. `requirements.txt` includes all dependencies
3. Sample data is included or generated on first run
4. API keys are configured via Railway environment variables

For Railway deployment, the demo script can be run as a one-time job or integrated into a web service.

