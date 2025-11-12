from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from datetime import datetime, timedelta
import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def verify_password(self, plain: str, hashed: str) -> bool:
        try:
            return pwd_context.verify(plain, hashed)
        except UnknownHashError:
            return False

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(self, data: dict) -> str:
        expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode = data.copy()
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm="HS256")

    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
