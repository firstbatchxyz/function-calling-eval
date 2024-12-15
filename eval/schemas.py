from typing import List, Dict, Any, Optional
from enum import Enum

from pydantic import BaseModel

from eval.settings import FLOAT_TOLERANCE

class OpenAIParameter(BaseModel):
    """OpenAI parameter schema."""
    type: str
    description: Optional[str] = None
    required: List[str]
    properties: Dict[str, Dict[str, str]]
    additionalProperties: bool = False

class OpenAIFunction(BaseModel):
    """OpenAI function schema."""
    name: str
    description: str
    parameters: OpenAIParameter

class FunctionResults(BaseModel):
    """Results from executing functions, including return values, variables and errors."""
    function_results: Dict[str, Any]
    variables: Dict[str, Any] 
    errors: List[str]

    def has_values(self, values_list: List[Any]) -> bool:
        """
        Check if all the values in the list exist in the variables, with a tolerance threshold for floats.

        Args:
            values_list: The values to search for
            tolerance: The tolerance threshold for floating point comparisons (default: 1e-6)

        Returns:
            bool: True if all the values are found in the variables, False otherwise
        """
        def values_match(value1: Any, value2: Any) -> bool:
            """Check if two values match, considering tolerance for floats."""
            if isinstance(value1, float) and isinstance(value2, float):
                return abs(value1 - value2) <= FLOAT_TOLERANCE
            return value1 == value2

        return all(
            any(values_match(value, var_value) for var_value in self.variables.values())
            for value in values_list
        )
    
    def has_functions(self, functions_list: List[str]) -> bool:
        """
        Check if all the functions in the list exist as keys in the function_results.

        Args:
            functions_list: The functions to search for

        Returns:
            bool: True if all the functions are found, False otherwise
        """
        return all(function in self.function_results.keys() for function in functions_list)
    
class Checklist(BaseModel):
    """Checklist for evaluating function calling."""
    functions: List[str]
    values: List[Any]

class PythonicRow(BaseModel):
    """
    Represents a row of data for evaluating pythonic function calling.
    
    Attributes:
        difficulty: The difficulty of the task
        function_schema_json: JSON schema of available functions
        function_schema_python: Python function definitions
        mock_functions: Mock implementations of functions
        completion: The assistant's response code
        user_query: The original user request
        function_results: Results from executing the functions
    """
    difficulty: str
    function_schema_json: List[OpenAIFunction]
    function_schema_python: str
    mock_functions: str
    completion: Optional[str] = None
    user_query: str
    checklist: Checklist
    
class EvalMode(str, Enum):
    """Evaluation mode for function calling."""
    PYTHONIC = "pythonic"
    JSON = "json"
