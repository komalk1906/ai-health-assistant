"""
security.py
------------
All password-hashing and JWT (JSON Web Token) logic lives here.

Why this matters for the viva:
- We NEVER store plain-text passwords. We store a bcrypt HASH instead.
  Even if the database is leaked, the original passwords cannot be
  recovered from the hash.
- JWT is a signed token the server gives the client after login. The
  client sends this token with every future request (in the
  `Authorization: Bearer <token>` header) instead of sending the
  password again. The server verifies the token's signature using
  SECRET_KEY to confirm it wasn't tampered with.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# --- Configuration (loaded from .env, never hard-coded) ---
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-insecure-secret-change-me")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# CryptContext handles hashing and verifying passwords using bcrypt.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Convert a plain-text password into a secure bcrypt hash."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a plain-text password against the stored bcrypt hash."""
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT access token.

    `data` typically contains {"sub": user_email} where "sub" (subject)
    is the standard JWT claim identifying who the token belongs to.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token.
    Returns the payload dict if valid, or None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
