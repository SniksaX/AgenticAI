# ai_agent_doc_gen/tools.py

import io
import sys
from func_timeout import func_timeout, FunctionTimedOut
from langchain.tools import Tool
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_openai import ChatOpenAI


def _analyze_code_llm_internal(code_snippet: str, llm_instance: 'ChatOpenAI') -> str:
    """
    Internal helper to analyze code using an LLM instance.
    """
    try:
        analysis_prompt = f"""
        Analyze the following Python code snippet. Identify:
        1. The main function(s) or class(es) defined.
        2. Its purpose or what it aims to achieve.
        3. Any parameters it takes and what they represent.
        4. What it typically returns.
        5. Any external libraries or modules it seems to depend on.
        6. Potential side effects or critical assumptions.

        Code:
        ```python
        {code_snippet}
        ```
        Provide a concise summary of your findings.
        """
        response = llm_instance.invoke(analysis_prompt)
        return response.content
    except Exception as e:
        return f"Error during code analysis: {e}"


def get_code_analyzer_tool(llm_instance: 'ChatOpenAI') -> Tool:
    return Tool(
        name="CodeAnalyzer",
        func=lambda code: _analyze_code_llm_internal(code, llm_instance),
        description="Analyzes a Python code snippet to extract its structure, parameters, return types, inferred purpose, and dependencies. Input should be a Python code string."
    )


def search_external_docs_mock(query: str) -> str:
    """
    Simulates searching a knowledge base for external documentation related to
    common Python libraries or specific code patterns.
    """
    mock_docs = {
        "requests.get": "The 'requests' library in Python is used for making HTTP requests. `requests.get()` is for GET requests. Example: import requests; response = requests.get('https://api.example.com')",
        "pandas.DataFrame": "Pandas DataFrame is a 2-dimensional labeled data structure with columns of potentially different types. Example: import pandas as pd; df = pd.DataFrame({'col1': [1,2], 'col2': ['A','B']})",
        "numpy.array": "NumPy arrays are the core of the NumPy library, used for numerical operations. Example: import numpy as np; arr = np.array([1, 2, 3])",
        "json.loads": "The `json.loads()` function parses a JSON string, converting it to a Python dictionary or list. Example: import json; data_str = '{\"name\": \"Alice\"}'; data_dict = json.loads(data_str)",
        "os.path": "The `os.path` module provides functions for manipulating pathnames. Example: import os; path = os.path.join('dir', 'file.txt')",
    }
    for key, value in mock_docs.items():
        if key.lower() in query.lower():
            return value
    return "No specific external documentation found for this query in the mock knowledge base. The requested query might be too specific or not a common library/function."


external_docs_search_tool = Tool(
    name="ExternalDocsSearch",
    func=search_external_docs_mock,
    description="Searches a mock knowledge base for external documentation related to common Python libraries or specific code patterns. Input should be a relevant keyword or function name (e.g., 'requests.get', 'pandas.DataFrame')."
)


def execute_python_code(code_snippet: str, timeout: int = 5) -> str:
    """
    Executes a given Python code snippet in a sandboxed environment and returns its stdout or stderr.
    Used to validate example code. Includes a timeout to prevent infinite loops.
    This version is robust against Markdown code fences.
    """
    cleaned_code = code_snippet.strip()
    if cleaned_code.startswith("```python"):
        cleaned_code = cleaned_code[len("```python"):].strip()
    if cleaned_code.startswith("```"):
        cleaned_code = cleaned_code[len("```"):].strip()
    if cleaned_code.endswith("```"):
        cleaned_code = cleaned_code[:-len("```")].strip()

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = io.StringIO()
    redirected_error = io.StringIO()
    sys.stdout = redirected_output
    sys.stderr = redirected_error

    try:
        safe_globals = {'__builtins__': {'print': print, 'len': len, 'range': range, 'type': type,
                                         'str': str, 'int': int, 'float': float, 'dict': dict, 'list': list, 'tuple': tuple, 'set': set}}
        safe_locals = {}

        func_timeout(timeout, exec, args=(
            cleaned_code, safe_globals, safe_locals))

        output = redirected_output.getvalue().strip()
        error = redirected_error.getvalue().strip()

        if error:
            return f"EXECUTION_ERROR: {error}"
        else:
            return f"EXECUTION_SUCCESS: {output}"
    except FunctionTimedOut:
        return f"EXECUTION_ERROR: Code execution timed out after {timeout} seconds. This usually means an infinite loop or very slow code."
    except Exception as e:
        error_class_name = type(e).__name__
        error_message = str(e)
        return f"EXECUTION_ERROR: A {error_class_name} occurred: {error_message}\n{redirected_error.getvalue().strip()}"

    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


code_execution_tool = Tool(
    name="CodeExecutionEnvironment",
    func=execute_python_code,
    description="Executes a given Python code snippet in a sandboxed environment and returns its stdout or stderr. Use this to validate example code. Input should be a runnable Python code string."
)
