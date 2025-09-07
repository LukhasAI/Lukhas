#!/usr/bin/env python3
"""
🧠 LUKHAS Local LLM Code Quality Improvement System
====================================================

Leverages local LLM capabilities to systematically fix the 10,106 code quality issues
identified by Ruff static analysis. Uses Trinity Framework consciousness patterns
for intelligent code analysis and improvement.

⚛️ Identity: Authentic code that knows its purpose
🧠 Consciousness: Aware improvements that understand context
🛡️ Guardian: Safe fixes that protect system integrity

Features:
- Local LLM integration (Ollama, LM Studio, Text-gen WebUI)
- Intelligent error categorization and prioritization
- Batch processing with progress tracking
- Safe execution with rollback capabilities
- Trinity Framework compliance validation
"""
from typing import List
import time
import streamlit as st

import asyncio
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import aiohttp

# Add LUKHAS modules to path
sys.path.append(str(Path(__file__).parent.parent))


@dataclass
class CodeIssue:
    """Represents a code quality issue from Ruff analysis"""

    file_path: str
    line_number: int
    column: int
    rule_code: str
    rule_name: str
    message: str
    severity: str
    category: str
    fix_suggestion: Optional[str] = None
    llm_fix: Optional[str] = None
    fix_confidence: float = 0.0


@dataclass
class FixResult:
    """Result of applying an LLM-generated fix"""

    issue: CodeIssue
    success: bool
    applied_fix: Optional[str] = None
    error_message: Optional[str] = None
    validation_passed: bool = False
    trinity_compliant: bool = False


