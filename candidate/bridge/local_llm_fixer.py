#!/usr/bin/env python3
"""
LUKHAS Local LLM Code Fixer
Integrates with Ollama/Deepseek for autonomous code quality improvements
Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""
import streamlit as st

import ast
import asyncio
import json
import logging
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import aiohttp

logger = logging.getLogger(__name__)


class FixType(Enum):
    """Types of fixes we can apply"""

    SYNTAX_ERROR = "syntax_error"
    UNDEFINED_NAME = "undefined_name"
    UNUSED_IMPORT = "unused_import"
    FORMATTING = "formatting"
    TYPE_ANNOTATION = "type_annotation"
    DOCSTRING = "docstring"


@dataclass
class CodeIssue:
    """Represents a code issue to fix"""

    file_path: str
    line_number: int
    issue_type: FixType
    message: str
    code_context: str
    severity: float = 0.5  # 0.0 to 1.0


@dataclass
class CodeFix:
    """Represents a proposed fix"""

    issue: CodeIssue
    original_code: str
    fixed_code: str
    confidence: float  # 0.0 to 1.0
    explanation: str


class LocalLLMFixer:
    """
    Integrates with local LLMs (Ollama) to fix code issues automatically.
    Uses LUKHAS consciousness principles for intelligent fixing.
    """

    def __init__(
        self,
        ollama_host: str = "http://localhost:11434",
        model: str = "deepseek-coder:6.7b",
        guardian_threshold: float = 0.85,
    ):
        self.ollama_host = ollama_host
        self.model = model
        self.guardian_threshold = guardian_threshold
        self.session: Optional[aiohttp.ClientSession] = None

        # Track fixes for learning
        self.successful_fixes: list[CodeFix] = []
        self.failed_fixes: list[CodeFix] = []

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def check_ollama_available(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            async with self.session.get(f"{self.ollama_host}/api/tags") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = [m["name"] for m in data.get("models", [])]
                    return self.model in models
        except Exception as e:
            logger.error(f"Ollama not available: {e}")
        return False

    async def analyze_file(self, file_path: str) -> list[CodeIssue]:
        """Analyze a Python file for issues"""
        issues = []

        try:
            with open(file_path) as f:
                content = f.read()

            # Check for syntax errors
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append(
                    CodeIssue(
                        file_path=file_path,
                        line_number=e.lineno or 0,
                        issue_type=FixType.SYNTAX_ERROR,
                        message=str(e),
                        code_context=self._get_context(content, e.lineno or 0),
                        severity=1.0,
                    )
                )

            # Run ruff for other issues
            issues.extend(await self._run_ruff_analysis(file_path))

        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")

        return issues

    async def _run_ruff_analysis(self, file_path: str) -> list[CodeIssue]:
        """Run ruff to find code issues"""
        issues = []

        try:
            result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "ruff",
                    "check",
                    file_path,
                    "--output-format",
                    "json",
                ],
                capture_output=True,
                text=True,
            )

            if result.stdout:
                ruff_issues = json.loads(result.stdout)
                for issue in ruff_issues:
                    issues.append(
                        CodeIssue(
                            file_path=file_path,
                            line_number=issue.get("location", {}).get("row", 0),
                            issue_type=self._map_ruff_code(issue.get("code", "")),
                            message=issue.get("message", ""),
                            code_context="",  # Will be filled later
                            severity=(0.7 if issue.get("code", "").startswith("F") else 0.5),
                        )
                    )
        except Exception as e:
            logger.error(f"Ruff analysis failed: {e}")

        return issues

    def _map_ruff_code(self, code: str) -> FixType:
        """Map ruff error codes to FixType"""
        if code.startswith("F821"):
            return FixType.UNDEFINED_NAME
        elif code.startswith("F401"):
            return FixType.UNUSED_IMPORT
        elif code.startswith("E") or code.startswith("W"):
            return FixType.FORMATTING
        elif code.startswith("UP"):
            return FixType.TYPE_ANNOTATION
        else:
            return FixType.FORMATTING

    def _get_context(self, content: str, line_number: int, context_lines: int = 3) -> str:
        """Get code context around a line"""
        lines = content.split("\n")
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)
        return "\n".join(lines[start:end])

    async def generate_fix(self, issue: CodeIssue) -> Optional[CodeFix]:
        """Generate a fix for a code issue using local LLM"""
        if not self.session:
            logger.error("Session not initialized")
            return None

        # Read the file content
        try:
            with open(issue.file_path) as f:
                content = f.read()
                lines = content.split("\n")
        except Exception as e:
            logger.error(f"Cannot read file {issue.file_path}: {e}")
            return None

        # Create prompt for LLM
        prompt = self._create_fix_prompt(issue, lines)

        # Call Ollama API
        try:
            response = await self._call_ollama(prompt)
            if response:
                return self._parse_fix_response(issue, response, lines)
        except Exception as e:
            logger.error(f"LLM fix generation failed: {e}")

        return None

    def _create_fix_prompt(self, issue: CodeIssue, lines: list[str]) -> str:
        """Create a prompt for the LLM to fix the issue"""
        context_start = max(0, issue.line_number - 5)
        context_end = min(len(lines), issue.line_number + 5)
        code_context = "\n".join(lines[context_start:context_end])

        prompt = f"""Fix the following Python code issue:

Issue Type: {issue.issue_type.value}
Error Message: {issue.message}
Line Number: {issue.line_number}

Code Context:
```python
{code_context}
```

