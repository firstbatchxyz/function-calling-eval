from typing import Dict, Any, List, Callable
import json

from eval.json_mode.engine import parse_json_completion, execute_json_function_calls, import_functions
from eval.model import get_completion
from eval.settings import PYTHONIC_DATA_PATH, JSON_SYSTEM_PROMPT_PATH
from eval.util import (
    load_pythonic_jsonl,
    load_system_prompt,
    insert_functions_schema,
    setup_logger
)

logger = setup_logger(__name__)

def evaluate_model_json(
    model_name: str,
    provider: str,
    strict: bool = False,
    data_path: str = PYTHONIC_DATA_PATH,
    show_completion: bool = False
) -> Dict[str, Any]:
    """
    Evaluate a model's JSON function calling capabilities.
    
    Args:
        model_name: Name of the model to evaluate
        provider: Provider to use
        data_path: Path to the .jsonl file
        show_completion: Whether to show model completions
        
    Returns:
        Dict containing evaluation metrics
    """
    logger.info(f"Evaluating model '{model_name}' with provider '{provider}' in JSON mode")

    # Load evaluation data
    rows = load_pythonic_jsonl(data_path)
    
    # Initialize metrics
    total = len(rows)
    correct = 0
    errors = []
    
    # Load system prompt
    system_prompt = load_system_prompt(JSON_SYSTEM_PROMPT_PATH)
    
    # Evaluate each example
    for row in rows:
        try:
            # Import mock functions
            functions: List[Callable] = import_functions(row.mock_functions)
            
            # Insert schema into system prompt
            inserted_system_prompt = insert_functions_schema(
                system_prompt, 
                json.dumps([schema.model_dump() for schema in row.function_schema_json], indent=4)
            )
            
            # Get completion
            completion = get_completion(
                model_name=model_name,
                provider=provider,
                system_prompt=inserted_system_prompt,
                user_query=row.user_query
            )

            if show_completion:
                logger.info(f"Completion:\n{completion}")
                
            # Parse JSON from completion
            function_calls = parse_json_completion(completion)
            
            # Execute function calls
            results = execute_json_function_calls(function_calls, functions)

            # Check if required functions were called with correct values
            score = results.check_score(row.checklist.values, row.checklist.functions)

            if strict:
                score = 1 if score >= 0.99 and score < 1.01 else 0

            correct += score
                
        except Exception as e:
            errors.append(f"Error processing row: {str(e)}")
    
    # Calculate metrics
    overall_accuracy = correct / total if total > 0 else 0
    overall_accuracy = round(overall_accuracy * 100, 2)
    
    return {
        "total_examples": total,
        "overall_accuracy": overall_accuracy,
        "errors": errors
    }
