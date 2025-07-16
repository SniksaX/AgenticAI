

from fastapi import FastAPI, HTTPException
import uvicorn
import logging
import traceback

from src.models import CodeInput, AgentOutput
from src.agent_core import process_code_with_agent


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent_logs.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


app = FastAPI(
    title="AI Code Documentation Agent API",
    description="API for an AI Agent that generates documentation and validated examples for Python code.",
    version="1.0.0",
)


@app.post("/process-code", response_model=AgentOutput, summary="Generate documentation and example for Python code")
async def process_code(input_data: CodeInput):
    """
    Receives a Python code snippet, processes it with the AI Agent to generate
    documentation and a validated executable example.
    """
    try:

        logger.info(
            f"--- NEW REQUEST ---\nReceived code snippet:\n{input_data.code_snippet}\n--------------------")

        agent_result = await process_code_with_agent(input_data.code_snippet)

        if agent_result["status"] == "success":

            logger.info(
                f"Agent's Chain of Thought:\n{agent_result['agent_trace']}")

            response_data = AgentOutput(
                status="success",
                documentation=agent_result["documentation"],
                example_code=agent_result["example_code"],
                agent_trace=agent_result['agent_trace']
            )

            logger.info(f"Successfully processed request. Sending response.")
            return response_data
        else:

            error_msg = agent_result.get(
                "error_message", "Unknown agent error.")
            logger.error(f"Agent execution failed. Error: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)

    except Exception as e:
        error_msg = f"An internal server error occurred: {str(e)}"
        logger.critical(
            f"Unhandled Exception in API endpoint: {error_msg}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
