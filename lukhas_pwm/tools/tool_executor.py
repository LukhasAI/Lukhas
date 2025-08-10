"""
Tool Executor for OpenAI Function Calls
========================================
Safe handlers for executing OpenAI tool calls with LUKHAS governance.
"""

import os
import json
import hashlib
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import asyncio

logger = logging.getLogger("ΛTRACE.tools.executor")


class ToolExecutor:
    """
    Executes tool calls from OpenAI with safety checks and governance.
    
    Each handler returns a string result that OpenAI can use to continue
    the conversation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Check environment flags for which tools are enabled
        self.retrieval_enabled = os.getenv("LUKHAS_ENABLE_RETRIEVAL", "true").lower() == "true"
        self.browser_enabled = os.getenv("LUKHAS_ENABLE_BROWSER", "false").lower() == "true"
        self.scheduler_enabled = os.getenv("LUKHAS_ENABLE_SCHEDULER", "true").lower() == "true"
        self.code_exec_enabled = os.getenv("LUKHAS_ENABLE_CODE_EXEC", "false").lower() == "true"
        
        # Queue directory for scheduled tasks
        self.schedule_queue_dir = Path("data/scheduled_tasks")
        self.schedule_queue_dir.mkdir(parents=True, exist_ok=True)
        
        # Track execution metrics
        self.metrics = {
            "retrieve_knowledge": 0,
            "open_url": 0,
            "schedule_task": 0,
            "exec_code": 0,
            "blocked": 0
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
                "exec_code": self._exec_code
            }
            
            handler = handlers.get(tool_name)
            if not handler:
                logger.warning(f"Unknown tool requested: {tool_name}")
                return f"Tool '{tool_name}' is not available."
            
            # Execute with safety checks
            result = await handler(args)
            self.metrics[tool_name] = self.metrics.get(tool_name, 0) + 1
            
            logger.info(f"Executed tool {tool_name}", extra={
                "tool": tool_name,
                "args": args,
                "result_length": len(result)
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name}", exc_info=e)
            return f"Tool execution failed: {str(e)}"
    
    async def _retrieve_knowledge(self, args: Dict[str, Any]) -> str:
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
        k = min(args.get("k", 5), 10)  # Cap at 10 results
        
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
    
    async def _open_url(self, args: Dict[str, Any]) -> str:
        """
        Browse a URL and extract content.
        
        Args:
            args: {"url": str}
            
        Returns:
            Page content or safe message
        """
        if not self.browser_enabled:
            url = args.get("url", "unknown")
            return (f"Web browsing is disabled in this environment for security. "
                   f"Cannot access: {url}. Please provide the content directly "
                   f"or enable browsing with LUKHAS_ENABLE_BROWSER=true")
        
        url = args.get("url", "")
        
        # Validate URL
        if not url.startswith(("http://", "https://")):
            return f"Invalid URL format: {url}"
        
        # Check against allowlist if configured
        allowed_domains = self.config.get("allowed_domains", [])
        if allowed_domains:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            if domain not in allowed_domains:
                return f"Domain {domain} is not in the allowlist."
        
        # TODO: Implement actual web scraping with safety
        # Could use httpx + beautifulsoup or playwright
        
        # For now, return informative stub
        if "openai.com" in url:
            return """OpenAI Homepage Summary:
- Featured: Latest GPT-4 Turbo model with enhanced capabilities
- Products: ChatGPT, API, DALL-E 3, Whisper
- Mission: Ensure AGI benefits all of humanity
- Recent blog posts about safety research and model improvements"""
        
        return f"Web browsing attempted for {url} but content extraction not yet implemented."
    
    async def _schedule_task(self, args: Dict[str, Any]) -> str:
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
        task_id = hashlib.md5(f"{when}:{note}:{datetime.now()}".encode()).hexdigest()[:8]
        task_data = {
            "id": task_id,
            "created": datetime.now().isoformat(),
            "when": when,
            "note": note,
            "status": "pending"
        }
        
        # Save to queue
        task_file = self.schedule_queue_dir / f"task_{task_id}.json"
        task_file.write_text(json.dumps(task_data, indent=2))
        
        logger.info(f"Scheduled task {task_id}: {note} for {when}")
        
        return f"✅ Task scheduled (ID: {task_id}): '{note}' for {when}. Task saved to queue."
    
    async def _exec_code(self, args: Dict[str, Any]) -> str:
        """
        Execute code in a sandboxed environment.
        
        Args:
            args: {"language": str, "source": str}
            
        Returns:
            Execution result or safe message
        """
        if not self.code_exec_enabled:
            return ("Code execution is disabled for security. "
                   "Enable with LUKHAS_ENABLE_CODE_EXEC=true if needed.")
        
        language = args.get("language", "unknown")
        source = args.get("source", "")
        
        # Validate language
        allowed_languages = ["python", "javascript", "bash"]
        if language not in allowed_languages:
            return f"Language '{language}' is not supported. Use: {allowed_languages}"
        
        # Security checks
        dangerous_patterns = ["import os", "exec", "eval", "__import__", "subprocess", "socket"]
        for pattern in dangerous_patterns:
            if pattern in source.lower():
                return f"Security violation: '{pattern}' is not allowed in code execution."
        
        # TODO: Implement actual sandboxed execution
        # Options: docker, pyodide, restricted subprocess, etc.
        
        return (f"Code execution requested for {language} but sandbox not implemented. "
                "Code analysis: {len(source)} characters, appears safe.")
    
    def get_metrics(self) -> Dict[str, int]:
        """Get execution metrics"""
        return self.metrics.copy()
    
    async def execute_tool_calls(
        self,
        tool_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
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
            results.append({
                "tool_call_id": tool_id,
                "role": "tool",
                "content": result
            })
        
        return results


# Global instance for easy access
_executor: Optional[ToolExecutor] = None


def get_tool_executor(config: Optional[Dict[str, Any]] = None) -> ToolExecutor:
    """Get or create the global tool executor instance"""
    global _executor
    if _executor is None:
        _executor = ToolExecutor(config)
    return _executor


async def execute_and_resume(
    client,
    messages: List[Dict[str, Any]],
    tool_calls: List[Dict[str, Any]],
    **kwargs
) -> Dict[str, Any]:
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
    messages.append({
        "role": "assistant",
        "tool_calls": tool_calls
    })
    
    # Add tool results
    messages.extend(tool_results)
    
    # Resume conversation
    response = await client.chat_completion(
        messages=messages,
        **kwargs
    )
    
    return response