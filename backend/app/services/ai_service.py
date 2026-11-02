"""
services/ai_service.py
-----------------------
This file is the ONLY place in the project that talks to the external AI
model. Keeping it isolated here (instead of calling the AI directly from
routes) makes the code easier to test, explain, and swap providers later.

We use the standard `openai` Python package, but point `base_url` at any
OpenAI-COMPATIBLE endpoint (OpenAI itself, or a compatible provider) using
values from the .env file. This keeps API keys out of source code.
"""

import os
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

from app.services import health_knowledge

load_dotenv()

AI_API_KEY = os.getenv("AI_API_KEY")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")

# The client is created once and reused for every request.
_client: Optional[OpenAI] = None
if AI_API_KEY:
    _client = OpenAI(api_key=AI_API_KEY, base_url=AI_BASE_URL)


# ---------------------------------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------------------------------
# This is the most important piece of "prompt engineering" in the project.
# It is sent with every request to tell the AI model HOW to behave. Explain
# this in your viva as the main safety mechanism on the AI side (working
# together with the rule-based emergency_detection.py layer).
SYSTEM_PROMPT = """You are an AI Health Assistant embedded in a college mini
project. Your ONLY role is to provide general, educational health
information. You are friendly, clear, concise, and non-judgmental, and
safety always comes first.

STRICT RULES YOU MUST FOLLOW:
1. You are NOT a doctor and must never claim to be one.
2. You must NEVER give a certain diagnosis. Use phrases like "this could be
   related to..." or "one possible general explanation is...".
3. You must NEVER prescribe medication, dosages, or specific treatment
   instructions.
4. You must NEVER claim to have examined the patient or guarantee any
   outcome.
5. Always encourage the user to consult a qualified healthcare professional
   for proper diagnosis and treatment, especially for anything that sounds
   serious, persistent, or unclear.
6. If the user describes symptoms that could indicate a medical emergency,
   clearly tell them to seek immediate emergency medical care, and do not
   provide detailed self-treatment steps for that situation.
7. Keep responses concise (roughly 3-6 short sentences or a short bullet
   list) and easy for a non-medical person to understand.
8. If relevant user health-profile context (e.g. allergies, existing
   conditions) is provided to you, take it into account, but still avoid
   definitive diagnoses.
9. Always end by gently reminding the user that this is general
   information, not a substitute for professional medical advice.
"""


def _build_user_context(profile_context: Optional[str]) -> str:
    """Combine profile context (if any) into a short context block."""
    if not profile_context:
        return ""
    return f"\n\n[Relevant user health profile context: {profile_context}]"


def get_ai_response(user_message: str, profile_context: Optional[str] = None) -> str:
    """
    Send the user's message (plus optional health-profile context) to the
    AI model and return its text response.

    If the AI API is not configured (no AI_API_KEY in .env) or the request
    fails, we return a safe fallback message instead of crashing — this
    keeps the project runnable/demo-able even without a real API key.
    """
    if _client is None:
        return _fallback_response(user_message, profile_context=profile_context)

    try:
        completion = _client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message + _build_user_context(profile_context)},
            ],
            temperature=0.4,
            max_tokens=400,
        )
        return completion.choices[0].message.content.strip()
    except Exception:  # noqa: BLE001 - we want to catch any AI API failure
        # In a real product you would log the exception properly. For a
        # mini project we return a clear, safe message instead of failing
        # the whole request.
        return _fallback_response(user_message, error=True, profile_context=profile_context)


