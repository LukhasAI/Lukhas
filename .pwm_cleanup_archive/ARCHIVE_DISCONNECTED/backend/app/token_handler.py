"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : token_handler.py                               │
│ DESCRIPTION : JWT token generation and validation for LUKHASID│
│ TYPE        : Token Manager                                  │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

import os
from datetime import datetime, timedelta

import jwt

# #ΛSECURITY_PATCH - Using environment variable for JWT secret
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable must be set")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour


# #ΛTOKEN_CHAIN
def create_access_token(data: dict) -> str:
    """
    Create a symbolic access token.
    """
    # #AIDENTITY_TRACE
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a symbolic access token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
