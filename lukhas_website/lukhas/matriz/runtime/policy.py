from __future__ import annotations

import logging
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Optional, Tuple, Union

logger = logging.getLogger(__name__)


RuleEvaluation = Union[bool, tuple[bool, Optional[str]]]
ConstitutionRule = Callable[[Mapping[str, object]], RuleEvaluation]


@dataclass
class PolicyEngine:
    """Constitution-aware trigger evaluation for MATRIZ runtime."""

    # ΛTAG: constitutional_binding
    constitution_rules: Sequence[ConstitutionRule | str] | None = None
    constitution_evaluator: Callable[[Mapping[str, object]], bool] | None = None
    _safety_guard: Any = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.constitution_evaluator is None:
            self._safety_guard = self._initialize_safety_guard()
            if self._safety_guard is not None:
                self.constitution_evaluator = self._build_guard_evaluator(self._safety_guard)

    def evaluate_trigger(self, trigger: Mapping[str, object]) -> bool:
        """Evaluate a trigger against constitutional rules and safety checks."""

        if not isinstance(trigger, Mapping):
            raise TypeError("trigger must be a mapping")

        if self.constitution_evaluator is not None:
            try:
                if not self.constitution_evaluator(trigger):
                    return False
            except Exception as exc:  # pragma: no cover - safety fallback
                logger.error("Constitution evaluator failure: %s", exc)

        labels = self._normalize_labels(trigger.get("constitution"))

        if self.constitution_rules and not self._apply_rules(trigger, labels):
            return False

        return "forbidden" not in labels

    def _initialize_safety_guard(self) -> Any | None:
        try:
            from qi.qi_wrapper import ConstitutionalSafetyGuard
        except Exception as exc:  # pragma: no cover - optional dependency
            logger.debug("ConstitutionalSafetyGuard unavailable: %s", exc)
            return None

        try:
            return ConstitutionalSafetyGuard()
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to initialize ConstitutionalSafetyGuard: %s", exc)
            return None

    def _build_guard_evaluator(self, guard: Any) -> Callable[[Mapping[str, object]], bool]:
        def evaluator(trigger: Mapping[str, object]) -> bool:
            payload = self._build_guard_payload(trigger)
            result = guard.check_constitutional_compliance(payload)
            compliant = bool(result.get("compliant", True))
            if not compliant:
                logger.warning("Trigger blocked by constitutional safety guard: %s", result)
            return compliant

        return evaluator

    def _build_guard_payload(self, trigger: Mapping[str, object]) -> dict[str, Any]:
        text_fields = ("text", "content", "payload", "message")
        text = next((str(trigger.get(field)) for field in text_fields if trigger.get(field)), "")
        context = trigger.get("context")
        if not isinstance(context, Mapping):
            context = {}

        flags_obj = trigger.get("content_flags", [])
        if isinstance(flags_obj, Sequence) and not isinstance(flags_obj, (str, bytes)):
            flags = [str(flag) for flag in flags_obj]
        elif flags_obj:
            flags = [str(flags_obj)]
        else:
            flags = []

        return {
            "text": text,
            "input_text": trigger.get("input_text") or text,
            "content_flags": flags,
            "context": dict(context),
            "pii_consent": bool(trigger.get("pii_consent", False)),
            "pii_masked": bool(trigger.get("pii_masked", False)),
        }

    def _apply_rules(self, trigger: Mapping[str, object], labels: set[str]) -> bool:
        for rule in self.constitution_rules or ():
            if callable(rule):
                allowed, reason = self._normalize_rule_result(rule(trigger))
            else:
                allowed, reason = self._evaluate_rule_token(rule, labels)

            if not allowed:
                if reason:
                    logger.info("Constitution rule rejected trigger: %s", reason)
                return False

        return True

    def _normalize_rule_result(self, result: RuleEvaluation) -> tuple[bool, str | None]:
        if isinstance(result, tuple):
            allowed = bool(result[0])
            reason = result[1] if len(result) > 1 else None
            return allowed, reason
        return bool(result), None

    def _evaluate_rule_token(self, rule: Any, labels: set[str]) -> tuple[bool, str | None]:
        if isinstance(rule, str):
            allowed = self._apply_string_rule(rule, labels)
            return allowed, f"string_rule:{rule}" if not allowed else None

        if isinstance(rule, Mapping):
            forbidden = self._to_label_set(
                rule.get("forbidden")
                or rule.get("deny")
                or rule.get("blocked")
                or rule.get("disallow")
            )
            if forbidden and labels & forbidden:
                return False, f"forbidden:{sorted(labels & forbidden)}"

            required = self._to_label_set(rule.get("require") or rule.get("required"))
            if required and not required.issubset(labels):
                missing = required - labels
                return False, f"missing_required:{sorted(missing)}"

            return True, None

        return True, None

    def _apply_string_rule(self, rule: str, labels: set[str]) -> bool:
        token = rule.strip()
        if not token:
            return True

        prefix, _, value = token.partition(":")
        if value:
            normalized_value = value.strip()
            directive = prefix.strip().lower()
            if directive in {"forbid", "forbidden", "deny", "block"}:
                return normalized_value not in labels
            if directive in {"require", "required", "need"}:
                return normalized_value in labels
            if directive in {"allow", "permit"}:
                return normalized_value in labels

        return token not in labels

    def _normalize_labels(self, labels_obj: Any) -> set[str]:
        if labels_obj is None:
            return set()
        if isinstance(labels_obj, str):
            return {labels_obj}
        if isinstance(labels_obj, Mapping):
            return {str(value) for value in labels_obj.values() if value is not None}
        if isinstance(labels_obj, Sequence) and not isinstance(labels_obj, (str, bytes)):
            normalized: set[str] = set()
            for item in labels_obj:
                normalized.update(self._normalize_labels(item))
            return normalized
        return {str(labels_obj)}

    def _to_label_set(self, values: Any) -> set[str]:
        if values is None:
            return set()
        if isinstance(values, str):
            return {values}
        if isinstance(values, Sequence) and not isinstance(values, (str, bytes)):
            return {str(value) for value in values if value is not None}
        return {str(values)}
