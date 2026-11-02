"""
routes/medicines.py
--------------------
    GET /api/medicines                  -> list medicines (optional ?search=text)
    GET /api/medicines/{medicine_name}  -> general (non-personalized) info

This reads from the local `medicines` SQLite table (sample/reference data
only — see app/database/seed_medicines.py). It does NOT call the AI model
and does NOT provide dosage or personalized prescriptions, matching the
project's safety requirements.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Medicine, User
from app.schemas.medicine import MedicineOut
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/medicines", tags=["Medicine Information"])


# NOTE: this route must be declared BEFORE "/{medicine_name}", otherwise
# FastAPI would treat an empty path as a medicine name.
@router.get("", response_model=List[MedicineOut])
def list_medicines(
    search: Optional[str] = Query(None, max_length=100, description="Part of a medicine name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all medicines (A-Z), or only those whose name contains `search`."""
    query = db.query(Medicine)
    if search and search.strip():
        # Escape LIKE wildcards typed by the user so "%" or "_" are treated as plain text
        term = search.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.filter(Medicine.name.ilike(f"%{term}%", escape="\\"))
    return query.order_by(Medicine.name).all()


@router.get("/{medicine_name}", response_model=MedicineOut)
def get_medicine_info(
    medicine_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # requires login, but info isn't user-specific
):
    # Case-insensitive lookup
    medicine = (
        db.query(Medicine)
        .filter(Medicine.name.ilike(medicine_name.strip()))
        .first()
    )
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No information found for medicine '{medicine_name}'.",
        )
    return medicine
