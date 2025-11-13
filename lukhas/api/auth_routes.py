from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from lukhas.api.auth import AuthManager
from lukhas.api.auth_helpers import get_auth_manager

router = APIRouter(tags=["Authentication"])

# --- In-memory User Store (for demonstration) ---
# In a real application, this would be a database.
_users_db = {
    "testuser": {
        "username": "testuser",
        "hashed_password": get_auth_manager().get_password_hash("testpassword"),
        "role": "user",
    },
    "admin_user": {
        "username": "admin_user",
        "hashed_password": get_auth_manager().get_password_hash("adminpassword"),
        "role": "admin",
    },
}

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_manager: AuthManager = Depends(get_auth_manager),
):
    """
    OAuth2-compatible endpoint to get an access token.
    """
    user = _users_db.get(form_data.username)
    if not user or not auth_manager.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_manager.create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}
