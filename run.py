import argparse
import asyncio
from eval.evaluate import evaluate_model, EvaluationMode

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="anthropic/claude-3.5-sonnet")
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--show_completion", action="store_true", default=False)
    parser.add_argument("--mode", choices=["json", "pythonic"], default="pythonic")
    args = parser.parse_args()

    if args.mode == "pythonic":
        mode = EvaluationMode.pythonic
    else:
        mode = EvaluationMode.json

    result = asyncio.run(
        evaluate_model(
            model_name=args.model,
            provider=args.provider,
            mode=mode,
            strict=args.strict,
            show_completion=args.show_completion,
        )
    )

    print(f"{args.mode.capitalize()}:", result)

if __name__ == "__main__":
    main()