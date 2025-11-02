# Code Style Guide

This project enforces a consistent code style to ensure readability and maintainability. We use the following tools to automate this process:

- **Black**: For uncompromising code formatting.
- **Ruff**: For fast and comprehensive linting.
- **mypy**: For static type checking.

These tools are configured to run automatically as pre-commit hooks and as part of our GitHub Actions CI/CD pipeline. This means that all code is automatically checked for style and correctness before it is committed or merged.

## Black

Black is a code formatter that reformats your Python code to a consistent style. You don't need to do anything to use it, as it runs automatically when you commit your changes.

## Ruff

Ruff is a linter that checks your code for a wide range of potential errors and style issues. Like Black, it runs automatically on commit.

### Import Ordering

Ruff also enforces a consistent import order. Imports are grouped into sections and sorted alphabetically. The sections are:

1.  Standard library imports
2.  Third-party imports
3.  First-party imports

## mypy

mypy is a static type checker for Python. It helps to catch type errors before they cause issues at runtime. mypy is also run automatically on commit.

### Type Annotation Standards

- All new code should be fully type-annotated.
- Use modern type hints (e.g., `list[int]` instead of `typing.List[int]`)
- Avoid `typing.Any` whenever possible.

## When to use # noqa

The `# noqa` comment is used to suppress a linter warning on a specific line. It should be used sparingly and only when there is a good reason to ignore a warning.

### Examples

-   **Intentional delayed imports**: In some cases, you may need to delay an import to avoid circular dependencies or for performance reasons. In these cases, you can use `# noqa: E402` to suppress the "module level import not at top of file" warning.

    ```python
    def my_function():
        import my_module  # noqa: E402
        ...
    ```

-   **False positives**: Sometimes, a linter may produce a false positive. If you are sure that the code is correct, you can use `# noqa` to suppress the warning. Always add a comment explaining why the warning is a false positive.

    ```python
    # The linter thinks this is a typo, but it's actually a valid name.
    my_variable = "foobar"  # noqa: TYPO001
    ```

## Lane Boundary Rules

The project is divided into "lanes," which are distinct parts of the codebase with different rules and dependencies. The lanes are:

-   `lukhas/`: The core application code.
-   `core/`: The core framework code.
-   `matriz/`: The data processing code.
-   `tests/`: The test code.
-   `tools/`: The development tools.

The following rules apply to imports between lanes:

-   Code in `lukhas/` can import from `core/` and `matriz/`.
-   Code in `core/` and `matriz/` cannot import from `lukhas/`.
-   Code in `tests/` and `tools/` can import from any lane.

These rules are enforced by the `import-linter` pre-commit hook.

## Manual Checks

If you want to run the checks manually, you can use the following commands:

```bash
black .
ruff check .
mypy .
```
