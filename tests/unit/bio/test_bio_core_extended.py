"""Extended tests for bio_core."""
import pytest
from bio.core.bio_core import BioCore


def test_bio_core_initialization():
    """Test BioCore initialization."""
    core = BioCore()
    assert core is not None


def test_bio_core_step():
    """Test BioCore stepping."""
    core = BioCore()
    snapshot = core.step()
    assert snapshot is not None


def test_record_emotion():
    """Test recording an emotion."""
    core = BioCore()
    snapshot = core.record_emotion(valence=0.5, arousal=0.2)
    assert snapshot.valence == 0.5
    assert snapshot.arousal == 0.2


def test_process_emotional_signal():
    """Test processing an emotional signal."""
    core = BioCore()
    signal = {"valence": -0.5, "arousal": 0.8}
    snapshot = core.process_emotional_signal(signal)
    assert snapshot.valence == -0.5
    assert snapshot.arousal == 0.8
