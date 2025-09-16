#!/usr/bin/env python3
"""Force LUKHAS AI ΛBot to actually think and heal by bypassing its ultra-conservative mode."""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_MAX_TOKENS = 250


logger = logging.getLogger("branding.force_healing")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


@dataclass(slots=True)
class HealingTaskResult:
    """Structured summary of a forced healing task execution."""

    task: str
    success: bool
    response: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    drift_score: float = 0.0
    affect_delta: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        """Return a concise textual summary for console output."""

        status_symbol = "✅" if self.success else "⚠️"
        base = f"{status_symbol} {self.task}"
        if self.response and "summary" in self.response:
            base += f" → {self.response['summary']}"
        if self.error:
            base += f" (error: {self.error})"
        base += f" [drift_score={self.drift_score:.2f}, affect_delta={self.affect_delta:.2f}]"
        return base

    def to_serializable(self) -> dict[str, Any]:
        """Convert the result into a JSON-serializable payload."""

        return {
            "task": self.task,
            "success": self.success,
            "response": self.response,
            "error": self.error,
            "drift_score": self.drift_score,
            "affect_delta": self.affect_delta,
            "metadata": self.metadata,
        }


def _load_controller() -> Any:
    """Attempt to import the live ABot controller; return ``None`` when unavailable."""

    try:
        from lukhas_ai_lambda_bot.core.openai_intelligent_controller import ABotIntelligentOpenAIController

        return ABotIntelligentOpenAIController()
    except Exception as exc:  # pragma: no cover - guard for missing dependency
        logger.warning("Unable to import ABotIntelligentOpenAIController: %s", exc)
        return None


def _generate_mock_response(task: str) -> dict[str, Any]:
    """Provide a deterministic fallback response when the controller is unavailable."""

    timestamp = datetime.now(timezone.utc).isoformat()
    return {
        "summary": "Generated reflective response using mock controller",
        "details": {
            "task": task,
            "generated_at": timestamp,
            "recommendations": [
                "Review controller integration paths",
                "Enable live healing mode after dependency installation",
                "Capture follow-up metrics once real responses are available",
            ],
        },
    }


def _process_controller_response(raw_response: Any) -> dict[str, Any]:
    """Normalize controller responses into a consistent symbolic payload."""

    if isinstance(raw_response, dict):
        payload = raw_response
    else:
        payload = {"content": str(raw_response)}

    summary_fields = [
        payload.get("summary"),
        payload.get("message"),
        payload.get("content"),
    ]
    summary = next(
        (value for value in summary_fields if isinstance(value, str) and value.strip()),
        "",
    )

    if not summary and isinstance(payload.get("choices"), list):
        choices = payload["choices"]
        if choices:
            choice = choices[0]
            if isinstance(choice, dict):
                summary = choice.get("message") or choice.get("text", "")

    usage = payload.get("usage") if isinstance(payload.get("usage"), dict) else {}

    return {
        "summary": summary.strip() or "No summary available",
        "raw": payload,
        "tokens": usage.get("total_tokens"),
    }


# ΛTAG: healing_protocol
def run_healing_task(task: str) -> HealingTaskResult:
    """Execute a forced healing task with graceful degradation and telemetry."""

    controller = _load_controller()
    metadata = {
        "model": DEFAULT_MODEL,
        "max_tokens": DEFAULT_MAX_TOKENS,
        "invoked_at": datetime.now(timezone.utc).isoformat(),
    }

    if controller is None:
        logger.info("Falling back to mock healing response for task: %s", task)
        mock_response = _generate_mock_response(task)
        return HealingTaskResult(
            task=task,
            success=False,
            response=mock_response,
            error="controller_unavailable",
            drift_score=0.25,
            affect_delta=-0.10,
            metadata={**metadata, "source": "mock"},
        )

    try:
        raw = controller.make_intelligent_request(
            prompt=task,
            model=DEFAULT_MODEL,
            max_tokens=DEFAULT_MAX_TOKENS,
            purpose="forced_healing",
            change_detected=True,
            user_request=True,
            urgency="HIGH",
        )
        processed = _process_controller_response(raw)
        return HealingTaskResult(
            task=task,
            success=True,
            response=processed,
            drift_score=0.05,
            affect_delta=0.15,
            metadata={**metadata, "source": "controller"},
        )
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.error("Healing task failed: %s", exc)
        return HealingTaskResult(
            task=task,
            success=False,
            error=str(exc),
            drift_score=0.30,
            affect_delta=-0.20,
            metadata={**metadata, "source": "controller"},
        )


def save_results(results: list[HealingTaskResult]) -> Path:
    """Persist healing task results for later analysis."""

    output_dir = Path(__file__).resolve().parent / "healing_reports"
    output_dir.mkdir(exist_ok=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "results": [result.to_serializable() for result in results],
    }

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"force_healing_{timestamp}.json"
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


def force_abot_to_heal() -> list[HealingTaskResult]:
    """Run the healing protocol across the standard task suite."""

    logger.info("🔥 FORCING LUKHAS AI ΛBot OUT OF ULTRA-CONSERVATIVE MODE")
    healing_tasks = [
        "Analyze the AI router cost calculation bug and provide a specific fix",
        "What improvements can you make to your own CLI interface?",
        "How can you optimize your financial intelligence to be more efficient?",
        "What security vulnerabilities do you see in your current system?",
        "Design 3 new features you think would make you more valuable",
    ]

    results: list[HealingTaskResult] = []
    for index, task in enumerate(healing_tasks, 1):
        logger.info("🎯 Forced Healing Task %s/%s", index, len(healing_tasks))
        logger.info("📝 %s", task)

        result = run_healing_task(task)
        logger.info(result.summary())
        results.append(result)

        logger.info("-" * 40)

    output_path = save_results(results)
    logger.info("📄 Healing transcripts saved to %s", output_path)
    return results


if __name__ == "__main__":
    print("💪 Forcing LUKHAS AI ΛBot out of ultra-conservative mode...")
    force_abot_to_heal()
