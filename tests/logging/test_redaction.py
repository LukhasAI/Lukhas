from observability.filters import redact_pii


def test_redact_email_and_token_like_strings():
    text = "contact me at alice@example.com; token=sk-ABC123xyz"
    red = redact_pii(text)
    assert "alice@" not in red
    assert "sk-ABC" not in red
