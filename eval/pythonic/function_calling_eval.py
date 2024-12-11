from typing import Dict, Any
import logging

from eval.util import load_pythonic_jsonl, extract_codeblocks, load_system_prompt, insert_functions_schema
from eval.pythonic.engine import import_functions, execute_python_code
from eval.model import get_completion
from eval.settings import PYTHONIC_DATA_PATH, PYTHONIC_SYSTEM_PROMPT_PATH, SHOW_COMPLETION_IN_EVAL

# Init logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

def evaluate_model(model_name: str, provider: str, data_path: str = PYTHONIC_DATA_PATH) -> Dict[str, Any]:
    """
    Evaluate a model's function calling capabilities using the pythonic.jsonl dataset.
    
    Args:
        model_name: Name of the model to evaluate
        provider: Provider to use
        data_path: Path to the pythonic.jsonl file
        
    Returns:
        Dict containing evaluation metrics:
        {
            "total_examples": int,
            "overall_accuracy": float,
            "errors": List[str]
        }
    """

    logger.info("Evaluating model '{}' with provider '{}'".format(model_name, provider))

    # Load evaluation data
    rows = load_pythonic_jsonl(data_path)
    
    # Initialize metrics
    total = len(rows)
    correct = 0
    errors = []
    
    # Load system prompt
    system_prompt = load_system_prompt(PYTHONIC_SYSTEM_PROMPT_PATH)
    
    # Evaluate each example
    for row in rows:
        try:
            # Import mock functions
            functions = import_functions(row.mock_functions)

            # Insert functions schema into system prompt
            inserted_system_prompt = insert_functions_schema(system_prompt, row.function_schema_python)
            
            # Get completion
            completion = get_completion(
                model_name=model_name,
                provider=provider,
                system_prompt=inserted_system_prompt,
                user_query=row.user_query
            )

            if SHOW_COMPLETION_IN_EVAL:
                logger.info(f"Completion: {completion}") 

            # Extract code from completion if needed
            code = extract_codeblocks(completion) if "```" in completion else completion
            
            # Execute the code with mock functions
            results = execute_python_code(code, functions)
            
            # Check if required functions were called
            if results.has_functions(row.checklist.functions) and results.has_values(row.checklist.values):
                correct += 1
                
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
