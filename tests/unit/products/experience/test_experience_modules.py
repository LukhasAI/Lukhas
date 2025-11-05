import warnings
from collections import Counter

import pytest
from products.experience.dashboard.consciousness import trace_dashboard
from pydantic.warnings import PydanticDeprecatedSince20

from products.experience.universal_language.core.core import (
    Grammar,
    Symbol,
    SymbolicDomain,
)
from products.experience.universal_language.core.multimodal import ModalityProcessor
from products.experience.voice.bridge.adaptation_module import (
    VoiceAdaptationModule,
    load_initial_emotion_map,
)
from products.experience.voice.bridge.validator import VoiceValidator
from system.common.event_bus import EventBus

warnings.filterwarnings("ignore", message="Import 'bio.bio_utilities' is deprecated")
warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)

pytestmark = pytest.mark.filterwarnings("ignore:Import 'bio.bio_utilities' is deprecated")


def test_trace_dashboard_uses_streamlit_facade():
    facade = trace_dashboard.st
    facade.reset()

    trace_dashboard.render_dashboard()

    recorded_methods = Counter(call.method for call in facade.calls)
    assert recorded_methods["title"] == 1
    assert recorded_methods["metric"] >= 2


def test_universal_adaptive_dashboard_event_bus():
    dashboard_module = pytest.importorskip(
        "products.experience.dashboard.interfaces.core.universal_adaptive_dashboard"
    )
    dashboard = dashboard_module.UniversalAdaptiveDashboard()
    assert isinstance(dashboard.event_bus, EventBus)


def test_voice_validator_logger_component_metadata():
    validator = VoiceValidator()
    component_meta = getattr(validator.logger, "extra", {}).get("component")
    assert component_meta == "VoiceValidator"


def test_voice_adaptation_initial_state_isolated():
    baseline = load_initial_emotion_map()
    module = VoiceAdaptationModule()
    module.emotion_map["calm"]["pitch"] += 0.05

    fresh_map = load_initial_emotion_map()
    assert fresh_map["calm"]["pitch"] == baseline["calm"]["pitch"]


def test_language_detection_and_emoji_categories():
    processor = ModalityProcessor()

    assert processor.detect_language("こんにちは世界") == "ja"
    assert processor.detect_language("¿Cómo estás?") == "es"
    categories = processor.get_emoji_categories("😊")
    assert "emotion" in categories


def test_grammar_validation_and_transformations():
    emotion_symbol = Symbol(
        id="EMO_TEST",
        domain=SymbolicDomain.EMOTION,
        name="joy",
        value=1.0,
    )
    action_symbol = Symbol(
        id="ACT_TEST",
        domain=SymbolicDomain.ACTION,
        name="share",
        value="share",
    )
    grammar = Grammar(
        rule_id="GRAM_TEST",
        name="Emotion Action",
        pattern="EMOTION ACTION",
        domain=SymbolicDomain.ACTION,
        transformations=["deduplicate", "tag:core", "adjust-confidence:0.1"],
    )

    assert grammar.validate([emotion_symbol, action_symbol])
    transformed = grammar.apply_transformations(
        [emotion_symbol, action_symbol, emotion_symbol]
    )
    assert len(transformed) == 2
    assert "core" in transformed[0].metadata.get("grammar_tags", [])
    assert transformed[0].confidence <= 1.0


def test_vocabulary_import_round_trip():
    vocab_module = pytest.importorskip(
        "products.experience.universal_language.core.vocabulary"
    )
    UnifiedVocabulary = vocab_module.UnifiedVocabulary
    unified = UnifiedVocabulary()
    payload = {
        "domains": {
            "vision": {
                "symbols": [
                    {
                        "id": "VISION_AURORA",
                        "domain": "vision",
                        "name": "aurora",
                        "value": "aurora",
                        "glyph": "🌌",
                    }
                ],
                "concepts": [
                    {
                        "concept_id": "VISION.AURORA",
                        "concept_type": "abstract",
                        "meaning": "aurora",
                        "symbols": [
                            {
                                "id": "VISION_AURORA",
                                "domain": "vision",
                                "name": "aurora",
                            }
                        ],
                    }
                ],
            }
        }
    }

    assert unified.import_vocabulary(payload)
    lookup = unified.lookup("aurora")
    assert lookup["symbols"]
    concept = unified.manager.find_concept("aurora")
    assert concept is not None
