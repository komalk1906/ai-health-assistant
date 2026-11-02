"""
routes/auth.py
---------------
Authentication endpoints:

    POST /api/auth/register  -> create a new account
    POST /api/auth/login     -> log in, get a JWT access token
    GET  /api/auth/me        -> get the currently logged-in user's details
    POST /api/auth/logout    -> "logout" endpoint (see note below)

Note on logout with JWT:
JWTs are stateless — the server does not "store" a session to delete. The
standard approach (used here) is that logout simply tells the client to
delete the token it is holding. We still expose a POST /logout endpoint
for a clean frontend flow and to demonstrate the concept in the viva.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.schemas.user import UserRegister, UserLogin, UserOut, Token
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """Create a new user account and immediately return a JWT token."""

    # Check for duplicate email
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    new_user = User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        age=payload.age,
        gender=payload.gender,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": new_user.email})
    return Token(access_token=access_token, user=UserOut.model_validate(new_user))


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """Verify credentials and return a JWT access token."""

    user = db.query(User).filter(User.email == payload.email).first()

    # Use the SAME error message for "no such user" and "wrong password" so
    # we don't leak which emails are registered (a basic security practice).
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password.",
    )

    if not user:
        raise invalid_credentials
    if not verify_password(payload.password, user.password_hash):
        raise invalid_credentials

    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Return details of the currently logged-in user (requires JWT token)."""
    return current_user


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Stateless logout: JWTs cannot be "deleted" server-side without an extra
    blocklist table (out of scope for this mini project). The client is
    responsible for deleting the token after calling this endpoint.
    """
    return {"message": "Logged out successfully. Please delete the token on the client side."}
