from typing import Dict, Any, List, Callable
import json
from tqdm import tqdm
import os
from eval.json_mode.engine import (
    parse_json_completion,
    execute_json_function_calls,
    import_functions,
)
from eval.model import get_completions_batch
from eval.settings import PYTHONIC_DATA_PATH, JSON_SYSTEM_PROMPT_PATH, BATCH_SIZE, JSON_RESULTS_PATH
from eval.util import (
    load_pythonic_jsonl,
    load_system_prompt,
    insert_functions_schema,
    setup_logger,
)

logger = setup_logger(__name__)


async def evaluate_model_json(
    model_name: str,
    provider: str,
    strict: bool = False,
    data_path: str = PYTHONIC_DATA_PATH,
    show_completion: bool = False,
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
    logger.info(
        f"Evaluating model '{model_name}' with provider '{provider}' in JSON mode"
    )

    if not os.path.exists(JSON_RESULTS_PATH):
        os.makedirs(JSON_RESULTS_PATH)

    run_path = JSON_RESULTS_PATH + "/" + model_name + "_" + provider
    if not os.path.exists(run_path):
        os.makedirs(run_path)

    # Load evaluation data
    rows = load_pythonic_jsonl(data_path)

    # Initialize metrics
    total = len(rows)
    correct = 0
    errors = []
    results = []

    if os.path.isfile(run_path + "/results.jsonl"):
        with open(f"{run_path}/results.jsonl", "r") as f:
            for line in f.readlines():
                result_row = json.loads(line)
                results.append(result_row)
                correct += result_row["score"]
        rows = rows[:len(results)]

    # Load system prompt
    system_prompt = load_system_prompt(JSON_SYSTEM_PROMPT_PATH)

    # Evaluate each example
    for i in tqdm(range(0, len(rows), BATCH_SIZE), desc="Processing Batches"):
        batch = rows[i : i + BATCH_SIZE]

        requests = []
        for row in batch:
            # Import mock functions
            functions: List[Callable] = import_functions(row.mock_functions)

            # Insert schema into system prompt
            inserted_system_prompt = insert_functions_schema(
                system_prompt,
                json.dumps(
                    [schema.model_dump() for schema in row.function_schema_json],
                    indent=4,
                ),
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
        completions = await get_completions_batch(requests)

        for j, completion in enumerate(completions):
            row = batch[j]

            try:
                if show_completion:
                    logger.info(f"Completion:\n{completion}")

                # Parse JSON from completion
                function_calls = parse_json_completion(completion)

                # Execute function calls
                result = execute_json_function_calls(
                    function_calls, requests[j]["functions"]
                )

                # Check if required functions were called with correct values
                score = result.check_score(
                    row.checklist.values, row.checklist.functions
                )

                if strict:
                    score = 1 if score >= 0.99 and score < 1.01 else 0

                correct += score

                results.append(
                    {
                        "function_calls": function_calls,
                        "score": score,
                        "results": result.model_dump_json(),
                        "expected": row.checklist.model_dump_json(),
                        "user_query": row.user_query,
                        "functions": row.function_schema_python,
                    }
                )

            except Exception as e:
                errors.append(f"Error processing row: {str(e)}")

    # Calculate metrics
    overall_accuracy = correct / total if total > 0 else 0
    overall_accuracy = round(overall_accuracy * 100, 2)

    # Save results
    with open(run_path + "/results.jsonl", "w") as f:
        for result in results:
            f.write(json.dumps(result) + "\n")

    return {
        "total_examples": total,
        "overall_accuracy": overall_accuracy,
        "errors": errors,
    }
