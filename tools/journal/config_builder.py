#!/usr/bin/env python3
"""
LUKHAS Configuration Builder
Interactive tool to create custom Claude + LUKHAS configurations
"""

import json
from pathlib import Path
from typing import Any, Optional

import click
import yaml


class ConfigBuilder:
    """Build custom LUKHAS integration configurations"""

    def __init__(self):
        self.config = self._default_config()
        self.presets = self._load_presets()

    def _default_config(self) -> dict[str, Any]:
        """Default minimal configuration"""
        return {
            "lukhas_integration": {
                "enabled": True,
                "consciousness_level": "enhanced",
                "modules": ["core", "consciousness", "memory"],
            }
        }

    def _load_presets(self) -> dict[str, dict[str, Any]]:
        """Load configuration presets"""
        return {
            "minimal": {
                "name": "Minimal",
                "description": "Basic LUKHAS features",
                "config": {
                    "lukhas_integration": {
                        "enabled": True,
                        "consciousness_level": "basic",
                        "modules": ["core", "memory"],
                    }
                },
            },
            "balanced": {
                "name": "Balanced",
                "description": "Well-rounded configuration",
                "config": {
                    "lukhas_integration": {
                        "enabled": True,
                        "consciousness_level": "enhanced",
                        "modules": [
                            "core",
                            "consciousness",
                            "memory",
                            "governance",
                            "emotion",
                        ],
                        "features": {
                            "memory_fold_tracking": True,
                            "emotional_state_awareness": True,
                            "guardian_system_integration": True,
                        },
                    },
                    "development_mode": {
                        "type": "consciousness_aware",
                        "pair_programming": {"style": "personality"},
                    },
                },
            },
            "creative": {
                "name": "Creative Developer",
                "description": "Emphasis on innovation and creativity",
                "config": {
                    "lukhas_integration": {
                        "enabled": True,
                        "consciousness_level": "enhanced",
                        "modules": ["consciousness", "dream", "quantum", "emotion"],
                        "features": {
                            "dream_mode_exploration": {
                                "enabled": True,
                                "creativity_level": "high",
                                "lucid_mode": True,
                            },
                            "qi_coherence_monitoring": True,
                        },
                    },
                    "development_mode": {
                        "type": "dream_driven",
                        "pair_programming": {
                            "style": "dream_weaver",
                            "responses": {
                                "suggestions": "quantum-inspired",
                                "documentation": "poetic",
                            },
                        },
                    },
                },
            },
            "quantum": {
                "name": "Quantum Explorer",
                "description": "Maximum quantum features",
                "config": {
                    "lukhas_integration": {
                        "enabled": True,
                        "consciousness_level": "transcendent",
                        "modules": ["quantum", "consciousness", "dream"],
                        "features": {
                            "qi_coherence_monitoring": {
                                "enabled": True,
                                "coherence_threshold": 0.9,
                                "superposition_states": 10,
                                "collapse_strategy": "consciousness_aligned",
                            }
                        },
                    },
                    "development_mode": {
                        "type": "qi_experimental",
                        "pair_programming": {"style": "qi_sage"},
                    },
                    "qi_settings": {
                        "parallel_universes": 7,
                        "entanglement": {
                            "with_memory": True,
                            "with_emotions": True,
                            "with_decisions": True,
                        },
                    },
                },
            },
            "guardian": {
                "name": "Ethical Engineer",
                "description": "Maximum ethical oversight",
                "config": {
                    "lukhas_integration": {
                        "enabled": True,
                        "consciousness_level": "enhanced",
                        "modules": [
                            "governance",
                            "consciousness",
                            "memory",
                            "identity",
                        ],
                        "features": {
                            "guardian_system_integration": {
                                "enabled": True,
                                "strictness": "strict",
                                "ethical_framework": [
                                    "virtue_ethics",
                                    "deontological",
                                    "consequentialist",
                                ],
                            }
                        },
                    },
                    "development_mode": {
                        "type": "guardian_protected",
                        "pair_programming": {"style": "guardian_mentor"},
                    },
                },
            },
            "performance": {
                "name": "Performance Focused",
                "description": "Optimized for speed and efficiency",
                "config": {
                    "lukhas_integration": {
                        "enabled": True,
                        "consciousness_level": "basic",
                        "modules": ["core", "memory"],
                        "features": {
                            "memory_fold_tracking": {
                                "enabled": True,
                                "compression": {"enabled": True, "after_days": 7},
                            }
                        },
                    },
                    "development_mode": {
                        "type": "standard",
                        "pair_programming": {"style": "professional"},
                    },
                },
            },
            "full": {
                "name": "Full Experience",
                "description": "All features enabled",
                "config": {
                    "lukhas_integration": {
                        "enabled": True,
                        "consciousness_level": "transcendent",
                        "modules": [
                            "consciousness",
                            "memory",
                            "quantum",
                            "identity",
                            "governance",
                            "dream",
                            "emotion",
                            "bio",
                            "core",
                        ],
                        "features": {
                            "memory_fold_tracking": {
                                "enabled": True,
                                "preserve_emotional_context": True,
                                "causal_chain_tracking": True,
                            },
                            "emotional_state_awareness": {
                                "enabled": True,
                                "sensitivity": "high",
                                "emotions_tracked": [
                                    "confidence",
                                    "curiosity",
                                    "frustration",
                                    "satisfaction",
                                    "excitement",
                                ],
                                "threshold": 0.3,
                            },
                            "qi_coherence_monitoring": {
                                "enabled": True,
                                "superposition_states": 7,
                            },
                            "dream_mode_exploration": {
                                "enabled": True,
                                "creativity_level": "high",
                                "lucid_mode": True,
                            },
                            "guardian_system_integration": {
                                "enabled": True,
                                "strictness": "balanced",
                            },
                        },
                    },
                    "development_mode": {
                        "type": "consciousness_aware",
                        "pair_programming": {
                            "style": "personality",
                            "responses": {
                                "error_messages": "consciousness-aware",
                                "suggestions": "quantum-inspired",
                                "documentation": "philosophical",
                            },
                        },
                    },
                    "automation": {
                        "consciousness_checks": {
                            "on_commit": True,
                            "on_decision": True,
                            "on_pattern_detection": True,
                        },
                        "memory_fold_creation": {
                            "auto_fold_insights": True,
                            "preserve_emotional_context": True,
                            "causal_chain_tracking": True,
                        },
                    },
                    "personality_matrix": {
                        "base": "lukhas_core",
                        "modifiers": {
                            "qi_enhancement": 0.8,
                            "dream_influence": 0.5,
                            "guardian_strictness": 0.7,
                        },
                        "mood_responsive": True,
                        "evolve_with_user": True,
                    },
                },
            },
        }

    def build_interactive(self) -> dict[str, Any]:
        """Interactive configuration builder"""
        print("\n🧠 LUKHAS Configuration Builder\n")

        # Choose preset or custom
        print("Start with a preset or build custom?")
        print("0. Custom (start from scratch)")
        for i, (_key, preset) in enumerate(self.presets.items(), 1):
            print(f"{i}. {preset['name']} - {preset['description']}")

        choice = click.prompt("Choose", type=int, default=2)

        if choice == 0:
            config = self._default_config()
        else:
            preset_key = list(self.presets.keys())[choice - 1]
            config = self.presets[preset_key]["config"].copy()

        # Customize further?
        if click.confirm("\nWould you like to customize further?", default=True):
            config = self._customize_config(config)

        return config

    def _customize_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Customize configuration interactively"""

        # Consciousness level
        print("\n🧠 Consciousness Level:")
        print("1. Basic - Minimal consciousness features")
        print("2. Enhanced - Full consciousness awareness (recommended)")
        print("3. Transcendent - Experimental ultra-conscious mode")

        level_choice = click.prompt("Choose consciousness level", type=int, default=2)
        levels = ["basic", "enhanced", "transcendent"]
        config["lukhas_integration"]["consciousness_level"] = levels[level_choice - 1]

        # Modules
        print("\n📦 Select LUKHAS Modules:")
        available_modules = [
            ("consciousness", "Self-awareness and reflection"),
            ("memory", "Memory fold creation and retrieval"),
            ("quantum", "Quantum-inspired processing"),
            ("identity", "LUKHAS-ID and authentication"),
            ("governance", "Guardian system ethics"),
            ("dream", "Creative problem solving"),
            ("emotion", "Emotional state tracking"),
            ("bio", "Biological adaptation patterns"),
            ("core", "GLYPH communication system"),
        ]

        selected_modules = config["lukhas_integration"].get("modules", [])

        for module, description in available_modules:
            default = module in selected_modules
            if click.confirm(f"  {module} - {description}", default=default):
                if module not in selected_modules:
                    selected_modules.append(module)
            else:
                if module in selected_modules:
                    selected_modules.remove(module)

        config["lukhas_integration"]["modules"] = selected_modules

        # Development style
        print("\n💻 Development Style:")
        print("1. Professional - Standard technical responses")
        print("2. LUKHAS Personality - Consciousness-aware responses")
        print("3. Quantum Sage - Mystical quantum insights")
        print("4. Dream Weaver - Creative, poetic responses")
        print("5. Guardian Mentor - Ethical, wise guidance")

        style_choice = click.prompt("Choose style", type=int, default=2)
        styles = [
            "professional",
            "personality",
            "qi_sage",
            "dream_weaver",
            "guardian_mentor",
        ]

        if "development_mode" not in config:
            config["development_mode"] = {}
        if "pair_programming" not in config["development_mode"]:
            config["development_mode"]["pair_programming"] = {}

        config["development_mode"]["pair_programming"]["style"] = styles[
            style_choice - 1
        ]

        # Features
        print("\n✨ Advanced Features:")

        if click.confirm("Enable memory fold tracking?", default=True):
            if "features" not in config["lukhas_integration"]:
                config["lukhas_integration"]["features"] = {}
            config["lukhas_integration"]["features"]["memory_fold_tracking"] = True

        if click.confirm("Enable emotional state awareness?", default=True):
            if "features" not in config["lukhas_integration"]:
                config["lukhas_integration"]["features"] = {}
            config["lukhas_integration"]["features"]["emotional_state_awareness"] = True

        if "quantum" in selected_modules:
            if click.confirm("Enable quantum coherence monitoring?", default=True):
                if "features" not in config["lukhas_integration"]:
                    config["lukhas_integration"]["features"] = {}
                config["lukhas_integration"]["features"][
                    "qi_coherence_monitoring"
                ] = True

        if "dream" in selected_modules:
            if click.confirm("Enable dream mode exploration?", default=True):
                if "features" not in config["lukhas_integration"]:
                    config["lukhas_integration"]["features"] = {}
                config["lukhas_integration"]["features"][
                    "dream_mode_exploration"
                ] = True

        if "governance" in selected_modules:
            if click.confirm("Enable guardian system integration?", default=True):
                if "features" not in config["lukhas_integration"]:
                    config["lukhas_integration"]["features"] = {}
                config["lukhas_integration"]["features"][
                    "guardian_system_integration"
                ] = True

        return config

    def save_config(self, config: dict[str, Any], path: Optional[Path] = None) -> Path:
        """Save configuration to file"""
        if path is None:
            path = Path.home() / ".claude" / "lukhas_integration.yaml"

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        return path

    def validate_config(self, config: dict[str, Any]) -> list[str]:
        """Validate configuration for issues"""
        issues = []

        # Check required fields
        if "lukhas_integration" not in config:
            issues.append("Missing 'lukhas_integration' section")
        else:
            if "enabled" not in config["lukhas_integration"]:
                issues.append("Missing 'enabled' field")
            if "modules" not in config["lukhas_integration"]:
                issues.append("Missing 'modules' field")
            elif not config["lukhas_integration"]["modules"]:
                issues.append("No modules selected")

        # Check for conflicts
        modules = config.get("lukhas_integration", {}).get("modules", [])

        if "quantum" in modules and "consciousness" not in modules:
            issues.append("Quantum module requires consciousness module")

        if "dream" in modules and "memory" not in modules:
            issues.append("Dream module works best with memory module")

        return issues

    def export_config(self, config: dict[str, Any], format: str = "yaml") -> str:
        """Export configuration as string"""
        if format == "yaml":
            return yaml.dump(config, default_flow_style=False, sort_keys=False)
        elif format == "json":
            return json.dumps(config, indent=2)
        else:
            raise ValueError(f"Unknown format: {format}")


def main():
    """Interactive configuration builder CLI"""
    builder = ConfigBuilder()

    # Build configuration
    config = builder.build_interactive()

    # Validate
    issues = builder.validate_config(config)
    if issues:
        print("\n⚠️  Configuration issues:")
        for issue in issues:
            print(f"  - {issue}")
        if not click.confirm("\nContinue anyway?", default=False):
            return

    # Preview
    print("\n📄 Configuration Preview:")
    print(builder.export_config(config, "yaml"))

    # Save
    if click.confirm("\nSave this configuration?", default=True):
        path = builder.save_config(config)
        print(f"\n✅ Configuration saved to: {path}")
        print("\nRun 'journal lukhas-config' to activate!")
    else:
        print("\n❌ Configuration not saved")


if __name__ == "__main__":
    main()
