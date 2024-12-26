from typing import Dict, Any
from tqdm import tqdm
from eval.pythonic.engine import import_functions, execute_python_code
from eval.model import get_completions_batch
from eval.settings import (
    PYTHONIC_DATA_PATH,
    PYTHONIC_SYSTEM_PROMPT_PATH,
    SHOW_COMPLETION_IN_EVAL,
    BATCH_SIZE,
)
from eval.util import (
    load_pythonic_jsonl,
    extract_codeblocks,
    load_system_prompt,
    insert_functions_schema,
    setup_logger,
)

# Set up logger using the utility function
logger = setup_logger(__name__)


async def evaluate_model_pythonic(
    model_name: str,
    provider: str,
    strict: bool = False,
    data_path: str = PYTHONIC_DATA_PATH,
    show_completion: bool = SHOW_COMPLETION_IN_EVAL,
) -> Dict[str, Any]:
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

    # Log evaluation details
    logger.info(
        "Evaluating model '{}' with provider '{}'{} in Pythonic mode".format(
            model_name, provider, " (showing completions)" if show_completion else ""
        )
    )

    # Load evaluation data
    rows = load_pythonic_jsonl(data_path)

    # Initialize metrics
    total = len(rows)
    correct = 0
    errors = []

    # Load system prompt
    system_prompt = load_system_prompt(PYTHONIC_SYSTEM_PROMPT_PATH)

    # Evaluate each example
    for i in tqdm(range(0, len(rows), BATCH_SIZE), desc="Processing Batches"):
        batch = rows[i : i + BATCH_SIZE]

        requests = []
        for row in batch:
            functions = import_functions(row.mock_functions)
            # Insert functions schema into system prompt
            inserted_system_prompt = insert_functions_schema(
                system_prompt, row.function_schema_python
            )
            requests.append(
                {
                    "model_name": model_name,
                    "provider": provider,
                    "system_prompt": inserted_system_prompt,
                    "user_query": row.user_query,
                    "functions": functions,
                }
            )
        try:
            completions = await get_completions_batch(requests)
        except Exception as e:
            raise RuntimeError("Error processing batch: {}".format(e))

        for j, completion in enumerate(completions):
            row = batch[j]
            try:
                if show_completion:
                    logger.info(f"Completion: {completion}")

                # Extract code from completion if needed
                code = (
                    extract_codeblocks(completion)
                    if "```" in completion
                    else completion
                )

                # Execute the code with mock functions
                results = execute_python_code(code, requests[j]["functions"])

                # Check if required functions were called
                score = results.check_score(
                    row.checklist.values, row.checklist.functions
                )

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
        "errors": errors,
    }
