---
status: wip
type: documentation
---
# README for core/lukhas_utils/

## Overview

The `core/lukhas_utils/` directory is designated for LUKHAS-specific utility functions, tools, and helper logic. These utilities are typically more specialized to the LUKHAS ecosystem than the general-purpose functions found in `core.common` or `core.helpers`. This directory might also house experimental logic or utilities that are closely tied to LUKHAS-internal conventions.

## Symbolic Notes & Conventions

-   **`# ΛUTIL`**: Marks functions that provide utility or helper capabilities, specific to LUKHAS.
-   **`# ΛNOTE`**: Provides context or explanation for the utility's purpose or design.
-   **`# ΛCAUTION`**: Flags utilities that are experimental, sensitive, or have potential risks if misused (e.g., use of `eval` in legacy examples, experimental algorithms).
-   **`# ΛECHO`**: Used for utilities that reflect or report on system state or generate identifiers based on internal LUKHAS principles (e.g., `generate_symbolic_id`, `create_diagnostic_payload`).
-   **`# ΛLEGACY`**: Designates utilities or patterns that are from older versions of LUKHAS and might be deprecated, less robust, or superseded by newer methods. They are kept for context or compatibility.
-   **`# ΛDREAM_LOOP`**: Would be applied if any utilities here are directly involved in processing or facilitating dream feedback loops (example commented out in `__init__.py`).
-   **Headers/Footers**: All Python files must include the standardized header and footer blocks.
-   **Logging**: All utilities should use `structlog` for logging, with `# ΛTRACE` for key operations.

## Key Utilities

The `core.lukhas_utils` module (currently via `__init__.py`) provides:

-   **`generate_symbolic_id(prefix: str = "sym_") -> str`**:
    -   Generates unique LUKHAS-specific symbolic identifiers.
    -   `# ΛUTIL`, `# ΛNOTE`, `# ΛECHO`.
-   **`legacy_parse_lukhas_command(command_string: str) -> Optional[Dict[str, Any]]`**:
    -   An example of a parser for a simple, LUKHAS-specific legacy command string.
    -   `# ΛUTIL`, `# ΛLEGACY`, `# ΛNOTE`, `# ΛCAUTION` (due to `eval`).
-   **`create_diagnostic_payload(component_id: str, status: SystemStatus, message: str, additional_data: Optional[Dict] = None) -> Dict`**:
    -   Creates a standardized diagnostic message payload for LUKHAS components.
    -   `# ΛUTIL`, `# ΛNOTE`, `# ΛECHO`.
    -   **Overlap/Move Candidate**: This utility is noted as a potential candidate for relocation to `core/diagnostic_engine/` if its functionality becomes more complex or tightly integrated with that engine's specific requirements.

*(An example placeholder for `experimental_dream_signature` is commented out in `__init__.py` to illustrate where a `# ΛDREAM_LOOP` related utility might go.)*

## Experimental or Deprecated Logic

-   **Experimental**: Any new, unproven utilities or those undergoing active development should be clearly marked with `# ΛCAUTION` and detailed notes about their experimental status in their docstrings and potentially in this README.
-   **Deprecated/Legacy**: Utilities like `legacy_parse_lukhas_command` are explicitly tagged `# ΛLEGACY`. Their use in new development is discouraged. This README should highlight such functions and suggest alternatives if available.

## Overlap and Potential Relocation

-   **`core/diagnostic_engine/`**: The `create_diagnostic_payload` utility is a prime candidate for evaluation. If the `diagnostic_engine` develops its own specific payload formats or requires more intricate logic for payload creation, this function might be better suited there. Currently, it serves as a general LUKHAS formatting tool.
-   **`identity/`**: If any utilities here deal with LUKHAS ID generation in a way that conflicts or overlaps with `core/identity/` or `lukhas/identity/` systems, this should be flagged. `generate_symbolic_id` is for general symbolic entities, not necessarily user/agent identities.
-   **`lukhas_analyze/`**: Utilities for data processing or transformation specific to LUKHAS analysis tasks might evolve here. If they become highly specialized for `lukhas_analyze`, they could be moved.
-   **`orchestration/`**: Utilities that support LUKHAS-specific orchestration patterns might be developed here.

Any significant overlaps or firm decisions on relocation should be documented in `JULES06_OVERLAP_TRACKER.md`.

## How to Use

Import functions from `core.lukhas_utils`:
```python
from core.lukhas_utils import generate_symbolic_id, create_diagnostic_payload
from core.common import SystemStatus # Assuming SystemStatus is used

# Generate a LUKHAS-specific ID
event_id = generate_symbolic_id("event_")

# Create a diagnostic report
report = create_diagnostic_payload(
    component_id="lukhas.core.moduleX",
    status=SystemStatus.WARNING,
    message="Unexpected latency detected.",
    additional_data={"latency_ms": 2000}
)
```

## Contribution Guidelines

-   Ensure new utilities are genuinely LUKHAS-specific or experimental. For general-purpose helpers, use `core.helpers`.
-   Clearly document the purpose, usage, and any LUKHAS-specific conventions related to the utility.
-   Use ΛTAGS appropriately, especially `# ΛLEGACY`, `# ΛCAUTION`, and `# ΛECHO`.
-   If a utility is experimental, state this clearly.
-   Consider if a new utility might better belong in a more specialized module (e.g., `diagnostic_engine`) and discuss/note this.
-   Update this README with new utilities or changes in status (e.g., experimental to stable, or flagging for deprecation).
