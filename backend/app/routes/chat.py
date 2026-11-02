"""
routes/chat.py
---------------
    POST /api/chat  -> talk to the AI Health Assistant

Flow (matches the project spec):
1. Receive & validate the user's message (Pydantic does validation for us).
2. Run the message through the rule-based emergency_detection layer FIRST.
3. If it's an emergency, skip the AI call and return a safe emergency
   message immediately (faster + guarantees a safe response).
4. Otherwise, fetch the user's health profile (if any) to build extra
   context for the AI.
5. Call the AI service to get a response.
6. Save the conversation (ChatMessage row) and a HealthHistory entry.
7. Return the AI response + disclaimer to the client.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User, HealthProfile, ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse
from app.utils.deps import get_current_user
from app.services.emergency_detection import check_emergency, emergency_message
from app.services.ai_service import get_ai_response
from app.services.history_service import build_profile_context, log_history

router = APIRouter(prefix="/api", tags=["AI Chat"])


@router.post("/chat", response_model=ChatResponse)
def chat_with_assistant(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Step 1 & 2: emergency keyword check runs BEFORE any AI call
    is_emergency, matched_keywords = check_emergency(payload.message)

    if is_emergency:
        ai_text = emergency_message()
    else:
        # Step 3: get profile context (optional, may be None)
        profile = db.query(HealthProfile).filter(
            HealthProfile.user_id == current_user.id
        ).first()
        profile_context = build_profile_context(profile)

        # Step 4: call the AI service
        ai_text = get_ai_response(payload.message, profile_context)

    # Step 5: store the conversation
    chat_row = ChatMessage(
        user_id=current_user.id,
        user_message=payload.message,
        ai_response=ai_text,
        is_emergency=1 if is_emergency else 0,
    )
    db.add(chat_row)
    db.commit()
    db.refresh(chat_row)

    # Step 6: log to unified health history
    log_history(
        db,
        current_user.id,
        "chat",
        f"Chat: \"{payload.message[:60]}\"",
        chat_row.id,
    )

    return ChatResponse(ai_response=ai_text, is_emergency=is_emergency)
