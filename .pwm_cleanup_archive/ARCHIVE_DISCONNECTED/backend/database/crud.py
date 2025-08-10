"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : crud.py                                        │
│ DESCRIPTION : Symbolic database operations for LucasID       │
│ TYPE        : CRUD Layer                                     │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

from sqlalchemy.orm import Session

from .models import User


def get_user_by_slug(db: Session, slug: str):
    """
    Retrieve a LucasID user by their symbolic username_slug.
    """
    return db.query(User).filter(User.username_slug == slug).first()


def get_user_by_email(db: Session, email: str):
    """
    Retrieve a user by email address.
    """
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_data: dict):
    """
    Create a new symbolic user record.
    """
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
