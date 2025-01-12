from typing import List, Callable, Dict, Any
import ast
from types import FunctionType
from concurrent.futures import ThreadPoolExecutor, TimeoutError

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
) -> FunctionResults:
    """
    Execute Python code with given functions and context variables, and return the results.
    """
    dangerous_builtins = ["exec", "eval", "execfile", "compile", "exit", "input"]

    if safe:
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

    # Create a copy of builtins and remove dangerous ones
    import builtins

    filtered_builtins = {
        k: v for k, v in builtins.__dict__.items() if k not in dangerous_builtins
    }

    env = {"__builtins__": filtered_builtins}
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
            if isinstance(node.value, ast.Call) and isinstance(
                node.value.func, ast.Name
            ):
                func_name = node.value.func.id
                var_name = node.targets[0].id
                function_to_variable.setdefault(func_name, []).append(var_name)

    # Wrap the provided functions to capture their return values
    call_results = {}

    def make_wrapper(func_name, func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            call_results.setdefault(func_name, []).append(result)
            return result

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
    function_results = {}
    for func_name, var_names in function_to_variable.items():
        function_results[func_name] = var_names

    return FunctionResults(
        function_results=function_results, variables=variables, errors=errors
    )
