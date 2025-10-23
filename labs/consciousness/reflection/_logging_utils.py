"""Context-aware logging helpers for reflection modules."""

from __future__ import annotations

from typing import Any, Optional

__all__ = ["ContextLogger"]


# ΛTAG: identity_logging_context
def _format_log_message(message: str, **context: Any) -> tuple[str, tuple[Any, ...]]:
    """Compose a logging message with appended context placeholders."""
    if not context:
        return message, ()
    ordered_keys = list(context.keys())
    context_pattern = " ".join(f"{key}=%s" for key in ordered_keys)
    formatted_message = f"{message} {context_pattern}"
    return formatted_message, tuple(context[key] for key in ordered_keys)


class ContextLogger:
    """Minimal adapter that emulates structlog-style binding on stdlib loggers."""

    _LOGGING_KWARGS = {"exc_info", "stack_info", "stacklevel", "extra"}

    def __init__(self, base_logger, context: Optional[dict[str, Any]] = None) -> None:
        self._logger = base_logger
        self._context: dict[str, Any] = context.copy() if context else {}

    def bind(self, **context: Any) -> "ContextLogger":
        merged = self._context.copy()
        merged.update(context)
        return ContextLogger(self._logger, merged)

    def getChild(self, suffix: str) -> "ContextLogger":
        child_logger = self._logger.getChild(suffix)
        return ContextLogger(child_logger, self._context)

    def _log(self, level: str, message: str, *args: Any, **kwargs: Any) -> None:
        logging_kwargs = {key: kwargs.pop(key) for key in list(kwargs) if key in self._LOGGING_KWARGS}
        if kwargs or self._context:
            combined = self._context.copy()
            combined.update(kwargs)
            formatted_message, context_args = _format_log_message(message, **combined)
            getattr(self._logger, level)(formatted_message, *(args + context_args), **logging_kwargs)
        else:
            getattr(self._logger, level)(message, *args, **logging_kwargs)

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._log("debug", message, *args, **kwargs)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._log("info", message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._log("warning", message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._log("error", message, *args, **kwargs)

    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._log("critical", message, *args, **kwargs)

    def log(self, level: int, message: str, *args: Any, **kwargs: Any) -> None:
        logging_kwargs = {key: kwargs.pop(key) for key in list(kwargs) if key in self._LOGGING_KWARGS}
        if kwargs or self._context:
            combined = self._context.copy()
            combined.update(kwargs)
            formatted_message, context_args = _format_log_message(message, **combined)
            self._logger.log(level, formatted_message, *(args + context_args), **logging_kwargs)
        else:
            self._logger.log(level, message, *args, **logging_kwargs)

    def __getattr__(self, item: str) -> Any:  # pragma: no cover - simple delegation
        return getattr(self._logger, item)
