log = logging.getLogger(__name__)
"""
LUKHΛS AI System - AI Integration Manager
File: ai_integration_manager.py
Path: integration/ai_integration_manager.py
Created: Unknown (Original by LUKHΛS AI Team)
Modified: 2024-07-26
Version: 1.0 (Standardized)
"""
# ΛTAGS: [Integration, AI_Services, TaskDelegation, OpenAI, Claude, GitHubCopilot]
# ΛNOTE: This manager orchestrates task delegation to external AI services.
import asyncio
import json

# Standard Library Imports
import os  # For example
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Union

# Third-Party Imports
import structlog

AIOHTTP_AVAILABLE_FLAG = False
try:
    import aiohttp

    AIOHTTP_AVAILABLE_FLAG = True
except ImportError:
    log_init_aim_aio = structlog.get_logger(__name__)
    log_init_aim_aio.warning("aiohttp lib not found. AIIntegrationManager async HTTP calls will use placeholder/fail.")

    class AIOHTTPClientSessionPH:
        async def __aenter__(self):
            return self

        async def __aexit__(self, et, ev, tb):
            pass

        async def post(self, u, h, j, timeout=0):

            class MR:
                status = 503

                async def json(self):
                    return {"error": "aiohttp_ph_err"}

                async def text(self):
                    return "aiohttp_ph_err_txt"

            return MR()

    aiohttp = type(
        "aiohttp_placeholder",
        (object,),
        {"ClientSession": AIOHTTPClientSessionPH},
    )()

log = structlog.get_logger(__name__)


def lukhas_tier_required(level: int):  # Placeholder:

    def decorator(func):
        func._lukhas_tier = level
        return func

    return decorator


DEFAULT_LUKHAS_AI_INTEGRATION_WORKSPACE = Path("./.lukhas_ai_integration_data")  # Changed name
DEFAULT_AI_CONFIG_FILENAME_STR = "ai_services_config.json"
DEFAULT_AI_RESPONSES_DIR_STR = "ai_service_responses"


@dataclass
class AITask:
    """Represents a task for an AI service."""

    id: str
    type: str
    prompt: str
    files: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    priority: int = 1


@dataclass
class AIResponse:
    """Represents a response from an AI service."""

    task_id: str
    service_name: str
    response_content: str
    metadata_dict: dict[str, Any] = field(default_factory=dict)
    success: bool = False


