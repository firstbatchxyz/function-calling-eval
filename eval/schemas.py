from typing import List, Dict, Any, Optional

from pydantic import BaseModel

class FunctionParameter(BaseModel):
    """Represents a parameter for a function with its type."""
    type: str


class Function(BaseModel):
    """Represents a function with its name and parameters."""
    name: str
    parameters: Dict[str, FunctionParameter]


class FunctionSchema(BaseModel):
    """Schema defining a collection of functions."""
    functions: List[Function]


class FunctionResults(BaseModel):
    """Results from executing functions, including return values, variables and errors."""
    function_results: Dict[str, Any]
    variables: Dict[str, Any] 
    errors: List[str]


class PythonicRow(BaseModel):
    """
    Represents a row of data for evaluating pythonic function calling.
    
    Attributes:
        needs_judge: Whether human evaluation is needed
        function_schema_json: JSON schema of available functions
        function_schema_python: Python function definitions
        mock_functions: Mock implementations of functions
        completion: The assistant's response code
        user_query: The original user request
        function_results: Results from executing the functions
    """
    needs_judge: bool
    function_schema_json: FunctionSchema
    function_schema_python: str
    mock_functions: str
    completion: str
    user_query: str
    function_results: Optional[FunctionResults] = None