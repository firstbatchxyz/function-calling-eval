MOCK_COMPLETION = """
tweets = get_tweets("#IslamMakhachev", 10)
sentiment_scores = [get_sentiment(tweet) for tweet in tweets]
average_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
fighter_record = get_fighter_record("Islam Makhachev")
"""

def get_completion(model_name: str, system_prompt: str, user_query: str) -> str:
    """
    Generate a completion for the given system prompt and user query.

    Args:
        model_name: The name of the LLM model to use.
        system_prompt: The prompt provided by the system.
        user_query: The query provided by the user.

    Returns:
        The LLM completion for the given system prompt and user query.
    """
    # Mock value for completion
    # TODO: Implement actual completion
    return MOCK_COMPLETION

