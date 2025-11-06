from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from labs.bridge.adapters.api_framework import JWTAdapter, JWTAlgorithm, TokenClaims
from labs.bridge.adapters.fastapi_middleware import JWTAuthMiddleware

# In a real application, these would come from a secure config
SECRET_KEY = "your-secret-key"
ALGORITHM = JWTAlgorithm.HS256

# 1. Initialize the JWT Adapter
jwt_adapter = JWTAdapter(secret_key=SECRET_KEY, algorithm=ALGORITHM, leeway=0)

# 2. Create the FastAPI app
app = FastAPI()

# 3. Add the JWT Auth Middleware
# Any routes not in 'unprotected_paths' will require a valid JWT
app.add_middleware(
    JWTAuthMiddleware,
    jwt_adapter=jwt_adapter,
    unprotected_paths={"/", "/docs", "/openapi.json", "/token"}
)

# Dependency to get the authenticated user's claims
async def get_current_user(request: Request) -> TokenClaims:
    return request.scope["auth"]

# 4. Create some routes
@app.get("/")
async def read_root():
    return {"message": "This is a public endpoint."}

@app.get("/protected")
async def read_protected(current_user: TokenClaims = Depends(get_current_user)):
    return {"message": "This is a protected endpoint.", "user": current_user}

@app.post("/token")
async def generate_token(user_id: str):
    """Generates a token for a given user_id."""
    token = jwt_adapter.create_token(subject=user_id)
    return {"access_token": token, "token_type": "bearer"}
