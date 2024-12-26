import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# General settings
SHOW_COMPLETION_IN_EVAL = False

# Pythonic settings
PYTHONIC_DATA_PATH = "data/function_calling_eval.jsonl"
PYTHONIC_SYSTEM_PROMPT_PATH = "eval/pythonic/system_prompt.txt"
FLOAT_TOLERANCE = 1e-6
BATCH_SIZE = 16
CODE_EXECUTION_TIMEOUT = 30  # Maximum time in seconds for code execution

# Json mode settings
JSON_SYSTEM_PROMPT_PATH = "eval/json_mode/system_prompt.txt"

# Provider settings
LM_STUDIO_URL = "http://localhost:1234/v1"
OLLAMA_URL = "http://localhost:11434/v1"
VLLM_URL = "http://localhost:8000/v1"
OPENROUTER_URL = "https://openrouter.ai/api/v1"

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

PROVIDER_URLS = {
    "lm_studio": (LM_STUDIO_URL, "api_key"),
    "ollama": (OLLAMA_URL, "api_key"),
    "vllm": (VLLM_URL, "api_key"),
    "openrouter": (OPENROUTER_URL, OPENROUTER_API_KEY),
}
