from fastapi.testclient import TestClient

from serve.main import app


class FakeService:
    async def generate(
        self, prompt: str, context=None, signals=None, params=None, task=None
    ):
        return {
            "content": "ok",
            "raw": {"choices": [{"message": {"content": "ok"}}]},
            "modulation": {
                "style": "DEFAULT",
                "params": {"temperature": 0.2, "max_tokens": 64},
                "signal_levels": {},
            },
            "metadata": {"moderation": "safe"},
        }


def test_openai_chat_route(monkeypatch):
    import serve.openai_routes as openai_routes

    # Ensure our router is mounted
    client = TestClient(app)

    # Monkeypatch the service provider
    monkeypatch.setattr(openai_routes, "get_service", lambda: FakeService())

    resp = client.post("/openai/chat", json={"prompt": "hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["content"] == "ok"
    assert "modulation" in data


class FakeStreamService:
    async def generate_stream(
        self, prompt: str, context=None, signals=None, params=None, task=None
    ):
        async def _gen():
            for ch in ["A", "B", "C"]:
                yield ch

        return _gen()


def test_openai_chat_stream_route(monkeypatch):
    import serve.openai_routes as openai_routes

    client = TestClient(app)
    monkeypatch.setattr(openai_routes, "get_service", lambda: FakeStreamService())

    resp = client.post("/openai/chat/stream", json={"prompt": "hello"})
    assert resp.status_code == 200
    # StreamingResponse is buffered by TestClient; validate full body
    assert resp.text == "ABC"
