"""
Tool Executor for OpenAI Function Calls
========================================
Safe handlers for executing OpenAI tool calls with LUKHAS governance.
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import subprocess
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

import aiohttp
import docker
from bs4 import BeautifulSoup

# Guardian System Integration
try:
    from candidate.governance.guardian_system import GuardianSystem
except ImportError:
    GuardianSystem = None
    
try:
    from candidate.core.security import AGISecuritySystem
except ImportError:
    AGISecuritySystem = None

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
            os.getenv("LUKHAS_ENABLE_CODE_EXEC", "true").lower() == "true"
        )

        # Queue directory for scheduled tasks
        self.schedule_queue_dir = Path("data/scheduled_tasks")
        self.schedule_queue_dir.mkdir(parents=True, exist_ok=True)

        # Security configuration
        self.security_config = self._init_security_config()
        
        # Rate limiting
        self._rate_limiter = {}
        self._request_timestamps = {}

        # Resource monitoring
        self._active_executions = 0
        self._max_concurrent_executions = int(os.getenv("LUKHAS_MAX_CONCURRENT_EXECUTIONS", "10"))
        
        # Docker client for sandboxed execution
        self._docker_client = None
        
        # Audit logging
        self.audit_log = Path("data/audit/tool_execution.log")
        self.audit_log.parent.mkdir(parents=True, exist_ok=True)

        # Track execution metrics
        self.metrics = {
            "retrieve_knowledge": 0,
            "open_url": 0,
            "schedule_task": 0,
            "exec_code": 0,
            "blocked": 0,
            "security_violations": 0,
            "rate_limited": 0,
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

        # Check against allowlist if configured
        allowed_domains = self.config.get("allowed_domains", [])
        if allowed_domains:
            from urllib.parse import urlparse

            domain = urlparse(url).netloc
            if domain not in allowed_domains:
                return f"Domain {domain} is not in the allowlist."

        # Implement comprehensive safe web scraping
        try:
            return await self._safe_web_scraper(url)
        except Exception as e:
            logger.error(f"Web scraping failed for {url}: {str(e)}", exc_info=True)
            return f"Failed to access {url}: {str(e)}"

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

        # Implement Docker-based sandboxed execution
        try:
            return await self._sandboxed_code_execution(language, source)
        except Exception as e:
            logger.error(f"Sandboxed execution failed: {str(e)}", exc_info=True)
            return f"Code execution failed: {str(e)}"

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

    def _init_security_config(self) -> Dict[str, Any]:
        """Initialize security configuration"""
        return {
            "allowed_domains": set(self.config.get("allowed_domains", [
                "openai.com",
                "anthropic.com", 
                "github.com",
                "arxiv.org",
                "wikipedia.org",
                "stackoverflow.com"
            ])),
            "blocked_patterns": [
                r"javascript:",
                r"data:",
                r"file://",
                r"ftp://",
                r"localhost",
                r"127\.0\.0\.1",
                r"192\.168\.",
                r"10\.",
                r"172\."
            ],
            "max_content_size": int(os.getenv("LUKHAS_MAX_CONTENT_SIZE", "1048576")),  # 1MB
            "request_timeout": int(os.getenv("LUKHAS_REQUEST_TIMEOUT", "30")),  # 30 seconds
            "rate_limit_requests": int(os.getenv("LUKHAS_RATE_LIMIT_REQUESTS", "10")),
            "rate_limit_window": int(os.getenv("LUKHAS_RATE_LIMIT_WINDOW", "60")),  # 1 minute
            "user_agent": "LUKHAS-AI-ToolExecutor/1.0 (Safe Web Scraper)"
        }

    async def _check_rate_limit(self, tool_name: str, user_id: str = "default") -> bool:
        """Check if request is within rate limits"""
        key = f"{tool_name}:{user_id}"
        now = time.time()
        
        if key not in self._request_timestamps:
            self._request_timestamps[key] = []
            
        # Clean old timestamps
        window_start = now - self.security_config["rate_limit_window"]
        self._request_timestamps[key] = [
            ts for ts in self._request_timestamps[key] if ts > window_start
        ]
        
        # Check rate limit
        if len(self._request_timestamps[key]) >= self.security_config["rate_limit_requests"]:
            self.metrics["rate_limited"] += 1
            return False
            
        self._request_timestamps[key].append(now)
        return True

    def _validate_url(self, url: str) -> bool:
        """Validate URL against security policies"""
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in ["http", "https"]:
                logger.warning(f"Blocked invalid scheme: {parsed.scheme}")
                return False
                
            # Check domain allowlist
            if self.security_config["allowed_domains"]:
                if parsed.netloc not in self.security_config["allowed_domains"]:
                    logger.warning(f"Blocked non-allowlisted domain: {parsed.netloc}")
                    return False
            
            # Check blocked patterns
            for pattern in self.security_config["blocked_patterns"]:
                if re.search(pattern, url, re.IGNORECASE):
                    logger.warning(f"Blocked URL matching pattern {pattern}: {url}")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return False

    async def _safe_web_scraper(self, url: str) -> str:
        """Safe web scraping with comprehensive security"""
        start_time = time.time()
        
        # Validate URL
        if not self._validate_url(url):
            self.metrics["security_violations"] += 1
            await self._audit_log("url_blocked", {"url": url, "reason": "security_validation_failed"})
            return f"URL blocked by security policy: {url}"
            
        # Check rate limits
        if not await self._check_rate_limit("open_url"):
            await self._audit_log("rate_limited", {"tool": "open_url", "url": url})
            return "Rate limit exceeded. Please wait before making more requests."
        
        try:
            # Create aiohttp session with security headers
            connector = aiohttp.TCPConnector(
                limit=10,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
            
            timeout = aiohttp.ClientTimeout(
                total=self.security_config["request_timeout"],
                connect=10
            )
            
            headers = {
                "User-Agent": self.security_config["user_agent"],
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=headers
            ) as session:
                
                async with session.get(url, allow_redirects=True, max_redirects=3) as response:
                    # Check content size
                    content_length = response.headers.get('content-length')
                    if content_length and int(content_length) > self.security_config["max_content_size"]:
                        await self._audit_log("content_too_large", {"url": url, "size": content_length})
                        return f"Content too large ({content_length} bytes). Maximum allowed: {self.security_config['max_content_size']}"
                    
                    # Check content type
                    content_type = response.headers.get('content-type', '').lower()
                    if not any(ct in content_type for ct in ['text/', 'application/json', 'application/xml']):
                        await self._audit_log("unsupported_content_type", {"url": url, "content_type": content_type})
                        return f"Unsupported content type: {content_type}"
                    
                    # Read content with size limit
                    content = b""
                    size = 0
                    async for chunk in response.content.iter_chunked(8192):
                        size += len(chunk)
                        if size > self.security_config["max_content_size"]:
                            await self._audit_log("content_too_large_streaming", {"url": url, "size": size})
                            return f"Content too large during streaming. Maximum allowed: {self.security_config['max_content_size']}"
                        content += chunk
                    
                    # Parse and extract content
                    text_content = content.decode('utf-8', errors='ignore')
                    extracted = await self._extract_safe_content(text_content, url)
                    
                    elapsed = time.time() - start_time
                    await self._audit_log("web_scrape_success", {
                        "url": url,
                        "content_size": len(text_content),
                        "extracted_size": len(extracted),
                        "elapsed_time": elapsed,
                        "status_code": response.status
                    })
                    
                    return extracted
                    
        except asyncio.TimeoutError:
            await self._audit_log("web_scrape_timeout", {"url": url})
            return f"Request timed out after {self.security_config['request_timeout']} seconds"
        except aiohttp.ClientError as e:
            await self._audit_log("web_scrape_client_error", {"url": url, "error": str(e)})
            return f"Network error accessing {url}: {str(e)}"
        except Exception as e:
            await self._audit_log("web_scrape_error", {"url": url, "error": str(e)})
            return f"Error scraping {url}: {str(e)}"

    async def _extract_safe_content(self, html_content: str, url: str) -> str:
        """Extract and sanitize content from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove dangerous elements
            for element in soup(["script", "style", "meta", "link", "noscript"]):
                element.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else "No title"
            
            # Extract main content
            main_content = ""
            
            # Try to find main content areas
            content_selectors = [
                'main', 'article', '[role="main"]',
                '.content', '.main-content', '.post-content',
                '.entry-content', '.article-content'
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    main_content = "\n".join(el.get_text(strip=True, separator=' ') for el in elements[:3])
                    break
            
            # Fallback to paragraphs and headings
            if not main_content:
                elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'], limit=10)
                main_content = "\n".join(el.get_text(strip=True) for el in elements if el.get_text(strip=True))
            
            # Extract metadata
            description = soup.find('meta', attrs={'name': 'description'})
            description_text = description.get('content', '') if description else ""
            
            # Format response
            response_parts = [f"Title: {title_text}"]
            if description_text:
                response_parts.append(f"Description: {description_text}")
            
            response_parts.append(f"URL: {url}")
            response_parts.append("Content:")
            response_parts.append(main_content[:2000] + "..." if len(main_content) > 2000 else main_content)
            
            return "\n\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Content extraction error: {e}")
            return f"Content extraction failed: {str(e)}"

    async def _get_docker_client(self):
        """Get or create Docker client"""
        if self._docker_client is None:
            try:
                self._docker_client = docker.from_env()
                # Test connection
                self._docker_client.ping()
                logger.info("Docker client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Docker client: {e}")
                self._docker_client = None
                raise RuntimeError(f"Docker not available: {e}")
        return self._docker_client

    async def _sandboxed_code_execution(self, language: str, source: str) -> str:
        """Execute code in a secure Docker sandbox"""
        if self._active_executions >= self._max_concurrent_executions:
            return f"Maximum concurrent executions ({self._max_concurrent_executions}) reached. Please wait."
        
        self._active_executions += 1
        execution_id = hashlib.sha256(f"{time.time()}{source}".encode()).hexdigest()[:12]
        
        try:
            await self._audit_log("code_execution_start", {
                "execution_id": execution_id,
                "language": language,
                "code_length": len(source),
                "active_executions": self._active_executions
            })
            
            # Enhanced security checks
            if not self._validate_code_security(source, language):
                self.metrics["security_violations"] += 1
                await self._audit_log("code_security_violation", {"execution_id": execution_id, "language": language})
                return "Code contains security violations and cannot be executed."
            
            docker_client = await self._get_docker_client()
            
            # Language-specific container configurations
            container_configs = {
                "python": {
                    "image": "python:3.11-alpine",
                    "command": ["python", "-c"],
                    "working_dir": "/sandbox",
                    "user": "nobody"
                },
                "javascript": {
                    "image": "node:18-alpine", 
                    "command": ["node", "-e"],
                    "working_dir": "/sandbox",
                    "user": "nobody"
                },
                "bash": {
                    "image": "alpine:latest",
                    "command": ["sh", "-c"],
                    "working_dir": "/sandbox", 
                    "user": "nobody"
                }
            }
            
            if language not in container_configs:
                return f"Language {language} not supported for sandboxed execution"
            
            config = container_configs[language]
            
            # Create temporary directory for execution
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write source code to file
                source_file = Path(temp_dir) / f"code.{language}"
                source_file.write_text(source)
                
                # Container resource limits
                container_limits = {
                    "mem_limit": "128m",
                    "memswap_limit": "128m", 
                    "cpu_period": 100000,
                    "cpu_quota": 50000,  # 50% of one CPU
                    "pids_limit": 100
                }
                
                # Network and security restrictions
                security_opts = [
                    "no-new-privileges:true"
                ]
                
                try:
                    # Run container with timeout
                    container = docker_client.containers.run(
                        image=config["image"],
                        command=config["command"] + [source],
                        remove=True,
                        stdout=True,
                        stderr=True,
                        timeout=30,  # 30 second timeout
                        working_dir=config["working_dir"],
                        user=config["user"],
                        network_disabled=True,  # No network access
                        read_only=True,  # Read-only filesystem
                        security_opt=security_opts,
                        **container_limits
                    )
                    
                    output = container.decode('utf-8') if isinstance(container, bytes) else str(container)
                    
                    await self._audit_log("code_execution_success", {
                        "execution_id": execution_id,
                        "language": language,
                        "output_length": len(output)
                    })
                    
                    # Truncate output if too long
                    if len(output) > 4000:
                        output = output[:4000] + "\n... (output truncated)"
                        
                    return f"Execution completed successfully:\n\n{output}"
                    
                except docker.errors.ContainerError as e:
                    error_output = e.stderr.decode('utf-8') if e.stderr else "No error details"
                    await self._audit_log("code_execution_container_error", {
                        "execution_id": execution_id,
                        "exit_code": e.exit_status,
                        "error": error_output
                    })
                    return f"Code execution failed with exit code {e.exit_status}:\n{error_output}"
                    
                except Exception as e:
                    await self._audit_log("code_execution_docker_error", {
                        "execution_id": execution_id,
                        "error": str(e)
                    })
                    return f"Docker execution error: {str(e)}"
                    
        except RuntimeError as e:
            return str(e)
        except Exception as e:
            await self._audit_log("code_execution_error", {
                "execution_id": execution_id,
                "error": str(e)
            })
            return f"Sandboxed execution failed: {str(e)}"
        finally:
            self._active_executions -= 1

    def _validate_code_security(self, source: str, language: str) -> bool:
        """Enhanced security validation for code"""
        # Common dangerous patterns across languages
        dangerous_patterns = {
            "all": [
                r"__import__",
                r"exec\s*\(",
                r"eval\s*\(",
                r"open\s*\(",
                r"file\s*\(",
                r"input\s*\(",
                r"raw_input\s*\(",
                r"subprocess",
                r"os\.",
                r"sys\.",
                r"socket",
                r"urllib",
                r"requests",
                r"http",
                r"net/http",
                r"fetch\s*\(",
                r"require\s*\(",
                r"import\s+os",
                r"import\s+sys",
                r"import\s+subprocess",
                r"from\s+os",
                r"from\s+sys",
                r"\.\.\/",  # Directory traversal
                r"\.\.\\",  # Directory traversal (Windows)
            ],
            "python": [
                r"compile\s*\(",
                r"globals\s*\(",
                r"locals\s*\(",
                r"vars\s*\(",
                r"dir\s*\(",
                r"hasattr\s*\(",
                r"getattr\s*\(",
                r"setattr\s*\(",
                r"delattr\s*\(",
                r"__.*__",  # Dunder methods
                r"threading",
                r"multiprocessing",
                r"ctypes"
            ],
            "javascript": [
                r"require\s*\(",
                r"process\.",
                r"global\.",
                r"window\.",
                r"document\.",
                r"location\.",
                r"navigator\.",
                r"XMLHttpRequest",
                r"fetch\s*\(",
                r"WebSocket",
                r"setTimeout",
                r"setInterval",
                r"Function\s*\(",
                r"constructor"
            ],
            "bash": [
                r"curl\s",
                r"wget\s", 
                r"nc\s",
                r"netcat\s",
                r"ssh\s",
                r"scp\s",
                r"rsync\s",
                r"rm\s+-rf",
                r"dd\s",
                r"mkfs\.",
                r"mount\s",
                r"umount\s",
                r"fdisk\s",
                r"iptables\s",
                r"sudo\s",
                r"su\s",
                r"passwd\s",
                r"adduser\s",
                r"userdel\s",
                r"kill\s+-9",
                r"pkill\s",
                r"systemctl\s",
                r"service\s",
                r"crontab\s"
            ]
        }
        
        # Check patterns for current language and all languages
        patterns_to_check = dangerous_patterns.get("all", []) + dangerous_patterns.get(language, [])
        
        for pattern in patterns_to_check:
            if re.search(pattern, source, re.IGNORECASE | re.MULTILINE):
                logger.warning(f"Blocked dangerous pattern in {language} code: {pattern}")
                return False
        
        # Additional checks
        if len(source) > 10000:  # Limit code size
            logger.warning("Code too large for execution")
            return False
            
        return True

    async def _audit_log(self, event: str, data: Dict[str, Any]):
        """Log security and execution events"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": event,
                "data": data
            }
            
            # Append to audit log
            with open(self.audit_log, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
                
        except Exception as e:
            logger.error(f"Audit logging failed: {e}")


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
