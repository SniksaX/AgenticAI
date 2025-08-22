# 🤖 AI Code Documentation Agent

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI Version](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com/)
[![LangChain Version](https://img.shields.io/badge/LangChain-0.1.0-FF4154.svg)](https://www.langchain.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-412991.svg)](https://openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 Overview

This project implements an intelligent AI Agent that generates high-quality, executable documentation for Python code snippets. Powered by **FastAPI** and **LangChain's ReAct Agent framework**, it not only drafts explanations but critically **validates generated example code** through a sandboxed execution environment, ensuring accuracy and reliability.

The agent is designed to understand code, create docstrings, and most importantly, self-correct example code based on live execution feedback until it runs successfully.

## ✨ Key Features

*   **Intelligent Code Analysis**: Leverages an LLM-powered tool to deeply analyze Python code structure, purpose, and dependencies.
*   **ReAct Agent Architecture**: Employs LangChain's ReAct (Reasoning and Acting) framework, enabling the agent to `Thought`, `Action`, `Observation` in an iterative loop for robust problem-solving.
*   **Self-Correction with Code Execution**: Integrates a sandboxed Python execution environment to test and validate generated example code. The agent actively corrects its examples based on runtime errors or successes.
*   **Comprehensive Documentation**: Produces rich documentation including docstrings, parameter descriptions, return types, and usage examples.
*   **FastAPI Backend**: Provides a robust and scalable API endpoint for easy integration and consumption.
*   **Detailed Logging**: Captures the agent's full "chain of thought" for transparency and debugging.

## 🚀 How it Works

The system operates as a sophisticated pipeline, where a FastAPI endpoint receives code, and an intelligent agent processes it through an iterative, self-correcting loop.

```mermaid
graph TD
    A[Client: POST /process-code { "code_snippet": "..." }] --> B(FastAPI Application)
    B --> C{AI Agent Core}
    C --> D[LLM Initialization]
    C --> E[Tool Assembly]
    D & E --> F(AgentExecutor - ReAct Loop)
    F -- Thought --> G{Action: CodeAnalyzer}
    G -- Observation --> F
    F -- Thought --> H{Action: Draft Docs & Example}
    H -- Thought --> I{Action: CodeExecutionEnvironment}
    I -- Observation (EXECUTION_ERROR) --> F
    F -- Thought --> J{Action: Revise Example & Re-Execute}
    J -- Observation (EXECUTION_SUCCESS) --> F
    F -- Thought --> K[Final Answer]
    K --> B
    B --> L[Client: JSON Response { documentation, example_code, agent_trace }]
