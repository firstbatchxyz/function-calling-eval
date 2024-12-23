from openai import OpenAI

from eval.settings import PROVIDER_URLS

# Initialize OpenAI clients for each provider
CLIENTS = {}
for provider, (url, api_key) in PROVIDER_URLS.items():
    CLIENTS[provider] = OpenAI(
        api_key=api_key,
        base_url=url
    )

def get_completion(model_name: str, provider: str, system_prompt: str, user_query: str) -> str:
    """
    Get a completion from a model for a given provider.

    Args:
        model_name: The name of the model to use
        provider: The provider to use
        system_prompt: The system prompt to use
        user_query: The user query to use

    Returns:
        The completion from the model
    """
    client = CLIENTS.get(provider)
    if not client:
        raise ValueError(f"Provider '{provider}' not recognized.")

    # Create the messages for the chat completion
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    # Make the API call to get the completion
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.0
    )

    # Extract and return the assistant's reply
    return response.choices[0].message.content