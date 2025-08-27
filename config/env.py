import os


def get(key: str, default=None):
    """Return env var value or default."""
    return os.getenv(key, default)


def require(key: str):
    """Return env var value or raise if missing."""
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Missing required env var: {key}")
    return value

