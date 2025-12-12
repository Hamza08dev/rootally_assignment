# DSL Grammar Specification

## Overview

This Domain-Specific Language (DSL) is designed for expressing trading strategy entry and exit conditions. The DSL provides a concise, readable syntax for defining technical analysis rules.

## Grammar Structure

### Strategy Definition

A strategy consists of one or both sections:
- **ENTRY**: Conditions that trigger a buy signal
- **EXIT**: Conditions that trigger a sell signal

```
strategy: entry_section exit_section?
        | exit_section
```

### Entry/Exit Sections

Each section contains a list of rules combined with boolean operators:

```
entry_section: "ENTRY" ":" rule_list
exit_section: "EXIT" ":" rule_list
```

### Rules and Boolean Logic

Rules can be combined using `AND` or `OR` operators. Parentheses can be used for grouping:

```
rule_list: rule (boolean_op rule)*
rule: comparison | "(" rule_list ")"
boolean_op: "AND" | "OR"
```

### Comparisons

Comparisons use standard relational operators:

```
comparison: expression operator expression
operator: ">" | "<" | ">=" | "<=" | "==" | "!=" | "crosses_above" | "crosses_below"
```

### Expressions

Expressions can be:
- **Series**: Price/volume data (`open`, `high`, `low`, `close`, `volume`)
- **Indicators**: Technical indicators (`sma`, `rsi`, `ema`)
- **Function Calls**: Time functions, cross functions, change functions
- **Numbers**: Numeric literals
- **Percentages**: Percentage literals (e.g., `5%`)

```
expression: series
          | indicator
          | function_call
          | number
          | percentage
          | "(" expression ")"
```

### Series

Price and volume data series:

```
series: SERIES_NAME
SERIES_NAME: "open" | "high" | "low" | "close" | "volume"
```

### Indicators

Technical indicators with optional period parameter:

```
indicator: indicator_name "(" expression ("," number)? ")"
indicator_name: "sma" | "rsi" | "ema"
```

Default periods:
- `rsi`: 14
- `sma`: 20
- `ema`: 20

### Time Functions

Access historical values:

```
time_function: "yesterday" "(" series ")"
             | "last_week" "(" series ")"
             | "n_days_ago" "(" series "," number ")"
```

### Cross Functions

Detect when one series crosses above or below another:

```
cross_function: "crosses_above" "(" expression "," expression ")"
              | "crosses_below" "(" expression "," expression ")"
```

### Change Functions

Calculate price changes:

```
change_function: "change" "(" series "," number ")"
               | "percent_change" "(" series "," number ")"
```

## Examples

### Example 1: Simple Moving Average Crossover

**Entry**: When close price crosses above 20-day SMA  
**Exit**: When close price crosses below 20-day SMA

```
ENTRY:
close crosses_above sma(close, 20)

EXIT:
close crosses_below sma(close, 20)
```

### Example 2: RSI Oversold Entry with Volume Filter

**Entry**: RSI below 30 AND volume above 1 million  
**Exit**: RSI above 70

```
ENTRY:
rsi(close, 14) < 30 AND volume > 1000000

EXIT:
rsi(close, 14) > 70
```

### Example 3: Price Above Moving Average with Volume Confirmation

**Entry**: Close above 50-day SMA AND volume greater than yesterday's volume  
**Exit**: Close below 50-day SMA

```
ENTRY:
close > sma(close, 50) AND volume > yesterday(volume)

EXIT:
close < sma(close, 50)
```

### Example 4: Multiple Conditions with OR Logic

**Entry**: Either RSI below 30 OR price crosses above yesterday's high  
**Exit**: RSI above 70 OR price crosses below yesterday's low

```
ENTRY:
rsi(close, 14) < 30 OR close crosses_above yesterday(high)

EXIT:
rsi(close, 14) > 70 OR close crosses_below yesterday(low)
```

### Example 5: Percentage Change Strategy

**Entry**: Close price increased by more than 5% compared to 5 days ago  
**Exit**: Close price decreased by more than 3% compared to 3 days ago

```
ENTRY:
percent_change(close, 5) > 5

EXIT:
percent_change(close, 3) < -3
```

### Example 6: Complex Multi-Condition Entry

**Entry**: Close above EMA(20) AND volume above 1M AND RSI between 50-70  
**Exit**: Close below EMA(20) OR RSI above 80

```
ENTRY:
close > ema(close, 20) AND volume > 1000000 AND rsi(close, 14) > 50 AND rsi(close, 14) < 70

EXIT:
close < ema(close, 20) OR rsi(close, 14) > 80
```

### Example 7: Price Breakout with Volume Spike

**Entry**: Close above last week's high AND volume is 50% higher than last week's average  
**Exit**: Close below last week's low

```
ENTRY:
close > last_week(high) AND volume > (last_week(volume) * 1.5)

EXIT:
close < last_week(low)
```

## Syntax Notes

1. **Whitespace**: Whitespace is ignored between tokens
2. **Case Sensitivity**: Keywords (`ENTRY`, `EXIT`, `AND`, `OR`) are case-sensitive
3. **Operator Precedence**: Use parentheses to control evaluation order
4. **Default Periods**: Indicator periods can be omitted to use defaults
5. **Numeric Literals**: Supports integers and floating-point numbers
6. **Percentages**: Use `%` suffix for percentage values (e.g., `5%`)

## Operator Reference

| Operator | Description | Example |
|----------|-------------|---------|
| `>` | Greater than | `close > 100` |
| `<` | Less than | `rsi(close) < 30` |
| `>=` | Greater than or equal | `volume >= 1000000` |
| `<=` | Less than or equal | `close <= sma(close, 20)` |
| `==` | Equal to | `close == 100` |
| `!=` | Not equal to | `volume != 0` |
| `crosses_above` | Crosses above | `close crosses_above sma(close, 20)` |
| `crosses_below` | Crosses below | `close crosses_below sma(close, 20)` |

## Function Reference

### Time Functions
- `yesterday(series)`: Value from previous trading day
- `last_week(series)`: Value from same day last week
- `n_days_ago(series, n)`: Value from n days ago

### Cross Functions
- `crosses_above(expr1, expr2)`: True when expr1 crosses above expr2
- `crosses_below(expr1, expr2)`: True when expr1 crosses below expr2

### Change Functions
- `change(series, n)`: Absolute change over n periods
- `percent_change(series, n)`: Percentage change over n periods

### Indicators
- `sma(series, period)`: Simple Moving Average
- `ema(series, period)`: Exponential Moving Average
- `rsi(series, period)`: Relative Strength Index

