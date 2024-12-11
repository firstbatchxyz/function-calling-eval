from enum import Enum

from eval.pythonic import evaluate_model_pythonic
from eval.settings import SHOW_COMPLETION_IN_EVAL

class EvaluationMode(Enum):
    """Evaluation modes for different types of model evaluation."""
    json = "json"
    pythonic = "pythonic"

def evaluate_model(
        model_name: str, 
        provider: str, 
        mode: EvaluationMode,
        show_completion: bool = SHOW_COMPLETION_IN_EVAL
    ):
    if mode == EvaluationMode.json:
        raise NotImplementedError("JSON evaluation mode is not implemented yet")
    elif mode == EvaluationMode.pythonic:
        return evaluate_model_pythonic(
            model_name=model_name,
            provider=provider,
            show_completion=show_completion
        )
