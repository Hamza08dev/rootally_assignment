"""
Code Generator - Converts AST to executable Python code.
"""

import sys
from pathlib import Path

# Add parent directory to path to allow imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from typing import Dict, List, Any, Callable
import pandas as pd
from src.indicators import (
    sma, rsi, ema,
    yesterday, last_week, n_days_ago,
    change, percent_change,
    crosses_above, crosses_below
)


class CodeGenerator:
    """Generator that converts AST to Python evaluation functions."""
    
    def __init__(self):
        """Initialize the code generator."""
        self.indicator_functions = {
            "sma": sma,
            "rsi": rsi,
            "ema": ema,
        }
        
        self.time_functions = {
            "yesterday": yesterday,
            "last_week": last_week,
            "n_days_ago": n_days_ago,
        }
        
        self.change_functions = {
            "change": change,
            "percent_change": percent_change,
        }
        
        self.cross_functions = {
            "crosses_above": crosses_above,
            "crosses_below": crosses_below,
        }
    
    def generate(self, ast: Dict[str, Any]) -> Callable:
        """
        Generate a Python function from AST that evaluates entry/exit conditions.
        
        Args:
            ast: AST dictionary with "entry" and/or "exit" keys
            
        Returns:
            Function that takes a DataFrame and returns signals DataFrame
        """
        def evaluate_strategy(df: pd.DataFrame) -> pd.DataFrame:
            """
            Evaluate strategy rules on a DataFrame.
            
            Args:
                df: DataFrame with OHLCV columns (open, high, low, close, volume)
                
            Returns:
                DataFrame with 'entry' and 'exit' boolean columns
            """
            signals = pd.DataFrame(index=df.index)
            signals['entry'] = False
            signals['exit'] = False
            
            # Evaluate entry conditions
            if "entry" in ast and ast["entry"]:
                entry_conditions = ast["entry"]
                if not isinstance(entry_conditions, list):
                    entry_conditions = [entry_conditions]
                
                entry_signals = None
                for condition in entry_conditions:
                    condition_result = self._evaluate_expression(condition, df)
                    if entry_signals is None:
                        entry_signals = condition_result
                    else:
                        # Combine with AND (default)
                        entry_signals = entry_signals & condition_result
                
                signals['entry'] = entry_signals.fillna(False)
            
            # Evaluate exit conditions
            if "exit" in ast and ast["exit"]:
                exit_conditions = ast["exit"]
                if not isinstance(exit_conditions, list):
                    exit_conditions = [exit_conditions]
                
                exit_signals = None
                for condition in exit_conditions:
                    condition_result = self._evaluate_expression(condition, df)
                    if exit_signals is None:
                        exit_signals = condition_result
                    else:
                        # Combine with AND (default)
                        exit_signals = exit_signals & condition_result
                
                signals['exit'] = exit_signals.fillna(False)
            
            return signals
        
        return evaluate_strategy
    
    def _evaluate_expression(self, expr: Any, df: pd.DataFrame) -> pd.Series:
        """
        Evaluate an AST expression node.
        
        Args:
            expr: AST node or value
            df: DataFrame with OHLCV data
            
        Returns:
            Series with boolean or numeric values
        """
        if isinstance(expr, dict):
            expr_type = expr.get("type", "")
            
            if expr_type == "series":
                series_name = expr.get("value", "")
                if series_name not in df.columns:
                    raise ValueError(f"Series '{series_name}' not found in DataFrame")
                return df[series_name]
            
            elif expr_type == "indicator":
                return self._evaluate_indicator(expr, df)
            
            elif expr_type == "function_call":
                return self._evaluate_function_call(expr, df)
            
            elif expr_type == "binary_op":
                return self._evaluate_binary_op(expr, df)
            
            elif expr_type == "boolean_op":
                return self._evaluate_boolean_op(expr, df)
            
            else:
                raise ValueError(f"Unknown expression type: {expr_type}")
        
        elif isinstance(expr, (int, float)):
            return pd.Series(expr, index=df.index)
        
        elif isinstance(expr, str):
            # Try as series name
            if expr in df.columns:
                return df[expr]
            # Otherwise treat as literal
            try:
                return pd.Series(float(expr), index=df.index)
            except ValueError:
                raise ValueError(f"Cannot evaluate expression: {expr}")
        
        else:
            raise ValueError(f"Unexpected expression type: {type(expr)}")
    
    def _evaluate_indicator(self, node: Dict[str, Any], df: pd.DataFrame) -> pd.Series:
        """Evaluate an indicator node."""
        name = node.get("name", "")
        series_name = node.get("series", "close")
        period = node.get("period", 20)
        
        if series_name not in df.columns:
            raise ValueError(f"Series '{series_name}' not found in DataFrame")
        
        series = df[series_name]
        
        if name not in self.indicator_functions:
            raise ValueError(f"Unknown indicator: {name}")
        
        func = self.indicator_functions[name]
        return func(series, period)
    
    def _evaluate_function_call(self, node: Dict[str, Any], df: pd.DataFrame) -> pd.Series:
        """Evaluate a function call node."""
        name = node.get("name", "")
        args = node.get("args", [])
        
        # Time functions
        if name in self.time_functions:
            if len(args) < 1:
                raise ValueError(f"Function '{name}' requires at least 1 argument")
            
            series_node = args[0]
            series = self._evaluate_expression(series_node, df)
            
            if name == "yesterday":
                return self.time_functions[name](series)
            elif name == "last_week":
                return self.time_functions[name](series)
            elif name == "n_days_ago":
                n = args[1] if len(args) > 1 else 1
                return self.time_functions[name](series, n)
        
        # Change functions
        elif name in self.change_functions:
            if len(args) < 1:
                raise ValueError(f"Function '{name}' requires at least 1 argument")
            
            series_node = args[0]
            series = self._evaluate_expression(series_node, df)
            n = args[1] if len(args) > 1 else 1
            
            return self.change_functions[name](series, n)
        
        # Cross functions
        elif name in self.cross_functions:
            if len(args) < 2:
                raise ValueError(f"Function '{name}' requires 2 arguments")
            
            left_expr = self._evaluate_expression(args[0], df)
            right_expr = self._evaluate_expression(args[1], df)
            
            return self.cross_functions[name](left_expr, right_expr)
        
        else:
            raise ValueError(f"Unknown function: {name}")
    
    def _evaluate_binary_op(self, node: Dict[str, Any], df: pd.DataFrame) -> pd.Series:
        """Evaluate a binary operation node."""
        operator = node.get("operator", ">")
        left = self._evaluate_expression(node.get("left"), df)
        right = self._evaluate_expression(node.get("right"), df)
        
        # Handle cross operators specially
        if operator == "crosses_above":
            return crosses_above(left, right)
        elif operator == "crosses_below":
            return crosses_below(left, right)
        
        # Standard comparison operators
        if operator == ">":
            return left > right
        elif operator == "<":
            return left < right
        elif operator == ">=":
            return left >= right
        elif operator == "<=":
            return left <= right
        elif operator == "==":
            return left == right
        elif operator == "!=":
            return left != right
        else:
            raise ValueError(f"Unknown operator: {operator}")
    
    def _evaluate_boolean_op(self, node: Dict[str, Any], df: pd.DataFrame) -> pd.Series:
        """Evaluate a boolean operation node."""
        operator = node.get("operator", "AND")
        left = self._evaluate_expression(node.get("left"), df)
        right = self._evaluate_expression(node.get("right"), df)
        
        if operator == "AND":
            return left & right
        elif operator == "OR":
            return left | right
        else:
            raise ValueError(f"Unknown boolean operator: {operator}")


def generate_code_from_ast(ast: Dict[str, Any]) -> Callable:
    """
    Convenience function to generate Python code from AST.
    
    Args:
        ast: AST dictionary
        
    Returns:
        Evaluation function
    """
    generator = CodeGenerator()
    return generator.generate(ast)

