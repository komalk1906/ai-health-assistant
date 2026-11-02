"""
services/emergency_detection.py
--------------------------------
A simple, RULE-BASED (not AI-based) safety layer that runs BEFORE we ever
call the AI model.

Why rule-based and not AI-based?
Because AI responses can vary, and for genuinely dangerous symptoms we want
a fast, predictable, 100%-reliable check that never depends on how the AI
model happens to phrase something. This is a common and important pattern
in real health-tech systems: a deterministic safety net in front of a
probabilistic AI model.

The design is intentionally MODULAR:
- `EMERGENCY_KEYWORDS` is just a Python list of phrases/keywords.
- To support more emergencies later, you only need to add more strings to
  this list (or load it from a JSON/DB file) — no other code changes needed.
"""

from typing import List, Tuple

# Each entry is a lowercase keyword/phrase we look for inside user input.
# Grouped by category only for readability; the detection logic below
# treats them as one flat list.
EMERGENCY_KEYWORDS: List[str] = [
    # Breathing
    "severe difficulty breathing",
    "can't breathe",
    "cannot breathe",
    "not able to breathe",
    "choking",
    "turning blue",

    # Consciousness
    "loss of consciousness",
    "unconscious",
    "unresponsive",
    "fainted and not waking up",

    # Cardiac
    "severe chest pain",
    "crushing chest pain",
    "chest pain radiating to arm",
    "heart attack",

    # Stroke signs (F.A.S.T.)
    "face drooping",
    "slurred speech",
    "sudden numbness on one side",
    "sudden weakness on one side",
    "signs of stroke",
    "stroke",

    # Allergic reaction
    "severe allergic reaction",
    "anaphylaxis",
    "throat closing",
    "swelling of face and throat",

    # Bleeding / injury
    "severe bleeding",
    "uncontrolled bleeding",
    "serious injury",
    "deep wound",
    "broken bone visible",
    "head injury with vomiting",

    # Other critical
    "suicidal",
    "want to end my life",
    "severe burns",
    "poisoning",
    "overdose",
    "seizure",
]


def check_emergency(text: str) -> Tuple[bool, List[str]]:
    """
    Check a free-text string (chat message or joined symptom list) for
    emergency keywords.

    Returns:
        (is_emergency, matched_keywords)
    """
    if not text:
        return False, []

    normalized = text.lower()
    matched = [kw for kw in EMERGENCY_KEYWORDS if kw in normalized]
    return (len(matched) > 0), matched


def emergency_message() -> str:
    """Standard safe message shown when an emergency is detected.

    Deliberately does NOT include any treatment instructions — only tells
    the user to seek immediate professional/emergency help.
    """
    return (
        "⚠️ Your message mentions symptoms that could be a medical "
        "emergency. Please seek immediate emergency medical assistance "
        "(call your local emergency number or go to the nearest emergency "
        "room right now). This assistant cannot provide emergency care."
    )
