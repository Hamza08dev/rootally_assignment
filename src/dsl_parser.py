"""
DSL Parser - Parses DSL text into Abstract Syntax Tree (AST) using Lark.
"""

from typing import Dict, List, Any, Union, Optional
from lark import Lark, Transformer, Tree, Token
from lark.exceptions import LarkError


# Lark grammar definition
DSL_GRAMMAR = """
start: strategy

strategy: entry_section exit_section?
        | exit_section

entry_section: "ENTRY" ":" rule_list
exit_section: "EXIT" ":" rule_list

rule_list: rule (boolean_op rule)*
rule: comparison | "(" rule_list ")"

comparison: expression operator expression

operator: ">" | "<" | ">=" | "<=" | "==" | "!=" | "crosses_above" | "crosses_below"

boolean_op: "AND" | "OR"

expression: series
          | indicator
          | function_call
          | number
          | percentage
          | "(" expression ")"

series: SERIES_NAME
SERIES_NAME: "open" | "high" | "low" | "close" | "volume"

indicator: indicator_name "(" expression ("," number)? ")"

indicator_name: INDICATOR_NAME_TOKEN
INDICATOR_NAME_TOKEN: "sma" | "rsi" | "ema"

function_call: time_function
             | cross_function
             | change_function

time_function: "yesterday" "(" series ")"
             | "last_week" "(" series ")"
             | "n_days_ago" "(" series "," number ")"

cross_function: "crosses_above" "(" expression "," expression ")"
              | "crosses_below" "(" expression "," expression ")"

change_function: "change" "(" series "," number ")"
               | "percent_change" "(" series "," number ")"

number: SIGNED_NUMBER
percentage: SIGNED_NUMBER "%"

%import common.SIGNED_NUMBER
%import common.WS
%ignore WS
"""


