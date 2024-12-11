from eval.pythonic import evaluate_model

result = evaluate_model(
    model_name="qwen2.5-coder:3b", 
    provider="ollama",
    show_completion=True
)

print(result)
