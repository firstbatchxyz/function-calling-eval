from typing import List, Callable, Dict, Any, get_type_hints, Union
import inspect
import json
import re
import logging

from eval.schemas import PythonicRow

def load_pythonic_jsonl(file_path: str) -> List[PythonicRow]:
    """
    Load the pythonic.jsonl file and return a list of PythonicRow objects.
    
    Args:
        file_path: Path to the pythonic.jsonl file
        
    Returns:
        List of PythonicRow objects
    """
    rows = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    data = json.loads(line)
                    row = PythonicRow(**data)
                    rows.append(row)
        return rows
    except Exception as e:
        raise Exception(f"Error loading pythonic.jsonl file: {str(e)}")

def extract_codeblocks(text: str) -> List[str]:
    """
    Extract code blocks from a given text and merge them into a single string.

    Args:
        text: The text to extract code blocks from

    Returns:
        List of code blocks
    """
    code_blocks = re.findall(r'```python(.*?)```', text, re.DOTALL)
    return "\n".join(code_blocks) if code_blocks else ""

def load_system_prompt(file_path: str) -> str:
    """
    Load the system prompt from a given file and return it as a string.

    Args:
        file_path: Path to the system prompt file
        
    Returns:
        System prompt as a string
    """
    try:
        with open(file_path, 'r') as f:
            return f.read() 
    except Exception as e:
        raise Exception(f"Error loading system prompt file: {str(e)}")
    
def insert_functions_schema(system_prompt: str, functions_schema: str) -> str:
    """
    Insert the functions schema into the system prompt.

    Args:
        system_prompt: The system prompt to insert the functions schema into
        functions_schema: The functions schema to insert into the system prompt
        
    Returns:
        System prompt with the functions schema inserted
    """
    return system_prompt.replace("{{functions_schema}}", functions_schema)

def setup_logger(logger_name: str) -> logging.Logger:
    """
    Set up and configure a logger with console handler.
    
    Args:
        logger_name: Name of the logger to configure
        
    Returns:
        Configured logger instance
    """
    # Init logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Only add handler if the logger doesn't already have handlers
    if not logger.handlers:
        # Create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Create a formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(console_handler)

    return logger

def functions_to_openai(functions: List[Callable]) -> List[Dict[str, Any]]:
    """
    Convert a list of functions to a list of OpenAI function definitions.
    Each function is converted to a dictionary format that OpenAI's API expects
    for function calling.

    Args:
        functions: List of functions to convert

    Returns:
        List of OpenAI function definitions in the format:
        [{
            "name": "function_name",
            "description": "function docstring",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "param1 description"},
                    ...
                },
                "required": ["param1", ...],
                "additionalProperties": false
            }
        }, ...]
    """
    def _type_to_json_schema(typ: type) -> Dict[str, Any]:
        """Convert Python types to JSON schema types."""
        # Handle Union types (e.g., Optional)
        origin = getattr(typ, '__origin__', None)
        if origin is Union:
            types = getattr(typ, '__args__', ())
            # Handle Optional (Union[T, None])
            if len(types) == 2 and types[1] is type(None):
                return _type_to_json_schema(types[0])
            
        # Handle List, Dict, etc.
        if origin is list:
            item_type = getattr(typ, '__args__', (Any,))[0]
            return {
                "type": "array",
                "items": _type_to_json_schema(item_type)
            }
        elif origin is dict:
            return {"type": "object"}
        
        # Handle basic types
        type_map = {
            str: {"type": "string"},
            int: {"type": "integer"},
            float: {"type": "number"},
            bool: {"type": "boolean"},
            list: {"type": "array"},
            dict: {"type": "object"},
            None: {"type": "null"}
        }
        return type_map.get(typ, {"type": "string"})

    openai_functions = []
    
    for func in functions:
        # Get function signature
        sig = inspect.signature(func)
        
        # Get type hints and docstring
        type_hints = get_type_hints(func)
        docstring = inspect.getdoc(func) or ""
        
        # Parse docstring to get parameter descriptions
        param_docs = {}
        if docstring:
            for line in docstring.split('\n'):
                if ':param' in line or 'Args:' in line:
                    match = re.search(r':param\s+(\w+):\s*(.+)', line)
                    if match:
                        param_docs[match.group(1)] = match.group(2).strip()
        
        # Build parameters schema
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            # Skip self parameter for methods
            if param_name == 'self':
                continue
                
            param_type = type_hints.get(param_name, str)
            type_schema = _type_to_json_schema(param_type)
            param_schema = {
                **type_schema,
                "description": param_docs.get(param_name, f"Parameter {param_name}")
            }
            
            properties[param_name] = param_schema
            
            # Add to required if parameter has no default value
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        # Create the OpenAI function definition
        function_def = {
            "name": func.__name__,
            "description": docstring.split('\n')[0] if docstring else func.__name__,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False
            }
        }
        
        openai_functions.append(function_def)
    
    return openai_functions