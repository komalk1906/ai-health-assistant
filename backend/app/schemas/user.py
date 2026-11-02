"""
schemas/user.py
----------------
Pydantic models define the *shape* of data going in and out of our API.

Difference from SQLAlchemy models (app/database/models.py):
- SQLAlchemy models  -> describe database TABLES.
- Pydantic schemas   -> describe API REQUEST/RESPONSE JSON.

FastAPI uses these schemas to automatically validate incoming JSON and to
generate the Swagger docs at /docs.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegister(BaseModel):
    """Data required to register a new account."""

    full_name: str = Field(..., min_length=2, max_length=100, examples=["Asha Patil"])
    email: EmailStr = Field(..., examples=["asha@example.com"])
    password: str = Field(..., min_length=6, max_length=72, examples=["StrongPass123"])
    age: Optional[int] = Field(None, ge=0, le=120, examples=[21])
    gender: Optional[str] = Field(None, examples=["Female"])


class UserLogin(BaseModel):
    """Data required to log in."""

    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Data we send back about a user (password_hash is deliberately excluded)."""

    id: int
    full_name: str
    email: EmailStr
    age: Optional[int] = None
    gender: Optional[str] = None
    created_at: datetime

    # Lets Pydantic read data directly from a SQLAlchemy object
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Response returned after a successful login/registration."""

    access_token: str
    token_type: str = "bearer"
    user: UserOut
