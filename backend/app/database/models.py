"""
models.py
---------
This file defines all the database tables using SQLAlchemy ORM classes.

Each Python class below becomes one SQL table. Each class attribute becomes
one column. SQLAlchemy converts Python objects <-> database rows for us so
we rarely have to write raw SQL.

Relationships (important for the viva):

    User (1) ----- (1) HealthProfile        [one user has one health profile]
    User (1) ----- (many) ChatMessage       [one user has many chat messages]
    User (1) ----- (many) SymptomCheck      [one user has many symptom checks]
    User (1) ----- (many) HealthHistory     [one user has many history entries]

    Medicine table is independent (a simple lookup/reference table).

We use ForeignKey columns to link child tables back to the User table, and
`relationship()` to let SQLAlchemy load related rows conveniently in Python
(e.g. `user.health_profile`, `user.chat_messages`).
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


class User(Base):
    """Stores account/login information for each user."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # bcrypt hash, never plain text
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # --- Relationships (one User -> many rows in other tables) ---
    health_profile = relationship(
        "HealthProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    chat_messages = relationship(
        "ChatMessage", back_populates="user", cascade="all, delete-orphan"
    )
    symptom_checks = relationship(
        "SymptomCheck", back_populates="user", cascade="all, delete-orphan"
    )
    history_entries = relationship(
        "HealthHistory", back_populates="user", cascade="all, delete-orphan"
    )


class HealthProfile(Base):
    """Stores extra health details for a user. One-to-one with User."""

    __tablename__ = "health_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    blood_group = Column(String(10), nullable=True)
    allergies = Column(Text, nullable=True)              # comma separated or free text
    existing_conditions = Column(Text, nullable=True)    # e.g. "diabetes, asthma"
    current_medications = Column(Text, nullable=True)
    emergency_contact = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="health_profile")


class ChatMessage(Base):
    """Stores each AI chat exchange (user's message + AI's reply)."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    is_emergency = Column(Integer, default=0)  # 0 = False, 1 = True (SQLite has no native bool)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_messages")


class SymptomCheck(Base):
    """Stores each symptom-checker request and its result."""

    __tablename__ = "symptom_checks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    symptoms = Column(Text, nullable=False)          # stored as comma-separated text
    severity = Column(String(20), nullable=True)      # LOW / MODERATE / HIGH
    possible_explanations = Column(Text, nullable=True)
    advice = Column(Text, nullable=True)
    is_emergency = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="symptom_checks")


class Medicine(Base):
    """Reference table with general (non-personalized) medicine information."""

    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    common_uses = Column(Text, nullable=True)
    precautions = Column(Text, nullable=True)
    side_effects = Column(Text, nullable=True)
    warnings = Column(Text, nullable=True)
    seek_professional_advice = Column(String(255), nullable=True)


class HealthHistory(Base):
    """
    A unified activity log for a user: symptom checks, chats, and profile
    updates all get a summarized entry here so the user has one place to
    view their full health-related history.
    """

    __tablename__ = "health_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    activity_type = Column(String(50), nullable=False)  # "chat" | "symptom_check" | "profile_update"
    description = Column(Text, nullable=False)           # short human-readable summary
    reference_id = Column(Integer, nullable=True)         # id of the related row (chat/symptom check)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="history_entries")
