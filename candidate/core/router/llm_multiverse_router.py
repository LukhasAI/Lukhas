"""
llm_multiverse_router.py

Routes queries dynamically across OpenAI, Anthropic, Gemini, Perplexity, and Azure GPT
based on task type, latency, compliance score, and symbolic reasoning priority.
"""

import uuid
from datetime import datetime
from typing import Literal

import openai

from candidate.bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
from candidate.bridge.llm_wrappers.azure_openai_wrapper import AzureOpenaiWrapper
from candidate.bridge.llm_wrappers.gemini_wrapper import GeminiWrapper

# === Initialize wrapper instances ===
from candidate.bridge.llm_wrappers.openai_wrapper import OpenaiWrapper
from candidate.bridge.llm_wrappers.perplexity_wrapper import PerplexityWrapper
from datetime import timezone

openai = OpenaiWrapper()
anthropic = AnthropicWrapper()
gemini = GeminiWrapper()
perplexity = PerplexityWrapper()
azure = AzureOpenaiWrapper()

# === Task types ===
TaskType = Literal["code", "ethics", "web", "creative", "general"]


def multiverse_route(task: str, task_type: TaskType = "general", debug: bool = False) -> str:
    """
    Routes the task to the most appropriate model.

    Args:
        task: The user input or task string
        task_type: Type of task to guide routing
        debug: If True, returns extra metadata

    Returns:
        Response from chosen model
    """

    trace_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    if debug:
        print(f"[Router] Task Type: {task_type} | Trace ID: {trace_id} | Timestamp: {timestamp}")

    if task_type == "code":
        response = openai.generate_response(task)
    elif task_type == "ethics":
        response = anthropic.generate_response(task)
    elif task_type == "web":
        response = perplexity.generate_response(task)
    elif task_type == "creative":
        response = gemini.generate_response(task)
    elif task_type == "general":
        response = azure.generate_response(task)
    else:
        response = "[Router Error] Unknown task type."

    if debug:
        return {
            "trace_id": trace_id,
            "timestamp": timestamp,
            "task": task,
            "type": task_type,
            "output": response,
        }

    return response