@lukhas_tier_required(2)
class AIIntegrationManager:
    """Manages task delegation to AI services like Claude, OpenAI, GitHub Copilot."""

    def __init__(
        self,
        workspace_root: Optional[Union[str, Path]] = None,
        config_filename: str = DEFAULT_AI_CONFIG_FILENAME_STR,
    ):
        self.workspace_path: Path = Path(workspace_root or DEFAULT_LUKHAS_AI_INTEGRATION_WORKSPACE).resolve()
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.cfg_file_path: Path = self.workspace_path / config_filename
        self.cfg: dict[str, Any] = self._load_ai_service_config()
        self.active_tasks_map: dict[str, AITask] = {}
        self.responses_storage_dir: Path = self.workspace_path / DEFAULT_AI_RESPONSES_DIR_STR
        self.responses_storage_dir.mkdir(parents=True, exist_ok=True)
        log.info(
            "AIIntegrationManager initialized.",
            workspace=str(self.workspace_path),
            cfg=str(self.cfg_file_path),
            resp_dir=str(self.responses_storage_dir),
        )
        if not self.cfg:
            log.warning(
                "AI service config empty. AI delegations may fail or use fallbacks.",
                cfg_path=str(self.cfg_file_path),
            )

    def _load_ai_service_config(self) -> dict[str, Any]:
        cfg_data: dict[str, Any] = {}
        log.debug("Loading AI service config.", path=str(self.cfg_file_path))
        if self.cfg_file_path.exists():
            try:
                with open(self.cfg_file_path, encoding="utf-8") as f:
                    cfg_data = json.load(f)
            except Exception as e:
                log.error(
                    "Failed to load/parse AI service config.",
                    path=str(self.cfg_file_path),
                    error=str(e),
                )
        else:
            log.warning(
                "AI service config file not found.",
                path=str(self.cfg_file_path),
            )
        # Env var overrides (LUKHΛS specific names)
        cfg_data.setdefault("anthropic_claude", {}).update(
            {
                "api_key": os.getenv(
                    "LUKHAS_ANTHROPIC_KEY",
                    cfg_data.get("anthropic_claude", {}).get("api_key"),
                ),
                "model": os.getenv(
                    "LUKHAS_CLAUDE_MODEL",
                    cfg_data.get("anthropic_claude", {}).get("model", "claude-3-opus-20240229"),
                ),
            }
        )  # Updated model
        cfg_data.setdefault("openai_gpt", {}).update(
            {
                "api_key": os.getenv(
                    "LUKHAS_OPENAI_KEY",
                    cfg_data.get("openai_gpt", {}).get("api_key"),
                ),
                "model": os.getenv(
                    "LUKHAS_OPENAI_MODEL",
                    cfg_data.get("openai_gpt", {}).get("model", "gpt-4-turbo"),
                ),
            }
        )  # Updated model
        cfg_data.setdefault("github_copilot", {}).update(
            {
                "cli_token": os.getenv(
                    "LUKHAS_GITHUB_TOKEN",
                    cfg_data.get("github_copilot", {}).get("cli_token"),
                ),
                "cli_enabled": bool(
                    os.getenv(
                        "LUKHAS_COPILOT_CLI_ENABLED",
                        cfg_data.get("github_copilot", {}).get("cli_enabled", False),
                    )
                ),
            }
        )
        log.info(
            "AI service config processed.",
            claude_key=bool(cfg_data["anthropic_claude"]["api_key"]),
            openai_key=bool(cfg_data["openai_gpt"]["api_key"]),
            gh_token=bool(cfg_data["github_copilot"]["cli_token"]),
        )
        return cfg_data

    async def _read_file_for_task(self, rel_path: str, max_chars: int = 2500) -> str:  # Renamed
        full_p = self.workspace_path / rel_path
        if not full_p.is_file():
            log.warning("File not found for task.", path=str(full_p))
            return f"[File N/A: {rel_path}]"
        try:
            with open(full_p, encoding="utf-8", errors="replace") as f:
                content = f.read(max_chars + 100)  # Read bit more
            return content[:max_chars] + "\n... [TRUNCATED]" if len(content) > max_chars else content
        except Exception as e:
            log.error("Error reading file for task.", path=str(full_p), error=str(e))
            return f"[Read Error: {rel_path} - {e}]"

    @lukhas_tier_required(3)
    async def delegate_to_claude(self, task: AITask) -> AIResponse:
        """Delegates a task to the Anthropic Claude API."""
        log.debug("Delegating to Claude.", task_id=task.id, type=task.type)
        cfg = self.cfg.get("anthropic_claude", {})
        key = cfg.get("api_key")
        if not key:
            log.error("Anthropic key N/A for Claude.", task=task.id)
            return AIResponse(task.id, "claude", "Error: Anthropic key missing.", {}, False)
        if not AIOHTTP_AVAILABLE_FLAG:
            log.error("aiohttp N/A for Claude.", task=task.id)
            return AIResponse(task.id, "claude", "Error: aiohttp missing.", {}, False)

        hdrs = {
            "x-api-key": key,
            "Content-Type": "application/json",
            "anthropic-version": cfg.get("api_version", "2023-06-01"),
        }
        # Build files context with proper async handling for consciousness node
        file_contents = []
        for fp in task.files:
            content = await self._read_file_for_task(fp, 3500)
            file_contents.append(f"\n\n--- File: {fp} ---\n{content}")
        files_ctx = "".join(file_contents)
        # Generic system prompt
        sys_prompt = "You are LUKHΛS AI assistant. Perform task with precision and symbolic awareness."
        user_prompt = f"Task ID: {task.id}\nType: {task.type}\nInstruction: {task.prompt}\nContext: {json.dumps(task.context,indent=2)}\nFiles:\n{files_ctx}\nResponse:"
        payload = {
            "model": cfg.get("model"),
            "max_tokens": cfg.get("max_tokens", 4096),
            "system": sys_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }  # Added system prompt
        try:
            async with aiohttp.ClientSession() as sess:  # type: ignore
                async with sess.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=hdrs,
                    json=payload,
                    timeout=180,
                ) as r:  # 3 min timeout
                    resp_data = await r.json()
                    if r.status == 200 and resp_data.get("content"):
                        text = "".join(b["text"] for b in resp_data["content"] if b["type"] == "text")
                        log.info("Claude task OK.", task=task.id, len=len(text))
                        return AIResponse(task.id, "claude_anthropic", text, resp_data, True)
                    else:
                        err = resp_data.get("error", {}).get("message", await r.text())
                        log.error(
                            "Claude API error.",
                            task=task.id,
                            status=r.status,
                            err=err,
                        )
                        return AIResponse(
                            task.id,
                            "claude_anthropic",
                            f"API Err {r.status}: {err}",
                            resp_data,
                            False,
                        )
        except asyncio.TimeoutError:
            log.error("Claude API timeout.", task=task.id)
            return AIResponse(
                task.id,
                "claude_anthropic",
                "Error: Claude timeout.",
                {},
                False,
            )
        except Exception as e:
            log.error(
                "Error delegating to Claude.",
                task=task.id,
                err=str(e),
                exc_info=True,
            )
            return AIResponse(task.id, "claude_anthropic", f"Request Err: {e}", {}, False)

    # ... Other delegate methods (OpenAI, Copilot) would be standardized similarly ...
    # Example for delegate_to_openai (conceptual, assuming OpenAI client is
    # different from Claude's raw HTTP)
    async def delegate_to_openai(self, task: AITask) -> AIResponse:
        log.debug("Delegating to OpenAI.", task_id=task.id, type=task.type)
        cfg = self.cfg.get("openai_gpt", {})
        key = cfg.get("api_key")
        if not key:
            log.error("OpenAI key N/A.", task=task.id)
            return AIResponse(task.id, "openai", "Error: OpenAI key missing.", {}, False)
        # This would use an OpenAI client, e.g. from the 'openai' library
        # For this example, I'll simulate a similar structure to Claude for consistency of the example
        # Actual OpenAI SDK usage would differ.
        log.warning("OpenAI delegation uses conceptual raw HTTP in this example; use OpenAI SDK in production.")
        if not AIOHTTP_AVAILABLE_FLAG:
            log.error("aiohttp N/A for OpenAI conceptual call.", task=task.id)
            return AIResponse(task.id, "openai", "Error: aiohttp missing.", {}, False)

        hdrs = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        # Build files context with proper async handling for consciousness node
        file_contents = []
        for fp in task.files:
            content = await self._read_file_for_task(fp, 1500)
            file_contents.append(f"\n\n--- File: {fp} ---\n{content}")
        files_ctx = "".join(file_contents)  # Smaller context for OpenAI

        sys_prompt = (
            "You are an expert AI assistant for LUKHΛS. Provide detailed, actionable software engineering analysis."
        )
        user_prompt = f"Task ID: {task.id}\nType: {task.type}\nInstruction: {task.prompt}\nContext: {json.dumps(task.context,indent=2)}\nFiles:\n{files_ctx}\nResponse:"
        payload = {
            "model": cfg.get("model"),
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": cfg.get("max_tokens", 2048),
            "temperature": 0.15,
        }
        try:
            async with aiohttp.ClientSession() as sess:  # type: ignore
                # type: ignore
                async with sess.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=hdrs,
                    json=payload,
                    timeout=120,
                ) as r:
                    resp_data = await r.json()
                    if r.status == 200 and resp_data.get("choices"):
                        text = resp_data["choices"][0]["message"]["content"]
                        log.info("OpenAI task OK.", task=task.id, len=len(text))
                        return AIResponse(task.id, "openai_gpt", text, resp_data, True)
                    else:
                        err = resp_data.get("error", {}).get("message", await r.text())
                        log.error(
                            "OpenAI API error.",
                            task=task.id,
                            status=r.status,
                            err=err,
                        )
                        return AIResponse(
                            task.id,
                            "openai_gpt",
                            f"API Err {r.status}: {err}",
                            resp_data,
                            False,
                        )
        except Exception as e:
            log.error(
                "Error delegating to OpenAI.",
                task=task.id,
                err=str(e),
                exc_info=True,
            )
            return AIResponse(task.id, "openai_gpt", f"Request Err: {e}", {}, False)

    # ΛNOTE: For GitHub Copilot CLI, ensure it's run in a non-blocking way if
    # manager is async.

    def use_github_copilot_cli(self, task: AITask) -> AIResponse:  # Renamed:
        """Uses GitHub Copilot CLI for code tasks. (Synchronous operation)"""
        log.debug("Using GitHub Copilot CLI.", task_id=task.id, type=task.type)
        # This is synchronous. If AIIntegrationManager is heavily async, run this in a thread pool.
        # e.g., await asyncio.to_thread(self._execute_copilot_cli_sync, task)
        cfg = self.cfg.get("github_copilot", {})
        if not cfg.get("cli_enabled", False):
            log.warning("Copilot CLI disabled in config.")
            return AIResponse(
                task.id,
                "gh_copilot_cli",
                "Error: Copilot CLI disabled.",
                {},
                False,
            )

        cmd_map = {"code_analysis": "explain", "generate": "suggest"}
        gh_cmd_base = [
            "gh",
            "copilot",
            cmd_map.get(task.type, "explain"),
            "--target",
            "shell",
        ]  # Default to explain
        # File arguments would need to be passed carefully to 'gh copilot'
        # This part is highly dependent on how 'gh copilot' takes file context for specific commands.
        # For simplicity, passing prompt only. Real use needs file context injection.
        # cmd_final = gh_cmd_base + task.files + [task.prompt] # This is likely
        # incorrect for gh CLI
        cmd_final = gh_cmd_base + [task.prompt]  # Simplified
        try:
            log.info(
                "Running GitHub Copilot CLI command.",
                cmd_preview=" ".join(cmd_final[:5]) + "...",
            )
            res = subprocess.run(
                cmd_final,
                capture_output=True,
                text=True,
                timeout=45,
                encoding="utf-8",
                errors="replace",
            )  # 45s timeout
            if res.returncode == 0:
                log.info("Copilot CLI task OK.", task=task.id, len=len(res.stdout))
                return AIResponse(
                    task.id,
                    "gh_copilot_cli",
                    res.stdout,
                    {"stderr": res.stderr},
                    True,
                )
            else:
                log.error(
                    "Copilot CLI error.",
                    task=task.id,
                    code=res.returncode,
                    err=res.stderr,
                )
                return AIResponse(
                    task.id,
                    "gh_copilot_cli",
                    f"Copilot Err {res.returncode}: {res.stderr}",
                    {},
                    False,
                )
        except subprocess.TimeoutExpired:
            log.error("Copilot CLI timeout.", task=task.id)
            return AIResponse(
                task.id,
                "gh_copilot_cli",
                "Error: Copilot CLI timeout.",
                {},
                False,
            )
        except FileNotFoundError:
            log.error("GitHub CLI (gh) not found.", task=task.id)
            return AIResponse(
                task.id,
                "gh_copilot_cli",
                "Error: GitHub CLI 'gh' not installed/found.",
                {},
                False,
            )
        except Exception as e:
            log.error(
                "Error with Copilot CLI.",
                task=task.id,
                err=str(e),
                exc_info=True,
            )
            return AIResponse(task.id, "gh_copilot_cli", f"Exec Err: {e}", {}, False)

    async def delegate_task(self, task: AITask, preferred_service: str = "auto") -> AIResponse:
        """Delegates task to the best/preferred available AI service."""
        self.active_tasks_map[task.id] = task
        log.info(
            "Delegating AI task.",
            id=task.id,
            type=task.type,
            preferred=preferred_service,
        )
        response: Optional[AIResponse] = None
        if preferred_service == "claude" or (
            preferred_service == "auto" and self.cfg.get("anthropic_claude", {}).get("api_key")
        ):
            response = await self.delegate_to_claude(task)
        elif preferred_service == "openai" or (
            preferred_service == "auto" and self.cfg.get("openai_gpt", {}).get("api_key")
        ):
            response = await self.delegate_to_openai(task)
        elif preferred_service == "copilot" and self.cfg.get("github_copilot", {}).get("cli_enabled"):
            # Run sync Copilot in executor for async context
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, self.use_github_copilot_cli, task)

        if response is None:
            response = self._local_analysis_fallback(task)  # Renamed
        self._save_ai_task_response(response)
        del self.active_tasks_map[task.id]
        return response  # type: ignore

    def _local_analysis_fallback(self, task: AITask) -> AIResponse:  # Renamed:
        log.warning("Using local fallback for AI task.", task_id=task.id)
        analysis_text = f"LOCAL FALLBACK ANALYSIS for task ID: {task.id}\nType: {task.type}\nPrompt: {task.prompt[:100]}...\nFiles: {task.files}\nContext: {task.context}\n(Full AI processing requires configured services.)"
        return AIResponse(
            task.id,
            "local_fallback_analyzer",
            analysis_text,
            task.context,
            True,
        )

    def _save_ai_task_response(self, response: AIResponse):  # Renamed:
        """Saves AI response to a JSON file."""
        fname = f"{response.task_id}_{response.service_name}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"  # ISO Z for filename
        fpath = self.responses_storage_dir / fname
        try:
            # Storing full response content for audit/review
            resp_dict = {
                "task_id": response.task_id,
                "service": response.service_name,
                "content": response.response_content,
                "meta": response.metadata_dict,
                "success": response.success,
                "saved_utc": datetime.now(timezone.utc).isoformat(),
            }
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(resp_dict, f, indent=2, ensure_ascii=False)
            log.info(
                "AI task response saved.",
                task=response.task_id,
                service=response.service_name,
                file=str(fpath),
            )
        except Exception as e:
            log.error("Failed to save AI response.", path=str(fpath), error=str(e))


