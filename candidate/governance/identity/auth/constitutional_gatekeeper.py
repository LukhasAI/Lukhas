"""
LUKHAS Constitutional Gatekeeper - Claude's Enforcement Middleware

This module implements constitutional AI enforcement for the LUKHAS authentication system.
It provides immutable logic for UI constraints, timeout enforcement, and grid size limits
with complete transparency and audit logging.

Author: LUKHAS Team
Date: June 2025
Constitutional AI Guidelines: Enforced
"""

import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

# Configure constitutional logging
logging.basicConfig(level=logging.INFO)
constitutional_logger = logging.getLogger("LUKHAS_CONSTITUTIONAL")


class ConstitutionalLevel(Enum):
    """Constitutional enforcement levels"""

    PERMISSIVE = "permissive"  # Basic guidelines
    STANDARD = "standard"  # Default enforcement
    STRICT = "strict"  # Maximum protection
    EMERGENCY = "emergency"  # Crisis mode


@dataclass
class ConstitutionalThresholds:
    """Immutable constitutional thresholds for UI enforcement"""

    max_grid_size: int = 16  # Maximum emoji grid size
    min_timeout_seconds: int = 3  # Minimum auth timeout
    max_timeout_seconds: int = 30  # Maximum auth timeout
    max_attention_load: float = 0.8  # Maximum cognitive load
    cultural_safety_required: bool = True
    audit_all_actions: bool = True

    def __post_init__(self):
        """Validate constitutional parameters are within safe ranges"""
        if self.max_grid_size > 20:
            raise ValueError("Constitutional violation: Grid size exceeds safety limits")
        if self.min_timeout_seconds < 1:
            raise ValueError("Constitutional violation: Timeout too short for human cognition")
        if self.max_attention_load > 1.0:
            raise ValueError("Constitutional violation: Cognitive load exceeds human capacity")


