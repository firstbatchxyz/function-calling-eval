from typing import List, Callable, Dict, Any
import ast
from types import FunctionType
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import builtins

from eval.settings import CODE_EXECUTION_TIMEOUT
from eval.schemas import FunctionResults


# Define custom exceptions
class NotAllowedError(Exception):
    """Raised when dangerous builtins are used in the code."""

    pass


class TimeoutError(Exception):
    """Raised when code execution exceeds the timeout limit."""

    pass


def import_functions(mock_functions: str) -> List[Callable]:
    """
    Import mock functions from a string containing function definitions and return them as callable functions.
    """
    namespace = {}
    import_string = (
        "from typing import List, Dict, Any, Union, Tuple, Callable, Optional"
    )
    exec(import_string, namespace)
    exec(mock_functions, namespace)
    functions = [obj for obj in namespace.values() if isinstance(obj, FunctionType)]
    if not functions:
        raise ValueError("No functions found in the provided mock functions string")
    return functions


def execute_python_code(
    code: str,
    functions: List[Callable] = [],
    context_variables: Dict[str, Any] = {},
    safe: bool = True,
    excluded_builtins: List[str] = [],
) -> FunctionResults:
    """
    Execute Python code with given functions and context variables, and return the results.
    Args:
        code: The Python code (in string format) to execute
        functions: A list of functions to be imported to be used in the code. (Optional, default: [])
        context_variables: A dictionary of variables to be added to the execution environment. (Optional, default: {})
        safe: Whether to check for dangerous builtins and prevent execution if found. (Optional, default: True)
        excluded_builtins: A list of builtins to be excluded from the execution environment. (Optional, default: [])
    Returns:
        FunctionResults: An object containing the results of the code execution.
    """
    # Initialize environment with default builtins
    env = {"__builtins__": builtins.__dict__.copy()}

    if safe:
        # Define dangerous builtins
        if not excluded_builtins:
            dangerous_builtins = [
                "exec",
                "eval",
                "execfile",
                "compile",
                "exit",
                "input",
            ]
        else:
            dangerous_builtins = excluded_builtins

        # Check for dangerous builtin usage
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in dangerous_builtins:
                return FunctionResults(
                    function_results={},
                    variables={},
                    errors=[
                        f"NotAllowedError: Usage of dangerous builtin '{node.id}' is not allowed"
                    ],
                )

        # Filter out dangerous builtins from environment
        env["__builtins__"] = {
            k: v for k, v in builtins.__dict__.items() if k not in dangerous_builtins
        }

    # Import typing functions and add context variables
    import_string = (
        "from typing import List, Dict, Any, Union, Tuple, Callable, Optional"
    )
    exec(import_string, env)
    env.update(context_variables)

    # Record initial environment keys
    initial_keys = set(env.keys())

    # Dictionary to hold function call results mapped to variable names
    function_to_variable = {}

    # Parse AST to map function calls to their assignment variables
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            # Handle direct assignments
            if isinstance(node.value, ast.Call) and isinstance(
                node.value.func, ast.Name
            ):
                func_name = node.value.func.id
                var_name = node.targets[0].id
                function_to_variable.setdefault(func_name, []).append(var_name)
            # Handle dictionary literals with function calls
            elif isinstance(node.value, ast.Dict):
                var_name = node.targets[0].id
                for key, value in zip(node.value.keys, node.value.values):
                    if isinstance(value, ast.Call) and isinstance(value.func, ast.Name):
                        func_name = value.func.id
                        if isinstance(key, ast.Constant):
                            full_var_name = f"{var_name}[{repr(key.value)}]"
                        elif isinstance(key, ast.Constant):
                            full_var_name = f"{var_name}[{repr(key.value)}]"
                        else:
                            full_var_name = var_name
                        function_to_variable.setdefault(func_name, []).append(
                            full_var_name
                        )
            # Handle dictionary and list comprehensions
            elif isinstance(node.value, (ast.DictComp, ast.ListComp)):
                for subnode in ast.walk(node.value):
                    if isinstance(subnode, ast.Call) and isinstance(
                        subnode.func, ast.Name
                    ):
                        func_name = subnode.func.id
                        var_name = node.targets[0].id
                        function_to_variable.setdefault(func_name, []).append(var_name)
        # Handle function definitions
        elif isinstance(node, ast.FunctionDef):
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Call) and isinstance(subnode.func, ast.Name):
                    func_name = subnode.func.id
                    var_name = f"{node.name}:internal"
                    function_to_variable.setdefault(func_name, []).append(var_name)

    # Wrap the provided functions to capture their return values
    def make_wrapper(func_name, func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    for func in functions:
        env[func.__name__] = make_wrapper(func.__name__, func)

    errors = []

    try:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(exec, code, env)
            try:
                future.result(timeout=CODE_EXECUTION_TIMEOUT)
            except TimeoutError:
                errors.append("Code execution exceeded timeout limit.")
            except Exception as e:
                import traceback

                errors.append(f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}")
    except Exception as e:
        errors.append(str(e))

    # Collect variables defined in the code
    variables = {
        k: v
        for k, v in env.items()
        if k not in initial_keys and not k.startswith("__") and not callable(v)
    }

    # Create function results mapping
    function_results = function_to_variable

    return FunctionResults(
        function_results=function_results, variables=variables, errors=errors
    )
