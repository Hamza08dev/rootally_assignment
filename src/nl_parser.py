"""
Natural Language Parser - Converts natural language trading rules to structured JSON.
"""

import json
import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class NLParser:
    """Parser that converts natural language trading rules to structured JSON."""
    
    def __init__(self, provider: str = "gemini"):
        """
        Initialize the NL parser.
        
        Args:
            provider: LLM provider ("openai", "anthropic", or "gemini")
        """
        self.provider = provider.lower()
        self.api_key = None
        self._setup_api()
    
    def _setup_api(self):
        """Setup API client based on provider."""
        if self.provider == "openai":
            try:
                import openai
                self.api_key = os.getenv("OPENAI_API_KEY")
                if not self.api_key:
                    raise ValueError("OPENAI_API_KEY not found in environment variables")
                self.client = openai.OpenAI(api_key=self.api_key)
                self._call_llm = self._call_openai
            except ImportError:
                raise ImportError("openai package not installed. Install with: pip install openai")
        elif self.provider == "anthropic":
            try:
                import anthropic
                self.api_key = os.getenv("ANTHROPIC_API_KEY")
                if not self.api_key:
                    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
                self.client = anthropic.Anthropic(api_key=self.api_key)
                self._call_llm = self._call_anthropic
            except ImportError:
                raise ImportError("anthropic package not installed. Install with: pip install anthropic")
        elif self.provider == "gemini":
            try:
                import google.generativeai as genai
                self.api_key = os.getenv("GEMINI_API_KEY")
                if not self.api_key:
                    raise ValueError("GEMINI_API_KEY not found in environment variables")
                genai.configure(api_key=self.api_key)
                self.client = genai
                # Default to gemini-2.5-flash, fallback to gemini-2.0-flash-exp if not available
                self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
                self._call_llm = self._call_gemini
            except ImportError:
                raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}. Supported: openai, anthropic, gemini")
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # Using mini for cost efficiency
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API."""
        response = self.client.messages.create(
            model="claude-3-haiku-20240307",  # Using haiku for cost efficiency
            max_tokens=1024,
            system=self._get_system_prompt(),
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API."""
        # Combine system prompt and user prompt
        full_prompt = f"{self._get_system_prompt()}\n\nUser input: {prompt}\n\nPlease respond with valid JSON only."
        
        try:
            model = self.client.GenerativeModel(self.model_name)
            
            # Try with JSON response format (supported in newer API versions)
            try:
                generation_config = self.client.types.GenerationConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                )
                response = model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
            except (AttributeError, TypeError):
                # Fallback if response_mime_type not supported in this version
                response = model.generate_content(
                    full_prompt,
                    generation_config={"temperature": 0.1}
                )
            
            return response.text
        except Exception as e:
            raise ValueError(f"Error calling Gemini API: {e}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for LLM."""
        return """You are a trading strategy parser that converts natural language trading rules into structured JSON format.

Convert the user's natural language trading instructions into a JSON object with the following structure:

{
  "entry": [
    {
      "left": "close",
      "operator": ">",
      "right": "sma(close,20)"
    }
  ],
  "exit": [
    {
      "left": "rsi(close,14)",
      "operator": "<",
      "right": 30
    }
  ]
}

Rules:
- "entry" and "exit" are arrays of condition objects
- Each condition has "left", "operator", and "right" fields
- Operators: ">", "<", ">=", "<=", "==", "!="
- Series: "open", "high", "low", "close", "volume"
- Indicators: "sma(series,period)", "rsi(series,period)", "ema(series,period)"
- Time functions: "yesterday(series)", "last_week(series)", "n_days_ago(series,n)"
- Cross functions: "crosses_above(series1,series2)", "crosses_below(series1,series2)"
- Change functions: "change(series,n)", "percent_change(series,n)"
- Numbers can be integers or floats
- Percentages should be converted to numbers (e.g., "30 percent" -> 30)
- Boolean logic: Multiple conditions in entry/exit arrays are combined with AND by default
- For OR logic, use separate condition objects and mark them appropriately

Examples:
- "Buy when close is above 20-day moving average" -> {"left": "close", "operator": ">", "right": "sma(close,20)"}
- "Exit when RSI(14) is below 30" -> {"left": "rsi(close,14)", "operator": "<", "right": 30}
- "Enter when price crosses above yesterday's high" -> {"left": "close", "operator": "crosses_above", "right": "yesterday(high)"}
- "Volume increases by more than 30 percent" -> {"left": "volume", "operator": ">", "right": "percent_change(volume,7) + 30"}

Always return valid JSON only, no additional text."""
    
    def parse(self, nl_text: str) -> Dict[str, Any]:
        """
        Parse natural language text into structured JSON.
        
        Args:
            nl_text: Natural language trading rule description
            
        Returns:
            Dictionary with "entry" and/or "exit" keys containing condition arrays
        """
        try:
            response = self._call_llm(nl_text)
            result = json.loads(response)
            
            # Validate structure
            if not isinstance(result, dict):
                raise ValueError("LLM response is not a dictionary")
            
            # Ensure entry and exit are lists
            if "entry" in result and not isinstance(result["entry"], list):
                result["entry"] = [result["entry"]] if result["entry"] else []
            if "exit" in result and not isinstance(result["exit"], list):
                result["exit"] = [result["exit"]] if result["exit"] else []
            
            # Ensure at least one section exists
            if "entry" not in result and "exit" not in result:
                raise ValueError("Response must contain at least 'entry' or 'exit'")
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing natural language: {e}")
    
    def parse_with_fallback(self, nl_text: str) -> Dict[str, Any]:
        """
        Parse with regex fallback if LLM fails.
        This is a simplified fallback for common patterns.
        
        Args:
            nl_text: Natural language trading rule description
            
        Returns:
            Dictionary with structured rules
        """
        try:
            return self.parse(nl_text)
        except Exception:
            # Fallback to simple regex-based parsing for common patterns
            return self._regex_fallback(nl_text)
    
    def _regex_fallback(self, text: str) -> Dict[str, Any]:
        """
        Simple regex-based fallback parser for common patterns.
        This handles basic cases when LLM is unavailable.
        """
        import re
        
        result = {"entry": [], "exit": []}
        text_lower = text.lower()
        
        # Detect entry/exit keywords
        entry_patterns = [
            (r"buy when (.+)", "entry"),
            (r"enter when (.+)", "entry"),
            (r"entry when (.+)", "entry"),
        ]
        
        exit_patterns = [
            (r"exit when (.+)", "exit"),
            (r"sell when (.+)", "exit"),
        ]
        
        # Simple pattern matching for common cases
        # This is a basic fallback - LLM is preferred
        
        # Example: "close > sma(close,20)"
        if "above" in text_lower and "moving average" in text_lower:
            # Extract period
            period_match = re.search(r'(\d+)[-\s]*day', text_lower)
            period = int(period_match.group(1)) if period_match else 20
            
            result["entry"].append({
                "left": "close",
                "operator": ">",
                "right": f"sma(close,{period})"
            })
        
        # Example: "RSI < 30"
        if "rsi" in text_lower:
            rsi_match = re.search(r'rsi[^\d]*(\d+)', text_lower)
            period = int(rsi_match.group(1)) if rsi_match else 14
            
            value_match = re.search(r'(?:below|under|less than|<\s*)(\d+)', text_lower)
            value = int(value_match.group(1)) if value_match else 30
            
            result["exit"].append({
                "left": f"rsi(close,{period})",
                "operator": "<",
                "right": value
            })
        
        # If no patterns matched, return empty structure
        if not result["entry"] and not result["exit"]:
            raise ValueError("Could not parse natural language with fallback parser")
        
        return result


def parse_nl_to_json(nl_text: str, provider: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to parse natural language to JSON.
    
    Args:
        nl_text: Natural language trading rule
        provider: LLM provider ("openai", "anthropic", or "gemini"), defaults to env var
        
    Returns:
        Structured JSON dictionary
    """
    if provider is None:
        provider = os.getenv("LLM_PROVIDER", "gemini")
    
    parser = NLParser(provider=provider)
    return parser.parse(nl_text)

