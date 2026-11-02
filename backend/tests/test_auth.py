"""
tests/test_auth.py
-------------------
Tests for registration, login, and protected route access.
"""


def test_register_success(client):
    response = client.post("/api/auth/register", json={
        "full_name": "Priya Sharma",
        "email": "priya@example.com",
        "password": "SecurePass1",
        "age": 24,
        "gender": "Female",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "priya@example.com"
    # Make sure password is never returned
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]


def test_register_duplicate_email(client, registered_user):
    response = client.post("/api/auth/register", json={
        "full_name": "Another Name",
        "email": registered_user["email"],  # same email as existing fixture user
        "password": "AnotherPass1",
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_success(client, registered_user):
    response = client.post("/api/auth/login", json={
        "email": registered_user["email"],
        "password": registered_user["password"],
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client, registered_user):
    response = client.post("/api/auth/login", json={
        "email": registered_user["email"],
        "password": "WrongPassword",
    })
    assert response.status_code == 401


def test_get_me_requires_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401  # No Authorization header sent


def test_get_me_with_valid_token(client, registered_user):
    response = client.get("/api/auth/me", headers=registered_user["headers"])
    assert response.status_code == 200
    assert response.json()["email"] == registered_user["email"]


def test_get_me_with_invalid_token(client):
    response = client.get(
        "/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401
