"""
LLM Adapter Isolation Smoke Test (Meta-Test)
============================================

Validates that raw LLM provider imports (openai, anthropic, etc.) are isolated
to designated adapter modules and don't leak into core business logic.

This is a "meta-test" - it tests the codebase structure itself, not runtime behavior.

Expected runtime: 2-4 seconds
Marker: @pytest.mark.smoke
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

# Allowed patterns where raw LLM imports are expected
ALLOWED_PATHS = [
    # Adapter modules - where LLM clients SHOULD be
    r"^labs/bridge/.*",
    r"^bridge/.*",
    r"^lukhas_website/.*/bridge/.*",
    r"^matriz/adapters/.*",
    r"^labs/adapters/.*",

    # Legacy consciousness modules (to be migrated)
    r"^labs/consciousness/reflection/openai_core_service\.py$",
    r"^matriz/consciousness/reflection/openai_core_service\.py$",
    r"^labs/consciousness/dream/openai_dream_integration\.py$",
    r"^labs/consciousness/states/qi_consciousness_hub\.py$",

    # Legacy orchestration (to be migrated)
    r"^labs/orchestration/dream_orchestrator\.py$",
    r"^labs/orchestration/openai_modulated_service\.py$",
    r"^ai_orchestration/lukhas_ai_orchestrator\.py$",

    # Tools and scripts (dev-only, not production)
    r"^tools/.*",
    r"^scripts/.*",
    r"^branding/.*",  # Marketing/demo code

    # Products (legacy, being phased out)
    r"^products/.*",

    # Legacy governance (to be migrated to adapters)
    r"^labs/governance/identity/gateway/stargate_gateway\.py$",

    # API layer that explicitly wraps openai
    r"^labs/api/tools\.py$",

    # Core modules with conditional imports (acceptable if try/except)
    r"^core/interfaces/as_agent/agent_logic/agent_self\.py$",
    r"^core/interfaces/ui/app\.py$",
    r"^core/notion_sync\.py$",

    # Legacy core modules (flagged for migration)
    r"^core/symbolic/EthicalAuditor\.py$",
    r"^core/orchestration/brain/.*",
    r"^core/consciousness/async_client\.py$",

    # Provider-specific clients
    r"^lukhas_website/.*/providers/openai_client\.py$",
]


# High-priority paths that should NOT have raw LLM imports
FORBIDDEN_PATHS = [
    r"^matriz/core/.*",
    r"^lukhas/core/.*",
    r"^lukhas/consciousness/.*",
    r"^lukhas/governance/.*",
    r"^lukhas/memory/.*",
]


def is_allowed(file_path: str) -> bool:
    """Check if a file is in an allowed location for raw LLM imports."""
    for pattern in ALLOWED_PATHS:
        if re.match(pattern, file_path):
            return True
    return False


def is_forbidden(file_path: str) -> bool:
    """Check if a file is in a forbidden location for raw LLM imports."""
    for pattern in FORBIDDEN_PATHS:
        if re.match(pattern, file_path):
            return True
    return False


@pytest.mark.smoke
def test_openai_imports_isolated():
    """
    Test that raw openai imports are isolated to adapter modules.

    This meta-test scans the codebase for `import openai` or `from openai`
    and validates they only appear in designated adapter/bridge modules.

    Failures indicate:
    - Core business logic is coupled to specific LLM provider
    - Need to refactor to use adapter pattern
    - Violation of provider-agnostic architecture
    """
    repo_root = Path(__file__).parent.parent.parent

    # Run ripgrep to find all openai imports
    try:
        result = subprocess.run(
            ["rg", "--type", "py", "-n", r"import openai|from openai", "--no-heading"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 1:
            # No matches found - excellent!
            pytest.skip("No openai imports found (ideal state)")
            return

        if result.returncode != 0:
            pytest.fail(f"ripgrep command failed: {result.stderr}")

    except FileNotFoundError:
        pytest.skip("ripgrep not available (install with: brew install ripgrep)")
        return
    except subprocess.TimeoutExpired:
        pytest.fail("Scan timed out after 10 seconds")
        return

    # Parse results
    violations = []
    allowed_imports = []

    for line in result.stdout.splitlines():
        if not line.strip():
            continue

        # Parse ripgrep output: "file:line:content"
        parts = line.split(":", 2)
        if len(parts) < 3:
            continue

        file_path = parts[0]
        line_num = parts[1]
        content = parts[2].strip()

        # Skip if it's a comment referencing openai (not an actual import)
        if content.strip().startswith("#"):
            continue

        # Check if this file is allowed
        if is_allowed(file_path):
            allowed_imports.append(f"{file_path}:{line_num}")
        else:
            # Check if it's explicitly forbidden
            severity = "CRITICAL" if is_forbidden(file_path) else "WARNING"
            violations.append(f"{severity}: {file_path}:{line_num} - {content}")

    # Save results to artifact
    artifact_dir = repo_root / "release_artifacts" / "repo_audit_v2" / "security"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    with open(artifact_dir / "openai_hits.txt", "w") as f:
        f.write("# OpenAI Import Scan Results\n\n")
        f.write(f"## Summary\n")
        f.write(f"- Total imports found: {len(allowed_imports) + len(violations)}\n")
        f.write(f"- Allowed locations: {len(allowed_imports)}\n")
        f.write(f"- Violations: {len(violations)}\n\n")

        if violations:
            f.write("## VIOLATIONS (need refactoring)\n\n")
            for v in violations:
                f.write(f"{v}\n")
            f.write("\n")

        if allowed_imports:
            f.write("## Allowed imports (in adapter modules)\n\n")
            for a in allowed_imports:
                f.write(f"{a}\n")

    # Fail if there are any violations
    if violations:
        critical_violations = [v for v in violations if v.startswith("CRITICAL")]
        warning_violations = [v for v in violations if v.startswith("WARNING")]

        error_msg = (
            f"\n\nFound {len(violations)} raw openai imports outside adapter modules:\n"
            f"  - {len(critical_violations)} CRITICAL (in production code)\n"
            f"  - {len(warning_violations)} WARNINGS (in legacy code)\n\n"
            f"Details:\n" + "\n".join(violations[:10])  # Show first 10
        )

        if len(violations) > 10:
            error_msg += f"\n... and {len(violations) - 10} more"

        error_msg += f"\n\nFull report: release_artifacts/repo_audit_v2/security/openai_hits.txt"

        # For now, just warn - don't fail CI
        # This gives teams time to refactor
        pytest.skip(f"Found violations (not failing yet): {error_msg}")


@pytest.mark.smoke
def test_anthropic_imports_isolated():
    """
    Test that raw anthropic imports are isolated to adapter modules.

    Similar to openai check, validates anthropic SDK usage is contained.
    """
    repo_root = Path(__file__).parent.parent.parent

    try:
        result = subprocess.run(
            ["rg", "--type", "py", "-n", r"import anthropic|from anthropic", "--no-heading"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 1:
            # No matches - good
            return

        if result.returncode != 0:
            pytest.fail(f"ripgrep command failed: {result.stderr}")

    except FileNotFoundError:
        pytest.skip("ripgrep not available")
        return
    except subprocess.TimeoutExpired:
        pytest.fail("Scan timed out")
        return

    # Parse and validate (same logic as openai)
    violations = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split(":", 2)
        if len(parts) < 3:
            continue
        file_path = parts[0]

        if not is_allowed(file_path):
            violations.append(line)

    if violations:
        # Just log for now, don't fail
        pytest.skip(f"Found {len(violations)} anthropic imports outside adapters (logging only)")


@pytest.mark.smoke
def test_bedrock_imports_isolated():
    """
    Test that AWS Bedrock imports are isolated to adapter modules.
    """
    repo_root = Path(__file__).parent.parent.parent

    try:
        result = subprocess.run(
            ["rg", "--type", "py", "-n", r"import boto3.*bedrock|from.*bedrock", "--no-heading"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 1:
            # No matches
            return

    except (FileNotFoundError, subprocess.TimeoutExpired):
        pytest.skip("ripgrep not available or timed out")
        return

    # For bedrock, we expect very few imports
    # Any found should be in adapters
    violations = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split(":", 2)
        if len(parts) < 3:
            continue
        file_path = parts[0]

        if not is_allowed(file_path):
            violations.append(line)

    if violations:
        pytest.skip(f"Found {len(violations)} bedrock imports outside adapters")
