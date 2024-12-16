from enum import Enum

from eval.pythonic import evaluate_model_pythonic
from eval.json_mode import evaluate_model_json
from eval.settings import SHOW_COMPLETION_IN_EVAL

class EvaluationMode(Enum):
    """Evaluation modes for different types of model evaluation."""
    json = "json"
    pythonic = "pythonic"

def evaluate_model(
        model_name: str, 
        provider: str, 
        mode: EvaluationMode,
        strict: bool = False,
        show_completion: bool = SHOW_COMPLETION_IN_EVAL
    ):
    if mode == EvaluationMode.json:
        return evaluate_model_json(
            model_name=model_name,
            provider=provider,
            show_completion=show_completion,
            strict=strict
        )
    elif mode == EvaluationMode.pythonic:
        return evaluate_model_pythonic(
            model_name=model_name,
            provider=provider,
            show_completion=show_completion,
            strict=strict
        )
