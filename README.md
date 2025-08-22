![alt text](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)

![alt text](https://img.shields.io/badge/Framework-FastAPI-05998b.svg)

![alt text](https://img.shields.io/badge/Powered%20by-LangChain-f19939.svg)
An AI-powered service that automatically generates documentation and validated, executable examples for Python code snippets.
 Core Features
Automated Docstrings: Analyzes Python functions to generate comprehensive, well-formatted docstrings.
Example Generation: Creates simple, illustrative code examples to demonstrate usage.
Self-Correction & Validation: A key feature—the agent executes its own generated examples in a sandboxed environment. If the code fails, it analyzes the error, corrects the code, and re-tests until it succeeds.
API-Driven: Built with FastAPI, providing a clean, modern REST API for easy integration.
Transparent Reasoning: The API can return the agent's full chain of thought, offering complete visibility into its analysis and decision-making process.
 How It Works
This project uses a ReAct (Reasoning and Acting) agent built with the LangChain framework. The agent follows a strict, iterative process to ensure the quality of its output:
Analyze: The agent first uses an CodeAnalyzer tool to understand the purpose, parameters, dependencies, and return values of the input code.
Draft: Based on its analysis, it drafts a docstring and a simple example.
Validate: This is the critical step. The agent executes the complete drafted example (including the function definition) in a CodeExecutionEnvironment.
Refine or Finalize:
If the execution fails, the agent reads the error message, refines its code, and returns to the validation step.
If the execution succeeds, the agent confidently packages the documentation and the now-proven example into a final answer.
This validation loop ensures that the generated code isn't just plausible—it's guaranteed to be runnable.
🛠️ Technology Stack
Backend: FastAPI
AI Framework: LangChain
LLM: OpenAI GPT-4o
Server: Uvicorn
Testing: Pytest
🚀 Getting Started
1. Prerequisites
Python 3.8+
An OpenAI API Key
2. Installation
Clone the repository:
code
Bash
git clone <your-repo-url>
cd <your-repo-directory>
Create and activate a virtual environment:
code
Bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
Install dependencies:
code
Bash
pip install -r requirements.txt
(Note: You will need to create a requirements.txt file from the project's imports. It should include fastapi, uvicorn, langchain, langchain-openai, python-dotenv, and func-timeout.)
Set up environment variables:
Create a file named .env in the root of the project and add your OpenAI API key:
code
Env
OPENAI_API_KEY="sk-..."
3. Running the Application
Launch the development server using Uvicorn:
code
Bash
uvicorn main:app --reload
The API will be available at http://127.0.0.1:8000. You can access the interactive Swagger UI documentation at http://127.0.0.1:8000/docs.
4. Running Tests
To ensure all components are working correctly, run the test suite:
code
Bash
pytest
 API Usage
You can send a POST request to the /process-code endpoint to have the agent document your code.
Example Request with curl
code
Bash
curl -X 'POST' \
  'http://127.0.0.1:8000/process-code' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "code_snippet": "def calculate_average(numbers):\n    if not numbers:\n        return 0\n    return sum(numbers) / len(numbers)"
}'
Example Successful Response
The API will return a JSON object containing the status, the generated documentation (which includes the validated example), and the agent's thought process.
code
JSON
{
  "status": "success",
  "documentation": "```python\ndef calculate_average(numbers):\n    \"\"\"\n    Calculates the average of a list of numbers.\n\n    Parameters:\n    numbers (list of int or float): A list of numbers to average.\n\n    Returns:\n    float: The average of the numbers, or 0 if the list is empty.\n\n    Example:\n    >>> calculate_average([10, 20, 30])\n    20.0\n    \"\"\"\n    if not numbers:\n        return 0\n    return sum(numbers) / len(numbers)\n\n# Example usage\nresult = calculate_average([15, 25, 35, 45])\nprint(f\"The average is: {result}\")\n```",
  "example_code": "See documentation for example (Agent combines them)",
  "agent_trace": "Thought: I need to analyze the code...\nAction: CodeAnalyzer...\nObservation: ...\nThought: I will draft documentation and an example...\nAction: CodeExecutionEnvironment...\nObservation: EXECUTION_SUCCESS: The average is: 30.0\nThought: The example code has been successfully validated. I am now ready to provide the final answer.\nFinal Answer: ..."
}
