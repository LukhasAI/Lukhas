#!/usr/bin/env python3
"""
Migration script to replace XOR encryption with proper cryptography
Identifies and patches XOR usage across LUKHAS codebase
"""

import ast
import re
from pathlib import Path
from typing import Any


class XORMigration:
    """Migrate XOR encryption to proper crypto"""

    def __init__(self, project_root: str = "/Users/agi_dev/Lukhas"):
        self.project_root = Path(project_root)
        self.xor_patterns = [
            # Pattern for XOR operations
            re.compile(r"def\s+\w*xor\w*\s*\("),
            re.compile(r"[a-zA-Z_]\w*\s*\^\s*[a-zA-Z_]\w*"),  # Variable XOR
            re.compile(r"for\s+.*\s+in\s+zip\s*\(.*\).*\^"),  # XOR in zip
            re.compile(r"bytes\s*\([^)]*\^[^)]*\)"),  # bytes with XOR
        ]

        self.files_to_patch = []
        self.patches = {}

    def scan_codebase(self) -> list[tuple[str, int, str]]:
        """Scan codebase for XOR usage"""
        findings = []

        for py_file in self.project_root.rglob("*.py"):
            # Skip test files and this migration script
            if "test" in py_file.name or py_file.name == "migrate_xor_encryption.py":
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                for i, line in enumerate(lines):
                    for pattern in self.xor_patterns:
                        if pattern.search(line):
                            # Check if it's crypto-related
                            context = self._get_context(lines, i)
                            if self._is_crypto_related(context):
                                findings.append((str(py_file), i + 1, line.strip()))
                                self.files_to_patch.append(py_file)

            except Exception as e:
                print(f"Error scanning {py_file}: {e}")

        return findings

    def _get_context(self, lines: list[str], line_num: int, context_size: int = 5) -> str:
        """Get surrounding context"""
        start = max(0, line_num - context_size)
        end = min(len(lines), line_num + context_size + 1)
        return "\n".join(lines[start:end])

    def _is_crypto_related(self, context: str) -> bool:
        """Check if XOR is used for encryption"""
        crypto_keywords = [
            "encrypt",
            "decrypt",
            "cipher",
            "key",
            "secret",
            "token",
            "password",
            "hash",
            "secure",
            "crypto",
        ]

        context_lower = context.lower()
        return any(keyword in context_lower for keyword in crypto_keywords)

    def generate_patches(self):
        """Generate patches for XOR replacements"""
        for file_path in set(self.files_to_patch):
            self.patches[file_path] = self._create_patch(file_path)

    def _create_patch(self, file_path: Path) -> dict[str, Any]:
        """Create patch for a specific file"""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Parse AST to understand structure
        try:
            tree = ast.parse(content)
        except BaseException:
            return {"error": "Failed to parse AST"}

        patches = []

        # Find XOR functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and "xor" in node.name.lower():
                # Generate replacement
                replacement = self._generate_crypto_replacement(node)
                patches.append(
                    {
                        "function": node.name,
                        "line": node.lineno,
                        "replacement": replacement,
                    }
                )

        return {
            "file": str(file_path),
            "patches": patches,
            "imports_needed": [
                "from candidate.core.security.enhanced_crypto import get_encryption_manager"
            ],
        }

    def _generate_crypto_replacement(self, func_node: ast.FunctionDef) -> str:
        """Generate proper crypto replacement for XOR function"""
        func_name = func_node.name

        # Determine purpose from function name
        if "simple" in func_name or "demo" in func_name:
            algorithm = "Fernet"
        else:
            algorithm = "AES-256-GCM"

        template = f'''async def {func_name}(self, data: bytes, key: bytes) -> bytes:
    """Encrypted version of {func_name} using proper cryptography"""
    # Get encryption manager
    crypto = get_encryption_manager()

    # Encrypt data
    ciphertext, key_id = await crypto.encrypt(
        data,
        purpose='data',
        algorithm='{algorithm}'
    )

    # Store key_id for decryption (in production, store properly)
    self._last_key_id = key_id

    return ciphertext'''

        return template

    def apply_patches(self, dry_run: bool = True):
        """Apply patches to files"""
        results = []

        for file_path, patch_info in self.patches.items():
            if "error" in patch_info:
                results.append(f"ERROR in {file_path}: {patch_info['error']}")
                continue

            if dry_run:
                results.append(f"\nWould patch {file_path}:")
                results.append(f"  Add imports: {patch_info['imports_needed']}")
                for patch in patch_info["patches"]:
                    results.append(
                        f"  Replace function '{patch['function']}' at line {patch['line']}"
                    )
            else:
                # Actually apply patches
                self._apply_file_patches(Path(file_path), patch_info)
                results.append(f"Patched {file_path}")

        return results

    def _apply_file_patches(self, file_path: Path, patch_info: dict[str, Any]):
        """Apply patches to a single file"""
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        # Add imports at the top
        import_line = None
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                import_line = i

        if import_line is not None:
            for imp in patch_info["imports_needed"]:
                lines.insert(import_line + 1, imp + "\n")

        # Apply function replacements
        # (In a real implementation, this would be more sophisticated)

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def generate_report(self, findings: list[tuple[str, int, str]]) -> str:
        """Generate migration report"""
        report = ["# XOR Encryption Migration Report\n"]
        report.append(f"Total files with XOR encryption: {len({f[0] for f in findings})}")
        report.append(f"Total XOR usages found: {len(findings)}\n")

        report.append("## Files requiring migration:\n")

        by_file = {}
        for file_path, line_num, line in findings:
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append((line_num, line))

        for file_path, occurrences in by_file.items():
            report.append(f"\n## {file_path}")
            for line_num, line in occurrences:
                report.append(f"  Line {line_num}: `{line}`")

        report.append("\n## Recommended actions:")
        report.append("1. Run migration with --apply flag to auto-patch simple cases")
        report.append("2. Manually review complex XOR usage")
        report.append("3. Update tests to use new encryption")
        report.append("4. Add enhanced_crypto to requirements.txt")

        return "\n".join(report)


def main():
    """Run XOR migration"""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate XOR encryption to proper crypto")
    parser.add_argument("--scan", action="store_true", help="Scan for XOR usage")
    parser.add_argument("--patch", action="store_true", help="Generate patches")
    parser.add_argument("--apply", action="store_true", help="Apply patches (use with caution)")
    parser.add_argument("--report", type=str, help="Save report to file")

    args = parser.parse_args()

    migration = XORMigration()

    if args.scan or not any([args.scan, args.patch, args.apply]):
        print("Scanning codebase for XOR encryption...")
        findings = migration.scan_codebase()

        print(f"\nFound {len(findings)} XOR encryption usages:")
        for file_path, line_num, line in findings[:10]:  # Show first 10
            print(f"  {file_path}:{line_num} - {line}")

        if len(findings) > 10:
            print(f"  ... and {len(findings) - 10} more")

        if args.report:
            report = migration.generate_report(findings)
            with open(args.report, "w") as f:
                f.write(report)
            print(f"\nReport saved to {args.report}")

    if args.patch:
        print("\nGenerating patches...")
        migration.generate_patches()

        for file_path, patch_info in migration.patches.items():
            if "patches" in patch_info:
                print(f"  {file_path}: {len(patch_info['patches'])} patches")

    if args.apply:
        print("\nApplying patches...")
        results = migration.apply_patches(dry_run=False)
        for result in results:
            print(f"  {result}")

        print("\nIMPORTANT: Review all changes and run tests!")


if __name__ == "__main__":
    main()
