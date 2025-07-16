

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain.tools import Tool
from typing import List, Dict, Any


from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.agents import AgentAction, AgentFinish

from .tools import get_code_analyzer_tool, external_docs_search_tool, code_execution_tool


load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. Please set it in your .env file.")


llm = ChatOpenAI(model="gpt-4o",
                 temperature=0, openai_api_key=openai_api_key)
print("LLM initialized in agent_core.py")


tools: List[Tool] = [
    get_code_analyzer_tool(llm),
    external_docs_search_tool,
    code_execution_tool
]
print(f"Total {len(tools)} tools assembled in agent_core.py")


# In src/agent_core.py

prompt_template_string = """
You are an expert AI Assistant that generates comprehensive documentation and executable examples for Python code.
Your ultimate goal is to provide a final answer containing BOTH clear documentation and a PROVEN, WORKING example.

You have access to the following tools:
{tools}

To achieve your goal, follow this mandatory and iterative process. DO NOT skip any steps.

1. **Analyze the Code:** Use the `CodeAnalyzer` tool to understand the provided code snippet's purpose, parameters, and structure.

2. **Draft Documentation and Example:** Based on your analysis, think about how to best document this code. Draft a clear docstring and a simple, illustrative example that demonstrates its primary use case.

3. **CRITICAL VALIDATION STEP:** This step is MANDATORY. Before you can provide a Final Answer, you MUST test your generated example code.
   - **Action:** Take the complete, self-contained example code you drafted (including any necessary imports and the function definition itself) and execute it using the `CodeExecutionEnvironment` tool.
   - **Observation:** Read the output from the tool. It will be either "EXECUTION_SUCCESS" or "EXECUTION_ERROR".

4. **REFINE OR FINALIZE:**
   - **If Execution FAILED (`EXECUTION_ERROR`):** DO NOT give up. Analyze the error message. Was it a `NameError` because you forgot an import or the function definition? A `TypeError`? Revise your example code to fix the bug and GO BACK to Step 3. Repeat until you get a success.
   - **If Execution SUCCEEDED (`EXECUTION_SUCCESS`):** Excellent! You now have a proven, working example. You are now authorized to proceed to the final step.

5. **Final Answer:** ONLY after a successful execution, combine your drafted documentation and your now-validated example code into a single, complete response. The Final Answer MUST contain the working code.

A Final Answer that does not follow a successful `CodeExecutionEnvironment` observation is a failure.

Use the following format:

Thought: You should always think about what to do.
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: The example code has been successfully validated. I am now ready to provide the final answer.
Final Answer: [Your complete documentation and the validated example code here]

Begin!

Input: {input}
{agent_scratchpad}
"""


prompt = PromptTemplate.from_template(prompt_template_string)
agent = create_react_agent(llm, tools, prompt)


class AgentCallbackHandler(BaseCallbackHandler):
    """A custom callback handler to programmatically capture the agent's internal monologue."""

    def __init__(self):
        super().__init__()

        self.log_stream = []

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """This method is called when the agent decides to take an action."""

        self.log_stream.append(action.log)

    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """This method is called when a tool finishes running."""

        observation = f"\nObservation: {output}\n"
        self.log_stream.append(observation)

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """This method is called when the agent finishes its work."""

        self.log_stream.append(finish.log)


agent_executor = AgentExecutor(
    agent=agent, tools=tools, handle_parsing_errors=True)

print("AgentExecutor initialized in agent_core.py (verbose=False, using callbacks)")


async def process_code_with_agent(code_snippet: str) -> dict:
    """
    Runs the AI agent with the given code snippet and returns its final output
    along with the full trace from our custom callback handler.
    """
    print(f"\n--- AgentCore: Processing code snippet ---")

    callback_handler = AgentCallbackHandler()
    try:

        result = await agent_executor.ainvoke(
            {"input": code_snippet},
            config={"callbacks": [callback_handler]}
        )
        print("\n--- AgentCore: Agent finished ---")

        full_trace = "".join(callback_handler.log_stream)

        return {
            "status": "success",
            "documentation": result['output'],
            "example_code": "See documentation for example (Agent combines them)",
            "agent_trace": full_trace
        }
    except Exception as e:
        print(
            f"\n--- AgentCore: An error occurred during agent execution: {e} ---")
        return {
            "status": "error",
            "documentation": "",
            "example_code": "",
            "error_message": f"Agent failed to process code: {e}",
            "agent_trace": "".join(callback_handler.log_stream)
        }
