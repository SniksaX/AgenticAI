# AI Code Documentation Agent

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI Version](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com/)
[![LangChain Version](https://img.shields.io/badge/LangChain-0.1.0-FF4154.svg)](https://www.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This is an intelligent API that automatically generates documentation and **verifiably correct** examples for any Python code snippet you provide.

The key feature is its **self-correction loop**: if the AI generates an example that fails, it analyzes the error, fixes its own code, and tries again until it works.

## Demonstration: Input vs. Output

Give the API a function with a bug...

#### Input (`POST /process-code`)

```json
{
  "code_snippet": "def get_user_initials(name: str):\n    # Bug: this will fail on single names\n    parts = name.split()\n    return f\"{parts}{parts}\""
}
...and get back fixed, documented, and validated code.
Output (200 OK)
code
JSON
{
  "status": "success",
  "documentation": "The `get_user_initials` function now correctly handles single names and includes a validated example.",
  "example_code": "def get_user_initials(name: str):\n    \"\"\"\n    Extracts the initials from a full name.\n\n    Handles both single names and multi-part names gracefully.\n\n    Args:\n        name (str): The input name (e.g., 'John Doe' or 'Alice').\n\n    Returns:\n        str: The initials (e.g., 'JD' or 'A').\n    \"\"\"\n    parts = name.split()\n    if len(parts) >= 2:\n        return f\"{parts}{parts[-1]}\"\n    elif parts:\n        return f\"{parts}\"\n    return \"\"\n\n# --- Validated Example ---\nprint(get_user_initials('Taylor Swift'))\nprint(get_user_initials('Beyonce'))",
  "agent_trace": "Thought: The initial code will raise an IndexError for a name like 'Cher'. I must add a check for the length of 'parts'. I will draft a corrected version and then validate it with the CodeExecutionEnvironment tool..."
}
How It Works: The Self-Correction Loop
This isn't just a simple prompt to an LLM. The agent follows a strict, iterative process defined by the ReAct (Reason + Act) framework:
Analyze: The agent first uses a CodeAnalyzer tool to understand the input code's purpose and identify potential flaws.
Draft: It writes documentation and an example to demonstrate the code's usage.
Validate: It executes the example in a sandboxed CodeExecutionEnvironment. This is the most critical step.
Observe & Repeat:
On Failure: The agent gets the exact error message (IndexError, TypeError, etc.). It is prompted to think about the error, revise its code, and go back to step 3.
On Success: The agent confirms the example is valid and proceeds to the final step.
Finalize: Only after successful validation does the agent package the documentation and working code into the final response.
Quickstart
1. Clone & Setup
code
Bash
git clone https://github.com/your-username/ai-code-doc-agent.git
cd ai-code-doc-agent

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
2. Configure API Key
Create a .env file in the root directory and add your OpenAI key:
code
Env
OPENAI_API_KEY="sk-..."
3. Run the Server
code
Bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
The API is now running. Open http://localhost:8000/docs for the interactive Swagger UI.
API Usage
Send a POST request to the /process-code endpoint.
curl Example
code
Bash
curl -X POST "http://localhost:8000/process-code" \
-H "Content-Type: application/json" \
-d '{
    "code_snippet": "def add(a, b): return a + b"
}'
Core Components
main.py: The FastAPI application. Defines the /process-code endpoint and handles HTTP logic.
src/agent_core.py: The brain of the project. It sets up the LangChain agent, defines the main ReAct prompt, and orchestrates the tool-using loop.
src/tools.py: Contains the custom tools the agent can use:
CodeAnalyzer: Intelligently inspects code.
CodeExecutionEnvironment: The secure sandbox for running and validating Python code.
Running Tests
To ensure the tools work as expected, run the included pytest suite:
code
Bash
pytest
License
This project is licensed under the MIT License.
