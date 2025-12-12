# DSL Specification Document

## Overview

This document describes the Domain-Specific Language (DSL) for expressing trading strategy rules. The DSL is designed to be readable, unambiguous, and capable of expressing complex trading logic including entry/exit conditions, technical indicators, and time-based lookbacks.

## Grammar (EBNF Notation)

```
strategy     ::= entry_section exit_section?
entry_section ::= "ENTRY:" rule_list
exit_section  ::= "EXIT:" rule_list
rule_list     ::= rule (("AND" | "OR") rule)*
rule          ::= comparison | "(" rule_list ")"
comparison    ::= expression operator expression
operator      ::= ">" | "<" | ">=" | "<=" | "==" | "!="
expression    ::= series | indicator | function_call | number | percentage
series        ::= "open" | "high" | "low" | "close" | "volume"
indicator     ::= indicator_name "(" series ("," number)? ")"
indicator_name ::= "sma" | "rsi" | "ema"
function_call ::= time_function | cross_function | change_function
time_function ::= "yesterday" "(" series ")" 
                | "last_week" "(" series ")"
                | "n_days_ago" "(" series "," number ")"
cross_function ::= "crosses_above" "(" series "," expression ")"
                 | "crosses_below" "(" series "," expression ")"
change_function ::= "change" "(" series "," number ")" 
                  | "percent_change" "(" series "," number ")"
number        ::= [0-9]+ ("." [0-9]+)?
percentage    ::= number "%"
```

## Operators

### Comparison Operators
- `>` : Greater than
- `<` : Less than
- `>=` : Greater than or equal to
- `<=` : Less than or equal to
- `==` : Equal to
- `!=` : Not equal to

### Boolean Operators
- `AND` : Logical AND (both conditions must be true)
- `OR` : Logical OR (at least one condition must be true)

Boolean operators have left-to-right precedence. Parentheses can be used to override precedence.

## Series References

The following series are available:
- `open` : Opening price
- `high` : Highest price
- `low` : Lowest price
- `close` : Closing price
- `volume` : Trading volume

## Technical Indicators

### SMA (Simple Moving Average)
**Syntax:** `sma(series, period)`

**Description:** Calculates the simple moving average of a series over the specified period.

**Parameters:**
- `series`: The price series (e.g., `close`, `high`)
- `period`: Number of periods (integer, e.g., `20`)

**Example:** `sma(close, 20)` - 20-day moving average of closing prices

### RSI (Relative Strength Index)
**Syntax:** `rsi(series, period)`

**Description:** Calculates the Relative Strength Index over the specified period. Returns a value between 0 and 100.

**Parameters:**
- `series`: The price series (typically `close`)
- `period`: Number of periods (integer, typically `14`)

**Example:** `rsi(close, 14)` - 14-period RSI of closing prices

### EMA (Exponential Moving Average)
**Syntax:** `ema(series, period)`

**Description:** Calculates the exponential moving average of a series over the specified period.

**Parameters:**
- `series`: The price series
- `period`: Number of periods (integer)

**Example:** `ema(close, 20)` - 20-day exponential moving average

## Time-Based Functions

### yesterday
**Syntax:** `yesterday(series)`

**Description:** Returns the value of the series from the previous trading day.

**Example:** `yesterday(close)` - Yesterday's closing price

### last_week
**Syntax:** `last_week(series)`

**Description:** Returns the value of the series from 7 trading days ago.

**Example:** `last_week(volume)` - Volume from last week

### n_days_ago
**Syntax:** `n_days_ago(series, n)`

**Description:** Returns the value of the series from n trading days ago.

**Parameters:**
- `series`: The series to reference
- `n`: Number of days to look back (integer)

**Example:** `n_days_ago(high, 5)` - High price from 5 days ago

## Cross Functions

### crosses_above
**Syntax:** `crosses_above(series1, series2)`

**Description:** Returns true when series1 crosses above series2 (i.e., series1 was below series2 in the previous period and is now above).

**Example:** `crosses_above(close, sma(close, 20))` - Price crosses above 20-day moving average

### crosses_below
**Syntax:** `crosses_below(series1, series2)`

**Description:** Returns true when series1 crosses below series2 (i.e., series1 was above series2 in the previous period and is now below).

**Example:** `crosses_below(close, sma(close, 20))` - Price crosses below 20-day moving average

## Change Functions

### change
**Syntax:** `change(series, n)`

**Description:** Returns the absolute change in the series over n periods.

**Example:** `change(close, 1)` - Change in closing price from yesterday

### percent_change
**Syntax:** `percent_change(series, n)`

**Description:** Returns the percentage change in the series over n periods.

**Example:** `percent_change(volume, 7)` - Percentage change in volume over last week

## Entry and Exit Sections

A strategy consists of:
1. **ENTRY section**: Conditions that trigger a position entry (buy signal)
2. **EXIT section**: Conditions that trigger a position exit (sell signal)

Both sections are optional, but at least one must be present. Rules within each section are combined with AND/OR logic.

## Examples

### Example 1: Simple Moving Average Crossover
```
ENTRY:
close > sma(close, 20) AND volume > 1000000

EXIT:
rsi(close, 14) < 30
```

### Example 2: Price Cross Above Yesterday's High
```
ENTRY:
crosses_above(close, yesterday(high))

EXIT:
close < sma(close, 20)
```

### Example 3: Volume Increase Strategy
```
ENTRY:
volume > 1000000 AND percent_change(volume, 7) > 30

EXIT:
close < low
```

### Example 4: Complex Boolean Logic
```
ENTRY:
(close > sma(close, 20) OR close > ema(close, 50)) AND volume > 500000

EXIT:
rsi(close, 14) < 30 OR rsi(close, 14) > 70
```

### Example 5: Multiple Conditions
```
ENTRY:
close > sma(close, 20) AND volume > 1000000 AND rsi(close, 14) > 50

EXIT:
rsi(close, 14) < 30 OR close < sma(close, 20)
```

## Assumptions and Design Decisions

1. **Case Sensitivity**: The DSL is case-insensitive for keywords (ENTRY, EXIT, AND, OR) but case-sensitive for series names and function names.

2. **Whitespace**: Whitespace is generally ignored except where it separates tokens.

3. **Number Format**: Numbers can be integers or decimals. Large numbers can be written with commas for readability (e.g., `1,000,000`), but commas are stripped during parsing.

4. **Precedence**: Boolean operators have equal precedence and are evaluated left-to-right. Parentheses must be used to override this.

5. **Indicator Defaults**: Some indicators have default periods if not specified:
   - RSI defaults to 14 periods
   - SMA defaults to 20 periods (if needed)

6. **Time Functions**: Time-based functions assume trading days, not calendar days. Weekends and holidays are skipped.

7. **Cross Detection**: Cross functions require at least 2 periods of data to detect a crossover (current and previous period).

8. **Validation**: The parser validates:
   - Series names must be one of: open, high, low, close, volume
   - Indicator names must be recognized
   - Function parameters must match expected types
   - Numbers must be valid numeric values

## Error Handling

The parser will raise informative errors for:
- Invalid syntax
- Unknown series or indicator names
- Mismatched parentheses
- Invalid operator usage
- Missing required parameters

Error messages include line numbers and context where possible.

