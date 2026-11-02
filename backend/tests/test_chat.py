"""
tests/test_chat.py
-------------------
Tests for the AI chat endpoint, including the emergency-detection layer.
Note: with no AI_API_KEY set in the test environment, ai_service.py returns
its safe fallback text — which is fine, since these tests check the API
contract (status codes, fields, emergency flag) not the exact AI wording.
"""


def test_chat_requires_auth(client):
    response = client.post("/api/chat", json={"message": "I have a headache"})
    assert response.status_code == 401


def test_chat_normal_message(client, registered_user):
    response = client.post(
        "/api/chat",
        json={"message": "I have a mild headache and slight fever."},
        headers=registered_user["headers"],
    )
    assert response.status_code == 200
    data = response.json()
    assert "ai_response" in data
    assert data["is_emergency"] is False
    assert "disclaimer" in data
    assert "not a substitute" in data["disclaimer"]


def test_chat_emergency_message(client, registered_user):
    response = client.post(
        "/api/chat",
        json={"message": "I am having severe chest pain and can't breathe"},
        headers=registered_user["headers"],
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_emergency"] is True
    assert "emergency" in data["ai_response"].lower()


def test_chat_empty_message_rejected(client, registered_user):
    response = client.post(
        "/api/chat", json={"message": ""}, headers=registered_user["headers"]
    )
    assert response.status_code == 422  # fails Pydantic min_length validation