Provide ONLY the fixed code for the problematic line(s). Do not include explanations or markdown.
Fixed code:"""

        return prompt

    async def _call_ollama(self, prompt: str) -> Optional[str]:
        """Call Ollama API for code generation"""
        try:
            async with self.session.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Low temperature for code fixes
                        "top_p": 0.9,
                        "max_tokens": 500,
                    },
                },
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("response", "")
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
        return None

    def _parse_fix_response(self, issue: CodeIssue, response: str, lines: list[str]) -> Optional[CodeFix]:
        """Parse LLM response into a CodeFix"""
        # Clean the response
        fixed_code = response.strip()

        # Remove markdown if present
        if "```" in fixed_code:
            fixed_code = re.search(r"```(?:python)?\n?(.*?)\n?```", fixed_code, re.DOTALL)
            fixed_code = fixed_code.group(1) if fixed_code else response.strip()

        # Get original code
        original_code = lines[issue.line_number - 1] if issue.line_number > 0 else ""

        # Calculate confidence based on issue type
        confidence = self._calculate_confidence(issue.issue_type, fixed_code)

        return CodeFix(
            issue=issue,
            original_code=original_code,
            fixed_code=fixed_code,
            confidence=confidence,
            explanation=f"Auto-fixed {issue.issue_type.value}",
        )

    def _calculate_confidence(self, fix_type: FixType, fixed_code: str) -> float:
        """Calculate confidence in a fix"""
        # Simple heuristic for now
        confidence_map = {
            FixType.FORMATTING: 0.95,
            FixType.UNUSED_IMPORT: 0.90,
            FixType.SYNTAX_ERROR: 0.70,
            FixType.UNDEFINED_NAME: 0.60,
            FixType.TYPE_ANNOTATION: 0.75,
            FixType.DOCSTRING: 0.85,
        }

        base_confidence = confidence_map.get(fix_type, 0.5)

        # Adjust based on code length (shorter fixes are usually safer)
        if len(fixed_code) < 50:
            base_confidence += 0.05
        elif len(fixed_code) > 200:
            base_confidence -= 0.10

        return min(max(base_confidence, 0.0), 1.0)

    async def apply_fix(self, fix: CodeFix, dry_run: bool = False) -> bool:
        """Apply a fix to the file"""
        if fix.confidence < self.guardian_threshold:
            logger.warning(f"Fix confidence {fix.confidence} below threshold {self.guardian_threshold}")
            return False

        try:
            with open(fix.issue.file_path) as f:
                lines = f.readlines()

            # Apply the fix
            if fix.issue.line_number > 0 and fix.issue.line_number <= len(lines):
                lines[fix.issue.line_number - 1] = fix.fixed_code + "\n"

            if not dry_run:
                with open(fix.issue.file_path, "w") as f:
                    f.writelines(lines)

                # Verify the fix didn't break syntax
                try:
                    with open(fix.issue.file_path) as f:
                        ast.parse(f.read())
                    self.successful_fixes.append(fix)
                    return True
                except SyntaxError:
                    # Revert the fix
                    lines[fix.issue.line_number - 1] = fix.original_code + "\n"
                    with open(fix.issue.file_path, "w") as f:
                        f.writelines(lines)
                    self.failed_fixes.append(fix)
                    return False
            else:
                logger.info(f"[DRY RUN] Would apply fix to {fix.issue.file_path}:{fix.issue.line_number}")
                return True

        except Exception as e:
            logger.error(f"Failed to apply fix: {e}")
            self.failed_fixes.append(fix)
            return False

    async def fix_file(self, file_path: str, dry_run: bool = False) -> dict[str, Any]:
        """Fix all issues in a file"""
        results = {
            "file": file_path,
            "issues_found": 0,
            "fixes_applied": 0,
            "fixes_failed": 0,
            "fixes": [],
        }

        # Analyze the file
        issues = await self.analyze_file(file_path)
        results["issues_found"] = len(issues)

        # Generate and apply fixes
        for issue in issues:
            fix = await self.generate_fix(issue)
            if fix:
                success = await self.apply_fix(fix, dry_run)
                if success:
                    results["fixes_applied"] += 1
                else:
                    results["fixes_failed"] += 1
                results["fixes"].append(
                    {
                        "issue": issue.message,
                        "confidence": fix.confidence,
                        "success": success,
                    }
                )

        return results

    def get_learning_stats(self) -> dict[str, Any]:
        """Get statistics about fixes for learning"""
        return {
            "successful_fixes": len(self.successful_fixes),
            "failed_fixes": len(self.failed_fixes),
            "success_rate": len(self.successful_fixes) / max(1, len(self.successful_fixes) + len(self.failed_fixes)),
            "average_confidence": sum(f.confidence for f in self.successful_fixes) / max(1, len(self.successful_fixes)),
        }


async def main():
    """Example usage"""
    async with LocalLLMFixer() as fixer:
        # Check if Ollama is available
        if not await fixer.check_ollama_available():
            print("❌ Ollama not available. Please install and run Ollama with deepseek-coder model.")
            print("   brew install ollama")
            print("   ollama pull deepseek-coder:6.7b")
            print("   ollama serve")
            return

        # Fix a specific file
        results = await fixer.fix_file("example.py", dry_run=True)
        print(f"Fixed {results['fixes_applied']} issues in {results['file']}")

        # Get learning stats
        stats = fixer.get_learning_stats()
        print(f"Success rate: {stats['success_rate']:.1%}")


if __name__ == "__main__":
    asyncio.run(main())