class ConstitutionalGatekeeper:
    """
    Constitutional AI enforcement middleware for LUKHAS authentication.

    This class implements Claude's constitutional guidelines with immutable logic
    to ensure user safety, cognitive accessibility, and cultural sensitivity.
    All enforcement actions are logged for transparency.
    """

    def __init__(self, enforcement_level: ConstitutionalLevel = ConstitutionalLevel.STANDARD):
        self.enforcement_level = enforcement_level
        self.thresholds = ConstitutionalThresholds()
        self.violation_history: list[dict] = []
        self.startup_time = datetime.now(timezone.utc)

        constitutional_logger.info(f"Constitutional Gatekeeper initialized with {enforcement_level.value} enforcement")

    def validate_ui_parameters(self, grid_size: int, timeout: int, attention_load: float) -> tuple[bool, list[str]]:
        """
        Validate UI parameters against constitutional constraints.

        Args:
            grid_size: Proposed emoji grid size
            timeout: Proposed authentication timeout in seconds
            attention_load: Estimated cognitive attention load (0.0-1.0)

        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations = []

        # Grid size validation
        if grid_size > self.thresholds.max_grid_size:
            violations.append(f"Grid size {grid_size} exceeds constitutional limit of {self.thresholds.max_grid_size}")

        # Timeout validation
        if timeout < self.thresholds.min_timeout_seconds:
            violations.append(
                f"Timeout {timeout}s below constitutional minimum of {self.thresholds.min_timeout_seconds}s"
            )
        elif timeout > self.thresholds.max_timeout_seconds:
            violations.append(
                f"Timeout {timeout}s exceeds constitutional maximum of {self.thresholds.max_timeout_seconds}s"
            )

        # Cognitive load validation
        if attention_load > self.thresholds.max_attention_load:
            violations.append(
                f"Attention load {attention_load} exceeds constitutional limit of {self.thresholds.max_attention_load}"
            )

        is_valid = len(violations) == 0

        # Log enforcement action
        self._log_enforcement_action(
            "ui_validation",
            {
                "grid_size": grid_size,
                "timeout": timeout,
                "attention_load": attention_load,
                "is_valid": is_valid,
                "violations": violations,
            },
        )

        return is_valid, violations

    def enforce_cultural_safety(self, emoji_list: list[str], user_culture: Optional[str] = None) -> list[str]:
        """
        Enforce cultural safety by filtering potentially offensive emojis.

        Args:
            emoji_list: List of emojis to validate
            user_culture: Optional user cultural context

        Returns:
            Filtered list of culturally safe emojis
        """
        if not self.thresholds.cultural_safety_required:
            return emoji_list

        # Enhanced cultural exclusion patterns based on research
        cultural_exclusions = {
            "religious_symbols": ["☪️", "✡️", "☦️", "🕎", "☸️", "🛐", "⛪", "🕌"],
            "political_symbols": ["🏴‍☠️", "⚡", "🗿", "🏴", "🚩"],
            "potentially_offensive": ["🖕", "💀", "👻", "💩"],
            # May be inappropriate in some cultures
            "cultural_specific": ["🍖", "🥓", "🍷", "🍺", "🐷", "🥛"],
            # Prayer vs namaste vs high-five interpretation differences
            "platform_variant_risk": ["🙏"],
            "age_sensitive": ["🍼", "👶", "🧸"],  # May cause discomfort for some users
            # Medical symbols that may trigger anxiety
            "health_sensitive": ["💊", "🩺", "⚕️", "🏥"],
            # Time pressure or complexity indicators
            "neurodivergent_challenging": ["⏰", "⏳", "📊", "📈"],
        }

        # Culture-specific additional exclusions
        if user_culture:
            culture_specific = {
                "islamic": cultural_exclusions["cultural_specific"] + ["🐶", "🎭"],
                "hindu": cultural_exclusions["cultural_specific"] + ["🥩", "🍖"],
                "jewish": cultural_exclusions["cultural_specific"] + ["🍤", "🦐", "🦀"],
                "buddhist": cultural_exclusions["cultural_specific"] + ["🥩", "🍖", "🐟"],
            }

            if user_culture.lower() in culture_specific:
                for emoji in culture_specific[user_culture.lower()]:
                    cultural_exclusions["cultural_specific"].append(emoji)

        filtered_emojis = []
        excluded_count = 0
        exclusion_reasons = []

        for emoji in emoji_list:
            is_safe = True
            for category, exclusions in cultural_exclusions.items():
                if emoji in exclusions:
                    excluded_count += 1
                    exclusion_reasons.append(f"{emoji} ({category})")
                    is_safe = False
                    break

            if is_safe:
                filtered_emojis.append(emoji)

        # Log cultural enforcement with detailed reasons
        self._log_enforcement_action(
            "cultural_safety",
            {
                "original_count": len(emoji_list),
                "filtered_count": len(filtered_emojis),
                "excluded_count": excluded_count,
                "exclusion_reasons": exclusion_reasons,
                "user_culture": user_culture,
            },
        )

        return filtered_emojis

    def validate_entropy_sync(self, device_count: int, sync_interval: float) -> bool:
        """
        Validate multi-device entropy synchronization parameters.

        Args:
            device_count: Number of devices in sync network
            sync_interval: Synchronization interval in seconds

        Returns:
            True if parameters are constitutionally valid
        """
        violations = []

        # Device count limits (prevent network overload)
        if device_count > 10:
            violations.append(f"Device count {device_count} exceeds constitutional limit of 10")

        # Sync interval limits (prevent spam/battery drain)
        if sync_interval < 1.0:
            violations.append(f"Sync interval {sync_interval}s too frequent, minimum 1.0s required")
        elif sync_interval > 300.0:  # 5 minutes max
            violations.append(f"Sync interval {sync_interval}s too infrequent, maximum 300s allowed")

        is_valid = len(violations) == 0

        self._log_enforcement_action(
            "entropy_sync_validation",
            {
                "device_count": device_count,
                "sync_interval": sync_interval,
                "is_valid": is_valid,
                "violations": violations,
            },
        )

        return is_valid

    def validate_neurodivergent_accessibility(self, ui_config: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate UI configuration for neurodivergent accessibility based on research.

        Args:
            ui_config: Dictionary containing UI configuration parameters

        Returns:
            Tuple of (is_accessible, list_of_accessibility_issues)
        """
        issues = []

        # ADHD-specific validations
        if ui_config.get("has_moving_elements", False):
            issues.append("Moving elements may distract ADHD users")

        if ui_config.get("popup_notifications", False):
            issues.append("Pop-up notifications can break ADHD user focus")

        if ui_config.get("time_pressure_indicators", False):
            issues.append("Time pressure indicators may cause ADHD anxiety")

        # Autism spectrum validations
        color_combinations = ui_config.get("color_scheme", {})
        if color_combinations.get("high_contrast", False) and color_combinations.get("bright_colors", False):
            issues.append("High contrast bright colors may cause autism spectrum sensory overload")

        if ui_config.get("unexpected_changes", False):
            issues.append("Unexpected interface changes violate autism spectrum predictability needs")

        audio_config = ui_config.get("audio", {})
        if audio_config.get("notification_sounds", False):
            issues.append("Audio notifications may cause autism spectrum sensory sensitivity")

        # Dyslexia validations
        font_config = ui_config.get("font", {})
        if font_config.get("complex_fonts", False):
            issues.append("Complex fonts create dyslexia reading barriers")

        if font_config.get("poor_contrast", False):
            issues.append("Poor contrast affects dyslexia text processing")

        if ui_config.get("lengthy_instructions", False):
            issues.append("Lengthy instructions may overwhelm dyslexic users")

        # General cognitive load validations
        element_count = ui_config.get("total_interactive_elements", 0)
        if element_count > 5:
            issues.append(f"Too many interactive elements ({element_count}) exceeds working memory capacity")

        processing_time = ui_config.get("required_processing_time_seconds", 0)
        if processing_time > 0 and processing_time < 10:
            issues.append(f"Processing time ({processing_time}s) may be insufficient for neurodivergent users")

        is_accessible = len(issues) == 0

        self._log_enforcement_action(
            "neurodivergent_accessibility",
            {
                "ui_config": ui_config,
                "is_accessible": is_accessible,
                "accessibility_issues": issues,
                "compliance_level": "WCAG_2.2_AA" if is_accessible else "NON_COMPLIANT",
            },
        )

        return is_accessible, issues

    def validate_post_quantum_security(self, crypto_config: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate post-quantum cryptography configuration based on security research.

        Args:
            crypto_config: Dictionary containing cryptographic configuration

        Returns:
            Tuple of (is_secure, list_of_security_issues)
        """
        issues = []

        # Validate PQC algorithm choices
        approved_algorithms = {
            "digital_signatures": ["CRYSTALS-Dilithium", "FALCON", "SPHINCS+"],
            "key_encapsulation": ["CRYSTALS-Kyber", "Classic McEliece", "HQC"],
            "hash_functions": ["SHA-3", "SHAKE-128", "SHAKE-256"],
        }

        signature_alg = crypto_config.get("digital_signature_algorithm")
        if signature_alg and signature_alg not in approved_algorithms["digital_signatures"]:
            issues.append(f"Digital signature algorithm '{signature_alg}' not NIST-approved for PQC")

        kem_alg = crypto_config.get("key_encapsulation_algorithm")
        if kem_alg and kem_alg not in approved_algorithms["key_encapsulation"]:
            issues.append(f"Key encapsulation algorithm '{kem_alg}' not NIST-approved for PQC")

        hash_alg = crypto_config.get("hash_algorithm")
        if hash_alg and hash_alg not in approved_algorithms["hash_functions"]:
            issues.append(f"Hash algorithm '{hash_alg}' not recommended for PQC applications")

        # Validate entropy requirements
        entropy_bits = crypto_config.get("entropy_bits", 0)
        if entropy_bits < 512:
            issues.append(f"Entropy ({entropy_bits} bits) below recommended minimum of 512 bits for PQC")

        # Validate key rotation policy
        key_rotation_hours = crypto_config.get("key_rotation_hours", 0)
        if key_rotation_hours == 0:
            issues.append("No key rotation policy defined - required for PQC security")
        elif key_rotation_hours > 168:  # 1 week
            issues.append(f"Key rotation interval ({key_rotation_hours}h) exceeds recommended maximum of 168h")

        # Validate quantum-safe transport
        transport_security = crypto_config.get("transport_security", {})
        if not transport_security.get("qi_safe_tls", False):
            issues.append("Transport layer not configured for quantum-safe TLS")

        # Validate resistance to classical attacks
        classical_resistance = crypto_config.get("classical_attack_resistance", {})
        if not classical_resistance.get("side_channel_protection", False):
            issues.append("Missing side-channel attack protection")

        if not classical_resistance.get("timing_attack_protection", False):
            issues.append("Missing timing attack protection")

        is_secure = len(issues) == 0

        self._log_enforcement_action(
            "post_quantum_security",
            {
                "crypto_config": crypto_config,
                "is_secure": is_secure,
                "security_issues": issues,
                "nist_compliance": is_secure,
            },
        )

        return is_secure, issues

    def _log_enforcement_action(self, action_type: str, details: dict[str, Any]):
        """
        Log constitutional enforcement actions for transparency.

        Args:
            action_type: Type of enforcement action
            details: Detailed information about the action
        """
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action_type": action_type,
            "enforcement_level": self.enforcement_level.value,
            "details": details,
            "session_id": id(self),
        }

        self.violation_history.append(log_entry)
        constitutional_logger.info(f"Constitutional action: {action_type} - {details}")

        # Limit history size to prevent memory issues
        if len(self.violation_history) > 1000:
            # Keep last 800 entries
            self.violation_history = self.violation_history[-800:]

    def get_enforcement_report(self) -> dict[str, Any]:
        """
        Generate comprehensive enforcement report for audit purposes.

        Returns:
            Dictionary containing enforcement statistics and history
        """
        return {
            "enforcement_level": self.enforcement_level.value,
            "startup_time": self.startup_time.isoformat(),
            "current_thresholds": asdict(self.thresholds),
            "total_actions": len(self.violation_history),
            "action_history": self.violation_history[-50:],  # Last 50 actions
            "uptime_hours": (datetime.now(timezone.utc) - self.startup_time).total_seconds() / 3600,
        }

    def emergency_lockdown(self, reason: str) -> dict[str, Any]:
        """
        Activate emergency constitutional lockdown.

        Args:
            reason: Reason for emergency activation

        Returns:
            Emergency status report
        """
        self.enforcement_level = ConstitutionalLevel.EMERGENCY

        # Emergency thresholds (ultra-conservative)
        self.thresholds = ConstitutionalThresholds(
            max_grid_size=4,  # Minimal cognitive load
            min_timeout_seconds=10,  # Extended time for decisions
            max_timeout_seconds=60,  # Extended maximum
            max_attention_load=0.3,  # Reduced cognitive demand
            cultural_safety_required=True,
            audit_all_actions=True,
        )

        emergency_report = {
            "emergency_activated": True,
            "activation_time": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
            "new_thresholds": asdict(self.thresholds),
            "previous_level": self.enforcement_level.value,
        }

        self._log_enforcement_action("emergency_lockdown", emergency_report)
        constitutional_logger.warning(f"EMERGENCY LOCKDOWN ACTIVATED: {reason}")

        return emergency_report


# Constitutional enforcement singleton (ensures consistency)
_constitutional_gatekeeper_instance = None


def get_constitutional_gatekeeper(
    enforcement_level: ConstitutionalLevel = ConstitutionalLevel.STANDARD,
) -> ConstitutionalGatekeeper:
    """
    Get the singleton constitutional gatekeeper instance.

    Args:
        enforcement_level: Desired enforcement level (only used on first call)

    Returns:
        ConstitutionalGatekeeper instance
    """
    global _constitutional_gatekeeper_instance

    if _constitutional_gatekeeper_instance is None:
        _constitutional_gatekeeper_instance = ConstitutionalGatekeeper(enforcement_level)

    return _constitutional_gatekeeper_instance
