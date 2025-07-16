# ai_agent_doc_gen/tests/test_tools.py

import pytest
from src.tools import execute_python_code, search_external_docs_mock


def test_execute_simple_print():
    """Tests that a simple, correct print statement executes successfully."""
    code = "print('Hello, World!')"
    result = execute_python_code(code)
    assert result == "EXECUTION_SUCCESS: Hello, World!"


def test_execute_multiline_function():
    """Tests execution of a multi-line function definition and call."""
    code = """
        def multiply(x, y):
            return x * y
            result = multiply(7, 6)
            print(result)
        """
    result = execute_python_code(code)
    assert result == "EXECUTION_SUCCESS: 42"


def test_execute_code_with_error():
    """Tests that the tool correctly captures a runtime error (ZeroDivisionError)."""
    code = "result = 10 / 0"
    result = execute_python_code(code)
    assert "EXECUTION_ERROR" in result
    assert "ZeroDivisionError" in result


def test_execute_code_with_timeout():
    """Tests that the tool correctly times out on an infinite loop."""
    code = "while True: pass"
    # code = True
    result = execute_python_code(code, timeout=1)
    assert "EXECUTION_ERROR" in result
    assert "timed out" in result


@pytest.mark.skip(reason="This test will fail until we fix the tool's input parsing")
def test_execute_with_markdown_fences_fails_before_fix():
    """
    This test reproduces the bug seen in the logs.
    The agent sends code wrapped in Markdown fences, which causes a syntax error.
    """
    code_from_agent = """```python
print("This will fail")
```"""
    result = execute_python_code(code_from_agent)
    assert "EXECUTION_SUCCESS" not in result
    assert "EXECUTION_ERROR: An unexpected error occurred during execution: invalid syntax" in result


def test_execute_with_markdown_fences_succeeds_after_fix():
    """
    This test will pass once we fix the tool to handle Markdown fences.
    It's the same input as the failing test above.
    """
    code_from_agent = """```python
                        print("This should succeed after the fix")```"""
    result = execute_python_code(code_from_agent)
    assert result == "EXECUTION_SUCCESS: This should succeed after the fix"


def test_search_docs_found():
    """Tests searching for a keyword that exists in our mock database."""
    result = search_external_docs_mock("requests.get")
    assert "HTTP requests" in result


def test_search_docs_not_found():
    """Tests searching for a keyword that does not exist."""
    result = search_external_docs_mock("unknown_library.function")
    assert "No specific external documentation found" in result
