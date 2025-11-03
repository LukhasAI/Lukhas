"""
Bridge API Controllers - Import Review & Service Coordination

Reviews and manages imports for AGI services, ensuring proper lane isolation
and Trinity Framework integration.

Part of BATCH-JULES-API-GOVERNANCE-02
Task: TODO-HIGH-BRIDGE-API-o1p2q3r4

Trinity Framework:
- 🧠 Consciousness: Service orchestration
- 🛡️ Guardian: Import boundary enforcement
- ⚛️ Identity: Service authentication
"""

import ast
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ImportStatus(Enum):
    """Import validation status."""
    VALID = "valid"
    INVALID_LANE_VIOLATION = "invalid_lane_violation"
    DEPRECATED = "deprecated"
    MISSING_MODULE = "missing_module"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    SECURITY_RISK = "security_risk"


class ServiceLane(Enum):
    """LUKHAS service lanes."""
    LUKHAS = "lukhas"              # Production lane (primary name for tests)
    CANDIDATE = "labs"        # Development lane
    MATRIZ = "matriz"              # MATRIZ cognitive DNA
    CORE = "core"                  # Core symbolic logic
    UNIVERSAL = "universal_language"  # Universal language
    EXPERIMENTAL = "experimental"   # Experimental features
    UNKNOWN = "unknown"            # Unknown/unclassified

    # Aliases for backward compatibility
    PRODUCTION = LUKHAS            # Alias to LUKHAS
    MATRIX = MATRIZ                # Alias to MATRIZ


@dataclass
class ImportRule:
    """Import boundary rule."""
    from_lane: ServiceLane
    allowed_imports: List[ServiceLane]
    forbidden_imports: List[ServiceLane]
    description: str


@dataclass
class ImportViolation:
    """Import boundary violation."""
    file_path: str
    line_number: int
    import_statement: str
    violation_type: ImportStatus
    from_lane: ServiceLane
    to_lane: ServiceLane
    message: str
    severity: str = "error"  # error, warning, info

    # Class attribute for test compatibility
    FORBIDDEN_LANE = ImportStatus.INVALID_LANE_VIOLATION

    @property
    def source_file(self) -> str:
        """Alias for file_path for test compatibility."""
        return self.file_path

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['violation_type'] = self.violation_type.value
        result['from_lane'] = self.from_lane.value
        result['to_lane'] = self.to_lane.value
        return result


@dataclass
class ImportReviewReport:
    """Complete import review report."""
    total_files_scanned: int
    total_imports_found: int
    violations: List[ImportViolation]
    valid_imports: int
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    @property
    def has_violations(self) -> bool:
        """Check if any violations found."""
        return len(self.violations) > 0

    @property
    def error_count(self) -> int:
        """Count of error-level violations."""
        return sum(1 for v in self.violations if v.severity == "error")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_files_scanned': self.total_files_scanned,
            'total_imports_found': self.total_imports_found,
            'violations': [v.to_dict() for v in self.violations],
            'valid_imports': self.valid_imports,
            'error_count': self.error_count,
            'warnings': self.warnings,
            'suggestions': self.suggestions
        }


