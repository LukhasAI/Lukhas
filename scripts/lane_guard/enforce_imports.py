
import ast
import os
import sys

FORBIDDEN_IMPORT = "lukhas"
CANDIDATE_DIR = "candidate"

def check_imports(file_path):
    with open(file_path, "r") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"Error parsing {file_path}: {e}")
        return []

    errors = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(FORBIDDEN_IMPORT):
                    errors.append(f"{file_path}:{node.lineno}: Found forbidden import: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith(FORBIDDEN_IMPORT):
                errors.append(f"{file_path}:{node.lineno}: Found forbidden import from: {node.module}")

    return errors

def main():
    found_errors = False
    for root, _, files in os.walk(CANDIDATE_DIR):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                errors = check_imports(file_path)
                if errors:
                    found_errors = True
                    for error in errors:
                        print(error)

    if found_errors:
        sys.exit(1)
    else:
        print("No forbidden imports found.")

if __name__ == "__main__":
    main()
