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


### JSON Mode Eval

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