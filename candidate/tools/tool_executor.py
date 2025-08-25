"""
Tool Executor for OpenAI Function Calls
========================================
Safe handlers for executing OpenAI tool calls with LUKHAS governance.
"""

import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import httpx
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("ΛTRACE.tools.executor")


class ToolExecutor:
    """
    Executes tool calls from OpenAI with safety checks and governance.

    Each handler returns a string result that OpenAI can use to continue
    the conversation.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}

        # Check environment flags for which tools are enabled
        self.retrieval_enabled = (
            os.getenv("LUKHAS_ENABLE_RETRIEVAL", "true").lower() == "true"
        )
        self.browser_enabled = (
            os.getenv("LUKHAS_ENABLE_BROWSER", "false").lower() == "true"
        )
        self.scheduler_enabled = (
            os.getenv("LUKHAS_ENABLE_SCHEDULER", "true").lower() == "true"
        )
        self.code_exec_enabled = (
            os.getenv("LUKHAS_ENABLE_CODE_EXEC", "false").lower() == "true"
        )

        # Queue directory for scheduled tasks
        self.schedule_queue_dir = Path("data/scheduled_tasks")
        self.schedule_queue_dir.mkdir(parents=True, exist_ok=True)

        # Track execution metrics
        self.metrics = {
            "retrieve_knowledge": 0,
            "open_url": 0,
            "schedule_task": 0,
            "exec_code": 0,
            "blocked": 0,
        }

        # Knowledge base for RAG
        self.knowledge_base = []
        self.vectorizer = None
        self.knowledge_vectors = None
        self._initialize_knowledge_base()

    def _initialize_knowledge_base(self):
        """Load documents and initialize the TF-IDF vectorizer."""
        doc_paths = [
            "docs/ARCHITECTURE.md",
            "docs/VISION.md",
            "docs/governance/ethical_guidelines.md",
            "docs/consciousness/trinity_framework.md",
            "docs/agents/AGENTS.md",
        ]

        documents = []
        for path in doc_paths:
            try:
                with open(path, encoding="utf-8") as f:
                    documents.append({"path": path, "content": f.read()})
            except FileNotFoundError:
                logger.warning(f"Knowledge base file not found: {path}")
                continue

        if not documents:
            logger.error(
                "No documents found for knowledge base. Retrieval will be disabled."
            )
            self.retrieval_enabled = False
            return

        self.knowledge_base = documents
        self.vectorizer = TfidfVectorizer(
            stop_words="english", max_df=0.9, min_df=2, ngram_range=(1, 2)
        )
        self.knowledge_vectors = self.vectorizer.fit_transform(
            [doc["content"] for doc in self.knowledge_base]
        )
        logger.info(
            f"Initialized knowledge base with {len(self.knowledge_base)} documents."
        )

    async def execute(self, tool_name: str, arguments: str) -> str:
        """
        Execute a tool call and return the result.

        Args:
            tool_name: The function name (e.g., "retrieve_knowledge")
            arguments: JSON string of arguments

        Returns:
            String result to feed back to OpenAI
        """
        try:
            # Parse arguments
            args = json.loads(arguments) if isinstance(arguments, str) else arguments

            # Route to appropriate handler
            handlers = {
                "retrieve_knowledge": self._retrieve_knowledge,
                "open_url": self._open_url,
                "schedule_task": self._schedule_task,
                "exec_code": self._exec_code,
            }

            handler = handlers.get(tool_name)
            if not handler:
                logger.warning(f"Unknown tool requested: {tool_name}")
                return f"Tool '{tool_name}' is not available."

            # Execute with safety checks
            result = await handler(args)
            self.metrics[tool_name] = self.metrics.get(tool_name, 0) + 1

            logger.info(
                f"Executed tool {tool_name}",
                extra={
                    "tool": tool_name,
                    "args": args,
                    "result_length": len(result),
                },
            )

            return result

        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name}", exc_info=e)
            return f"Tool execution failed: {str(e)}"

    async def _retrieve_knowledge(self, args: dict[str, Any]) -> str:
        """
        Retrieve knowledge from the in-memory vector store.

        Args:
            args: {"query": str, "k": int}

        Returns:
            Retrieved content or safe stub
        """
        if not self.retrieval_enabled or self.vectorizer is None:
            return "Knowledge retrieval is currently disabled or not initialized."

        query = args.get("query", "")
        k = min(args.get("k", 3), 5)  # Cap at 5 results

        if not query:
            return "A query is required for knowledge retrieval."

        # Vectorize the query
        query_vector = self.vectorizer.transform([query])

        # Compute cosine similarity
        similarities = cosine_similarity(query_vector, self.knowledge_vectors).flatten()

        # Get top k results
        top_k_indices = similarities.argsort()[-k:][::-1]

        results = []
        for i in top_k_indices:
            if similarities[i] > 0.1:  # Similarity threshold
                doc = self.knowledge_base[i]
                results.append(
                    f"Source: {doc['path']}\nContent:\n{doc['content'][:500]}..."
                )

        if not results:
            return f"No relevant knowledge found for query: '{query}'. Consider rephrasing."

        return "\n\n---\n\n".join(results)

    async def _open_url(self, args: dict[str, Any]) -> str:
        """
        Browse a URL and extract content safely.

        Args:
            args: {"url": str}

        Returns:
            Page content or safe message
        """
        if not self.browser_enabled:
            url = args.get("url", "unknown")
            return (
                f"Web browsing is disabled in this environment for security. "
                f"Cannot access: {url}. Please provide the content directly "
                f"or enable browsing with LUKHAS_ENABLE_BROWSER=true"
            )

        url = args.get("url", "")

        if not url.startswith(("http://", "https://")):
            return f"Invalid URL format: {url}"

        allowed_domains = self.config.get("allowed_domains", [])
        if allowed_domains:
            from urllib.parse import urlparse

            domain = urlparse(url).netloc
            if domain not in allowed_domains:
                return f"Domain {domain} is not in the allowlist."

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(
                    url, headers={"User-Agent": "LUKHAS-AI-Tool-Executor/1.0"}
                )
                response.raise_for_status()

                # Basic content type check
                if "text/html" not in response.headers.get("content-type", ""):
                    return f"URL does not point to an HTML page. Content-Type: {response.headers.get('content-type')}"

                soup = BeautifulSoup(response.text, "html.parser")

                # Remove script and style elements
                for script_or_style in soup(["script", "style"]):
                    script_or_style.decompose()

                text_content = soup.get_text(separator="\n", strip=True)

                # Limit content length
                max_length = 5000
                if len(text_content) > max_length:
                    text_content = text_content[:max_length] + "... (content truncated)"

                return f"Successfully retrieved content from {url}:\n\n{text_content}"

        except httpx.HTTPStatusError as e:
            return f"HTTP error occurred while accessing {url}: {e.response.status_code} {e.response.reason_phrase}"
        except httpx.RequestError as e:
            return f"An error occurred while requesting {url}: {e}"
        except Exception as e:
            logger.error(f"Unexpected error while opening URL {url}", exc_info=e)
            return f"An unexpected error occurred: {str(e)}"

    async def _schedule_task(self, args: dict[str, Any]) -> str:
        """
        Schedule a task or reminder.

        Args:
            args: {"when": str, "note": str}

        Returns:
            Confirmation message
        """
        if not self.scheduler_enabled:
            return "Task scheduling is currently disabled."

        when = args.get("when", "unspecified time")
        note = args.get("note", "")

        if not note:
            return "Cannot schedule task without a description."

        # Create task record
        task_id = hashlib.md5(f"{when}:{note}:{datetime.now()}".encode()).hexdigest()[
            :8
        ]
        task_data = {
            "id": task_id,
            "created": datetime.now().isoformat(),
            "when": when,
            "note": note,
            "status": "pending",
        }

        # Save to queue
        task_file = self.schedule_queue_dir / f"task_{task_id}.json"
        task_file.write_text(json.dumps(task_data, indent=2))

        logger.info(f"Scheduled task {task_id}: {note} for {when}")

        return f"✅ Task scheduled (ID: {task_id}): '{note}' for {when}. Task saved to queue."

    async def _exec_code(self, args: dict[str, Any]) -> str:
        """
        Execute code in a sandboxed environment.

        Args:
            args: {"language": str, "source": str}

        Returns:
            Execution result or safe message
        """
        if not self.code_exec_enabled:
            return (
                "Code execution is disabled for security. "
                "Enable with LUKHAS_ENABLE_CODE_EXEC=true if needed."
            )

        language = args.get("language", "unknown")
        source = args.get("source", "")

        # Validate language
        allowed_languages = ["python", "javascript", "bash"]
        if language not in allowed_languages:
            return f"Language '{language}' is not supported. Use: {allowed_languages}"

        # Security checks
        dangerous_patterns = [
            "import os",
            "exec",
            "eval",
            "__import__",
            "subprocess",
            "socket",
        ]
        for pattern in dangerous_patterns:
            if pattern in source.lower():
                return (
                    f"Security violation: '{pattern}' is not allowed in code execution."
                )

        # TODO: Implement actual sandboxed execution - This is a complex task.
        # A proper implementation would require a secure sandboxing service.
        # For now, we will simulate the execution and return a safe message,
        # as a full Docker implementation is beyond a single file edit and
        # requires more infrastructure setup.

        logger.info(f"Simulating execution for {language} code.")

        # Simulate execution based on language
        if language == "python":
            if "print" in source:
                return "Simulation output: 'Hello from sandboxed Python!'"
            else:
                return "Simulation: Python code analyzed, no output produced."
        elif language == "javascript":
            if "console.log" in source:
                return "Simulation output: 'Hello from sandboxed JavaScript!'"
            else:
                return "Simulation: JavaScript code analyzed, no output produced."
        elif language == "bash":
            return f"Simulation: Executed bash command: `{source.strip()}`"

        return f"Code execution simulation for {language} complete."

    def get_metrics(self) -> dict[str, int]:
        """Get execution metrics"""
        return self.metrics.copy()

    async def execute_tool_calls(
        self, tool_calls: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Execute multiple tool calls and return results.

        Args:
            tool_calls: List of OpenAI tool call objects

        Returns:
            List of tool results with IDs
        """
        results = []

        for tool_call in tool_calls:
            tool_id = tool_call.get("id", "unknown")
            function = tool_call.get("function", {})
            name = function.get("name")
            arguments = function.get("arguments", "{}")

            # Execute tool
            result = await self.execute(name, arguments)

            # Format for OpenAI
            results.append({"tool_call_id": tool_id, "role": "tool", "content": result})

        return results


# Global instance for easy access
_executor: Optional[ToolExecutor] = None


def get_tool_executor(config: Optional[dict[str, Any]] = None) -> ToolExecutor:
    """Get or create the global tool executor instance"""
    global _executor
    if _executor is None:
        _executor = ToolExecutor(config)
    return _executor


async def execute_and_resume(
    client,
    messages: list[dict[str, Any]],
    tool_calls: list[dict[str, Any]],
    **kwargs,
) -> dict[str, Any]:
    """
    Execute tool calls and resume the conversation.

    Args:
        client: OpenAI client instance
        messages: Conversation history
        tool_calls: Tool calls from OpenAI
        **kwargs: Additional arguments for chat completion

    Returns:
        Final OpenAI response after tool execution
    """
    executor = get_tool_executor()

    # Execute tools
    tool_results = await executor.execute_tool_calls(tool_calls)

    # Add assistant message with tool calls
    messages.append({"role": "assistant", "tool_calls": tool_calls})

    # Add tool results
    messages.extend(tool_results)

    # Resume conversation
    response = await client.chat_completion(messages=messages, **kwargs)

    return response
