from datetime import datetime, timezone


def utc_now() -> datetime:
    """Returns the current time in UTC with timezone information."""
    return datetime.now(timezone.utc)
