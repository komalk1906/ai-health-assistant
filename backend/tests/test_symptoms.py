"""
tests/test_symptoms.py
-----------------------
Tests for the /api/symptoms/check endpoint.
"""


def test_symptom_check_requires_auth(client):
    response = client.post("/api/symptoms/check", json={"symptoms": ["headache"]})
    assert response.status_code == 401


def test_symptom_check_normal(client, registered_user):
    response = client.post(
        "/api/symptoms/check",
        json={"symptoms": ["headache", "fever", "fatigue"]},
        headers=registered_user["headers"],
    )
    assert response.status_code == 200
    data = response.json()
    assert data["severity"] in ("LOW", "MODERATE", "HIGH")
    assert data["is_emergency"] is False
    assert isinstance(data["professional_attention_recommended"], bool)


def test_symptom_check_emergency(client, registered_user):
    response = client.post(
        "/api/symptoms/check",
        json={"symptoms": ["loss of consciousness", "severe chest pain"]},
        headers=registered_user["headers"],
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_emergency"] is True
    assert data["severity"] == "HIGH"
    assert data["emergency_message"] is not None


def test_symptom_check_empty_list_rejected(client, registered_user):
    response = client.post(
        "/api/symptoms/check", json={"symptoms": []}, headers=registered_user["headers"]
    )
    assert response.status_code == 422
