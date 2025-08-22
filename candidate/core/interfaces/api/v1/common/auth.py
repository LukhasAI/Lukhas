# ΛTAG: api_auth

from fastapi import Header, HTTPException


async def verify_api_key(x_api_key: str = Header(...)) -> None:
    """Simple API key verification."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API Key")
    # TODO: use validators for real key check
