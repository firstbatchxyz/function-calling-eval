from eval.evaluate import evaluate_model, EvaluationMode

model_name = "qwen2.5-coder:7b-instruct-fp16"

result = evaluate_model(    
    model_name=model_name, 
    provider="ollama",
    mode=EvaluationMode.pythonic,
    show_completion=True
)

print(f"Pythonic: {result}")

result = evaluate_model(    
    model_name=model_name, 
    provider="ollama",
    mode=EvaluationMode.json,
    show_completion=True
)

print(f"JSON (warning: not implemented): {result}")