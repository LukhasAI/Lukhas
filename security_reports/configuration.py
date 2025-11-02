"""Configuration helpers for the security_reports module."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, MutableMapping
import yaml

_PACKAGE_ROOT = Path(__file__).resolve().parent
_DEFAULT_CONFIG_PATH = _PACKAGE_ROOT / "config" / "config.yaml"


@dataclass(frozen=True, slots=True)
class SecurityReportsConfig:
    """Typed representation of the security reports configuration."""

    name: str
    version: str
    description: str
    log_level: str
    debug_mode: bool
    performance_monitoring: bool

    def is_secure(self) -> bool:
        """Return ``True`` when the configuration satisfies security requirements."""

        return not self.debug_mode and self.log_level.upper() not in {"DEBUG", "TRACE"}


class SecurityConfigurationError(ValueError):
    """Raised when the configuration contains insecure or invalid values."""


def _load_yaml_config(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, MutableMapping):
        raise SecurityConfigurationError("Configuration must be a mapping")
    return data


def _validate_runtime_settings(runtime: Mapping[str, Any]) -> None:
    debug_mode = runtime.get("debug_mode", False)
    if debug_mode:
        raise SecurityConfigurationError("Debug mode must be disabled in security_reports")

    log_level = str(runtime.get("log_level", "INFO"))
    if log_level.upper() in {"DEBUG", "TRACE"}:
        raise SecurityConfigurationError("Log level must not be DEBUG/TRACE for security reports")


def load_config(path: str | Path | None = None) -> SecurityReportsConfig:
    """Load and validate the security reports configuration.

    Parameters
    ----------
    path:
        Optional path to the configuration file. When omitted the default
        ``config/config.yaml`` relative to the package root is used.
    """

    config_path = Path(path) if path is not None else _DEFAULT_CONFIG_PATH
    data = _load_yaml_config(config_path)

    module = data.get("module") or {}
    runtime = data.get("runtime") or {}

    name = str(module.get("name", "")).strip()
    if name != "security_reports":
        raise SecurityConfigurationError("Module name must be 'security_reports'")

    description = str(module.get("description", "")).strip()
    version = str(module.get("version", "")).strip()

    _validate_runtime_settings(runtime)

    return SecurityReportsConfig(
        name=name,
        version=version,
        description=description,
        log_level=str(runtime.get("log_level", "INFO")),
        debug_mode=bool(runtime.get("debug_mode", False)),
        performance_monitoring=bool(runtime.get("performance_monitoring", True)),
    )


__all__ = ["SecurityReportsConfig", "SecurityConfigurationError", "load_config"]