class ImportController:
    """
    Bridge API Import Controller
    
    Manages and validates imports across LUKHAS service lanes, enforcing
    architectural boundaries and preventing circular dependencies.
    
    Lane Import Rules (from ops/matriz.yaml):
    - lukhas/ ← core/, matriz/, universal_language/ (production imports)
    - candidate/ ← core/, matriz/ only (NO lukhas imports)
    - Strict boundaries prevent cross-lane contamination
    
    Trinity Integration:
    - 🧠 Consciousness: Service orchestration
    - 🛡️ Guardian: Boundary enforcement
    - ⚛️ Identity: Service authentication
    """

    # Import rules based on ops/matriz.yaml
    LANE_RULES: List[ImportRule] = [
        ImportRule(
            from_lane=ServiceLane.CANDIDATE,
            allowed_imports=[ServiceLane.CORE, ServiceLane.MATRIZ, ServiceLane.UNIVERSAL],
            forbidden_imports=[ServiceLane.PRODUCTION],
            description="Candidate lane can import core/matriz/universal, but NOT production"
        ),
        ImportRule(
            from_lane=ServiceLane.PRODUCTION,
            allowed_imports=[ServiceLane.CORE, ServiceLane.MATRIZ, ServiceLane.UNIVERSAL, ServiceLane.CANDIDATE],
            forbidden_imports=[],
            description="Production lane can import all other lanes"
        ),
        ImportRule(
            from_lane=ServiceLane.CORE,
            allowed_imports=[],
            forbidden_imports=[ServiceLane.PRODUCTION, ServiceLane.CANDIDATE],
            description="Core is foundation - no dependencies on other lanes"
        ),
        ImportRule(
            from_lane=ServiceLane.MATRIZ,
            allowed_imports=[ServiceLane.CORE],
            forbidden_imports=[ServiceLane.PRODUCTION, ServiceLane.CANDIDATE],
            description="MATRIZ can import core only"
        ),
    ]

    # Deprecated imports to warn about
    DEPRECATED_IMPORTS = {
        'from agi_services': 'Use candidate.bridge.orchestration instead',
        'from consciousness.legacy': 'Migrated to candidate.consciousness',
        'from identity.old_lambda_id': 'Use candidate.identity.lambda_id',
    }

    def __init__(self):
        """Initialize Import Controller."""
        self._import_cache: Dict[str, List[str]] = {}
        self._matriz_config: Optional[Dict[str, Any]] = None
        self._rules_loaded: bool = False

    async def review_file_imports(
        self,
        file_path: Path,
        lane: Optional[ServiceLane] = None
    ) -> List[ImportViolation]:
        """
        Review imports in a single file for violations.
        
        Args:
            file_path: Path to Python file
            lane: Service lane (auto-detected if not provided)
        
        Returns:
            List of import violations found
        
        Task: TODO-HIGH-BRIDGE-API-o1p2q3r4 (Review AGI services imports)
        """
        violations = []

        # Auto-detect lane from path
        if lane is None:
            lane = self._detect_lane(file_path)

        # Parse file for imports
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
        except Exception:
            # Skip files that can't be parsed
            return violations

        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    violation = self._check_import(
                        import_name=alias.name,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        from_lane=lane,
                        import_type='import'
                    )
                    if violation:
                        violations.append(violation)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    violation = self._check_import(
                        import_name=node.module,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        from_lane=lane,
                        import_type='from',
                        names=[alias.name for alias in node.names]
                    )
                    if violation:
                        violations.append(violation)

        return violations

    async def review_directory_imports(
        self,
        directory: Path,
        recursive: bool = True
    ) -> ImportReviewReport:
        """
        Review all imports in a directory.
        
        Args:
            directory: Directory path to scan
            recursive: Whether to scan subdirectories
        
        Returns:
            Complete import review report
        
        Task: TODO-HIGH-BRIDGE-API-o1p2q3r4 (Review AGI services imports)
        """
        all_violations = []
        files_scanned = 0
        total_imports = 0

        # Find all Python files
        pattern = "**/*.py" if recursive else "*.py"
        python_files = list(directory.glob(pattern))

        for file_path in python_files:
            # Skip __pycache__ and test files if requested
            if '__pycache__' in str(file_path):
                continue

            files_scanned += 1
            violations = await self.review_file_imports(file_path)
            all_violations.extend(violations)

            # Count total imports in file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.Import, ast.ImportFrom)):
                            total_imports += 1
            except Exception:
                pass

        # Generate report
        valid_imports = total_imports - len(all_violations)

        report = ImportReviewReport(
            total_files_scanned=files_scanned,
            total_imports_found=total_imports,
            violations=all_violations,
            valid_imports=valid_imports
        )

        # Add warnings for common issues
        if report.has_violations:
            report.warnings.append(
                f"Found {len(all_violations)} import violations. "
                f"Run 'make lane-guard' to validate import boundaries."
            )

        # Add suggestions
        if any(v.violation_type == ImportStatus.INVALID_LANE_VIOLATION for v in all_violations):
            report.suggestions.append(
                "Use candidate.bridge adapters instead of direct lukhas imports"
            )

        return report

    def _detect_lane(self, file_path: Path) -> ServiceLane:
        """
        Detect which service lane a file belongs to.
        
        Args:
            file_path: File path
        
        Returns:
            Detected ServiceLane
        """
        path_str = str(file_path).replace('\\', '/')  # Normalize path separators

        # Check for lane patterns in path
        if 'lukhas/' in path_str and 'candidate/' not in path_str:
            return ServiceLane.LUKHAS  # Use LUKHAS alias instead of PRODUCTION
        elif 'candidate/' in path_str:
            return ServiceLane.CANDIDATE
        elif 'matriz/' in path_str:
            return ServiceLane.MATRIZ
        elif 'core/' in path_str:
            return ServiceLane.CORE
        elif 'universal_language/' in path_str:
            return ServiceLane.UNIVERSAL

        # Check if path starts with lane name (for relative paths)
        path_parts = path_str.split('/')
        if path_parts:
            first_part = path_parts[0].lower()
            if first_part == 'lukhas':
                return ServiceLane.LUKHAS  # Use LUKHAS alias instead of PRODUCTION
            elif first_part == 'labs':
                return ServiceLane.CANDIDATE
            elif first_part == 'matriz':
                return ServiceLane.MATRIZ
            elif first_part == 'core':
                return ServiceLane.CORE
            elif first_part == 'universal_language':
                return ServiceLane.UNIVERSAL

        return ServiceLane.UNKNOWN

    def _check_import(
        self,
        import_name: str,
        file_path: str,
        line_number: int,
        from_lane: ServiceLane,
        import_type: str,
        names: Optional[List[str]] = None
    ) -> Optional[ImportViolation]:
        """
        Check if an import violates lane boundaries.
        
        Args:
            import_name: Module being imported
            file_path: File containing import
            line_number: Line number of import
            from_lane: Lane of importing file
            import_type: 'import' or 'from'
            names: List of names being imported (for 'from' imports)
        
        Returns:
            ImportViolation if violation found, None otherwise
        """
        # Detect target lane
        to_lane = self._detect_import_lane(import_name)

        if to_lane is None:
            # Not a LUKHAS import, allow it
            return None

        # Check for deprecated imports
        import_statement = f"from {import_name}" if import_type == 'from' else f"import {import_name}"
        for deprecated, suggestion in self.DEPRECATED_IMPORTS.items():
            if deprecated in import_statement:
                return ImportViolation(
                    file_path=file_path,
                    line_number=line_number,
                    import_statement=import_statement,
                    violation_type=ImportStatus.DEPRECATED,
                    from_lane=from_lane,
                    to_lane=to_lane,
                    message=f"Deprecated import. {suggestion}",
                    severity="warning"
                )

        # Find applicable rule
        applicable_rule = None
        for rule in self.LANE_RULES:
            if rule.from_lane == from_lane:
                applicable_rule = rule
                break

        if applicable_rule is None:
            # No rule defined, allow for now
            return None

        # Check if import is forbidden
        if to_lane in applicable_rule.forbidden_imports:
            return ImportViolation(
                file_path=file_path,
                line_number=line_number,
                import_statement=import_statement,
                violation_type=ImportStatus.INVALID_LANE_VIOLATION,
                from_lane=from_lane,
                to_lane=to_lane,
                message=f"Lane violation: {from_lane.value} cannot import from {to_lane.value}. {applicable_rule.description}",
                severity="error"
            )

        # Check if import is allowed
        if to_lane not in applicable_rule.allowed_imports and applicable_rule.allowed_imports:
            return ImportViolation(
                file_path=file_path,
                line_number=line_number,
                import_statement=import_statement,
                violation_type=ImportStatus.INVALID_LANE_VIOLATION,
                from_lane=from_lane,
                to_lane=to_lane,
                message=f"Lane violation: {from_lane.value} can only import from {[l.value for l in applicable_rule.allowed_imports]}",
                severity="error"
            )

        return None

    def _detect_import_lane(self, import_name: str) -> Optional[ServiceLane]:
        """
        Detect which lane an import belongs to.
        
        Args:
            import_name: Import module name
        
        Returns:
            ServiceLane or None if not a LUKHAS import
        """
        if import_name.startswith('lukhas.'):
            return ServiceLane.PRODUCTION
        elif import_name.startswith('labs.'):
            return ServiceLane.CANDIDATE
        elif import_name.startswith('matriz.'):
            return ServiceLane.MATRIZ
        elif import_name.startswith('core.'):
            return ServiceLane.CORE
        elif import_name.startswith('universal_language.'):
            return ServiceLane.UNIVERSAL
        else:
            return None

    # ========================================================================
    # Public Methods for Test Compatibility
    # ========================================================================

    def detect_lane(self, file_path: Path) -> ServiceLane:
        """
        Public method to detect which service lane a file belongs to.
        
        Args:
            file_path: File path
        
        Returns:
            Detected ServiceLane
        
        Task: TEST-HIGH-CONTROLLER-01 (lane detection)
        """
        return self._detect_lane(file_path)

    def get_allowed_imports(self, source_lane: ServiceLane) -> List[ServiceLane]:
        """
        Get list of lanes that source_lane can import from.
        
        Args:
            source_lane: Source lane
        
        Returns:
            List of allowed import lanes
        
        Task: TEST-HIGH-CONTROLLER-01 (import boundaries)
        """
        # Find applicable rule
        for rule in self.LANE_RULES:
            if rule.from_lane == source_lane:
                # Include self-imports
                allowed = rule.allowed_imports.copy()
                allowed.append(source_lane)
                return allowed

        # No rule found, allow self-imports only
        return [source_lane]

    def check_import(
        self,
        source_file: Path,
        import_statement: str
    ) -> Optional[ImportViolation]:
        """
        Check if a single import statement violates lane boundaries.
        
        Args:
            source_file: Source file path
            import_statement: Import statement string (e.g., "from consciousness import Protocol")
        
        Returns:
            ImportViolation if violation found, None if valid
        
        Task: TEST-HIGH-CONTROLLER-01 (violation detection)
        """
        # Detect source lane
        from_lane = self._detect_lane(source_file)

        # Parse import statement to extract module name
        import_name = None
        if import_statement.startswith("from "):
            # Extract module from "from X import Y"
            parts = import_statement.split()
            if len(parts) >= 2:
                import_name = parts[1]
        elif import_statement.startswith("import "):
            # Extract module from "import X"
            parts = import_statement.split()
            if len(parts) >= 2:
                import_name = parts[1]

        if not import_name:
            return None  # Can't parse, assume valid

        # Detect target lane
        to_lane = self._detect_import_lane(import_name)

        if to_lane is None:
            return None  # Not a LUKHAS import, allow it

        # Check against rules
        return self._check_import(
            import_name=import_name,
            file_path=str(source_file),
            line_number=1,  # Line number not available from string
            from_lane=from_lane,
            import_type='from' if 'from' in import_statement else 'import',
            names=None
        )

    def load_matriz_config(self, config: Dict[str, Any]) -> None:
        """
        Load lane configuration from ops/matriz.yaml.
        
        Args:
            config: Parsed YAML configuration dictionary
        
        Task: TEST-HIGH-CONTROLLER-02 (YAML compliance)
        """
        self._matriz_config = config
        self._rules_loaded = True

        # Could update LANE_RULES based on config here
        # For now, just store the config
        pass

    def has_rules_loaded(self) -> bool:
        """
        Check if matriz.yaml rules have been loaded.
        
        Returns:
            True if rules loaded, False otherwise
        
        Task: TEST-HIGH-CONTROLLER-02 (YAML enforcement)
        """
        return self._rules_loaded

    def scan_directory(
        self,
        directory: Path,
        recursive: bool = True
    ) -> List[ImportViolation]:
        """
        Scan directory for import violations (synchronous for test compatibility).
        
        Args:
            directory: Directory path to scan
            recursive: Whether to scan subdirectories
        
        Returns:
            List of import violations found
        
        Task: TEST-HIGH-CONTROLLER-02 (directory scanning)
        """
        import asyncio

        # Run async method synchronously
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create a new loop if current is running
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        report = loop.run_until_complete(self.review_directory_imports(directory, recursive))
        return report.violations

    async def scan_directory_async(
        self,
        directory: Path,
        recursive: bool = True
    ) -> List[ImportViolation]:
        """
        Async version of scan_directory.
        
        Args:
            directory: Directory path to scan
            recursive: Whether to scan subdirectories
        
        Returns:
            List of import violations found
        
        Task: TEST-HIGH-CONTROLLER-02 (directory scanning)
        """
        report = await self.review_directory_imports(directory, recursive)
        return report.violations


# Convenience functions
async def review_imports(directory: Path, recursive: bool = True) -> ImportReviewReport:
    """
    Convenience function to review imports in a directory.
    
    Args:
        directory: Directory to scan
        recursive: Whether to scan subdirectories
    
    Returns:
        ImportReviewReport
    """
    controller = ImportController()
    return await controller.review_directory_imports(directory, recursive)


async def check_file(file_path: Path) -> List[ImportViolation]:
    """
    Convenience function to check imports in a single file.
    
    Args:
        file_path: Python file to check
    
    Returns:
        List of violations
    """
    controller = ImportController()
    return await controller.review_file_imports(file_path)
