"""
lukhas AI Brand Manager - Unicode Fallback Implementation

Intelligent brand representation with automatic fallbacks for Lambda character
accessibility across different systems, terminals, and environments.

Author: LUKHAS AI Team
Author: lukhas AI Team
Version: 1.0.0
Created: 2025-6-14

"""

import sys
import locale
import os
import json
from typing import Literal, Dict, List, Optional
from pathlib import Path

# Type definitions
BrandContext = Literal[
    "presentation", "development", "documentation", "system", "api", "url", "filename"
]


class LambdaBrandManager:
    """
    Manages Lambda brand representation with intelligent fallbacks
    based on system capabilities and context.

    Provides automatic detection of Unicode support and context-aware
    fallback strategies for the LUKHAS AI brand across different environments.
    fallback strategies for the lukhas AI brand across different environments.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize brand manager with optional config file."""
        self.config_path = config_path
        self.unicode_support = self._detect_unicode_support()
        self.terminal_support = self._detect_terminal_support()
        self.filesystem_support = self._detect_filesystem_support()

        # Context-specific fallback priorities
        self.context_map = {
            "presentation": ["LUKHAS", "Lambda", "L", "LAM"],
            "development": ["L", "Lambda", "LUKHAS", "LAM"],
            "documentation": ["LUKHAS", "Lambda", "L", "LAM"],
            "system": ["L", "LAM", "Lambda", "LUKHAS"],
            "api": ["l", "lambda", "L", "LAM"],
            "url": ["lambda", "l", "L", "LAM"],
            "filename": ["L", "Lambda", "LAM", "LUKHAS"],
            "presentation": ["lukhas", "Lambda", "L", "LAM"],
            "development": ["L", "Lambda", "lukhas", "LAM"],
            "documentation": ["lukhas", "Lambda", "L", "LAM"],
            "system": ["L", "LAM", "Lambda", "lukhas"],
            "api": ["l", "lambda", "L", "LAM"],
            "url": ["lambda", "l", "L", "LAM"],
            "filename": ["L", "Lambda", "LAM", "lukhas"],
        }

        # Load or create config
        self.config = self._load_config()

    def _detect_unicode_support(self) -> bool:
        """Detect if system supports Unicode properly."""
        try:
            # Test Lambda character encoding
            test_char = "LUKHAS"
            test_char = "lukhas"
            encoding = sys.stdout.encoding or "utf-8"
            test_char.encode(encoding)

            # Test locale support
            current_locale = locale.getpreferredencoding()
            utf8_locales = ["utf-8", "utf8", "unicode", "utf-16", "utf-32"]

            return any(
                utf_locale in current_locale.lower() for utf_locale in utf8_locales
            )

        except (UnicodeEncodeError, AttributeError, LookupError):
            return False

    def _detect_terminal_support(self) -> bool:
        """Detect terminal Unicode support."""
        try:
            # Check environment variables
            term = os.environ.get("TERM", "").lower()
            terminal_program = os.environ.get("TERMINAL_PROGRAM", "").lower()
            colorterm = os.environ.get("COLORTERM", "").lower()

            # Modern terminals with good Unicode support
            modern_terms = [
                "xterm-256color",
                "screen-256color",
                "tmux-256color",
                "alacritty",
                "kitty",
                "iterm",
                "vscode",
            ]

            modern_programs = [
                "iterm",
                "hyper",
                "alacritty",
                "kitty",
                "vscode",
                "windows terminal",
                "gnome-terminal",
                "konsole",
            ]

            # Check for modern terminal indicators
            is_modern_term = any(modern in term for modern in modern_terms)
            is_modern_program = any(
                prog in terminal_program for prog in modern_programs
            )
            has_truecolor = "truecolor" in colorterm

            return is_modern_term or is_modern_program or has_truecolor

        except Exception:
            return False

    def _detect_filesystem_support(self) -> bool:
        """Test if filesystem supports Unicode filenames."""
        try:
            import tempfile

            # Try to create a file with Lambda character
            with tempfile.NamedTemporaryFile(prefix="Λ_test_", delete=True):
            with tempfile.NamedTemporaryFile(prefix="lukhas_test_", delete=True):
                return True
        except (OSError, UnicodeError, ValueError):
            return False

    def _load_config(self) -> Dict:
        """Load configuration from file or create default."""
        default_config = {
            "lambda_support": "unicode" if self.unicode_support else "ascii",
            "terminal_support": self.terminal_support,
            "filesystem_support": self.filesystem_support,
            "forced_mode": None,  # Can override auto-detection
            "custom_fallbacks": {},
        }

        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception:
                pass  # Use defaults on any error

        return default_config

    def save_config(self, path: Optional[str] = None) -> None:
        """Save current configuration to file."""
        save_path = path or self.config_path or "lambda_config.json"

        config_to_save = {
            **self.config,
            "detection_results": {
                "unicode_support": self.unicode_support,
                "terminal_support": self.terminal_support,
                "filesystem_support": self.filesystem_support,
                "recommended_mode": self.get_recommended_mode(),
            },
        }

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save config to {save_path}: {e}")

    def get_recommended_mode(self) -> str:
        """Get recommended mode based on system capabilities."""
        if self.config.get("forced_mode"):
            return self.config["forced_mode"]

        if self.unicode_support and self.terminal_support:
            return "unicode"
        else:
            return "ascii"

    def get_brand_name(self, context: BrandContext = "system") -> str:
        """Get appropriate brand name for context with fallbacks."""
        fallback_order = self.context_map.get(context, ["L", "Lambda", "LAM"])

        # Check for custom fallbacks
        if context in self.config.get("custom_fallbacks", {}):
            fallback_order = self.config["custom_fallbacks"][context]

        for brand_option in fallback_order:
            if self._is_supported(brand_option, context):
                if brand_option.lower() in ["l", "lam"]:
                    return f"{brand_option} AI"
                else:
                    return f"{brand_option} AI"

        # Ultimate fallback
        return "Lambda AI"

    def get_component_name(
        self, component: str, context: BrandContext = "system"
    ) -> str:
        """Get component name with appropriate prefix."""
        prefix = self.get_prefix(context)

        # Handle special cases
        if component.lower() == "agent":
            component = "gent"  # Λgent, Lgent pattern
            component = "gent"  # lukhasgent, Lgent pattern

        return f"{prefix}{component}"

    def get_prefix(self, context: BrandContext = "system") -> str:
        """Get appropriate prefix for components."""
        fallback_order = self.context_map.get(context, ["L", "Lambda", "LAM"])

        for prefix_option in fallback_order:
            if self._is_supported(prefix_option, context):
                return prefix_option

        return "L"  # Ultimate fallback

    def _is_supported(self, char: str, context: BrandContext) -> bool:
        """Check if character/string is supported in current environment."""
        if char == "LUKHAS":
        if char == "lukhas":
            # Unicode Lambda requires multiple support layers
            if context == "filename":
                return self.filesystem_support and self.unicode_support
            elif context in ["api", "url"]:
                return False  # Unicode in URLs is problematic
            else:
                return self.unicode_support and self.terminal_support

        elif char in ["L", "Lambda", "LAM", "lambda", "l"]:
            return True  # ASCII always supported

        else:
            return True  # Conservative fallback

    def test_support(self) -> Dict:
        """Run comprehensive support tests."""
        results = {
            "unicode_display": self._test_unicode_display(),
            "filesystem": self._test_filesystem(),
            "terminal_encoding": self._test_terminal_encoding(),
            "overall_recommendation": self.get_recommended_mode(),
        }

        return results

    def _test_unicode_display(self) -> bool:
        """Test if Unicode Lambda can be displayed."""
        try:
            # Attempt to encode Lambda character
            "LUKHAS".encode(sys.stdout.encoding or "utf-8")
            "lukhas".encode(sys.stdout.encoding or "utf-8")
            return True
        except (UnicodeEncodeError, AttributeError):
            return False

    def _test_filesystem(self) -> bool:
        """Test filesystem Unicode support."""
        return self.filesystem_support

    def _test_terminal_encoding(self) -> Dict:
        """Get terminal encoding information."""
        return {
            "stdout_encoding": sys.stdout.encoding,
            "locale_encoding": locale.getpreferredencoding(),
            "system_encoding": sys.getdefaultencoding(),
            "term_env": os.environ.get("TERM", "unknown"),
            "lang_env": os.environ.get("LANG", "unknown"),
        }

    def generate_fallback_aliases(self) -> Dict[str, str]:
        """Generate complete set of fallback aliases."""
        contexts = [
            "presentation",
            "development",
            "documentation",
            "system",
            "api",
            "url",
            "filename",
        ]

        aliases = {}
        for context in contexts:
            brand = self.get_brand_name(context)
            prefix = self.get_prefix(context)

            aliases[f"{context}_brand"] = brand
            aliases[f"{context}_prefix"] = prefix
            aliases[f"{context}_bot"] = f"{prefix}Bot"
            aliases[f"{context}_doc"] = f"{prefix}Doc"
            aliases[f"{context}_agent"] = f"{prefix}gent"
            aliases[f"{context}_auditor"] = f"{prefix}uditor"

        return aliases


