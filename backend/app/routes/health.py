"""
routes/health.py
-----------------
Health Profile endpoints:

    POST /api/health/profile  -> create the logged-in user's health profile
    GET  /api/health/profile  -> view the logged-in user's health profile
    PUT  /api/health/profile  -> update the logged-in user's health profile

Every route here uses `Depends(get_current_user)`, so a user can only ever
create/view/update THEIR OWN profile — there is no way to pass another
user's ID, which is how we enforce "users can only access their own data".
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User, HealthProfile
from app.schemas.health import HealthProfileCreate, HealthProfileOut
from app.utils.deps import get_current_user
from app.services.history_service import log_history

router = APIRouter(prefix="/api/health", tags=["Health Profile"])


@router.post("/profile", response_model=HealthProfileOut, status_code=status.HTTP_201_CREATED)
def create_health_profile(
    payload: HealthProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A health profile already exists for this user. Use PUT to update it.",
        )

    profile = HealthProfile(user_id=current_user.id, **payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)

    log_history(db, current_user.id, "profile_update", "Health profile created.", profile.id)
    return profile


@router.get("/profile", response_model=HealthProfileOut)
def get_health_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No health profile found. Create one first using POST /api/health/profile.",
        )
    return profile


@router.put("/profile", response_model=HealthProfileOut)
def update_health_profile(
    payload: HealthProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No health profile found. Create one first using POST /api/health/profile.",
        )

    # Only update fields the client actually sent (exclude_unset=True)
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    log_history(db, current_user.id, "profile_update", "Health profile updated.", profile.id)
    return profile
