import pytest
from fastapi.testclient import TestClient

from core.settings import Param
from router.v1.endpoint.authentication_layer import router  # Import your FastAPI router
from core.schema.login_transaction import Login
import bcrypt

# Create a TestClient for the FastAPI app
client = TestClient(router)


@pytest.fixture(scope="module")
def test_user():
    return {"username": "testuser", "password": "testpassword"}


def test_register_user_success(test_user):
    # Test a successful user registration
    response = client.post("/register", json=test_user)
    assert response.status_code == 200
    assert response.json()['status'] == "success"


def test_login_user_success(test_user):
    # Test a successful login
    hashed_password = bcrypt.hashpw(test_user['password'].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    with open(Param.AUTH_HASH_PASS_FILE, "w") as f:
        f.write(f"{test_user['username']}:{hashed_password}\n")
    response = client.post("/login", json=test_user)
    assert response.status_code == 200
    assert response.json()['status'] == "success"


@pytest.mark.xfail(reason="Login User Wrong")
@pytest.mark.parametrize("testlist", [
    # Validate Testing
    {"username": "testuser", "password": "testpassword222"},
    {"username": "testuser", "password": "testpassword3333"}

])
def test_login_user_fail(test_user, testlist):
    # Test a failed login

    response = client.post("/login", json=testlist)
    assert response.status_code == 200
    assert response.json() == {"status": "fail"}


@pytest.mark.xfail(reason="Duplicate User")
def test_register_user_duplicate(test_user):
    # Test registering a duplicate user (should raise HTTPException)
    with open(Param.AUTH_HASH_PASS_FILE, "w") as f:
        f.write(
            f"{test_user['username']}:{bcrypt.hashpw(test_user['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')}\n")
    response = client.post("/register", json=test_user)
    assert response.status_code == 422
    assert response.json() == {"detail": "Duplicate User"}
