"""
schemas/health.py
------------------
Schemas for the Health Profile feature and the Health History feature.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class HealthProfileCreate(BaseModel):
    """Used for both creating and updating a health profile (all optional)."""

    height_cm: Optional[float] = Field(None, gt=0, le=300, examples=[170.5])
    weight_kg: Optional[float] = Field(None, gt=0, le=500, examples=[65.0])
    blood_group: Optional[str] = Field(None, examples=["O+"])
    allergies: Optional[str] = Field(None, examples=["Peanuts, Penicillin"])
    existing_conditions: Optional[str] = Field(None, examples=["Asthma"])
    current_medications: Optional[str] = Field(None, examples=["Inhaler (as needed)"])
    emergency_contact: Optional[str] = Field(None, examples=["+91-9876543210"])


class HealthProfileOut(BaseModel):
    id: int
    user_id: int
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    existing_conditions: Optional[str] = None
    current_medications: Optional[str] = None
    emergency_contact: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HealthHistoryOut(BaseModel):
    id: int
    activity_type: str
    description: str
    reference_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
