# Getting Started with LUKHAS AI

This guide will help you get started with the LUKHAS AI project.

## 1. Environment Setup

First, you need to set up your Python environment. We recommend using a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Some examples and tests require additional dependencies. You can install them with:

```bash
pip install qiskit simpleaudio pip-audit
sudo apt-get update && sudo apt-get install -y libasound2-dev
```

## 2. Running the Examples

The `candidate` directory contains several examples that demonstrate the basic functionality of the different modules. You can run them directly from the command line.

For example, to run the core module example:

```bash
python candidate/core/examples/basic/example.py
```

To run the bridge module example, you will need to set the `OPENAI_API_KEY` environment variable:

```bash
export OPENAI_API_KEY="your-api-key"
python candidate/bridge/examples/basic/example.py
```

## 3. Running the Tests

The `tests` directory contains unit, integration, and security tests. You can run all the tests with `pytest`:

```bash
pytest
```

To run a specific test file:

```bash
pytest tests/unit/core_functionality_test.py
```

### Coverage

The project is configured to measure test coverage. After running the tests, you can view the coverage report in the terminal. The required coverage is 15%.

## 4. Next Steps

Now that you have a basic understanding of the project, you can start exploring the different modules and contributing to the codebase. Here are some good places to start:

*   Read the `AGENTS.md` file in the root directory for an overview of the project.
*   Read the `README.md` files in the `candidate` and `lukhas` directories for more information about the different modules.
*   Explore the examples in the `candidate` directory to see how the different modules are used.
*   Run the tests in the `tests` directory to see how the different modules are tested.
