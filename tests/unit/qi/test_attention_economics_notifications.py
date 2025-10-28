import importlib
import importlib.util
import sys
import types
from pathlib import Path

import pytest


QI_PACKAGE_PATH = Path(__file__).resolve().parents[3] / "qi"

if "qi" not in sys.modules:
    qi_stub = types.ModuleType("qi")
    qi_stub.__path__ = [str(QI_PACKAGE_PATH)]
    sys.modules["qi"] = qi_stub

spec = importlib.util.spec_from_file_location(
    "qi.attention_economics", QI_PACKAGE_PATH / "attention_economics.py"
)
attention_economics = importlib.util.module_from_spec(spec)
sys.modules["qi.attention_economics"] = attention_economics
sys.modules["qi"].attention_economics = attention_economics

assert spec.loader is not None  # for type checkers
spec.loader.exec_module(attention_economics)

AttentionToken = attention_economics.AttentionToken
AttentionTokenType = attention_economics.AttentionTokenType
QIAttentionEconomics = attention_economics.QIAttentionEconomics


class RecordingMessenger:
    def __init__(self):
        self.calls: list[tuple[str, dict[str, object]]] = []

    async def send_notification(self, channel: str, payload: dict[str, object]) -> bool:
        self.calls.append((channel, payload))
        return True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_entangle_attention_tokens_notifies_consciousness_hub():
    messenger = RecordingMessenger()
    economics = QIAttentionEconomics(consciousness_messenger=messenger)

    token_a = AttentionToken(
        token_id="token_a",
        owner_id="user-1",
        token_type=AttentionTokenType.FOCUSED,
        value=1.0,
    )
    token_b = AttentionToken(
        token_id="token_b",
        owner_id="user-2",
        token_type=AttentionTokenType.CREATIVE,
        value=2.0,
    )

    economics.tokens[token_a.token_id] = token_a
    economics.tokens[token_b.token_id] = token_b

    success = await economics.entangle_attention_tokens(
        [token_a.token_id, token_b.token_id],
        entanglement_type="bell_state",
    )

    assert success is True
    assert len(messenger.calls) == 2

    channels = {channel for channel, _ in messenger.calls}
    assert channels == {"attention.entanglement.created"}

    notifications = {payload["recipient"]["user_id"]: payload for _, payload in messenger.calls}
    assert set(notifications) == {"user-1", "user-2"}

    for payload in notifications.values():
        event = payload["event"]
        assert event["entanglement_type"] == "bell_state"
        assert set(event["token_ids"]) == {"token_a", "token_b"}
        assert set(event["owner_token_ids"]).issubset({"token_a", "token_b"})
        assert payload["metadata"]["total_tokens"] == 2
        assert set(payload["metadata"]["unique_owner_ids"]) == {"user-1", "user-2"}
