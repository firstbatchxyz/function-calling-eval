from typing import Dict, Any, List

from eval.util import load_pythonic_jsonl, extract_codeblocks
from eval.engine import import_functions, execute_python_code
from eval.model import get_completion

def evaluate_model(model_name: str, data_path: str = "data/pythonic.jsonl") -> Dict[str, Any]:
    """
    Evaluate a model's function calling capabilities using the pythonic.jsonl dataset.
    
    Args:
        model_name: Name of the model to evaluate
        data_path: Path to the pythonic.jsonl file
        
    Returns:
        Dict containing evaluation metrics:
        {
            "total_examples": int,
            "overall_accuracy": float,
            "errors": List[str]
        }
    """
    # Load evaluation data
    rows = load_pythonic_jsonl(data_path)
    
    # Initialize metrics
    total = len(rows)
    correct = 0
    errors = []
    
    # Evaluate each example
    for row in rows:
        try:
            # Import mock functions
            functions = import_functions(row.mock_functions)
            
            # TODO: In reality, you would get the completion from the model here
            # For now, we'll use the completion from the jsonl file
            completion = get_completion(model_name, "", row.user_query)
            
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
    
    return {
        "total_examples": total,
        "overall_accuracy": overall_accuracy,
        "errors": errors
    }
