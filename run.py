from eval.evaluate import evaluate_model, EvaluationMode

result = evaluate_model(    
    model_name="qwen2.5-coder:3b", 
    provider="ollama",
    mode=EvaluationMode.pythonic,
    show_completion=True
)

print(result)