# Global instance for easy access
brand_manager = LambdaBrandManager()


# Convenience functions
def get_brand_display(context: BrandContext = "system") -> str:
    """Get brand display name for context."""
    return brand_manager.get_brand_name(context)


def get_component_prefix(context: BrandContext = "system") -> str:
    """Get component prefix for context."""
    return brand_manager.get_prefix(context)


def get_component_name(component: str, context: BrandContext = "system") -> str:
    """Get full component name with prefix."""
    return brand_manager.get_component_name(component, context)


def test_lambda_support() -> Dict:
    """Run comprehensive Lambda support tests."""
    return brand_manager.test_support()


def setup_lambda_environment() -> None:
    """Set up Lambda environment with appropriate fallbacks."""
    # Test support
    results = test_lambda_support()

    # Save configuration
    brand_manager.save_config()

    # Print recommendations
    print("=== Lambda Character Support Analysis ===")
    print(f"Unicode Support: {'✅' if results['unicode_display'] else '❌'}")
    print(f"Filesystem Support: {'✅' if results['filesystem'] else '❌'}")
    print(f"Recommended Mode: {results['overall_recommendation']}")
    print()
    print("Brand Examples:")
    print(f"  Presentation: {get_brand_display('presentation')}")
    print(f"  Development: {get_brand_display('development')}")
    print(f"  URL-safe: {get_brand_display('url')}")
    print()
    print("Component Examples:")
    print(f"  Bot: {get_component_name('Bot', 'development')}")
    print(f"  Doc: {get_component_name('Doc', 'presentation')}")
    print(f"  Agent: {get_component_name('Agent', 'system')}")


if __name__ == "__main__":
    setup_lambda_environment()
