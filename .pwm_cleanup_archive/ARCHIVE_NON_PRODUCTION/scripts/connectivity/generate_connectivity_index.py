import ast
import json
import os
from dataclasses import dataclass, field
from typing import Dict, Set

# ΛTAG: connectivity_index_script


@dataclass
class SymbolInfo:
    name: str
    kind: str  # class/function/dataclass
    used: bool = False
    used_by: Set[str] = field(default_factory=set)


def collect_definitions(file_path: str) -> Dict[str, SymbolInfo]:
    with open(file_path, encoding="utf-8", errors="ignore") as f:
        source = f.read()
    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError:
        return {}
    definitions: Dict[str, SymbolInfo] = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            kind = (
                "dataclass"
                if any(
                    isinstance(dec, ast.Name)
                    and dec.id == "dataclass"
                    or isinstance(dec, ast.Attribute)
                    and dec.attr == "dataclass"
                    for dec in node.decorator_list
                )
                else "class"
            )
            definitions[node.name] = SymbolInfo(name=node.name, kind=kind)
        elif isinstance(node, ast.FunctionDef):
            definitions[node.name] = SymbolInfo(name=node.name, kind="function")
    return definitions


def module_name(repo_root: str, file_path: str) -> str:
    rel = os.path.relpath(file_path, repo_root)
    return os.path.splitext(rel)[0].replace(os.sep, ".")


def collect_imports(repo_root: str) -> Dict[tuple, Set[str]]:
    imports: Dict[tuple, Set[str]] = {}
    for root, _dirs, files in os.walk(repo_root):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                try:
                    with open(path, encoding="utf-8", errors="ignore") as src:
                        tree = ast.parse(src.read(), filename=path)
                except SyntaxError:
                    continue
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        mod = node.module
                        if node.level:
                            current_mod_parts = module_name(repo_root, path).split(".")
                            base = current_mod_parts[: -node.level]
                            if mod:
                                mod = ".".join(base + [mod])
                            else:
                                mod = ".".join(base)
                        if mod:
                            for alias in node.names:
                                key = (mod, alias.name)
                                imports.setdefault(key, set()).add(path)
    return imports


def generate_connectivity_index(target_dir: str, repo_root: str) -> Dict:
    imports = collect_imports(repo_root)
    result = {"directory": os.path.relpath(target_dir, repo_root), "files": []}
    for root, _dirs, files in os.walk(target_dir):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                defs = collect_definitions(path)
                mod = module_name(repo_root, path)
                file_entry = {"path": os.path.relpath(path, repo_root), "symbols": []}
                for name, info in defs.items():
                    used_by = imports.get((mod, name), set())
                    info.used = bool(used_by)
                    info.used_by = {os.path.relpath(p, repo_root) for p in used_by}
                    file_entry["symbols"].append(
                        {
                            "name": info.name,
                            "kind": info.kind,
                            "used": info.used,
                            "used_by": sorted(info.used_by),
                        }
                    )
                result["files"].append(file_entry)
    return result


def write_reports(index: Dict, output_dir: str) -> None:
    json_path = os.path.join(output_dir, "CONNECTIVITY_INDEX.json")
    md_path = os.path.join(output_dir, "CONNECTIVITY_INDEX.md")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Connectivity Index for {index['directory']}\n\n")
        for file in index["files"]:
            f.write(f"## {file['path']}\n\n")
            f.write("| Name | Kind | Used | Used By |\n")
            f.write("| --- | --- | --- | --- |\n")
            for sym in file["symbols"]:
                used_by = ", ".join(sym["used_by"]) if sym["used_by"] else "N/A"
                f.write(
                    f"| {sym['name']} | {sym['kind']} | {sym['used']} | {used_by} |\n"
                )
            f.write("\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate connectivity index for a module"
    )
    parser.add_argument("target", help="Target directory to analyze")
    parser.add_argument("--repo-root", default=os.getcwd(), help="Repository root")
    args = parser.parse_args()

    index = generate_connectivity_index(args.target, args.repo_root)
    write_reports(index, args.target)
    print(f"Connectivity index generated at {args.target}")
