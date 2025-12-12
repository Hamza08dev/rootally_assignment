"""
DSL Generator - Converts structured JSON to DSL text format.
"""

from typing import Dict, List, Any, Optional


class DSLGenerator:
    """Generator that converts structured JSON to DSL text."""
    
    def __init__(self):
        """Initialize the DSL generator."""
        pass
    
    def generate(self, structured_json: Dict[str, Any]) -> str:
        """
        Generate DSL text from structured JSON.
        
        Args:
            structured_json: Dictionary with "entry" and/or "exit" keys
            
        Returns:
            DSL text string
        """
        lines = []
        
        # Generate entry section
        if "entry" in structured_json and structured_json["entry"]:
            lines.append("ENTRY:")
            entry_dsl = self._generate_rule_list(structured_json["entry"])
            lines.append(entry_dsl)
            lines.append("")  # Empty line between sections
        
        # Generate exit section
        if "exit" in structured_json and structured_json["exit"]:
            lines.append("EXIT:")
            exit_dsl = self._generate_rule_list(structured_json["exit"])
            lines.append(exit_dsl)
        
        return "\n".join(lines).strip()
    
    def _generate_rule_list(self, rules: List[Dict[str, Any]], use_and: bool = True) -> str:
        """
        Generate DSL for a list of rules.
        
        Args:
            rules: List of rule dictionaries
            use_and: Whether to combine with AND (True) or OR (False)
            
        Returns:
            DSL text for the rule list
        """
        if not rules:
            return ""
        
        if len(rules) == 1:
            return self._generate_rule(rules[0])
        
        # Combine multiple rules
        operator = " AND " if use_and else " OR "
        rule_strings = [self._generate_rule(rule) for rule in rules]
        return operator.join(f"({s})" if " AND " in s or " OR " in s else s for s in rule_strings)
    
    def _generate_rule(self, rule: Dict[str, Any]) -> str:
        """
        Generate DSL for a single rule.
        
        Args:
            rule: Rule dictionary with "left", "operator", "right" keys
            
        Returns:
            DSL text for the rule
        """
        left = self._generate_expression(rule.get("left", ""))
        operator = rule.get("operator", ">")
        right = self._generate_expression(rule.get("right", ""))
        
        # Handle special operators
        if operator == "crosses_above":
            return f"crosses_above({left}, {right})"
        elif operator == "crosses_below":
            return f"crosses_below({left}, {right})"
        else:
            return f"{left} {operator} {right}"
    
    def _generate_expression(self, expr: Any) -> str:
        """
        Generate DSL for an expression (left or right side of comparison).
        
        Args:
            expr: Expression value (string, number, or dict)
            
        Returns:
            DSL text representation
        """
        if isinstance(expr, (int, float)):
            return str(expr)
        elif isinstance(expr, str):
            # Check if it's already a function call
            if "(" in expr and ")" in expr:
                return expr
            # Otherwise it's a series name
            return expr
        elif isinstance(expr, dict):
            # Handle nested expressions
            if "type" in expr:
                return self._generate_ast_node(expr)
            else:
                # Treat as a rule
                return f"({self._generate_rule(expr)})"
        else:
            return str(expr)
    
    def _generate_ast_node(self, node: Dict[str, Any]) -> str:
        """
        Generate DSL from an AST node (for advanced cases).
        
        Args:
            node: AST node dictionary
            
        Returns:
            DSL text
        """
        node_type = node.get("type", "")
        
        if node_type == "series":
            return node.get("value", "")
        elif node_type == "indicator":
            name = node.get("name", "")
            params = node.get("params", [])
            params_str = ", ".join(str(p) for p in params)
            return f"{name}({params_str})"
        elif node_type == "function_call":
            name = node.get("name", "")
            args = node.get("args", [])
            args_str = ", ".join(self._generate_expression(a) for a in args)
            return f"{name}({args_str})"
        elif node_type == "binary_op":
            left = self._generate_ast_node(node.get("left", {}))
            op = node.get("op", ">")
            right = self._generate_ast_node(node.get("right", {}))
            return f"{left} {op} {right}"
        else:
            return str(node)


def json_to_dsl(structured_json: Dict[str, Any]) -> str:
    """
    Convenience function to convert structured JSON to DSL.
    
    Args:
        structured_json: Dictionary with "entry" and/or "exit" keys
        
    Returns:
        DSL text string
    """
    generator = DSLGenerator()
    return generator.generate(structured_json)

