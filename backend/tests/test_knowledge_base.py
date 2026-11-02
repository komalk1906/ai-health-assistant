"""
tests/test_knowledge_base.py
-----------------------------
Tests for the built-in health knowledge base, the offline (no AI key) chat
and symptom replies, and the new medicine list/search endpoint.

The fixture below forces "demo mode" (no external AI client) so these tests
are deterministic even if a real AI_API_KEY exists in your .env file.
"""

import pytest


@pytest.fixture(autouse=True)
def force_demo_mode(monkeypatch):
    monkeypatch.setattr("app.services.ai_service._client", None)


def chat(client, user, message):
    return client.post("/api/chat", json={"message": message}, headers=user["headers"])


# ---------- Chat: topic answers ----------

def test_chat_topic_answer_mentions_headache_and_fever(client, registered_user):
    data = chat(client, registered_user, "I have a headache and mild fever.").json()
    text = data["ai_response"].lower()
    assert "headache" in text and "fever" in text
    assert "see a doctor" in text or "medical help" in text
    assert data["is_emergency"] is False


def test_chat_replies_differ_by_topic(client, registered_user):
    cough = chat(client, registered_user, "I have a bad cough").json()["ai_response"]
    sleep = chat(client, registered_user, "I cannot sleep at night").json()["ai_response"]
    assert cough != sleep
    assert "cough" in cough.lower()
    assert "sleep" in sleep.lower()


def test_chat_unknown_message_asks_for_more_detail(client, registered_user):
    text = chat(client, registered_user, "asdf qwerty zxcv").json()["ai_response"].lower()
    assert "more detail" in text


# ---------- Chat: medicines ----------

def test_chat_medicine_question_uses_medicine_info(client, registered_user):
    text = chat(client, registered_user, "Tell me about ibuprofen").json()["ai_response"]
    assert "Ibuprofen" in text
    assert "Precautions" in text


def test_chat_brand_name_maps_to_medicine(client, registered_user):
    text = chat(client, registered_user, "Can I take Crocin for fever?").json()["ai_response"]
    assert "Paracetamol" in text


def test_chat_refuses_dosage_questions(client, registered_user):
    text = chat(client, registered_user, "How many mg of paracetamol should I take?").json()["ai_response"].lower()
    assert "not able to recommend doses" in text


def test_chat_how_much_water_is_not_treated_as_dosage(client, registered_user):
    text = chat(client, registered_user, "How much water should I drink?").json()["ai_response"].lower()
    assert "not able to recommend doses" not in text
    assert "water" in text


# ---------- Symptom checker (offline rules) ----------

def test_symptom_checker_low_severity_for_single_mild_symptom(client, registered_user):
    r = client.post("/api/symptoms/check", json={"symptoms": ["sneezing"]}, headers=registered_user["headers"])
    assert r.status_code == 200
    assert r.json()["severity"] == "LOW"
    assert r.json()["is_emergency"] is False


def test_symptom_checker_red_flag_raises_severity(client, registered_user):
    r = client.post(
        "/api/symptoms/check",
        json={"symptoms": ["stomach pain", "blood in stool"]},
        headers=registered_user["headers"],
    )
    assert r.status_code == 200
    assert r.json()["severity"] == "HIGH"
    assert r.json()["professional_attention_recommended"] is True


# ---------- Medicines list / search ----------

def test_medicine_list_requires_auth(client):
    assert client.get("/api/medicines").status_code == 401


def test_medicine_list_returns_all_sorted(client, registered_user):
    r = client.get("/api/medicines", headers=registered_user["headers"])
    assert r.status_code == 200
    names = [m["name"] for m in r.json()]
    assert len(names) >= 20
    assert names == sorted(names)
    assert "Paracetamol" in names and "Oral Rehydration Salts" in names


def test_medicine_search_filters_by_name(client, registered_user):
    r = client.get("/api/medicines?search=para", headers=registered_user["headers"])
    assert [m["name"] for m in r.json()] == ["Paracetamol"]


def test_medicine_search_no_match_returns_empty_list(client, registered_user):
    r = client.get("/api/medicines?search=zzzzzz", headers=registered_user["headers"])
    assert r.status_code == 200 and r.json() == []


def test_medicine_search_treats_percent_as_plain_text(client, registered_user):
    r = client.get("/api/medicines?search=%25", headers=registered_user["headers"])
    assert r.status_code == 200 and r.json() == []
