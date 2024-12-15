import json
from typing import Dict, Any, List, Callable

from eval.schemas import FunctionResults
from eval.pythonic.engine import import_functions, execute_python_code

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
    # Convert JSON function calls to Python code
    python_code = []
    for call in function_calls:
        func_name = call.get('name')
        args = call.get('args', [])
        kwargs = call.get('kwargs', {})
        
        # Build argument string
        arg_parts = []
        if args:
            arg_parts.extend(str(arg) for arg in args)
        if kwargs:
            arg_parts.extend(f"{k}={repr(v)}" for k, v in kwargs.items())
        arg_string = ', '.join(arg_parts)
        
        # Build function call
        python_code.append(f"{func_name}({arg_string})")
    
    # Join all function calls with newlines
    final_code = '\n'.join(python_code)
    
    # Execute the generated Python code using execute_python_code
    return execute_python_code(final_code, functions)