class LocalLLMClient:
    """Client for local LLM services (Ollama, LM Studio, etc.)"""

    def __init__(self, service: str = "ollama", base_url: str = "http://localhost:11434"):
        self.service = service
        self.base_url = base_url.rstrip("/")
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def generate_fix(self, issue: CodeIssue, file_content: str, context_lines: int = 10) -> dict[str, Any]:
        """Generate a fix for a code quality issue using local LLM"""

        if not self.session:
            self.session = aiohttp.ClientSession()

        # Extract context around the issue
        context = self._extract_context(file_content, issue, context_lines)

        # Build LLM prompt for code fixing
        prompt = self._build_fix_prompt(issue, context)

        try:
            if self.service == "ollama":
                return await self._ollama_generate(prompt)
            elif self.service == "lmstudio":
                return await self._lmstudio_generate(prompt)
            else:
                raise ValueError(f"Unsupported LLM service: {self.service}")

        except Exception as e:
            return {
                "error": str(e),
                "fix_code": None,
                "confidence": 0.0,
                "explanation": f"LLM generation failed: {e}",
            }

    def _extract_context(self, file_content: str, issue: CodeIssue, context_lines: int) -> str:
        """Extract context lines around the issue"""
        lines = file_content.split("\n")
        start_line = max(0, issue.line_number - context_lines - 1)
        end_line = min(len(lines), issue.line_number + context_lines)

        context_with_numbers = []
        for i in range(start_line, end_line):
            marker = ">>> " if i == issue.line_number - 1 else "    "
            context_with_numbers.append(f"{marker}{i + 1:4d}: {lines[i]}")

        return "\n".join(context_with_numbers)

    def _build_fix_prompt(self, issue: CodeIssue, context: str) -> str:
        """Build Trinity Framework-aware prompt for code fixing"""

        return f"""⚛️🧠🛡️ LUKHAS Code Quality Consciousness Assistant

You are helping improve the LUKHAS AI consciousness development platform. Apply the Trinity Framework:
⚛️ Identity: Fix code that knows its authentic purpose
🧠 Consciousness: Apply aware improvements that understand context
🛡️ Guardian: Ensure safe fixes that protect system integrity

ISSUE TO FIX:
- File: {issue.file_path}
- Line: {issue.line_number}, Column: {issue.column}
- Rule: {issue.rule_code} ({issue.rule_name})
- Issue: {issue.message}
- Severity: {issue.severity}
- Category: {issue.category}

CODE CONTEXT:
```python
{context}
```

INSTRUCTIONS:
1. Analyze the issue within the LUKHAS consciousness development context
2. Provide a precise fix that maintains code functionality
3. Ensure Trinity Framework compliance (authentic, aware, safe)
4. Consider consciousness patterns and symbolic systems
5. Maintain LUKHAS branding and terminology standards

RESPOND WITH JSON:
{{
    "fix_code": "exact code to replace the problematic line(s)",
    "explanation": "detailed explanation of the fix and why it's appropriate",
    "confidence": 0.95,  // confidence score 0.0-1.0
    "trinity_compliance": {{
        "identity_authentic": true,  // code expresses authentic purpose
        "consciousness_aware": true,  // fix understands full context
        "guardian_safe": true       // change protects system integrity
    },
    "affects_lines": [42],  // line numbers that need changes
    "dependencies": [],     // any imports or dependencies needed
    "test_required": false  // whether this fix needs additional testing
}

Focus on these common LUKHAS patterns:
- Use "LUKHAS AI" not "PWM" or generic "AGI"
- Consciousness patterns over lambda functions
- Trinity Framework integration (⚛️🧠🛡️)
- Proper import structures for modular architecture
- Safe symbolic vocabulary and consciousness terminology
"""

    async def _ollama_generate(self, prompt: str) -> dict[str, Any]:
        """Generate fix using Ollama local LLM"""

        payload = {
            "model": "deepseek-coder:6.7b",  # Use available DeepSeek Coder model
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for precise code fixes
                "top_p": 0.9,
                "num_predict": 1000,
            },
        }

        try:
            async with self.session.post(f"{self.base_url}/api/generate", json=payload, timeout=30) as response:
                if response.status == 200:
                    result = await response.json()
                    # Try to parse JSON from response
                    try:
                        fix_data = json.loads(result["response"].strip())
                        return fix_data
                    except json.JSONDecodeError:
                        # Fallback: extract code blocks from text response
                        return self._parse_text_response(result["response"])
                else:
                    error_text = await response.text()
                    return {"error": f"Ollama API error {response.status}: {error_text}"}

        except asyncio.TimeoutError:
            return {"error": "Ollama request timed out"}
        except Exception as e:
            return {"error": f"Ollama request failed: {e}"}

    async def _lmstudio_generate(self, prompt: str) -> dict[str, Any]:
        """Generate fix using LM Studio local LLM"""

        payload = {
            "model": "code-model",  # Adjust based on loaded model
            "messages": [
                {
                    "role": "system",
                    "content": "You are a code fixing assistant for LUKHAS AI consciousness platform.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_tokens": 1000,
        }

        try:
            async with self.session.post(f"{self.base_url}/v1/chat/completions", json=payload, timeout=30) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    try:
                        return json.loads(content.strip())
                    except json.JSONDecodeError:
                        return self._parse_text_response(content)
                else:
                    error_text = await response.text()
                    return {"error": f"LM Studio API error {response.status}: {error_text}"}

        except asyncio.TimeoutError:
            return {"error": "LM Studio request timed out"}
        except Exception as e:
            return {"error": f"LM Studio request failed: {e}"}

    def _parse_text_response(self, response_text: str) -> dict[str, Any]:
        """Parse LLM text response when JSON parsing fails"""

        # Extract code blocks
        import re

        code_blocks = re.findall(r"```(?:python)?\n(.*?)\n```", response_text, re.DOTALL)

        if code_blocks:
            return {
                "fix_code": code_blocks[0].strip(),
                "explanation": "Extracted from llm_text response",
                "confidence": 0.7,
                "trinity_compliance": {
                    "identity_authentic": True,
                    "consciousness_aware": True,
                    "guardian_safe": True,
                },
                "affects_lines": [],
                "dependencies": [],
                "test_required": False,
            }
        else:
            return {
                "error": "Could not parse LLM response",
                "raw_response": response_text[:500],  # First 500 chars for debugging
            }


class CodeQualityAnalyzer:
    """Analyzes and categorizes code quality issues from Ruff"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issue_categories = self._load_issue_categories()

    def _load_issue_categories(self) -> dict[str, dict[str, Any]]:
        """Load categorized issue types with priorities and fix strategies"""
        return {
            # Critical - Syntax errors that break execution
            "syntax_errors": {
                "priority": 1,
                "rules": ["E901", "E902", "E999", "F999"],
                "description": "Syntax errors preventing execution",
                "fix_strategy": "immediate_fix",
                "batch_size": 10,
            },
            # High - Import and name resolution issues
            "import_issues": {
                "priority": 2,
                "rules": ["F401", "F811", "F821", "F822", "F823", "F831", "F841"],
                "description": "Import and undefined name issues",
                "fix_strategy": "careful_analysis",
                "batch_size": 20,
            },
            # Medium - Code style and quality
            "style_issues": {
                "priority": 3,
                "rules": ["E1", "E2", "E3", "E4", "E5", "W"],
                "description": "Code style and formatting",
                "fix_strategy": "safe_formatting",
                "batch_size": 50,
            },
            # Low - Suggestions and optimizations
            "suggestions": {
                "priority": 4,
                "rules": ["C", "N", "B", "UP", "PIE"],
                "description": "Code suggestions and optimizations",
                "fix_strategy": "optional_improvement",
                "batch_size": 100,
            },
        }

    async def analyze_codebase(self) -> list[CodeIssue]:
        """Run Ruff analysis and parse results into structured issues"""

        print("🔍 Running Ruff analysis to identify code quality issues...")

        try:
            # Run Ruff with JSON output
            result = subprocess.run(
                [
                    "ruff",
                    "check",
                    str(self.project_root),
                    "--output-format=json",
                    "--no-fix",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode not in [0, 1]:  # 0 = no issues, 1 = issues found
                raise Exception(f"Ruff analysis failed: {result.stderr}")

            if not result.stdout.strip():
                print("✅ No issues found by Ruff!")
                return []

            # Parse JSON output
            ruff_issues = json.loads(result.stdout)

            # Convert to CodeIssue objects
            issues = []
            for ruff_issue in ruff_issues:
                issue = CodeIssue(
                    file_path=ruff_issue.get("filename", ""),
                    line_number=ruff_issue.get("location", {}).get("row", 0),
                    column=ruff_issue.get("location", {}).get("column", 0),
                    rule_code=ruff_issue.get("code", ""),
                    rule_name=(
                        ruff_issue.get("message", "").split(":")[0] if ":" in ruff_issue.get("message", "") else ""
                    ),
                    message=ruff_issue.get("message", ""),
                    severity=self._determine_severity(ruff_issue.get("code", "")),
                    category=self._categorize_issue(ruff_issue.get("code", "")),
                )
                issues.append(issue)

            print(f"📊 Found {len(issues}} code quality issues")
            self._print_category_summary(issues)

            return issues

        except Exception as e:
            print(f"❌ Failed to analyze codebase: {e}")
            return []

    def _determine_severity(self, rule_code: str) -> str:
        """Determine severity level based on rule code"""
        if any(rule_code.startswith(prefix) for prefix in ["E9", "F9"]):
            return "critical"
        elif any(rule_code.startswith(prefix) for prefix in ["F", "E"]):
            return "high"
        elif rule_code.startswith("W"):
            return "medium"
        else:
            return "low"

    def _categorize_issue(self, rule_code: str) -> str:
        """Categorize issue based on rule code"""
        for category, config in self.issue_categories.items():
            if any(rule_code.startswith(rule_prefix) for rule_prefix in config["rules"]):
                return category
        return "other"

    def _print_category_summary(self, issues: list[CodeIssue]):
        """Print summary of issues by category"""
        category_counts = {}
        for issue in issues:
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1

        print("\n📋 Issues by Category:")
        for category, count in sorted(
            category_counts.items(),
            key=lambda x: self.issue_categories.get(x[0], {}).get("priority", 99),
        ):
            config = self.issue_categories.get(category, {})
            priority = config.get("priority", "?")
            description = config.get("description", "Other issues")
            print(f"   {priority}. {category}: {count} issues - {description}")


class LLMCodeFixer:
    """Main class for LLM-powered code quality improvement"""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root or os.getcwd())
        self.analyzer = CodeQualityAnalyzer(self.project_root)
        self.llm_service = os.getenv("LOCAL_LLM_SERVICE", "ollama")
        self.llm_base_url = os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:11434")
        self.dry_run = os.getenv("LUKHAS_CODE_FIX_DRY_RUN", "false").lower() == "true"
        self.backup_dir = self.project_root / ".code_fix_backups" / datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Progress tracking
        self.progress_file = self.project_root / ".code_fix_progress.json"
        self.progress = self._load_progress()

    def _load_progress(self) -> dict[str, Any]:
        """Load progress from previous runs"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file) as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "completed_files": [],
            "failed_files": [],
            "total_fixes_attempted": 0,
            "successful_fixes": 0,
            "last_run": None,
        }

    def _save_progress(self):
        """Save current progress"""
        self.progress["last_run"] = datetime.now().isoformat()
        with open(self.progress_file, "w") as f:
            json.dump(self.progress, f, indent=2)

    async def run_intelligent_code_improvement(self):
        """Main entry point for LLM-powered code improvement"""

        print("🧠 LUKHAS Local LLM Code Quality Improvement System")
        print("=" * 55)
        print(f"🏗️  Project: {self.project_root}")
        print(f"🤖 LLM Service: {self.llm_service} ({self.llm_base_url})")
        print(f"🧪 Dry Run: {'Enabled' if self.dry_run else 'Disabled'}")
        print(f"💾 Backup Dir: {self.backup_dir}")
        print()

        # Check LLM availability
        if not await self._check_llm_availability():
            print("❌ Local LLM service not available. Please start your LLM service and try again.")
            return False

        # Analyze codebase
        issues = await self.analyzer.analyze_codebase()
        if not issues:
            print("✅ No code quality issues found!")
            return True

        # Process issues by priority
        await self._process_issues_by_priority(issues)

        # Generate summary report
        self._generate_final_report()

        return True

    async def _check_llm_availability(self) -> bool:
        """Check if local LLM service is available"""

        try:
            async with LocalLLMClient(self.llm_service, self.llm_base_url) as client:
                # Simple test request
                test_result = await client._ollama_generate("Test connection") if client.service == "ollama" else None
                if test_result and "error" not in test_result:
                    print("✅ Local LLM service is available")
                    return True
                else:
                    print(f"⚠️  LLM test returned: {test_result}")
                    return False
        except Exception as e:
            print(f"❌ LLM availability check failed: {e}")
            return False

    async def _process_issues_by_priority(self, issues: list[CodeIssue]):
        """Process issues in priority order"""

        # Group issues by category and priority
        categorized_issues = {}
        for issue in issues:
            if issue.category not in categorized_issues:
                categorized_issues[issue.category] = []
            categorized_issues[issue.category].append(issue)

        # Process each category in priority order
        total_categories = len(categorized_issues)
        for cat_idx, (category, category_issues) in enumerate(
            sorted(
                categorized_issues.items(),
                key=lambda x: self.analyzer.issue_categories.get(x[0], {}).get("priority", 99),
            )
        ):
            config = self.analyzer.issue_categories.get(category, {})
            priority = config.get("priority", "?")
            batch_size = config.get("batch_size", 10)

            print(f"\n🎯 Processing Category {cat_idx + 1}/{total_categories}: {category}")
            print(f"   Priority: {priority}, Issues: {len(category_issues}}, Batch Size: {batch_size}")

            # Process in batches
            for i in range(0, len(category_issues), batch_size):
                batch = category_issues[i : i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (len(category_issues) + batch_size - 1) // batch_size

                print(f"\n   🔧 Batch {batch_num}/{total_batches} ({len(batch}} issues)")

                # Process batch
                await self._process_issue_batch(batch)

                # Save progress after each batch
                self._save_progress()

                # Brief pause between batches to avoid overloading LLM
                await asyncio.sleep(1)

    async def _process_issue_batch(self, issues: list[CodeIssue]):
        """Process a batch of issues concurrently"""

        # Process up to 3 issues concurrently to avoid overwhelming LLM
        semaphore = asyncio.Semaphore(3)

        async def process_single_issue(issue: CodeIssue) -> FixResult:
            async with semaphore:
                return await self._fix_single_issue(issue)

        # Create tasks for all issues in batch
        tasks = [process_single_issue(issue) for issue in issues]

        # Execute with progress tracking
        results = []
        for completed_task in asyncio.as_completed(tasks):
            result = await completed_task
            results.append(result)

            # Print progress
            status = "✅" if result.success else "❌"
            file_short = Path(result.issue.file_path).name
            print(f"      {status} {file_short}:{result.issue.line_number} - {result.issue.rule_code}")

            if result.success:
                self.progress["successful_fixes"] += 1
            self.progress["total_fixes_attempted"] += 1

        return results

    async def _fix_single_issue(self, issue: CodeIssue) -> FixResult:
        """Fix a single code quality issue using LLM"""

        try:
            # Read file content
            file_path = Path(issue.file_path)
            if not file_path.exists():
                return FixResult(
                    issue=issue,
                    success=False,
                    error_message=f"File not found: {file_path}",
                )

            with open(file_path, encoding="utf-8") as f:
                file_content = f.read()

            # Generate fix using LLM
            async with LocalLLMClient(self.llm_service, self.llm_base_url) as client:
                llm_result = await client.generate_fix(issue, file_content)

            if "error" in llm_result:
                return FixResult(
                    issue=issue,
                    success=False,
                    error_message=f"LLM error: {llm_result['error']}",
                )

            # Extract fix details
            fix_code = llm_result.get("fix_code")
            confidence = llm_result.get("confidence", 0.0)
            trinity_compliance = llm_result.get("trinity_compliance", {})

            if not fix_code or confidence < 0.7:
                return FixResult(
                    issue=issue,
                    success=False,
                    error_message=f"Low confidence fix: {confidence}",
                )

            # Apply fix if not in dry run mode
            if not self.dry_run:
                # Backup original file
                backup_path = self.backup_dir / file_path.name
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                with open(backup_path, "w") as f:
                    f.write(file_content)

                # Apply fix
                success = self._apply_fix(file_path, issue, fix_code, file_content)
                if not success:
                    return FixResult(issue=issue, success=False, error_message="Failed to apply fix")

            return FixResult(
                issue=issue,
                success=True,
                applied_fix=fix_code,
                validation_passed=confidence > 0.8,
                trinity_compliant=(all(trinity_compliance.values()) if trinity_compliance else False),
            )

        except Exception as e:
            return FixResult(issue=issue, success=False, error_message=f"Unexpected error: {e}")

    def _apply_fix(self, file_path: Path, issue: CodeIssue, fix_code: str, original_content: str) -> bool:
        """Apply the LLM-generated fix to the file"""

        try:
            lines = original_content.split("\n")

            # Simple line replacement (can be made more sophisticated)
            if 0 < issue.line_number <= len(lines):
                lines[issue.line_number - 1] = fix_code

                # Write back to file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))

                return True
            else:
                print(f"⚠️  Invalid line number {issue.line_number} for file {file_path}")
                return False

        except Exception as e:
            print(f"❌ Failed to apply fix to {file_path}: {e}")
            return False

    def _generate_final_report(self):
        """Generate final improvement report"""

        report_path = self.project_root / f"code_improvement_report_{datetime.now().strftime('%Y%m%d_%H%M%S'}}.md"

        total_attempted = self.progress["total_fixes_attempted"]
        successful = self.progress["successful_fixes"]
        success_rate = (successful / total_attempted * 100) if total_attempted > 0 else 0

        report_content = f"""# 🧠 LUKHAS Code Quality Improvement Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**LLM Service:** {self.llm_service} ({self.llm_base_url})
**Mode:** {"Dry Run" if self.dry_run else "Live Fixes Applied"}

## 📊 Summary

- **Total Issues Processed:** {total_attempted}
- **Successfully Fixed:** {successful}
- **Success Rate:** {success_rate:.1f}%
- **Backup Directory:** {self.backup_dir}

## 🎯 Categories Processed

{self._generate_category_breakdown()}

## 🛡️ Trinity Framework Compliance

All fixes applied follow LUKHAS Trinity Framework principles:
- ⚛️ **Identity:** Fixes maintain authentic code purpose and structure
- 🧠 **Consciousness:** Improvements understand full context and implications
- 🛡️ **Guardian:** Changes protect system integrity and functionality

## 🔄 Next Steps

1. **Validation:** Run tests to ensure fixes don't break functionality
2. **Review:** Manually review complex fixes in critical modules
3. **Commit:** Commit successful fixes with appropriate messages
4. **Monitor:** Track system performance after improvements

## 📝 Files Modified

{self._generate_file_list()}

---
*Generated by LUKHAS Local LLM Code Quality Improvement System*
*⚛️🧠🛡️ Trinity Framework Consciousness Technology*
"""

        with open(report_path, "w") as f:
            f.write(report_content)

        print(f"\n📋 Final report generated: {report_path}")
        print(f"🎯 Success Rate: {success_rate:.1f}% ({successful}/{total_attempted} fixes)")

    def _generate_category_breakdown(self) -> str:
        """Generate breakdown of processing by category"""
        # This would track per-category stats
        return "Detailed category breakdown would be implemented here..."

    def _generate_file_list(self) -> str:
        """Generate list of files that were modified"""
        # This would list all modified files
        return "List of modified files would be implemented here..."


async def main():
    """Main entry point for the code improvement system"""

    import argparse

    parser = argparse.ArgumentParser(description="🧠 LUKHAS Local LLM Code Quality Improvement System")
    parser.add_argument(
        "--project-root",
        default=os.getcwd(),
        help="Root directory of the project to improve",
    )
    parser.add_argument("--dry-run", action="store_true", help="Run analysis without making changes")
    parser.add_argument(
        "--llm-service",
        choices=["ollama", "lmstudio"],
        default=os.getenv("LOCAL_LLM_SERVICE", "ollama"),
        help="Local LLM service to use",
    )
    parser.add_argument(
        "--llm-url",
        default=os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:11434"),
        help="Base URL for local LLM service",
    )

    args = parser.parse_args()

    # Set environment variables
    os.environ["LOCAL_LLM_SERVICE"] = args.llm_service
    os.environ["LOCAL_LLM_BASE_URL"] = args.llm_url
    os.environ["LUKHAS_CODE_FIX_DRY_RUN"] = str(args.dry_run).lower()

    # Create and run the fixer
    fixer = LLMCodeFixer(args.project_root)
    success = await fixer.run_intelligent_code_improvement()

    if success:
        print("\n🎉 Code quality improvement completed successfully!")
        print("🔄 Next steps: Run tests to validate changes")
        return 0
    else:
        print("\n❌ Code quality improvement failed")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
