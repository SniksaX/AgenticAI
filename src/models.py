# ai_agent_doc_gen/models.py

from pydantic import BaseModel, Field


class CodeInput(BaseModel):
    code_snippet: str = Field(
        ..., description="The Python code snippet to document and generate an example for.")


class AgentOutput(BaseModel):
    status: str = Field(
        ..., description="The status of the agent's operation (e.g., 'success', 'error').")
    documentation: str = Field(...,
                               description="The generated documentation for the code snippet.")
    example_code: str = Field(...,
                              description="The validated, executable example code snippet.")
    agent_trace: str = Field(
        None, description="Optional: The full trace of the agent's thought process (for debugging).")
    error_message: str = Field(
        None, description="Optional: An error message if the operation failed.")
