"""
routes/symptoms.py
-------------------
    POST /api/symptoms/check  -> analyze a list of symptoms

Same emergency-first pattern as chat.py: we check for emergency keywords
across the combined symptom list BEFORE calling the AI model.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User, HealthProfile, SymptomCheck
from app.schemas.chat import SymptomCheckRequest, SymptomCheckResponse
from app.utils.deps import get_current_user
from app.services.emergency_detection import check_emergency, emergency_message
from app.services.ai_service import get_symptom_analysis
from app.services.history_service import build_profile_context, log_history

router = APIRouter(prefix="/api/symptoms", tags=["Symptom Checker"])


@router.post("/check", response_model=SymptomCheckResponse)
def check_symptoms(
    payload: SymptomCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    combined_text = ", ".join(payload.symptoms)
    is_emergency, matched_keywords = check_emergency(combined_text)

    if is_emergency:
        result = {
            "severity": "HIGH",
            "possible_explanations": (
                "The symptoms you described may indicate a medical emergency."
            ),
            "advice": "Do not wait — seek emergency medical help immediately.",
            "professional_attention_recommended": True,
        }
        emergency_note = emergency_message()
    else:
        profile = db.query(HealthProfile).filter(
            HealthProfile.user_id == current_user.id
        ).first()
        profile_context = build_profile_context(profile)
        result = get_symptom_analysis(payload.symptoms, profile_context)
        emergency_note = None

    # Save to symptom_checks table
    record = SymptomCheck(
        user_id=current_user.id,
        symptoms=combined_text,
        severity=result["severity"],
        possible_explanations=result["possible_explanations"],
        advice=result["advice"],
        is_emergency=1 if is_emergency else 0,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    log_history(
        db,
        current_user.id,
        "symptom_check",
        f"Symptom check: {combined_text[:60]} (severity: {result['severity']})",
        record.id,
    )

    return SymptomCheckResponse(
        symptoms=payload.symptoms,
        possible_explanations=result["possible_explanations"],
        severity=result["severity"],
        advice=result["advice"],
        professional_attention_recommended=result["professional_attention_recommended"],
        is_emergency=is_emergency,
        emergency_message=emergency_note,
    )
