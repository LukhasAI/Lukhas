# Investigation Report: `lukhas.api` Import Stability

**Date:** 2025-11-12

**Author:** Jules

## 1. Summary

This investigation was initiated to address import safety and stability within the `lukhas_website.lukhas.api` module. The initial state of the `api/__init__.py` file used dynamic `sys.path` manipulation, which is a fragile and opaque way to manage dependencies.

The `__init__.py` was refactored to use explicit relative imports, which is a more robust and standard Python practice. However, creating a validation test for this change revealed a cascade of `ImportError` exceptions stemming from deep, cross-cutting dependencies and a circular import issue in a related module.

This report documents the findings and recommends an architectural review of the `api` module and its dependencies.

## 2. Findings

### 2.1. Initial State of `api/__init__.py`

- The module dynamically appended a path to `sys.path`.
- It used a broad `contextlib.suppress(ImportError)` block, hiding potential import failures.
- Analysis showed that no other modules in the codebase relied on this dynamic behavior; submodules were imported directly (e.g., `from lukhas.api.auth_helpers import ...`).

### 2.2. Refactoring and Testing Issues

The `api/__init__.py` was refactored to explicitly import its submodules (e.g., `from . import auth_helpers`). A validation test was created to ensure all submodules were exposed correctly. This test immediately failed, revealing a chain of unresolved dependencies.

The following import errors were encountered sequentially:

1.  **`NameError: name 'Dict' is not defined`**
    -   **Source:** `lukhas_website/lukhas/api/system_endpoints.py`
    -   **Reason:** Missing `from typing import Dict`.
    -   **Status:** Fixed.

2.  **`ModuleNotFoundError: No module named 'fastapi'`**
    -   **Source:** `lukhas_website/lukhas/api/auth_helpers.py` and other submodules.
    -   **Reason:** Core dependency for the API modules.

3.  **`ModuleNotFoundError: No module named 'structlog'`**
    -   **Source:** `lukhas_website/lukhas/api/identity.py`
    -   **Reason:** Logging dependency.

4.  **`ModuleNotFoundError: No module named 'opentelemetry'`**
    -   **Source:** `lukhas_website/lukhas/api/oidc.py`
    -   **Reason:** Tracing/metrics dependency.

5.  **`ModuleNotFoundError: No module named 'prometheus_client'`**
    -   **Source:** `lukhas_website/lukhas/api/oidc.py`
    -   **Reason:** Metrics dependency.

6.  **`ModuleNotFoundError: No module named 'streamlit'`**
    -   **Source:** `lukhas_website/lukhas/api/oidc.py`
    -   **Reason:** Unclear why an OIDC module would depend on a UI framework.

7.  **`ImportError: cannot import name 'auth' from partially initialized module 'governance.identity'`**
    -   **Source:** `lukhas_website/lukhas/api/identity.py` (and others)
    -   **Reason:** This points to a **circular dependency** within the `lukhas.governance` module, which is imported by `lukhas.api.identity`. This is a critical architectural issue that prevents the entire module from loading.

### 2.3. Dependency Chain and Circularity

The import chain is roughly as follows:

`test_api_import.py` -> `lukhas.api` -> `lukhas.api.identity` -> `lukhas.governance` -> `governance.identity` -> (circular import)

The `api` module, which should theoretically be a stable interface, is tightly coupled to the `governance` and `identity` systems. The circular dependency within `governance` makes it impossible to reliably import *any* module that depends on it, including `lukhas.api`.

## 3. Recommendations

### 3.1. On the `__init__.py` Strategy

The refactored `__init__.py` with explicit relative imports is the correct approach. It makes dependencies clear and avoids `sys.path` magic.

However, whether this `__init__.py` should expose *all* submodules is now questionable. Given the dependency issues, it may be better to have a minimal `__init__.py` and encourage direct, targeted imports from consumers, e.g., `from lukhas.api.dreams import router`. This would prevent a consumer from unintentionally trying to load the entire dependency graph of the `api` module.

### 3.2. Architectural Review

A **needs-architecture-review** is strongly recommended.

1.  **Decouple the `api` module:** The `api` module should not have so many transitive dependencies on complex systems like `governance`. It should be a lightweight layer that routes requests, ideally depending on interfaces or adapters rather than concrete implementations.
2.  **Resolve the circular dependency:** The circular import in `lukhas.governance` must be broken. This is a critical flaw that will continue to cause instability.
3.  **Dependency Audit:** The dependencies of each `api` submodule should be reviewed. The presence of `streamlit` in an OIDC implementation, for example, is highly suspect and may indicate misplaced logic.

### 3.3. On Testing

Creating a working, isolated test for `lukhas.api` is not feasible without extensive, brittle mocking of large parts of the LUKHAS application. This is a strong signal that the module is not well-encapsulated.

**Do not create a broken test.** The test files created during this investigation will be removed. Future testing efforts should resume only after the architectural issues are addressed.