class TaskTemplates:  # Static methods, no init needed
    @staticmethod
    def code_analysis(file_paths: list[str], analysis_focus: str = "modularization") -> AITask:  # Renamed, more params
        return AITask(
            id=f"code_analysis_{Path(file_paths[0]).stem if file_paths else 'general'}_{uuid.uuid4().hex[:6]}",
            type="code_analysis",
            prompt=f"Analyze code for architecture, dependencies, security, "
            f"optimization. Focus on {analysis_focus}.",
            files=file_paths,
            context={
                "analysis_type": "comprehensive",
                "focus_area": analysis_focus,
            },
        )

    # Add other templates: modularization_strategy, security_review etc.


"""
# --- Example Usage (Commented Out & Standardized) ---
async def main_ai_integration_manager_demo_run():
    if not structlog.get_config():
        structlog.configure(processors=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.dev.ConsoleRenderer()
        ])
    log.info("🚀 AI Integration Manager Demo Init...")
    ws_path = DEFAULT_LUKHAS_AI_INTEGRATION_WORKSPACE / "demo_run_aim"; ws_path.mkdir(parents=True,exist_ok=True)
    cfg_file = ws_path / DEFAULT_AI_CONFIG_FILENAME_STR
    if not cfg_file.exists():
        log.warning("Demo AI cfg missing, creating dummy.", path=str(cfg_file))
        # Dummy config assumes placeholders for keys, or user sets env vars LUKHAS_ANTHROPIC_KEY etc.
        dummy_cfg_data = {"anthropic_claude":{"api_key":"YOUR_CLAUDE_KEY_HERE_OR_ENV"},
    "openai_gpt":{"api_key":"YOUR_OPENAI_KEY_HERE_OR_ENV"}, "github_copilot":{"cli_enabled":False}
        try:
            with open(cfg_file,"w",encoding="utf-8") as f:json.dump(dummy_cfg_data,f,
    indent=2)
            log.info("Dummy AI cfg created for demo.", path=str(cfg_file))
        except IOError as e: log.error("Could not write dummy AI cfg.", error=str(e)):

    mgr = AIIntegrationManager(workspace_root=ws_path)
    (ws_path / "src").mkdir(exist_ok=True) # Create src dir in demo workspace
    with open(ws_path / "src/sample_code.py", "w") as f: f.write("def lukhas_greet(): return 'Hello from LUKHΛS AI!'"):

    task_instance = TaskTemplates.code_analysis(files=["src/sample_code.py"],
    analysis_focus="readability_and_best_practices")
    log.info(f"🚀 Delegating task to AI: {task_instance.id} (type: {task_instance.type})")
    response_obj = await mgr.delegate_task(task_instance, preferred_service="auto")
    log.info(f"✅ Response from {response_obj.service_name}: Success={response_obj.success}", content_preview=response_obj.response_content[:250]+"...")
    log.info("🏁 AI Integration Manager Demo Complete 🏁")

if __name__ == "__main__":
    # asyncio.run(main_ai_integration_manager_demo_run())
    pass
"""
# --- LUKHΛS AI System Footer ---
# File Origin: LUKHΛS Core Integration Layer
# Context: Manages task delegation to various AI services (Claude, OpenAI, GitHub Copilot).
# ACCESSED_BY: ['TaskOrchestrator', 'LambdaBotCore', 'AutomatedCodeReviewer'] # Conceptual
# MODIFIED_BY: ['CORE_DEV_AI_SERVICES_TEAM'] # Conceptual
# Tier Access: Varies by method (Tier 2-3 for AI service interactions) # Conceptual
# Related Components: ['aiohttp', 'OpenAI_SDK', 'Anthropic_SDK', 'GitHub_CLI'] # Conceptual
# CreationDate: Unknown | LastModifiedDate: 2024-07-26 | Version: 1.0
# --- End Footer ---
