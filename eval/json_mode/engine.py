import json
from typing import Dict, Any, List, Callable

from eval.schemas import FunctionResults
from eval.pythonic.engine import execute_python_code, import_functions
from eval.util import setup_logger

logger = setup_logger(__name__)

def parse_json_completion(completion: str) -> List[Dict[str, Any]]:
    """Parse the completion string to extract JSON array of function calls."""
    try:
        # Remove ```json and ``` if present
        clean_completion = completion
        if "```json" in completion:
            start = completion.find("```json") + 7
            end = completion.rfind("```")
            clean_completion = completion[start:end].strip()

        # Try to parse the cleaned completion as JSON array
        return json.loads(clean_completion)
    except json.JSONDecodeError:
        # If that fails, try to find JSON array within the completion
        try:
            start = completion.find('[')
            end = completion.rfind(']') + 1
            if start >= 0 and end > start:
                json_str = completion[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            raise ValueError("Could not parse JSON array from completion")

def execute_json_function_calls(
    function_calls: List[Dict[str, Any]],
    functions: List[Callable]
) -> FunctionResults:
    """
    Execute function calls specified in JSON format using mock functions.
    
    Args:
        function_calls: List of dictionaries containing function calls and their arguments
        functions: List of function implementations
        
    Returns:
        FunctionResults containing execution results
    """
    python_code = []
    
    for call_dict in function_calls:
        # Handle each function call in the dictionary
        for func_name, params in call_dict.items():
            # Build argument string from the params dictionary
            arg_parts = []
            
            # Handle text parameter as a string
            for param_name, param_value in params.items():
                if isinstance(param_value, str):
                    arg_parts.append(f"{param_name}='{param_value}'")
                else:
                    arg_parts.append(f"{param_name}={repr(param_value)}")
            
            arg_string = ', '.join(arg_parts)
            python_code.append(f"{func_name}({arg_string})")
    
    # Join all function calls with newlines
    final_code = '\n'.join(python_code)
    
    # Execute the generated Python code using execute_python_code
    return execute_python_code(final_code, functions)