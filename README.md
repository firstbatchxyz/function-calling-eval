# Function Calling Evaluation

This repository is designed for evaluating pythonic function calling abilities.
Designed by Dria. 




```python

def extract_text_from_pdf_document(file_path: str) -> str:
    """Extracts text from a PDF document at the specified file path.
        Args:
            file_path (str): The path to the PDF document

        Returns:
            str: The extracted text from the PDF document
    """
                            
        pass

def extract_text_from_pdf_document(file_path: str) -> str:
    mock_outputs = {
        'empty.pdf': '',
        'large.pdf': 'This is a large document with lots of text...',
        'error.pdf': 'Error: Unable to extract text.',
    }
    return mock_outputs.get(file_path, 'Default mock text from the PDF document.')
```

## JSON Mode Eval

#### Proposed format for json-mode eval data:

| Prompt | Completion | Schema | SchemaJSON |
|----------|----------|----------|----------|



#### Prompt

 ```json
 [
   {
      "content":"You are a helpful assistant that answers in JSON. Here's the json schema you must adhere to:\n<schema>\n{'title': 'PortfolioPerformance', 'type': 'object', 'properties': {'capitalGains': {'title': 'Capital Gains', 'type': 'number', 'format': 'currency'}, 'interestIncome': {'title': 'Interest Income', 'type': 'number', 'format': 'currency'}, 'totalReturn': {'title': 'Total Return', 'type': 'number', 'format': 'percentage'}}, 'required': ['capitalGains', 'interestIncome', 'totalReturn']}\n</schema>\n",
      "role":"system"
   },
   {
      "content":"I am analyzing the performance of our mortgage REIT's investment portfolio and need to track key financial metrics. Specifically, I require a JSON object that captures the following data points: capital gains realized this quarter, which are $1,250,000.00, interest income generated from mortgage-backed securities, which is $375,000.00, and the total return percentage over the past year, which is 8.5%. This information will be used to update our investors and for internal performance reviews. Please provide a JSON object that includes these metrics with appropriate formatting for currency and percentages.",
      "role":"user"
   }]
```  

#### Completion
```json
{"capitalGains": 1250000.0, "interestIncome": 375000.0, "totalReturn": 8.5} 
```


#### Schema
```python
from pydantic import BaseModel, Field

class PortfolioPerformance(BaseModel):
    capitalGains: float = Field(..., title="Capital Gains", description="Capital Gains", example=0.0)
    interestIncome: float = Field(..., title="Interest Income", description="Interest Income", example=0.0)
    totalReturn: float = Field(..., title="Total Return", description="Total Return as a percentage", example=0.0)
    
    class Config:
        schema_extra = {
            "example": {
                "capitalGains": 1000.50,
                "interestIncome": 500.25,
                "totalReturn": 0.12,  # Represented as a percentage
            }
        }
```
 
 
 #### SchemaJSON
 ```json
 {"title": "PortfolioPerformance", "type": "object", "properties": {"capitalGains": {"title": "Capital Gains", "type": "number", "format": "currency"}, "interestIncome": {"title": "Interest Income", "type": "number", "format": "currency"}, "totalReturn": {"title": "Total Return", "type": "number", "format": "percentage"}}, "required": ["capitalGains", "interestIncome", "totalReturn"]}
 ```


 ### Evaluation Method

 Evaluate by deserializing completion into given python class Schema.

## Pythonic Function Calling Eval

#### Proposed format for pythonic function calling eval data:

| Field | Description | Example |
|-------|-------------|---------|
| difficulty | The difficulty of the task | "easy", "hard" |
| function_schema_json | JSON representation of available functions | {"name": "get_tweets", "parameters": {...}} |
| function_schema_python | Python function definitions with types | def get_tweets(hashtag: str) -> list[str] |
| mock_functions | Mock implementation returning expected output | def mock_get_tweets(): return ["tweet1"] |
| completion | The assistant's response/code | result = get_tweets("#AI") |
| user_query | The user's original request | "Get latest AI tweets" |
| checklist | List of called functions and values to check for in the function results | { "functions": [get_tweets, get_fighter_record, get_sentiment], "values": [0.7999999999999999, {"name": "Islam Makhachev", "wins": 17, "losses": 1, "draws": 0}] } |

#### System Prompt Template

You are an expert AI assistant that specializes in providing Python code to solve the task/problem at hand provided by the user.

You can use Python code freely, including the following available functions:

<|functions_schema|>
{{functions_schema}}
<|end_functions_schema|>

Think step by step and provide your reasoning, outside of the function calls.
You can write Python code and use the available functions. The multi-turn conversation between you and the user starts now. The user will provide you with the results of the code execution, in between <|function_results|> and <|end_function_results|> tags and you will answer as if you were directly answering the user. In this second response, be concise and to the point. Provide all your python code in a SINGLE markdown code block like the following:

```python
result = example_function(arg1, "string")
result2 = example_function2(result, arg2)
```

DO NOT use print() statements AT ALL. Avoid mutating variables whenever possible. 

> **functions_schema**: functions_schema is just function definitions in Python, with typed arguments and return type(s), the docstring and a mock implementation.

#### Example Row

##### Difficulty:
easy

##### Function Schema JSON:
```json
{
  "functions": [
    {
      "name": "get_tweets",
      "parameters": {
        "hashtag": {"type": "string"},
        "num_tweets": {"type": "integer"}
      }
    },
    {
      "name": "get_fighter_stats", 
      "parameters": {
        "fighter": {"type": "string"}
      }
    },
    {
      "name": "get_sentiment",
      "parameters": {
        "text": {"type": "string"}
      }
    }
  ]
}
```

##### Functions Schema Python:
```python
def get_tweets(hashtag: str, num_tweets: int) -> list[str]:
    """Get the latest tweets with a given hashtag."""
    pass

def get_fighter_record(fighter: str) -> dict:
    """Get the stats for a given fighter, namely wins, losses and draws."""
    pass

def get_sentiment(text: str) -> float:
    """Get the sentiment of a given text."""
    pass
```

##### Mock Functions:
```python
def get_tweets(hashtag: str, num_tweets: int) -> list[str]:
    """Get the latest tweets with a given hashtag."""
    return ["good tweet"] * num_tweets

def get_fighter_record(fighter: str) -> dict:
    """Get the stats for a given fighter, namely wins, losses and draws."""
    return {"name": fighter, "wins": 17, "losses": 1, "draws": 0}

def get_sentiment(text: str) -> float:
    """Get the sentiment of a given text."""
    return 0.8
```

##### User Query:   
What is the current sentiment about Islam Makhachev and his current record?

##### Completion:
To determine the current sentiment about Islam Makhachev and his record, we need to:

1. Get the latest tweets mentioning him.
2. Analyze the sentiment of these tweets.
3. Retrieve his current fighting record.

Let's start by getting the latest tweets with the hashtag `#IslamMakhachev` and analyzing their sentiment.

```python
tweets = get_tweets("#IslamMakhachev", 10)
sentiment_scores = [get_sentiment(tweet) for tweet in tweets]
average_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
fighter_record = get_fighter_record("Islam Makhachev")
```

##### Values List:
```json
{
  "functions": ["get_tweets", "get_fighter_record", "get_sentiment"],
  "values": [
    0.7999999999999999,
    {
        "name": "Islam Makhachev",
        "wins": 17,
        "losses": 1,
        "draws": 0
    }
  ]
}
```
