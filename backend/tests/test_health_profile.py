"""
tests/test_health_profile.py
-----------------------------
Tests for creating, viewing, and updating a user's health profile.
"""

import uuid


def test_create_profile_requires_auth(client):
    response = client.post("/api/health/profile", json={"blood_group": "O+"})
    assert response.status_code == 401


def test_create_and_get_profile(client, registered_user):
    headers = registered_user["headers"]

    create_resp = client.post("/api/health/profile", json={
        "height_cm": 170,
        "weight_kg": 65,
        "blood_group": "O+",
        "allergies": "Peanuts",
        "existing_conditions": "Asthma",
        "current_medications": "Inhaler",
        "emergency_contact": "+91-9999999999",
    }, headers=headers)
    assert create_resp.status_code == 201
    assert create_resp.json()["blood_group"] == "O+"

    get_resp = client.get("/api/health/profile", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["allergies"] == "Peanuts"


def test_create_duplicate_profile_fails(client, registered_user):
    headers = registered_user["headers"]
    client.post("/api/health/profile", json={"blood_group": "A+"}, headers=headers)
    second_resp = client.post("/api/health/profile", json={"blood_group": "B+"}, headers=headers)
    assert second_resp.status_code == 400


def test_get_profile_not_found(client):
    # Register a brand-new user with no profile yet
    reg = client.post("/api/auth/register", json={
        "full_name": "No Profile User",
        "email": f"noprofile-{uuid.uuid4().hex[:8]}@example.com",
        "password": "NoProfile123",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    response = client.get("/api/health/profile", headers=headers)
    assert response.status_code == 404


def test_update_profile(client, registered_user):
    headers = registered_user["headers"]
    client.post("/api/health/profile", json={"blood_group": "AB+"}, headers=headers)

    update_resp = client.put("/api/health/profile", json={"blood_group": "O-"}, headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["blood_group"] == "O-"
