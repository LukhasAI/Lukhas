"""
Login/Signup handler guidance (placeholder)
=========================================

This module intentionally contains documentation-only guidance to avoid
undefined names in linting. Implement real FastAPI handlers elsewhere:

Example sketch (do not copy verbatim):

    from fastapi import APIRouter, HTTPException
    from .identity.store import create_user, verify_user

    router = APIRouter()

    @router.post("/signup")
    def signup(payload: SignupRequest):
        user = create_user(payload.email, payload.password)
        return {"id": user.id}

    @router.post("/login")
    def login(payload: LoginRequest):
        user = verify_user(payload.email, payload.password)
        if not user:
            raise HTTPException(status_code=401, detail="invalid credentials")
        return issue_jwt(user)

"""