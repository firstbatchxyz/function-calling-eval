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

    def has_values(self, values_list: List[Any]) -> bool:
        """
        Check if all the values in the list exist in the variables.

        Args:
            values_list: The values to search for

        Returns:
            bool: True if all the values are found in the variables, False otherwise
        """
        return all(value in self.variables.values() for value in values_list)
    
    def has_functions(self, functions_list: List[str]) -> bool:
        """
        Check if all the functions in the list exist as keys in the function_results.

        Args:
            functions_list: The functions to search for

        Returns:
            bool: True if all the functions are found, False otherwise
        """
        return all(function in self.function_results.keys() for function in functions_list)

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
    function_schema_json: FunctionSchema
    function_schema_python: str
    mock_functions: str
    completion: str
    user_query: str
    function_results: Optional[FunctionResults] = None