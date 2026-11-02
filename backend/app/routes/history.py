"""
routes/history.py
------------------
    GET /api/history      -> list all of the logged-in user's history entries
    GET /api/history/{id} -> view one specific history entry

Authorization: a user can only ever query rows where user_id matches their
own current_user.id. If they request an id belonging to someone else, we
return 404 (not 403) so we don't reveal whether that id even exists.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User, HealthHistory
from app.schemas.health import HealthHistoryOut
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/history", tags=["Health History"])


@router.get("", response_model=list[HealthHistoryOut])
def list_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entries = (
        db.query(HealthHistory)
        .filter(HealthHistory.user_id == current_user.id)
        .order_by(HealthHistory.created_at.desc())
        .all()
    )
    return entries


@router.get("/{history_id}", response_model=HealthHistoryOut)
def get_history_item(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = (
        db.query(HealthHistory)
        .filter(HealthHistory.id == history_id, HealthHistory.user_id == current_user.id)
        .first()
    )
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History entry not found.",
        )
    return entry
