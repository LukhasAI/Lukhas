import asyncio
import sys
from types import ModuleType
from unittest.mock import patch

from memory.memoria import create_core_memoria_component
from quantum_mind import ConsciousnessPhase

# Provide minimal stubs for core.common dependencies used by DreamModule
core_common = ModuleType("core.common.__init__")


class _BaseModule:
    def __init__(self, module_name: str):
        self.module_name = module_name


core_common.BaseModule = _BaseModule


def symbolic_vocabulary(func=None):
    return func


def ethical_validation(func=None):
    return func


core_common.symbolic_vocabulary = symbolic_vocabulary
core_common.ethical_validation = ethical_validation
sys.modules.setdefault("core.common.__init__", core_common)

from dream.core import DreamModule


def test_memoria_records_phase():
    memoria = create_core_memoria_component()
    with patch(
        "lukhas.memory.memoria.get_current_phase", return_value=ConsciousnessPhase.DREAM
    ):
        result = memoria.process_symbolic_trace("data", 1)
    phase = memoria.get_last_consciousness_phase()
    assert phase == ConsciousnessPhase.DREAM.value
    assert memoria.trace_store[result["trace_id"]]["consciousness_phase"] == phase


def test_dream_state_includes_phase():
    memoria = create_core_memoria_component()
    with patch(
        "lukhas.memory.memoria.get_current_phase", return_value=ConsciousnessPhase.WAKE
    ):
        memoria.process_symbolic_trace("data", 1)
    dream = DreamModule()
    dream.set_memory_module(memoria)

    async def run():
        return await dream.get_current_dream_state()

    result = asyncio.run(run())
    assert result["dream_state"]["consciousness_phase"] == ConsciousnessPhase.WAKE.value
