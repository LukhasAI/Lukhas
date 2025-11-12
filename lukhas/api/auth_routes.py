from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Dict, List
import time
import redis.asyncio as redis
import json
import os

from lukhas.api.auth_helpers import auth_manager

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def get_redis_client():
    return redis_client

# Rate limiting for login attempts
RATE_LIMIT = 5  # attempts
RATE_LIMIT_WINDOW = 60  # seconds

async def check_rate_limit(identifier: str, redis_client: redis.Redis) -> bool:
    now = time.time()
    key = f"rate_limit:{identifier}"

    async with redis_client.pipeline() as pipe:
        pipe.lrem(key, 0, now - RATE_LIMIT_WINDOW)
        pipe.lpush(key, now)
        pipe.llen(key)
        results = await pipe.execute()

    return results[2] <= RATE_LIMIT

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

@router.post("/register")
async def register_user(form_data: OAuth2PasswordRequestForm = Depends(), redis_client: redis.Redis = Depends(get_redis_client)):
    user_key = f"user:{form_data.username}"
    if await redis_client.exists(user_key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    hashed_password = auth_manager.get_password_hash(form_data.password)
    await redis_client.hset(user_key, mapping={
        "username": form_data.username,
        "hashed_password": hashed_password,
    })

    return {"status": "User registered successfully"}

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    if not await check_rate_limit(form_data.username, redis_client):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
        )

    user_key = f"user:{form_data.username}"
    user = await redis_client.hgetall(user_key)
    if not user or not auth_manager.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_manager.create_access_token(data={"user_id": user["username"]})
    refresh_token = auth_manager.create_refresh_token(data={"user_id": user["username"]})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

class RefreshTokenRequest(BaseModel):
    refresh_token: str

from lukhas.api.auth_helpers import get_current_user

@router.post("/token/refresh", response_model=Token)
async def refresh_access_token(request: RefreshTokenRequest):
    payload = auth_manager.decode_access_token(request.refresh_token)
    if not payload or "user_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload["user_id"]
    # In a real app, you might want to check if the user still exists and is active

    new_access_token = auth_manager.create_access_token(data={"user_id": user_id})
    new_refresh_token = auth_manager.create_refresh_token(data={"user_id": user_id})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }

class MFASetupResponse(BaseModel):
    secret: str
    provisioning_uri: str

@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(current_user: str = Depends(get_current_user), redis_client: redis.Redis = Depends(get_redis_client)):
    secret = auth_manager.generate_totp_secret()
    user_key = f"user:{current_user}"
    await redis_client.hset(user_key, "totp_secret", secret)
    provisioning_uri = auth_manager.get_totp_provisioning_uri(secret, current_user)
    return {"secret": secret, "provisioning_uri": provisioning_uri}

class MFAVerifyRequest(BaseModel):
    code: str

@router.post("/mfa/verify")
async def verify_mfa(request: MFAVerifyRequest, current_user: str = Depends(get_current_user), redis_client: redis.Redis = Depends(get_redis_client)):
    user_key = f"user:{current_user}"
    user = await redis_client.hgetall(user_key)
    if not user or "totp_secret" not in user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not set up for this user.",
        )

    if not auth_manager.verify_totp(user["totp_secret"], request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code.",
        )

    return {"status": "MFA verified successfully"}
