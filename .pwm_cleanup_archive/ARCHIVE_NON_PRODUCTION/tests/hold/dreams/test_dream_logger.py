import logging

from dream.oneiric_engine.oneiric_core.utils.symbolic_logger import DreamLogger


def test_dream_logger_basic(caplog):
    logger = DreamLogger("test_logger")
    with caplog.at_level(logging.INFO):
        logger.log("hello")
    assert "hello" in caplog.text
