"""
tests/conftest.py
------------------
Shared pytest fixtures for all test files.

Key idea: tests must NOT use the real health_assistant.db file. We create a
separate, temporary SQLite database just for testing, and override
FastAPI's `get_db` dependency to use it. This is a standard FastAPI testing
pattern that's easy to explain in a viva.
"""

import os
import sys
import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Make sure "app" package is importable when running `pytest` from backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database.connection import Base, get_db
from app.database.seed_medicines import seed_medicines

TEST_DATABASE_URL = "sqlite:///./test_health_assistant.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Create fresh tables before the test session, drop them after.

    Note: app.main's startup event seeds sample medicines into the
    PRODUCTION database engine (app.database.connection.engine), not this
    test engine, because it isn't aware of our dependency override. So we
    seed the medicines table directly here using the test session, or the
    medicine-lookup tests would see an empty table.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        seed_medicines(db)
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_health_assistant.db"):
        os.remove("./test_health_assistant.db")


@pytest.fixture()
def client():
    """A TestClient instance for making requests to the app in tests."""
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def registered_user(client):
    """Register a user and return (email, password, token, headers)."""
    unique_email = f"testuser-{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "full_name": "Test User",
        "email": unique_email,
        "password": "TestPass123",
        "age": 22,
        "gender": "Other",
    }
    response = client.post("/api/auth/register", json=payload)
    data = response.json()
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return {"email": payload["email"], "password": payload["password"],
            "token": token, "headers": headers}
