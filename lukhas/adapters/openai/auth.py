from fastapi import Header, HTTPException

UNAUTHORIZED = {"error":{"type":"unauthorized","message":"missing or invalid token"}}

def require_bearer(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail=UNAUTHORIZED)
    # TODO: verify token via policy_guard (owner/scopes); support PATs and service tokens
