# DPAB-α: Dria Pythonic Agent Benchmark

DPAB-α is a comprehensive benchmark designed to evaluate LLMs function calling capabilities through both Pythonic and JSON-based approaches. 
This benchmark contains 100 synthetically generated and validated problems across different difficulty levels.

Each task has both functions defined in Python and JSON schemas. 
The benchmark evaluates the model's ability to generate correct function calls based on the given problem description.

Pythonic function calling performance often outstrips JSON-based function calling in scenarios that require creative or multi-step solutions, reinforcing the premise that Pythonic function calling can be more natural and powerful.

### Installation

```bash
git clone https://github.com/firstbatchxyz/function-calling-eval.git
cd function-calling-eval
pip install -r requirements.txt
```

### Usage

Basic usage:

```bash
python run.py --model anthropic/claude-3.5-sonnet --provider openrouter
```

### Command Line Arguments

- `--model`: Model identifier (default: "anthropic/claude-3.5-sonnet")
- `--provider`: API provider (default: "openrouter")
- `--strict`: Enable strict evaluation mode (optional)
- `--show_completion`: Show model completions (default: False)
- `--mode`: Evaluation mode, either "json" or "pythonic" (default: "pythonic")

#### Providers

DBAP-a supports the following providers:

- `openrouter`: OpenRouter API
- `lm_studio`: LM Studio
- `vllm`: Local models via vLLM
- `ollama`: Local models via Ollama

### Example

```bash
# Evaluate Claude 3.5 in pythonic mode
python run.py --model anthropic/claude-3.5-sonnet --provider openrouter --mode pythonic --strict 

# Evaluate with JSON mode and show completions
python run.py --model qwen/qwen-2.5-7b-instruct --provider openrouter --mode json --strict  --show_completion
```

### Benchmark Structure

Each test case in the benchmark contains:
- `difficulty`: Easy or hard
- `function_schema_python`: Python function definitions
- `function_schema_json`: JSON function schemas
- `mock_functions`: Implementation with return values
- `user_query`: Natural language question
- `checklist`: Validation criteria

## Results

Current benchmark results for various models **(strict)**:

| Model Name                      | Pythonic | JSON |
|---------------------------------|----------|------|
| **Closed Models**               |          |      |
| Claude 3.5 Sonnet              | 87       | 45   |
| o1-preview-2024-09-12           | 55       | 39   |
| o1-mini-2024-09-12              | 59       | 35   |
| gpt-4o-2024-11-20              | 60       | 30   |
| **Open Models**                 |          |      |
| **> 100B Parameters**           |          |      |
| DeepSeek V3 (685B)             | 63       | 33   |
| MiniMax-01                     | 62       | 40   |
| Llama-3.1-405B-Instruct        | 60       | 38   |
| **> 30B Parameters**            |          |      |
| Qwen-2.5-Coder-32b-Instruct    | 68       | 32   |
| Qwen-2.5-72b-instruct          | 65       | 39   |
| Llama-3.3-70b-Instruct         | 59       | 40   |
| QwQ-32b-Preview                | 47       | 21   |
| **< 20B Parameters**           |          |      |
| Dria-Agent-a-7B               | 70       | 38   |
| Qwen2.5-Coder-7B-Instruct      | 44       | 39   |
| Dria-Agent-a-3B               | 72       | 31   |
| Qwen2.5-Coder-3B-Instruct      | 26       | 37   |
| Qwen-2.5-7B-Instruct           | 47       | 34   |
| Phi-4 (14B)                    | 55       | 35   |

For details, please refer to our [blog post](https://huggingface.co/blog/andthattoo/dpab-a).

#### Citation

If you use this benchmark in your research, please cite:

```bibtex
@misc{Dria-Agent-a,
      url={https://huggingface.co/blog/andthattoo/dria-agent-a},
      title={Dria-Agent-a},
      author={"andthattoo", "Atakan Tekparmak"}
}
```
