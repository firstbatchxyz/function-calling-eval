from eval.evaluate import evaluate_model, EvaluationMode

model_name = "qwen/qwen-2.5-coder-32b-instruct"

result = evaluate_model(    
    model_name=model_name, 
    provider="openrouter",
    mode=EvaluationMode.pythonic,
    strict=True,
    show_completion=False
)

print(f"Pythonic: {result}")      

result = evaluate_model(    
    model_name=model_name, 
    provider="openrouter",
    mode=EvaluationMode.json,
    strict=True,
    show_completion=False
)

print(f"JSON: {result}")