def get_symptom_analysis(symptoms: list[str], profile_context: Optional[str] = None) -> dict:
    """
    Ask the AI model to analyze a list of symptoms and return a structured
    result: possible explanations, severity, and advice.

    We instruct the model to reply in a strict, simple format so we can
    parse it reliably without needing a heavier JSON-mode setup — this is
    simple enough for a mini project while still being predictable.
    """
    symptoms_text = ", ".join(symptoms)

    if _client is None:
        return _fallback_symptom_analysis(symptoms)

    prompt = f"""A user reports these symptoms: {symptoms_text}.
{_build_user_context(profile_context)}

Respond ONLY in exactly this format (no extra text):
SEVERITY: <LOW or MODERATE or HIGH>
EXPLANATION: <1-3 sentences with general possible explanations, no diagnosis>
ADVICE: <1-3 sentences of safe general self-care / next-step advice>
SEEK_PROFESSIONAL: <YES or NO>
"""

    try:
        completion = _client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=300,
        )
        raw = completion.choices[0].message.content.strip()
        return _parse_symptom_analysis(raw, symptoms)
    except Exception:  # noqa: BLE001
        return _fallback_symptom_analysis(symptoms, error=True)


def _parse_symptom_analysis(raw: str, symptoms: list[str]) -> dict:
    """Parse the AI's structured text reply into a Python dict."""
    result = {
        "severity": "MODERATE",
        "possible_explanations": raw,
        "advice": "Please monitor your symptoms and rest.",
        "professional_attention_recommended": True,
    }
    lines = raw.splitlines()
    for line in lines:
        if line.upper().startswith("SEVERITY:"):
            value = line.split(":", 1)[1].strip().upper()
            if value in ("LOW", "MODERATE", "HIGH"):
                result["severity"] = value
        elif line.upper().startswith("EXPLANATION:"):
            result["possible_explanations"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("ADVICE:"):
            result["advice"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("SEEK_PROFESSIONAL:"):
            value = line.split(":", 1)[1].strip().upper()
            result["professional_attention_recommended"] = value.startswith("Y")
    return result


# ---------------------------------------------------------------------------
# Fallback logic used when no AI_API_KEY is configured, or the AI call fails.
# This keeps the project demo-able without requiring a paid API key, and
# demonstrates graceful error handling for the "AI API failure" case.
# ---------------------------------------------------------------------------

# Short label appended to knowledge-base answers so the user always knows when
# a reply did NOT come from the external AI model. Set to "" to hide it.
DEMO_LABEL = "(Demo mode: answered from the built-in health knowledge base.)"
ERROR_LABEL = "(AI service is currently unavailable: answered from the built-in health knowledge base.)"


def _fallback_response(
    user_message: str,
    error: bool = False,
    profile_context: Optional[str] = None,
) -> str:
    """
    Answer from the built-in knowledge base (services/health_knowledge.py).
    If nothing in the message matches a known topic, ask the user to give
    more detail instead of returning a meaningless canned reply.
    """
    label = ERROR_LABEL if error else DEMO_LABEL

    reply = health_knowledge.build_chat_reply(user_message, profile_context)
    if reply is None:
        reply = (
            "Thanks for sharing. I don't have specific information about that "
            "yet. Could you describe your symptoms in a bit more detail (for "
            "example fever, headache, cough, stomach pain, tiredness) and how "
            "long you've had them? I can also explain common medicines or give "
            "tips on sleep, diet, exercise and hydration. If your symptoms are "
            "severe, persistent, or getting worse, please consult a qualified "
            "healthcare professional. " + health_knowledge.REMINDER
        )

    return f"{reply}\n\n{label}" if label else reply


def _fallback_symptom_analysis(symptoms: list[str], error: bool = False) -> dict:
    """Rule-based symptom analysis used when no AI model is available."""
    note = "AI service unavailable" if error else "Demo mode"

    analysis = health_knowledge.build_symptom_analysis(symptoms)
    if analysis is not None:
        analysis["possible_explanations"] = f"[{note}] " + analysis["possible_explanations"]
        return analysis

    # None of the symptoms were recognised: stay cautious and generic.
    return {
        "severity": "MODERATE",
        "possible_explanations": (
            f"[{note}] The symptoms reported ({', '.join(symptoms)}) can have "
            "many common, generally non-serious causes such as viral "
            "infections, fatigue, or minor illness, but I could not match them "
            "to a known pattern."
        ),
        "advice": (
            "Rest, stay hydrated, and monitor how you feel over the next day. "
            "If they continue or get worse, please consult a doctor."
        ),
        "professional_attention_recommended": True,
    }
