import logging

logger = logging.getLogger(__name__)
from lukhas.core.common.logger import JSONFormatter
from lukhas.memory.emotional import EmotionalMemoryManager


def test_logger_jsonformatter_utc_timestamp():
    formatter = JSONFormatter()
    record = type(
        "R",
        (),
        {
            "levelname": "INFO",
            "module": "x",
            "funcName": "f",
            "lineno": 1,
            "getMessage": lambda self: "msg",
            "thread": 1,
            "threadName": "t",
        },
    )()
    out = formatter.format(record)
    assert "+00:00" in out or "Z" in out


def test_emotional_memory_manager_utc_timestamps():
    mgr = EmotionalMemoryManager()
    mem_id = mgr.store_emotional_memory("hello", "joy", 0.8)
    mem = mgr.retrieve_emotional_memory(mem_id)
    assert mem is not None
    assert "+00:00" in mem["timestamp"]
