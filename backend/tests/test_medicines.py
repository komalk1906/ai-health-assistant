"""
tests/test_medicines.py
------------------------
Tests for the /api/medicines/{medicine_name} endpoint.
"""


def test_medicine_lookup_requires_auth(client):
    response = client.get("/api/medicines/Paracetamol")
    assert response.status_code == 401


def test_medicine_lookup_found(client, registered_user):
    response = client.get("/api/medicines/Paracetamol", headers=registered_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Paracetamol"
    assert "common_uses" in data


def test_medicine_lookup_case_insensitive(client, registered_user):
    response = client.get("/api/medicines/ibuprofen", headers=registered_user["headers"])
    assert response.status_code == 200
    assert response.json()["name"] == "Ibuprofen"


def test_medicine_lookup_not_found(client, registered_user):
    response = client.get(
        "/api/medicines/NonExistentMedicineXYZ", headers=registered_user["headers"]
    )
    assert response.status_code == 404
