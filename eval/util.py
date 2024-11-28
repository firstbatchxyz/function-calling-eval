from typing import List
import json
import re

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