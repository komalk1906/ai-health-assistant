"""
services/history_service.py
----------------------------
Small shared helper functions used by multiple routes:

1. `build_profile_context` - turns a user's HealthProfile row into a short
   plain-text summary we can safely pass to the AI as extra context.
2. `log_history` - inserts one row into the `health_history` table so the
   user's activity (chats, symptom checks, profile updates) can all be
   viewed together via GET /api/history.

Keeping this logic here (instead of repeating it in every route file)
follows the DRY principle (Don't Repeat Yourself).
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.database.models import HealthProfile, HealthHistory


def build_profile_context(profile: Optional[HealthProfile]) -> Optional[str]:
    """Build a short text summary of relevant health-profile fields."""
    if profile is None:
        return None

    parts = []
    if profile.allergies:
        parts.append(f"Allergies: {profile.allergies}")
    if profile.existing_conditions:
        parts.append(f"Existing conditions: {profile.existing_conditions}")
    if profile.current_medications:
        parts.append(f"Current medications: {profile.current_medications}")

    if not parts:
        return None
    return "; ".join(parts)


def log_history(
    db: Session,
    user_id: int,
    activity_type: str,
    description: str,
    reference_id: Optional[int] = None,
) -> HealthHistory:
    """Create and save one HealthHistory row."""
    entry = HealthHistory(
        user_id=user_id,
        activity_type=activity_type,
        description=description,
        reference_id=reference_id,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
