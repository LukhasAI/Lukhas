from sqlmodel import SQLModel, Field, Session, create_engine, select
from passlib.hash import argon2
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    mfa_level: int = 1

import os
os.makedirs("data", exist_ok=True)
_engine = create_engine("sqlite:///data/users.db", echo=False)
SQLModel.metadata.create_all(_engine)

def create_user(email: str, password: str):
    with Session(_engine) as s:
        user = User(email=email.lower().strip(),
                    password_hash=argon2.hash(password))
        s.add(user); s.commit(); s.refresh(user); return user

def verify_user(email: str, password: str):
    with Session(_engine) as s:
        user = s.exec(select(User).where(User.email==email.lower().strip())).first()
        if not user: return None
        return user if argon2.verify(password, user.password_hash) else None