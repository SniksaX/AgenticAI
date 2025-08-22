# AI Code Documentation Agent

[![Python Version](https://imgshields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI Version](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com/)
[![LangChain Version](https://img.shields.io/badge/LangChain-0.1.0-FF4154.svg)](https://www.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository contains the source code for an AI-powered agent designed to automatically generate documentation and validated executable examples for Python code. The system is built with FastAPI and leverages the LangChain ReAct framework to enable a sophisticated reasoning and self-correction loop.

## Table of Contents

- [Architectural Overview](#architectural-overview)
- [Core Features](#core-features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Running the Application](#running-the-application)
  - [API Endpoint Reference](#api-endpoint-reference)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Architectural Overview

The application exposes a single API endpoint that accepts a Python code snippet. This snippet is processed by a LangChain agent that iteratively analyzes the code, drafts documentation, generates an example, and validates that example within a sandboxed execution environment. The agent corrects its own output based on execution feedback until a valid example is produced.

The data flow is as follows:

```mermaid
graph TD
    A[Client Request: POST /process-code] --> B[FastAPI Application: main.py]
    B --> C{Agent Core: agent_core.py}
    C --> D[LangChain AgentExecutor]
    D -- 1. Analyze --> E[Tool: CodeAnalyzer]
    E -- Analysis --> D
    D -- 2. Draft --> F(Agent LLM Brain)
    F -- Drafted Example --> D
    D -- 3. Validate --> G[Tool: CodeExecutionEnvironment]
    G -- Execution Result (Error) --> D
    D -- 4. Self-Correct --> F
    F -- Corrected Example --> D
    D -- 5. Re-Validate --> G
    G -- Execution Result (Success) --> D
    D -- 6. Finalize --> H[Generate Final Answer]
    H --> B
    B --> I[JSON Response to Client]
Core Features
ReAct Agent Framework: Utilizes a Reason-Act loop, allowing the agent to make decisions, execute tools, and observe outcomes to inform its next steps.
Sandboxed Code Execution: Integrates a secure, sandboxed environment to execute agent-generated code, providing direct feedback for validation and self-correction.
Dynamic Error Correction: The agent is explicitly prompted to analyze execution errors (NameError, SyntaxError, etc.) and revise its code until it runs successfully.
Modular Tooling: The agent's capabilities are defined by a set of distinct, testable tools for code analysis and execution.
RESTful API: A robust API built with FastAPI, including automated OpenAPI (Swagger) documentation.
Getting Started
Prerequisites
Python 3.9 or later
An OpenAI API Key
Installation
Clone the repository:
code
Bash
git clone https://github.com/your-username/ai-code-doc-agent.git
cd ai-code-doc-agent
Create and activate a Python virtual environment:
code
Bash
python -m venv venv
source venv/bin/activate
On Windows, use .\venv\Scripts\activate
Install the required dependencies:
code
Bash
pip install -r requirements.txt
(Note: If a requirements.txt file is not present, generate it via pip freeze > requirements.txt)
Configure environment variables:
Create a .env file in the project's root directory and add your OpenAI API key:
code
Env
OPENAI_API_KEY="sk-..."
Usage
Running the Application
Execute the following command from the root directory to start the Uvicorn server:
code
Bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
The API is now accessible at http://localhost:8000.
API Endpoint Reference
POST /process-code
This endpoint processes a Python code snippet and returns generated documentation and a validated example.
Request Body:
code
JSON
{
  "code_snippet": "def example_function(param1: int):\n    return param1 * 2"
}
Success Response (200 OK):
code
JSON
{
  "status": "success",
  "documentation": "Generated documentation text...",
  "example_code": "Validated example code...",
  "agent_trace": "The agent's internal thought process..."
}
Error Response (500 Internal Server Error):
code
JSON
{
  "detail": "An internal server error occurred: [Error details]"
}
You can interact with the live API and view the auto-generated documentation via Swagger UI at http://localhost:8000/docs.
Testing
This project uses pytest for unit testing the agent's tools.
To run the test suite, execute the following command from the root directory:
code
Bash
pytest```

## Project Structure
.
├── .env # Environment variables (not version controlled)
├── agent_logs.log # Log file for agent activity
├── main.py # FastAPI application entry point
├── README.md # This file
├── requirements.txt # Project dependencies
├── src
│ ├── init.py
│ ├── agent_core.py # Core agent logic, prompts, and executor
│ ├── models.py # Pydantic models for API data contracts
│ └── tools.py # Agent's custom tools
└── tests
├── init.py
└── test_tools.py # Unit tests for the custom tools
code
Code
## Contributing

Contributions to this project are welcome. Please adhere to the following guidelines:
1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Commit your changes with clear, descriptive messages.
4.  Ensure all tests pass before submitting.
5.  Open a pull request for review.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
