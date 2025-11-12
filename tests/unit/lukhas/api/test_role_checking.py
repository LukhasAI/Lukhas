import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient

# Import the code to be tested
from lukhas.api.auth_helpers import ROLE_HIERARCHY, has_role
from lukhas.api.features import get_current_user, require_role


# Basic Test: has_role function
def test_has_role_direct_access():
    assert has_role("admin", "admin") == True
    assert has_role("admin", "user") == True
    assert has_role("user", "admin") == False
    assert has_role("guest", "user") == False

# Setup a dummy FastAPI app for testing dependencies
app = FastAPI()

@app.get("/admin")
async def admin_route(current_user: dict = Depends(require_role("admin"))):
    return {"message": "Welcome admin!"}

@app.get("/moderator")
async def moderator_route(current_user: dict = Depends(require_role("moderator"))):
    return {"message": "Welcome moderator!"}

@app.get("/user")
async def user_route(current_user: dict = Depends(require_role("user"))):
    return {"message": "Welcome user!"}

@app.get("/guest")
async def guest_route(current_user: dict = Depends(require_role("guest"))):
    return {"message": "Welcome guest!"}

client = TestClient(app)

# Mock get_current_user dependency
def mock_get_current_user(role: str):
    def override():
        return {"id": "testuser", "role": role}
    return override

# Parametrized tests for different user roles
@pytest.mark.parametrize("role, accessible_endpoints, forbidden_endpoints", [
    ("admin", ["/admin", "/moderator", "/user", "/guest"], []),
    ("moderator", ["/moderator", "/user", "/guest"], ["/admin"]),
    ("user", ["/user", "/guest"], ["/admin", "/moderator"]),
    ("guest", ["/guest"], ["/admin", "/moderator", "/user"]),
])
def test_role_access(role, accessible_endpoints, forbidden_endpoints):
    app.dependency_overrides[get_current_user] = mock_get_current_user(role)

    for endpoint in accessible_endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200, f"Role {role} should access {endpoint}"

    for endpoint in forbidden_endpoints:
        response = client.get(endpoint)
        assert response.status_code == 403, f"Role {role} should not access {endpoint}"

# Test for invalid roles
def test_invalid_role():
    app.dependency_overrides[get_current_user] = mock_get_current_user("invalid_role")
    response = client.get("/user")
    assert response.status_code == 403

# Test for no role (defaults to guest)
def test_no_role():
    app.dependency_overrides[get_current_user] = mock_get_current_user(None)
    response = client.get("/guest")
    assert response.status_code == 200
    response = client.get("/user")
    assert response.status_code == 403

# Clean up dependency overrides
def teardown_function():
    app.dependency_overrides = {}

# More granular tests for has_role
@pytest.mark.parametrize("user_role, required_role, expected", [
    ("admin", "admin", True),
    ("admin", "moderator", True),
    ("admin", "user", True),
    ("admin", "guest", True),
    ("moderator", "admin", False),
    ("moderator", "moderator", True),
    ("moderator", "user", True),
    ("moderator", "guest", True),
    ("user", "admin", False),
    ("user", "moderator", False),
    ("user", "user", True),
    ("user", "guest", True),
    ("guest", "admin", False),
    ("guest", "moderator", False),
    ("guest", "user", False),
    ("guest", "guest", True),
    # Edge cases
    ("admin", "nonexistent", False),
    ("nonexistent", "user", False),
    (None, "user", False),
    ("user", None, False),
    ("", "user", False),
    ("user", "", False),
    (1, "user", False),
    ("user", 1, False),
])
def test_has_role_granular(user_role, required_role, expected):
    assert has_role(user_role, required_role) == expected
