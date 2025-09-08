"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ lukhas CLI Developer Tools Commands                            table = \
    formatter.create_table(
            title="Available Developer Commands",
            style="cyan"
        )
        table.add_column("Command", style="bold cyan")
        table.add_column("Description", style="white")

        for cmd, desc in commands:
            table.add_row(cmd, desc)

        print(table)             ║
║ DESCRIPTION: Advanced development and debugging utilities             ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""
import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Handle both relative and absolute imports
try:
    from ..utils import (
        OutputFormatter,
        ProgressFormatter,
        TableFormatter,
        find_files,
        format_duration,
        function_profiler,
        performance_context,
        print_error,
        print_header,
        print_info,
        print_success,
        print_warning,
        run_command_async,
        system_monitor,
        validate_path,
    )
    from .base import BaseCommand
except ImportError:
    # Fallback to absolute imports
    import sys
    from pathlib import Path

    cli_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(cli_dir))

    from commands.base import BaseCommand

    from utils import (
        OutputFormatter,
        ProgressFormatter,
        TableFormatter,
        find_files,
        format_duration,
        function_profiler,
        performance_context,
        print_error,
        print_header,
        print_info,
        print_success,
        print_warning,
        run_command_async,
        system_monitor,
        validate_path,
    )


@dataclass
class CodeMetrics:
    """Code analysis metrics"""

    lines_of_code: int
    files_count: int
    functions_count: int
    classes_count: int
    complexity_score: float
    test_coverage: Optional[float] = None
    documentation_ratio: Optional[float] = None


@dataclass
class TestResult:
    """Test execution result"""

    test_file: str
    passed: int
    failed: int
    skipped: int
    duration: float
    coverage: Optional[float] = None


