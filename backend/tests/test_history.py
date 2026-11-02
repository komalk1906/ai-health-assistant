"""
tests/test_history.py
----------------------
Tests for /api/history and /api/history/{id}, including the important
security check: a user must NOT be able to view another user's history.
"""

import uuid


def test_history_requires_auth(client):
    response = client.get("/api/history")
    assert response.status_code == 401


def test_history_list_after_activity(client, registered_user):
    headers = registered_user["headers"]

    # Generate some activity: a chat message
    client.post("/api/chat", json={"message": "I have a sore throat"}, headers=headers)

    response = client.get("/api/history", headers=headers)
    assert response.status_code == 200
    entries = response.json()
    assert len(entries) >= 1
    assert entries[0]["activity_type"] in ("chat", "symptom_check", "profile_update")


def test_history_item_not_found(client, registered_user):
    response = client.get("/api/history/999999", headers=registered_user["headers"])
    assert response.status_code == 404


def test_user_cannot_view_another_users_history(client, registered_user):
    headers_a = registered_user["headers"]

    # User A creates a chat -> generates a history entry
    client.post("/api/chat", json={"message": "I feel tired"}, headers=headers_a)
    history_a = client.get("/api/history", headers=headers_a).json()
    entry_id = history_a[0]["id"]

    # Register a second user (User B)
    reg_b = client.post("/api/auth/register", json={
        "full_name": "User B",
        "email": f"userb-{uuid.uuid4().hex[:8]}@example.com",
        "password": "UserBPass123",
    })
    headers_b = {"Authorization": f"Bearer {reg_b.json()['access_token']}"}

    # User B tries to access User A's history entry by id -> must fail
    response = client.get(f"/api/history/{entry_id}", headers=headers_b)
    assert response.status_code == 404
