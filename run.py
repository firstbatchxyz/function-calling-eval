from eval.pythonic.function_calling_eval import evaluate_model



result = evaluate_model("llama3.2:latest", "ollama")

print(result)