import hashlib
import os
import pyotp
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
import secrets

# It is strongly recommended to load this from an environment variable in production
SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(32)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthManager:
    def __init__(self, secret_key: str):
        if not secret_key:
            raise ValueError("A secret key is required for AuthManager")
        self.secret_key = secret_key
        self.algorithm = "HS256"

    def _prehash_password(self, password: str) -> str:
        # Pre-hash password with SHA-256 to handle bcrypt's 72-byte limit
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def verify_password(self, plain: str, hashed: str) -> bool:
        pre_hashed_plain = self._prehash_password(plain)
        return pwd_context.verify(pre_hashed_plain, hashed)

    def get_password_hash(self, password: str) -> str:
        pre_hashed_password = self._prehash_password(password)
        return pwd_context.hash(pre_hashed_password)

    def create_access_token(self, data: dict, expires_delta: timedelta = timedelta(minutes=30)) -> str:
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        expire = now + expires_delta
        to_encode.update({"exp": expire, "iat": now})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, data: dict, expires_delta: timedelta = timedelta(days=7)) -> str:
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        expire = now + expires_delta
        to_encode.update({"exp": expire, "iat": now})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_access_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            return None

    # MFA Methods
    def generate_totp_secret(self) -> str:
        return pyotp.random_base32()

    def get_totp_provisioning_uri(self, secret: str, user_id: str, issuer_name: str = "LUKHAS AI") -> str:
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=user_id, issuer_name=issuer_name)

    def verify_totp(self, secret: str, code: str) -> bool:
        totp = pyotp.TOTP(secret)
        return totp.verify(code)

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

reusable_oauth2 = HTTPBearer(scheme_name="Bearer")

auth_manager = AuthManager(secret_key=SECRET_KEY)

async def get_current_user(token: str = Depends(reusable_oauth2)) -> str:
    payload = auth_manager.decode_access_token(token.credentials)
    if not payload or "user_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload["user_id"]
