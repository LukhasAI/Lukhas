from lukhas_pwm.client import LukhasPWM, LukhasError


class FakeResp:
    def __init__(self, status=200, json_data=None, text="", ctype="application/json"):
        self.status_code = status
        self._json = json_data
        self.text = text
        self.headers = {"content-type": ctype}
        self.reason = "OK" if status == 200 else "ERR"

    def json(self):
        return self._json


def test_feedback_and_lut(monkeypatch):
    calls = []

    def fake_request(self, method, url, params=None, json=None, timeout=None):
        calls.append((method, url))
        if url.endswith("/feedback/card"):
            return FakeResp(json_data={"status": "ok"})
        if url.endswith("/feedback/lut"):
            return FakeResp(json_data={"version": 1})
        raise AssertionError("unexpected url " + url)

    monkeypatch.setattr("requests.Session.request", fake_request, raising=True)
    c = LukhasPWM("http://x")
    assert c.feedback_card(target_action_id="A", rating=5)["status"] == "ok"
    assert c.feedback_lut()["version"] == 1
