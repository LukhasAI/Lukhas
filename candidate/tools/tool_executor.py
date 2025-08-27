"""
Tool Executor for OpenAI Function Calls
========================================
Safe handlers for executing OpenAI tool calls with LUKHAS governance.
"""

import hashlib
import json
import logging
import os
import time
import tempfile
import shutil
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
import docker

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
            os.getenv("LUKHAS_ENABLE_BROWSER", "true").lower() == "true"
        )
        self.scheduler_enabled = (
            os.getenv("LUKHAS_ENABLE_SCHEDULER", "true").lower() == "true"
        )
        self.code_exec_enabled = (
            os.getenv("LUKHAS_ENABLE_CODE_EXEC", "true").lower() == "true" # Enabled for dev
        )

        # Queue directory for scheduled tasks
        self.schedule_queue_dir = Path("data/scheduled_tasks")
        self.schedule_queue_dir.mkdir(parents=True, exist_ok=True)

        # Rate limiting for browsing
        self.domain_last_request = {}
        self.rate_limit_seconds = self.config.get("rate_limit_seconds", 2)

        # Track execution metrics
        self.metrics = {
            "retrieve_knowledge": 0,
            "open_url": 0,
            "schedule_task": 0,
            "exec_code": 0,
            "blocked": 0,
        }

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
            if tool_name == "exec_code": # This is a sync function
                 result = self._exec_code(args)
            else:
                 result = await handler(args)

            self.metrics[tool_name] = self.metrics.get(tool_name, 0) + 1

            logger.info(
                f"Executed tool {tool_name}",
                extra={
                    "tool": tool_name,
                    "args": args,
                    "result_length": len(str(result)),
                },
            )

            return str(result)

        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name}", exc_info=e)
            return f"Tool execution failed: {str(e)}"

    async def _retrieve_knowledge(self, args: dict[str, Any]) -> str:
        """
        Retrieve knowledge from vector store or memory system.

        Args:
            args: {"query": str, "k": int}

        Returns:
            Retrieved content or safe stub
        """
        if not self.retrieval_enabled:
            return "Knowledge retrieval is currently disabled."

        query = args.get("query", "")
        min(args.get("k", 5), 10)  # Cap at 10 results

        # TODO: Integrate with actual RAG/vector store
        # For now, return contextual stub based on query

        if "ethical AI" in query.lower():
            return """Retrieved knowledge about ethical AI:
1. Transparency and Explainability: AI systems should be interpretable with clear documentation
2. Fairness and Non-discrimination: AI must avoid bias and ensure equitable treatment
3. Privacy and Security: Strong data protection and user consent mechanisms are essential
4. Human Oversight: Maintain meaningful human control over AI decisions
5. Accountability: Clear responsibility chains for AI system outcomes"""

        elif "openai" in query.lower() and "2024" in query:
            return """Retrieved knowledge about OpenAI 2024:
- GPT-4 Turbo announced with 128K context window
- Custom GPTs marketplace launched
- Assistant API v2 with improved function calling
- DALL-E 3 integration with ChatGPT
- Advanced voice capabilities released"""

        else:
            # Generic fallback
            return f"No specific knowledge found for query: '{query}'. Consider rephrasing or trying different keywords."

    async def _open_url(self, args: dict[str, Any]) -> str:
        """
        Browse a URL and extract content.

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

        # Validate URL
        if not url.startswith(("http://", "https://")):
            return f"Invalid URL format: {url}"

        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        # Check against allowlist if configured
        allowed_domains = self.config.get("allowed_domains", [])
        if allowed_domains and domain not in allowed_domains:
            self.metrics["blocked"] += 1
            return f"Domain {domain} is not in the allowlist."

        # Rate limiting
        current_time = time.time()
        last_request_time = self.domain_last_request.get(domain, 0)
        if current_time - last_request_time < self.rate_limit_seconds:
            self.metrics["blocked"] += 1
            return f"Rate limit exceeded for {domain}. Please wait a moment before trying again."
        self.domain_last_request[domain] = current_time

        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
                headers = {
                    "User-Agent": "LUKHAS-AI-Tool-Executor/1.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                }
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type.lower():
                    return f"Cannot parse content of type '{content_type}'. Only HTML is supported."

                if len(response.content) > 2 * 1024 * 1024:  # 2MB limit
                    return "Page content is too large to process (limit is 2MB)."

                soup = BeautifulSoup(response.content, "lxml")

                for tag in soup(["script", "style", "nav", "footer", "aside"]):
                    tag.decompose()

                title = soup.title.string if soup.title else ""
                body_text = soup.body.get_text(separator=' ', strip=True) if soup.body else ""

                full_text = f"Title: {title}\n\n{body_text}".strip()

                max_length = self.config.get("max_content_length", 8000)
                if len(full_text) > max_length:
                    full_text = full_text[:max_length] + f"... (truncated from {len(full_text)} chars)"

                return f"Successfully retrieved and parsed content from {url}:\n\n{full_text}"

        except httpx.TimeoutException:
            return f"Request to {url} timed out."
        except httpx.RequestError as e:
            logger.warning(f"Failed to open URL {url}: {e}")
            return f"Error fetching URL: {e}"
        except Exception as e:
            logger.error(f"An unexpected error occurred while opening URL {url}", exc_info=e)
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

    def _exec_code(self, args: dict[str, Any]) -> str:
        """
        Execute code in a sandboxed environment using Docker.

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
            return f"Language '{language}' is not supported. Use one of: {allowed_languages}"

        # Basic security check on source before handing to Docker
        dangerous_patterns = {
            "python": ["__import__", "socket", "os", "subprocess", "eval", "exec"],
            "javascript": ["require('fs')", "require('child_process')", "eval"],
            "bash": [":(){:|:&};:", "rm -rf"], # fork bomb and dangerous rm
        }
        for pattern in dangerous_patterns.get(language, []):
            if pattern in source:
                self.metrics["blocked"] += 1
                return f"Security violation: pattern '{pattern}' is not allowed for {language}."

        try:
            client = docker.from_env(timeout=60)
        except docker.errors.DockerException:
            return "Docker is not available or configured correctly. Cannot execute code."

        temp_dir = tempfile.mkdtemp()

        try:
            dockerfile_content, filename, cmd = self._get_docker_config(language)

            with open(os.path.join(temp_dir, filename), "w", encoding="utf-8") as f:
                f.write(source)

            with open(os.path.join(temp_dir, "Dockerfile"), "w", encoding="utf-8") as f:
                f.write(dockerfile_content.format(filename=filename))

            image_tag = f"lukhas-exec-{hashlib.md5(source.encode()).hexdigest()[:12]}"

            # Build the image
            try:
                logger.info(f"Building docker image {image_tag} for {language} code.")
                image, _ = client.images.build(path=temp_dir, tag=image_tag, rm=True, forcerm=True, timeout=120)
            except docker.errors.BuildError as e:
                logger.error(f"Docker build failed for {language}: {e}")
                log_str = "\n".join([str(line) for line in e.build_log])
                return f"Docker build failed:\n{log_str[:2000]}"

            # Run the container
            container = None
            try:
                logger.info(f"Running container for image {image_tag}.")
                container = client.containers.run(
                    image.id,
                    command=cmd.format(filename=filename),
                    detach=True,
                    mem_limit="256m",
                    cpus=0.5,
                    network_disabled=True,
                )

                # Wait for container to finish, with timeout
                try:
                    container.wait(timeout=30)
                    stdout = container.logs(stdout=True, stderr=False).decode('utf-8', 'ignore')
                    stderr = container.logs(stdout=False, stderr=True).decode('utf-8', 'ignore')
                    output = f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}"
                except Exception as wait_e: # Container ran too long
                    container.kill()
                    output = f"Execution timed out after 30 seconds."

            except docker.errors.ContainerError as e:
                logger.error(f"Docker container failed for {language}: {e}")
                return f"Container execution failed: {e.stderr.decode('utf-8', 'ignore') if e.stderr else str(e)}"
            finally:
                if container:
                    try:
                        container.remove(force=True)
                    except docker.errors.NotFound:
                        pass
                # Clean up the image
                try:
                    client.images.remove(image.id, force=True)
                except docker.errors.ImageNotFound:
                    pass
                except Exception as e:
                    logger.warning(f"Failed to remove docker image {image_tag}: {e}")

            return f"Execution successful:\n---\n{output[:8000]}"

        except Exception as e:
            logger.error(f"An unexpected error occurred during code execution: {e}", exc_info=True)
            return f"An unexpected error occurred during execution: {str(e)}"
        finally:
            shutil.rmtree(temp_dir)

    def _get_docker_config(self, language: str) -> tuple[str, str, str]:
        if language == "python":
            return """
FROM python:3.11-slim
WORKDIR /app
COPY {filename} .
""", "script.py", "python {filename}"
        elif language == "javascript":
            return """
FROM node:20-slim
WORKDIR /app
COPY {filename} .
""", "script.js", "node {filename}"
        elif language == "bash":
            return """
FROM bash:5.2
WORKDIR /app
COPY {filename} .
RUN chmod +x {filename}
""", "script.sh", "./{filename}"
        else:
            raise ValueError(f"Unsupported language: {language}")

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
            if name == "exec_code":
                # Run sync function in async context
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, self._exec_code, json.loads(arguments))
            else:
                result = await self.execute(name, arguments)

            # Format for OpenAI
            results.append({"tool_call_id": tool_id, "role": "tool", "content": str(result)})

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
    response = await client.chat.completions.create(messages=messages, **kwargs)

    return response