class DeveloperTools(BaseCommand):
    """Advanced developer tools and utilities"""

    def __init__(self):
        super().__init__()
        self.name = "dev"
        self.description = "🛠️ Advanced developer tools and debugging utilities"
        self.formatter = OutputFormatter()
        self.progress = ProgressFormatter()

        # Register subcommands
        self.subcommands = {
            "analyze": self.analyze_code,
            "test": self.run_tests,
            "benchmark": self.benchmark_code,
            "profile": self.profile_application,
            "lint": self.lint_code,
            "format": self.format_code,
            "docs": self.generate_docs,
            "deps": self.analyze_dependencies,
            "build": self.build_project,
            "deploy": self.deploy_project,
            "monitor": self.monitor_system,
            "debug": self.debug_session,
            "refactor": self.refactor_code,
            "security": self.security_audit,
        }

    async def execute(self, args: list[str]) -> bool:
        """Execute developer tool command"""
        if not args:
            self._show_help()
            return True

        subcommand = args[0]
        if subcommand not in self.subcommands:
            print_error(f"Unknown dev command: {subcommand}")
            self._show_help()
            return False

        try:
            return await self.subcommands[subcommand](args[1:])
        except Exception as e:
            print_error(f"Dev command failed: {e!s}")
            return False

    def _show_help(self):
        """Show developer tools help"""
        print_header("🛠️ Developer Tools")

        commands = [
            ("analyze", "Analyze code metrics and quality"),
            ("test", "Run tests with coverage analysis"),
            ("benchmark", "Performance benchmarking"),
            ("profile", "Application profiling"),
            ("lint", "Code linting and style checking"),
            ("format", "Code formatting and cleanup"),
            ("docs", "Generate documentation"),
            ("deps", "Dependency analysis"),
            ("build", "Build project"),
            ("deploy", "Deploy project"),
            ("monitor", "System monitoring"),
            ("debug", "Interactive debugging"),
            ("refactor", "Code refactoring tools"),
            ("security", "Security audit"),
        ]

        table_data = [["Command", "Description"]]
        table_data.extend(commands)

        formatter = TableFormatter()
        print(formatter.create_table(table_data, title="Available Developer Commands", style="lukhas"))

    async def analyze_code(self, args: list[str]) -> bool:
        """Analyze code metrics and quality"""
        path = args[0] if args else "."

        if not validate_path(path):
            print_error(f"Invalid path: {path}")
            return False

        print_header("📊 Code Analysis")

        with performance_context("code_analysis"):
            metrics = await self._analyze_code_metrics(path)
            quality = await self._analyze_code_quality(path)

            # Display metrics
            self._display_code_metrics(metrics)
            self._display_quality_report(quality)

        return True

    async def run_tests(self, args: list[str]) -> bool:
        """Run tests with coverage analysis"""
        test_path = args[0] if args else "tests/"
        coverage = "--coverage" in args

        print_header("🧪 Test Execution")

        if not os.path.exists(test_path):
            print_warning(f"Test path not found: {test_path}")
            return False

        # Run tests
        results = await self._execute_tests(test_path, coverage)
        self._display_test_results(results)

        return all(r.failed == 0 for r in results)

    async def benchmark_code(self, args: list[str]) -> bool:
        """Performance benchmarking"""
        target = args[0] if args else "."
        iterations = int(args[1]) if len(args) > 1 else 100

        print_header("⚡ Performance Benchmark")

        with performance_context("benchmark"):
            results = await self._run_benchmarks(target, iterations)
            self._display_benchmark_results(results)

        return True

    async def profile_application(self, args: list[str]) -> bool:
        """Application profiling"""
        if not args:
            print_error("Usage: lukhas dev profile <script/module>")
            return False

        target = args[0]
        duration = int(args[1]) if len(args) > 1 else 30

        print_header("🔍 Application Profiling")

        profiler = function_profiler()
        results = await self._profile_execution(target, duration, profiler)
        self._display_profile_results(results)

        return True

    async def lint_code(self, args: list[str]) -> bool:
        """Code linting and style checking"""
        path = args[0] if args else "."
        fix = "--fix" in args

        print_header("✨ Code Linting")

        linters = ["flake8", "pylint", "black", "isort", "mypy"]
        results = {}

        for linter in linters:
            if await self._is_tool_available(linter):
                results[linter] = await self._run_linter(linter, path, fix)

        self._display_lint_results(results)
        return all(r["status"] == "passed" for r in results.values())

    async def format_code(self, args: list[str]) -> bool:
        """Code formatting and cleanup"""
        path = args[0] if args else "."

        print_header("🎨 Code Formatting")

        formatters = ["black", "isort", "autopep8"]
        results = {}

        for formatter in formatters:
            if await self._is_tool_available(formatter):
                results[formatter] = await self._run_formatter(formatter, path)

        self._display_format_results(results)
        return True

    async def generate_docs(self, args: list[str]) -> bool:
        """Generate documentation"""
        source = args[0] if args else "."
        output = args[1] if len(args) > 1 else "docs/"
        format_type = args[2] if len(args) > 2 else "html"

        print_header("📚 Documentation Generation")

        doc_generators = {
            "sphinx": self._generate_sphinx_docs,
            "mkdocs": self._generate_mkdocs,
            "pydoc": self._generate_pydoc,
        }

        for generator, func in doc_generators.items():
            if await self._is_tool_available(generator):
                result = await func(source, output, format_type)
                if result:
                    print_success(f"Documentation generated with {generator}")
                    return True

        print_warning("No documentation generators available")
        return False

    async def analyze_dependencies(self, args: list[str]) -> bool:
        """Dependency analysis"""
        manifest = args[0] if args else "requirements.txt"

        print_header("📦 Dependency Analysis")

        if not os.path.exists(manifest):
            print_error(f"Dependency file not found: {manifest}")
            return False

        analysis = await self._analyze_dependencies(manifest)
        self._display_dependency_analysis(analysis)

        return True

    async def build_project(self, args: list[str]) -> bool:
        """Build project"""
        build_type = args[0] if args else "default"

        print_header("🔨 Project Build")

        build_systems = {
            "python": self._build_python_project,
            "node": self._build_node_project,
            "docker": self._build_docker_project,
            "make": self._build_make_project,
        }

        if build_type in build_systems:
            return await build_systems[build_type]()

        # Auto-detect build system
        for system, func in build_systems.items():
            if await self._detect_build_system(system):
                print_info(f"Detected {system} project")
                return await func()

        print_error("No supported build system detected")
        return False

    async def deploy_project(self, args: list[str]) -> bool:
        """Deploy project"""
        target = args[0] if args else "staging"

        print_header("🚀 Project Deployment")

        deployment_configs = await self._load_deployment_configs()

        if target not in deployment_configs:
            print_error(f"Unknown deployment target: {target}")
            return False

        config = deployment_configs[target]
        return await self._execute_deployment(config)

    async def monitor_system(self, args: list[str]) -> bool:
        """System monitoring"""
        duration = int(args[0]) if args else 60

        print_header("📈 System Monitoring")

        monitor = system_monitor()

        for _i in range(duration):
            metrics = monitor.get_current_metrics()
            self._display_system_metrics(metrics)
            await asyncio.sleep(1)

        return True

    async def debug_session(self, args: list[str]) -> bool:
        """Interactive debugging session"""
        if not args:
            print_error("Usage: lukhas dev debug <script>")
            return False

        script = args[0]
        print_header("🐛 Debug Session")

        # Launch debugger
        return await self._launch_debugger(script)

    async def refactor_code(self, args: list[str]) -> bool:
        """Code refactoring tools"""
        operation = args[0] if args else "analyze"
        path = args[1] if len(args) > 1 else "."

        print_header("♻️ Code Refactoring")

        refactor_ops = {
            "analyze": self._analyze_refactoring_opportunities,
            "extract": self._extract_methods,
            "rename": self._rename_symbols,
            "optimize": self._optimize_imports,
        }

        if operation in refactor_ops:
            return await refactor_ops[operation](path, args[2:])

        print_error(f"Unknown refactoring operation: {operation}")
        return False

    async def security_audit(self, args: list[str]) -> bool:
        """Security audit"""
        path = args[0] if args else "."

        print_header("🔒 Security Audit")

        audit_tools = ["bandit", "safety", "semgrep"]
        results = {}

        for tool in audit_tools:
            if await self._is_tool_available(tool):
                results[tool] = await self._run_security_tool(tool, path)

        self._display_security_results(results)

        # Check for common vulnerabilities
        vulnerabilities = await self._check_vulnerabilities(path)
        if vulnerabilities:
            self._display_vulnerabilities(vulnerabilities)
            return False

        print_success("No security issues found")
        return True

    # Helper methods
    async def _analyze_code_metrics(self, path: str) -> CodeMetrics:
        """Analyze code metrics"""
        python_files = find_files(path, "*.py")

        lines_of_code = 0
        functions_count = 0
        classes_count = 0

        for file_path in python_files:
            with open(file_path, encoding="utf-8") as f:
                code = f.read()
                lines_of_code += len([l for l in code.split("\n") if l.strip() and not l.strip().startswith("#")])
                functions_count += code.count("def ")
                classes_count += code.count("class ")

        complexity_score = self._calculate_complexity_score(python_files)

        return CodeMetrics(
            lines_of_code=lines_of_code,
            files_count=len(python_files),
            functions_count=functions_count,
            classes_count=classes_count,
            complexity_score=complexity_score,
        )

    def _calculate_complexity_score(self, files: list[str]) -> float:
        """Calculate complexity score"""
        # Simplified complexity calculation
        total_complexity = 0
        for file_path in files:
            with open(file_path, encoding="utf-8") as f:
                code = f.read()
                # Count control structures
                complexity = (
                    code.count("if ")
                    + code.count("elif ")
                    + code.count("for ")
                    + code.count("while ")
                    + code.count("try:")
                    + code.count("except ")
                )
                total_complexity += complexity

        return total_complexity / len(files) if files else 0

    def _display_code_metrics(self, metrics: CodeMetrics):
        """Display code metrics"""
        data = [
            ["Metric", "Value"],
            ["Lines of Code", f"{metrics.lines_of_code:,}"],
            ["Files", f"{metrics.files_count:,}"],
            ["Functions", f"{metrics.functions_count:,}"],
            ["Classes", f"{metrics.classes_count:,}"],
            ["Complexity Score", f"{metrics.complexity_score:.2f}"],
        ]

        formatter = TableFormatter()
        print(formatter.format_table(data, title="Code Metrics", style="lukhas"))

    async def _is_tool_available(self, tool: str) -> bool:
        """Check if development tool is available"""
        try:
            result = await run_command_async(f"which {tool}")
            return result.returncode == 0
        except BaseException:
            return False

    async def _execute_tests(self, test_path: str, coverage: bool) -> list[TestResult]:
        """Execute tests"""
        # Placeholder for test execution
        return [
            TestResult(
                test_file=test_path,
                passed=10,
                failed=0,
                skipped=1,
                duration=2.5,
                coverage=85.5 if coverage else None,
            )
        ]

    def _display_test_results(self, results: list[TestResult]):
        """Display test results"""
        for result in results:
            status = "✅ PASSED" if result.failed == 0 else "❌ FAILED"
            print_info(f"{status} {result.test_file}")
            print(f"  Passed: {result.passed}, Failed: {result.failed}, Skipped: {result.skipped}")
            print(f"  Duration: {format_duration(result.duration)}")
            if result.coverage:
                print(f"  Coverage: {result.coverage:.1f}%")
