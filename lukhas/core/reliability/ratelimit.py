def rate_limit_error(retry_after_s: int):
    return {
        "error": {"type": "rate_limit_exceeded", "message": "rate limit exceeded"},
        "headers": {"Retry-After": str(retry_after_s)}
    }
