import sys
import types

# Ensure asyncpg is stubbed for imports
sys.modules.setdefault("asyncpg", types.ModuleType("asyncpg"))

from starlette.requests import Request

from consent.api import get_client_context, get_client_ip

# ΛTAG: request_utils

def make_request(headers=None, client=("1.2.3.4", 1234)) -> Request:
    scope = {
        "type": "http",
        "headers": [
            (k.lower().encode(), v.encode()) for k, v in (headers or {}).items()
        ],
        "client": client,
    }
    return Request(scope)


def test_get_client_ip_forwarded():
    request = make_request(
        headers={"X-Forwarded-For": "8.8.8.8, 1.1.1.1"}, client=("0.0.0.0", 0)
    )
    assert get_client_ip(request) == "8.8.8.8"


def test_get_client_ip_real_ip():
    request = make_request(headers={"X-Real-IP": "7.7.7.7"}, client=("0.0.0.0", 0))
    assert get_client_ip(request) == "7.7.7.7"


def test_get_client_ip_default():
    request = make_request(client=("9.9.9.9", 0))
    assert get_client_ip(request) == "9.9.9.9"


def test_get_client_ip_unknown():
    request = make_request()
    request.scope["client"] = None
    assert get_client_ip(request) == "unknown"


def test_get_client_context():
    headers = {
        "User-Agent": "agent",
        "Referer": "ref",
        "Accept-Language": "en",
        "X-Session-ID": "sid",
        "X-Client-Fingerprint": "fp",
    }
    request = make_request(headers=headers)
    context = get_client_context(request)
    assert context == {
        "user_agent": "agent",
        "referer": "ref",
        "accept_language": "en",
        "session_id": "sid",
        "client_fingerprint": "fp",
    }
