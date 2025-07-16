+--------------------------------------------------------------------------------------------------+
|                                  Client (e.g., curl, Postman)                                    |
|                           POST /process-code { "code_snippet": "..." }                           |
+--------------------------------------------------------------------------------------------------+
                                                 |
                                                 V
+--------------------------------------------------------------------------------------------------+
|                                FastAPI Application (`main.py`)                                   |
|                                                                                                  |
|   1. Receives HTTP POST request.                                                                 |
|   2. Validates input against `CodeInput` Pydantic model.                                         |
|   3. Calls `agent_core.process_code_with_agent(code_snippet)` and awaits the result.             |
|   4. Formats the final result into `AgentOutput` Pydantic model and returns as JSON response.    |
+--------------------------------------------------------------------------------------------------+
                                                 |
                                                 V
+--------------------------------------------------------------------------------------------------+
|                                   AI Agent Core (`agent_core.py`)                                |
|                                                                                                  |
|   +---------------------------------------+      +-------------------------------------------+   |
|   |         LLM Initialization            |      |            Tool Assembly                  |   |
|   | `llm = ChatOpenAI(model="gpt-4o")`    |      | `tools = [CodeAnalyzer, DocsSearch, ...]` |   |
|   +---------------------------------------+      +-------------------------------------------+   |
|                      |                                            |                              |
|                      +-----------------------+--------------------+                              |
|                                              |                                                   |
|                                              V                                                   |
|   +------------------------------------------------------------------------------------------+   |
|   |                                  AgentExecutor (`agent`)                                 |   |
|   |                                                                                          |   |
|   |   [ Executes the ReAct (Reasoning & Acting) Loop until a Final Answer is reached ]       |   |
|   |                                                                                          |   |
|   |   +----------------------------------------------------------------------------------+   |   |
|   |   |                      Agent's Internal "Chain of Thought"                         |   |   |
|   |   +----------------------------------------------------------------------------------+   |   |
|   |   |                                                                                  |   |   |
|   |   | Thought: "My goal is to document this code. My first step is to analyze it."     |   |   |
|   |   |                                                                                  |   |   |
|   |   |   +--------------------------------------------------------------------------+   |   |   |
|   |   |   | Action: Decides to use a tool. LLM Output: `CodeAnalyzer`                |   |   |   |
|   |   |   +--------------------------------------------------------------------------+   |   |   |
|   |   |                          |                                                       |   |   |
|   |   |                          V (Calls Tool with Input)                               |   |   |
|   |   |   +--------------------------------------------------------------------------+   |   |   |
|   |   |   | Action Input: The raw `code_snippet` from the user.                      |   |   |   |
|   |   |   +--------------------------------------------------------------------------+   |   |   |
|   |   |                          |                                                       |   |   |
|   |   +--------------------------+---------------------------------------------------+   |   |   |
|   |                              |                                                       |   |   |
|   |                              +---------------------------------------------------+   |   |   |
|   |                                                                                  |   |   |   |
|   |   <------------------------------------------------------------------------------+   |   |   |
|   |   |                                                                              |   |   |   |
|   |   |   +--------------------------------------------------------------------------+   |   |   |
|   |   |   | Observation: The result from the executed tool is fed back to the agent. |   |   |   |
|   |   |   +--------------------------------------------------------------------------+   |   |   |
|   |   |                                                                                  |   |   |
|   |   | Thought: "The analysis is complete. Now I will draft an example and then I MUST  |   |   |
|   |   |          validate it using the CodeExecutionEnvironment tool."                   |   |   |
|   |   |                                                                                  |   |   |
|   |   |             [ ... This loop of Thought -> Action -> Observation ... ]            |   |   |
|   |   |             [ ... continues, using other tools as needed.     ... ]              |   |   |
|   |   |                                                                                  |   |   |
|   |   |   +--------------------------------------------------------------------------+   |   |   |
|   |   |   |                      SELF-CORRECTION LOOP (Example)                      |   |   |   |
|   |   |   |                                                                          |   |   |   |
|   |   |   | 1. Thought: "I'll test my generated example."                            |   |   |   |
|   |   |   | 2. Action: `CodeExecutionEnvironment`                                    |   |   |   |
|   |   |   | 3. Action Input: "```python\nprint(my_func())\n```"                      |   |   |   |
|   |   |   | 4. Observation: "EXECUTION_ERROR: NameError: name 'my_func' is not       |   |   |   |
|   |   |   |                 defined"                                                 |   |   |   |
|   |   |   | 5. Thought: "The error is `NameError`. I forgot to include the           |   |   |   |
|   |   |   |             function definition. I will correct the code and re-run."    |   |   |   |
|   |   |   | 6. Action: `CodeExecutionEnvironment` (again)                            |   |   |   |
|   |   |   | 7. Action Input: "```python\ndef my_func():...\nprint(my_func())\n```"   |   |   |   |
|   |   |   | 8. Observation: "EXECUTION_SUCCESS: ..."                                 |   |   |   |
|   |   |   +--------------------------------------------------------------------------+   |   |   |
|   |   |                                                                                  |   |   |
|   |   | Thought: "The example is now validated. I can provide the Final Answer."         |   |   |
|   |   |                                                                                  |   |   |
|   |   |   +--------------------------------------------------------------------------+   |   |   |
|   |   |   | Final Answer: The complete documentation and validated code.             |   |   |   |
|   |   |   +--------------------------------------------------------------------------+   |   |   |
|   |   |                                                                                  |   |   |
|   |   +----------------------------------------------------------------------------------+   |   |
|   +------------------------------------------------------------------------------------------+   |
|                                              ^                                                   |
|                                              |                                                   |
|                               +--------------+--------------+                                    |
|                               |                             |                                    |
|   +-------------------------------------------+ +------------------------------------------------+
|   |     Agent Prompt (`PromptTemplate`)       | |             Custom Tools (`tools.py`)          |
|   +-------------------------------------------+ +------------------------------------------------+
|   | - Defines the agent's goal and persona.   | |*Each is a Python function with a description.* |
|   | - MANDATES the validation step.           | |                                                |
|   | - Provides tool descriptions to the LLM.  | | **CodeAnalyzerTool:** Analyzes code structure. |
|   | - Formats the entire input for the LLM.   | | **ExternalDocsSearchTool:** Mock doc search.   |
|   +-------------------------------------------+ | **CodeExecutionEnvironment:** Executes code,   |
|                                                 |     cleans input, and reports success/failure. |
|                                                 +------------------------------------------------+
|                                                                                                  |
+--------------------------------------------------------------------------------------------------+
                                                 ^
                                                 | (API Calls)
                                                 |
+--------------------------------------------------------------------------------------------------+
|                                    External AI Provider (OpenAI)                                 |
|                                                                                                  |
|   - Receives formatted prompts from the LangChain agent.                                         |
|   - Generates the `Thought`, `Action`, `Action Input`, or `Final Answer` text.                   |
|   - Does not have state; simply responds to each input.                                          |
+--------------------------------------------------------------------------------------------------+