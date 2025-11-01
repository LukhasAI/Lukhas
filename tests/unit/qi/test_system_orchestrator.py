"""Unit tests for the QI system orchestrator security handling."""

from types import SimpleNamespace
from pathlib import Path
import importlib
import types
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:  # pragma: no cover - defensive path setup for pytest
    sys.path.insert(0, str(ROOT))

tests_unit_path = str(Path(__file__).resolve().parents[1])
if tests_unit_path in sys.path:  # pragma: no cover - prefer repository packages over test namespaces
    sys.path.remove(tests_unit_path)

for module_name in list(sys.modules):
    if module_name.startswith("consciousness"):
        sys.modules.pop(module_name)

for module_name in ("qi", "qi.security"):
    if module_name in sys.modules:  # pragma: no cover - ensure clean imports
        del sys.modules[module_name]

if "consciousness" not in sys.modules:
    consciousness_module = types.ModuleType("consciousness")
    consciousness_module.__path__ = []  # type: ignore[attr-defined]
    sys.modules["consciousness"] = consciousness_module

if "consciousness.qi" not in sys.modules:
    consciousness_qi_module = types.ModuleType("consciousness.qi")
    consciousness_qi_module.qi = object()
    sys.modules["consciousness.qi"] = consciousness_qi_module
    sys.modules["consciousness"].qi = consciousness_qi_module  # type: ignore[attr-defined]


def _install_stub_module(name: str, attributes: dict[str, object]) -> None:
    if name in sys.modules:  # pragma: no cover - allow real modules to take precedence
        return

    module = types.ModuleType(name)
    for attr_name, attr_value in attributes.items():
        setattr(module, attr_name, attr_value)
    sys.modules[name] = module


def _install_orchestrator_dependency_stubs(module) -> None:
    module.QINeuralSymbolicProcessor = lambda *args, **kwargs: SimpleNamespace()
    module.DistributedQuantumSafeOrchestrator = lambda *args, **kwargs: SimpleNamespace()
    module.QIUIOptimizer = lambda *args, **kwargs: SimpleNamespace()
    module.QIAssociativeMemoryBank = lambda *args, **kwargs: SimpleNamespace()

    class _StubTelemetry:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    module.QISafeTelemetry = _StubTelemetry


def _install_orchestrator_dependency_stubs(module) -> None:
    module.QINeuralSymbolicProcessor = lambda *args, **kwargs: SimpleNamespace()
    module.DistributedQuantumSafeOrchestrator = lambda *args, **kwargs: SimpleNamespace()
    module.QIUIOptimizer = lambda *args, **kwargs: SimpleNamespace()
    module.QIAssociativeMemoryBank = lambda *args, **kwargs: SimpleNamespace()

    class _StubTelemetry:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    module.QISafeTelemetry = _StubTelemetry


class _StubDreamQuantumConfig:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class _StubQIDreamAdapter:
    def __init__(self, *args, **kwargs):
        self.config = kwargs.get("config")
        self.active = False

    async def start_dream_cycle(self, *_args, **_kwargs):  # pragma: no cover - support optional paths
        self.active = True

    async def stop_dream_cycle(self):  # pragma: no cover - support optional paths
        self.active = False


class _StubVoiceQuantumConfig:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class _StubQIVoiceEnhancer:
    def __init__(self, *args, **kwargs):
        self.config = kwargs.get("config")

    async def _quantum_voice_process(self, *_args, **_kwargs):  # pragma: no cover - optional path
        return {}

    async def _quantum_speech_generate(self, *_args, **_kwargs):  # pragma: no cover - optional path
        return {}


_install_stub_module(
    "qi.dream_adapter",
    {
        "DreamQuantumConfig": _StubDreamQuantumConfig,
        "QIDreamAdapter": _StubQIDreamAdapter,
    },
)

_install_stub_module(
    "qi.voice_enhancer",
    {
        "VoiceQuantumConfig": _StubVoiceQuantumConfig,
        "QIVoiceEnhancer": _StubQIVoiceEnhancer,
    },
)

_install_stub_module("streamlit", {})

SecurityException = importlib.import_module("qi.security").SecurityException
QIAGISystem = importlib.import_module("qi.states.system_orchestrator").QIAGISystem




def test_qiagisystem_init_requires_security_mesh():
    orchestrator_module = importlib.import_module("qi.states.system_orchestrator")
    _install_orchestrator_dependency_stubs(orchestrator_module)

    class _StubConfig:
        qi_security_config = object()
        cluster_config = object()
        telemetry_endpoint = "https://telemetry.invalid"

    config = _StubConfig()

    with pytest.raises(SecurityException) as exc_info:
        orchestrator_module.QIAGISystem(config)

    assert exc_info.value.code == "missing_security_mesh"
    assert exc_info.value.details.get("config_type") == config.__class__.__name__
class _StubSecurityMesh:
    def __init__(self, *, valid: bool) -> None:
        self._valid = valid
        self.validate_calls = 0

    async def validate_request(self, request) -> bool:  # pragma: no cover - exercise in tests
        self.validate_calls += 1
        return self._valid


@pytest.mark.asyncio
async def test_process_user_request_raises_security_exception_on_failed_validation():
    orchestrator = QIAGISystem.__new__(QIAGISystem)
    security_mesh = _StubSecurityMesh(valid=False)
    orchestrator.security_mesh = security_mesh

    trace = {}

    async def _start_processing_trace():
        trace["started"] = "trace-id"
        return trace["started"]

    async def _end_processing_trace(processing_id):
        trace["ended"] = processing_id

    orchestrator._start_processing_trace = _start_processing_trace
    orchestrator._end_processing_trace = _end_processing_trace

    request = SimpleNamespace()
    qi_session = SimpleNamespace()

    with pytest.raises(SecurityException) as exc_info:
        await orchestrator.process_user_request(request, qi_session)

    assert "integrity validation" in str(exc_info.value)
    assert security_mesh.validate_calls == 1
    assert trace.get("ended") == trace.get("started")


def test_qiagisystem_init_requires_security_mesh():
    orchestrator_module = importlib.import_module("qi.states.system_orchestrator")
    _install_orchestrator_dependency_stubs(orchestrator_module)

    class _StubConfig:
        qi_security_config = object()
        cluster_config = object()
        telemetry_endpoint = "https://telemetry.invalid"

    config = _StubConfig()

    with pytest.raises(SecurityException) as exc_info:
        orchestrator_module.QIAGISystem(config)

    assert exc_info.value.code == "missing_security_mesh"
    assert exc_info.value.details.get("config_type") == config.__class__.__name__
