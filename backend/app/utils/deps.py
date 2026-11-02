"""
deps.py
-------
Shared FastAPI "dependencies" — reusable pieces of logic that routes can
plug in with `Depends(...)`.

`get_current_user` is the most important one: it protects a route by
requiring a valid JWT token, and gives the route the logged-in User
object automatically. Any route that includes:

    current_user: User = Depends(get_current_user)

will now require the `Authorization: Bearer <token>` header, and will
return HTTP 401 automatically if the token is missing/invalid/expired.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.utils.security import decode_access_token

# tokenUrl points Swagger UI ("/docs") to our login endpoint so the
# "Authorize" button there works out of the box.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user
