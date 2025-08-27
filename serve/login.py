from identity.store import create_user, verify_user
# in signup handler:
u = create_user(payload.email, payload.password)
# in login handler:
u = verify_user(payload.email, payload.password)
if not u: raise HTTPException(status_code=401, detail="invalid credentials")
# existing JWT issue path unchanged; use u.email/u.id as claims