class DSLTransformer(Transformer):
    """Transform Lark parse tree into AST structure."""
    
    def start(self, items):
        """Root node."""
        result = {}
        for item in items:
            if isinstance(item, dict):
                result.update(item)
        return result
    
    def strategy(self, items):
        """Strategy node."""
        result = {}
        for item in items:
            if isinstance(item, dict):
                result.update(item)
        return result
    
    def entry_section(self, items):
        """Entry section."""
        return {"entry": items[0]}
    
    def exit_section(self, items):
        """Exit section."""
        return {"exit": items[0]}
    
    def rule_list(self, items):
        """Rule list - combine rules with boolean operators."""
        if len(items) == 1:
            return items[0]
        
        # Build a tree of boolean operations
        result = items[0]
        for i in range(1, len(items), 2):
            if i + 1 < len(items):
                op = items[i]
                right = items[i + 1]
                result = {
                    "type": "boolean_op",
                    "operator": op,
                    "left": result,
                    "right": right
                }
        return result
    
    def rule(self, items):
        """Single rule."""
        return items[0]
    
    def comparison(self, items):
        """Comparison operation."""
        left, op, right = items
        return {
            "type": "binary_op",
            "operator": op,
            "left": left,
            "right": right
        }
    
    def operator(self, items):
        """Operator token."""
        if not items or len(items) == 0:
            # This shouldn't happen, but handle gracefully
            return ">"
        return str(items[0])
    
    def boolean_op(self, items):
        """Boolean operator."""
        if not items or len(items) == 0:
            return "AND"
        return str(items[0]).upper()
    
    def expression(self, items):
        """Expression."""
        return items[0]
    
    def series(self, items):
        """Series reference."""
        if not items or len(items) == 0:
            raise ValueError("Series rule matched but no items found")
        # Handle both token and string inputs
        value = items[0] if isinstance(items[0], str) else str(items[0])
        return {
            "type": "series",
            "value": value
        }
    
    def indicator(self, items):
        """Indicator call."""
        name = str(items[0])
        expr_node = items[1]
        period = items[2] if len(items) > 2 else None
        
        # Default periods
        if period is None:
            if name == "rsi":
                period = 14
            elif name == "sma":
                period = 20
            elif name == "ema":
                period = 20
        
        # Extract series value from expression node
        if isinstance(expr_node, dict):
            if expr_node.get("type") == "series":
                series_value = expr_node.get("value")
            else:
                series_value = str(expr_node)
        else:
            series_value = str(expr_node)
        
        return {
            "type": "indicator",
            "name": name,
            "series": series_value,
            "period": period
        }
    
    def indicator_name(self, items):
        """Indicator name."""
        if not items or len(items) == 0:
            raise ValueError("Indicator name rule matched but no items found")
        return str(items[0])
    
    def function_call(self, items):
        """Function call."""
        return items[0]
    
    def time_function(self, items):
        """Time-based function."""
        func_name = items[0]
        series_node = items[1]
        series_value = series_node.get("value") if isinstance(series_node, dict) else str(series_node)
        
        if func_name == "yesterday":
            return {
                "type": "function_call",
                "name": "yesterday",
                "args": [{"type": "series", "value": series_value}]
            }
        elif func_name == "last_week":
            return {
                "type": "function_call",
                "name": "last_week",
                "args": [{"type": "series", "value": series_value}]
            }
        elif func_name == "n_days_ago":
            n = items[2] if len(items) > 2 else 1
            return {
                "type": "function_call",
                "name": "n_days_ago",
                "args": [
                    {"type": "series", "value": series_value},
                    n
                ]
            }
    
    def cross_function(self, items):
        """Cross function."""
        func_name = str(items[0])
        left_expr = items[1]
        right_expr = items[2]
        
        return {
            "type": "function_call",
            "name": func_name,
            "args": [left_expr, right_expr]
        }
    
    def change_function(self, items):
        """Change function."""
        func_name = str(items[0])
        series_node = items[1]
        n = items[2] if len(items) > 2 else 1
        series_value = series_node.get("value") if isinstance(series_node, dict) else str(series_node)
        
        return {
            "type": "function_call",
            "name": func_name,
            "args": [
                {"type": "series", "value": series_value},
                n
            ]
        }
    
    def number(self, items):
        """Number literal."""
        value = float(items[0])
        # Return as int if it's a whole number
        return int(value) if value.is_integer() else value
    
    def percentage(self, items):
        """Percentage literal."""
        return float(items[0])


class DSLParser:
    """Parser for DSL text into AST."""
    
    def __init__(self):
        """Initialize the parser."""
        self.parser = Lark(DSL_GRAMMAR, start='start', parser='lalr', transformer=DSLTransformer())
    
    def parse(self, dsl_text: str) -> Dict[str, Any]:
        """
        Parse DSL text into AST.
        
        Args:
            dsl_text: DSL text string
            
        Returns:
            AST dictionary with "entry" and/or "exit" keys
            
        Raises:
            ValueError: If parsing fails
        """
        try:
            # Clean up the input
            dsl_text = dsl_text.strip()
            
            # Parse
            result = self.parser.parse(dsl_text)
            
            # Ensure entry and exit are lists
            if isinstance(result, dict):
                if "entry" in result and not isinstance(result["entry"], list):
                    result["entry"] = [result["entry"]] if result["entry"] else []
                if "exit" in result and not isinstance(result["exit"], list):
                    result["exit"] = [result["exit"]] if result["exit"] else []
            
            return result
            
        except LarkError as e:
            raise ValueError(f"DSL parsing error: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing DSL: {e}")
    
    def validate(self, dsl_text: str) -> bool:
        """
        Validate DSL syntax without building full AST.
        
        Args:
            dsl_text: DSL text to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            self.parse(dsl_text)
            return True
        except ValueError:
            return False


def parse_dsl_to_ast(dsl_text: str) -> Dict[str, Any]:
    """
    Convenience function to parse DSL to AST.
    
    Args:
        dsl_text: DSL text string
        
    Returns:
        AST dictionary
    """
    parser = DSLParser()
    return parser.parse(dsl_text)

