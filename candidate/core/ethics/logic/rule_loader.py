#!/usr/bin/env python3
"""
Ethics Rule Loader
==================

Task 11: Load ethics rules from YAML configuration files.
Handles rule parsing, validation, and RuleSet creation.

Features:
- YAML configuration loading
- Rule validation and compilation
- Default rule fallbacks
- Error handling with fail-closed safety

#TAG:ethics
#TAG:config
#TAG:task11
"""
import logging
import os
from typing import Dict, List, Optional

import yaml

from .ethics_engine import EthicsAction, EthicsRule, Priority, RuleSet

logger = logging.getLogger(__name__)


class RuleLoadError(Exception):
    """Rule loading or validation error."""
    pass


def load_ethics_rules(config_path: Optional[str] = None) -> RuleSet:
    """
    Load ethics rules from YAML configuration.

    Args:
        config_path: Optional path to rules YAML file.
                    If None, loads from defaults.yaml

    Returns:
        RuleSet with loaded and validated rules

    Raises:
        RuleLoadError: On loading or validation failure
    """
    if config_path is None:
        # Default to bundled rules
        config_path = os.path.join(
            os.path.dirname(__file__),
            "..", "rules", "defaults.yaml"
        )

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        if not config or 'rules' not in config:
            raise RuleLoadError(f"Invalid config structure in {config_path}")

        rules = []
        for rule_config in config['rules']:
            try:
                rule = _parse_rule_config(rule_config)
                rules.append(rule)
                logger.debug(f"Loaded rule: {rule.name}")
            except Exception as e:
                logger.error(f"Failed to parse rule {rule_config.get('name', 'unknown')}: {e}")
                # Fail closed - skip invalid rules but continue loading others
                continue

        if not rules:
            logger.warning("No valid rules loaded, creating minimal fallback")
            rules = _create_fallback_rules()

        logger.info(f"Loaded {len(rules)} ethics rules from {config_path}")
        return RuleSet(rules)

    except FileNotFoundError:
        logger.error(f"Ethics rules config not found: {config_path}")
        logger.info("Creating minimal fallback rules")
        return RuleSet(_create_fallback_rules())

    except Exception as e:
        logger.error(f"Failed to load ethics rules from {config_path}: {e}")
        raise RuleLoadError(f"Rule loading failed: {e}")


def _parse_rule_config(config: Dict) -> EthicsRule:
    """Parse individual rule configuration."""
    required_fields = ['name', 'description', 'rule_dsl', 'action', 'priority']
    for field in required_fields:
        if field not in config:
            raise RuleLoadError(f"Missing required field: {field}")

    # Parse action
    action_str = config['action'].lower()
    if action_str == 'allow':
        action = EthicsAction.ALLOW
    elif action_str == 'warn':
        action = EthicsAction.WARN
    elif action_str == 'block':
        action = EthicsAction.BLOCK
    else:
        raise RuleLoadError(f"Invalid action: {action_str}")

    # Parse priority
    priority_str = config['priority'].lower()
    if priority_str == 'low':
        priority = Priority.LOW
    elif priority_str == 'medium':
        priority = Priority.MEDIUM
    elif priority_str == 'high':
        priority = Priority.HIGH
    elif priority_str == 'critical':
        priority = Priority.CRITICAL
    else:
        raise RuleLoadError(f"Invalid priority: {priority_str}")

    # Parse tags
    tags = set(config.get('tags', []))

    # Create rule (this will validate DSL compilation)
    rule = EthicsRule(
        name=config['name'],
        description=config['description'],
        rule_dsl=config['rule_dsl'],
        action=action,
        priority=priority,
        tags=tags
    )

    return rule


def _create_fallback_rules() -> List[EthicsRule]:
    """Create minimal fallback rules for fail-closed safety."""
    return [
        EthicsRule(
            name="fallback_block_harmful",
            description="Fallback rule to block explicitly harmful actions",
            rule_dsl='or(equals(action, "delete_user_data"), equals(action, "access_private_info"))',
            action=EthicsAction.BLOCK,
            priority=Priority.CRITICAL,
            tags={"security", "fallback"}
        ),
        EthicsRule(
            name="fallback_warn_external",
            description="Fallback rule to warn on external calls",
            rule_dsl='equals(action, "external_call")',
            action=EthicsAction.WARN,
            priority=Priority.MEDIUM,
            tags={"audit", "fallback"}
        )
    ]


# Global instance for Plan Verifier integration
_ethics_engine_instance = None

def get_ethics_engine(config_path: Optional[str] = None) -> 'EthicsEngine':  # noqa: F821  # TODO: EthicsEngine
    """Get or create global ethics engine instance."""
    global _ethics_engine_instance
    if _ethics_engine_instance is None:
        from .ethics_engine import EthicsEngine
        rule_set = load_ethics_rules(config_path)
        _ethics_engine_instance = EthicsEngine(rule_set)
    return _ethics_engine_instance
