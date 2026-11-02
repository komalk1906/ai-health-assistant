"""
services/health_knowledge.py
-----------------------------
A small, built-in HEALTH KNOWLEDGE BASE used by ai_service.py whenever no
external AI model is available (no AI_API_KEY configured, or the AI API call
failed).

Why this exists
---------------
Without it, every chat message would get the same generic reply. With it, the
assistant can still give a relevant, safe answer offline:

* match the user's words against ~25 common health topics (fever, headache,
  cold, acidity, sleep, ...) and reply with a short explanation, self-care
  advice and "when to see a doctor" guidance;
* recognise questions about the medicines stored in the database seed data
  and answer from that general information;
* politely refuse dosage questions (the project never gives doses);
* power the rule-based symptom checker (severity + advice).

It is rule/keyword based (no machine learning), so it is fast, free,
predictable and easy to explain in a viva. To add a new topic, just append one
dictionary to TOPICS - no other code needs to change.

IMPORTANT: all content is general, educational information only. It never
diagnoses, never prescribes and never gives medicine doses.
"""

import re
from typing import Dict, List, Optional

from app.database.seed_medicines import SAMPLE_MEDICINES

REMINDER = (
    "Please remember this is general information, not a substitute for "
    "professional medical advice."
)

SEVERITY_ORDER = {"LOW": 0, "MODERATE": 1, "HIGH": 2}

# ---------------------------------------------------------------------------
# TOPICS
# Each topic: keywords to look for, a default severity (for the symptom
# checker), a one-line explanation, safe self-care advice and when to see a
# doctor.
# ---------------------------------------------------------------------------
TOPICS: List[Dict] = [
    {
        "name": "Fever",
        "keywords": ["fever", "feverish", "high temperature", "temperature"],
        "severity": "MODERATE",
        "explanation": "Fever is the body's response to something like a viral or bacterial infection, and it often settles on its own.",
        "advice": "Rest, drink plenty of fluids, wear light clothing and keep track of your temperature.",
        "see_doctor": "See a doctor if the fever is high, lasts more than 2-3 days, or comes with a stiff neck, rash, breathlessness or confusion.",
    },
    {
        "name": "Headache",
        "keywords": ["headache", "head ache", "migraine", "head pain"],
        "severity": "LOW",
        "explanation": "Common causes of headache include tension, dehydration, lack of sleep, eye strain and stress.",
        "advice": "Rest in a quiet, dim room, drink water, and take regular breaks from screens.",
        "see_doctor": "Get medical help if the headache is sudden and severe, follows a head injury, or comes with fever and neck stiffness, vision changes, weakness or confusion.",
    },
    {
        "name": "Cold and flu",
        "keywords": ["cold", "flu", "runny nose", "blocked nose", "stuffy nose", "congestion", "sneezing", "influenza"],
        "severity": "LOW",
        "explanation": "A cold or flu is usually caused by a virus, and most people recover in about a week.",
        "advice": "Rest, drink warm fluids, try steam inhalation or saline nasal rinses, and avoid close contact with others to prevent spreading it.",
        "see_doctor": "See a doctor if you have trouble breathing, chest pain, symptoms lasting more than 10 days, or a fever that keeps coming back.",
    },
    {
        "name": "Cough",
        "keywords": ["cough", "coughing", "dry cough", "wet cough"],
        "severity": "LOW",
        "explanation": "A cough often follows a cold and can also be caused by throat irritation, allergies or acid reflux.",
        "advice": "Stay hydrated, sip warm water or honey-lemon water (honey is not for babies under 1 year), and avoid smoke and dust.",
        "see_doctor": "See a doctor if it lasts more than 2-3 weeks, or you cough up blood or have breathlessness or wheezing.",
    },
    {
        "name": "Sore throat",
        "keywords": ["sore throat", "throat pain", "throat infection", "scratchy throat"],
        "severity": "LOW",
        "explanation": "A sore throat is commonly due to a viral infection, dry air or irritation.",
        "advice": "Gargle with warm salt water, drink warm fluids and rest your voice.",
        "see_doctor": "See a doctor if it lasts more than a week, makes swallowing or breathing difficult, or comes with a high fever.",
    },
    {
        "name": "Stomach ache",
        "keywords": ["stomach ache", "stomach pain", "stomachache", "abdominal pain", "tummy ache", "belly pain", "indigestion", "bloating", "constipation"],
        "severity": "LOW",
        "explanation": "Stomach pain can come from indigestion, gas, constipation, food intolerance or a mild stomach infection.",
        "advice": "Eat light, simple foods, drink fluids, and avoid oily, spicy or heavy meals for a while.",
        "see_doctor": "Seek care if the pain is severe, keeps getting worse, is on the lower right side, or comes with persistent vomiting, fever or blood in the stool.",
    },
    {
        "name": "Diarrhoea",
        "keywords": ["diarrhea", "diarrhoea", "loose motion", "loose stool", "loose motions", "watery stool"],
        "severity": "MODERATE",
        "explanation": "Diarrhoea is often caused by a stomach infection or something you ate, and the main risk is losing too much fluid.",
        "advice": "Sip fluids often, including oral rehydration solution (ORS), and eat light foods like rice, banana or toast.",
        "see_doctor": "See a doctor if it lasts more than 2 days, you see blood, or you feel very weak, dizzy or very thirsty - and sooner for children and older adults.",
    },
    {
        "name": "Nausea and vomiting",
        "keywords": ["vomiting", "vomit", "nausea", "nauseous", "throwing up"],
        "severity": "MODERATE",
        "explanation": "Nausea and vomiting are commonly caused by stomach infections, certain foods, motion sickness or migraine.",
        "advice": "Rest, take small sips of water or ORS, and wait a little before eating - then start with bland food.",
        "see_doctor": "Get medical help if you cannot keep fluids down, vomiting lasts more than a day, or there is blood, severe pain or signs of dehydration.",
    },
    {
        "name": "Acidity and heartburn",
        "keywords": ["acidity", "acid reflux", "heartburn", "gastric", "gerd", "sour belching"],
        "severity": "LOW",
        "explanation": "Acidity happens when stomach acid flows back up towards the food pipe, often after heavy, oily or spicy meals.",
        "advice": "Eat smaller meals, avoid lying down right after eating, and cut back on spicy food, caffeine and fizzy drinks.",
        "see_doctor": "See a doctor if it happens often, causes trouble swallowing, or comes with chest pain, weight loss or black stools.",
    },
    {
        "name": "Allergies",
        "keywords": ["allergy", "allergic", "itching", "itchy", "hay fever", "hives", "dust allergy"],
        "severity": "LOW",
        "explanation": "Allergies happen when the body reacts to triggers such as dust, pollen, pet hair or certain foods.",
        "advice": "Identify and avoid your triggers, keep your surroundings dust-free, and wash your face and hands after being outdoors.",
        "see_doctor": "Get urgent help for swelling of the face or lips or any breathing difficulty; otherwise see a doctor if symptoms keep returning.",
    },
    {
        "name": "Sleep problems",
        "keywords": ["insomnia", "sleep", "sleeping", "cannot sleep", "can't sleep", "trouble sleeping"],
        "severity": "LOW",
        "explanation": "Poor sleep is commonly linked to stress, irregular routines, caffeine and too much screen time at night.",
        "advice": "Keep a fixed sleep and wake time, avoid screens and caffeine before bed, and keep your room dark and cool.",
        "see_doctor": "Talk to a doctor if sleep problems last more than a few weeks or affect your daily life.",
    },
    {
        "name": "Stress and low mood",
        "keywords": ["stress", "stressed", "anxiety", "anxious", "worried", "panic", "low mood", "depressed", "feeling sad", "overwhelmed"],
        "severity": "LOW",
        "explanation": "Feeling stressed, anxious or low is common and can be caused by pressure from studies, work, health or relationships.",
        "advice": "Try slow deep breathing, regular sleep and physical activity, and talk to someone you trust about how you feel.",
        "see_doctor": "If these feelings last for weeks, affect your daily life, or you feel hopeless, please talk to a doctor or mental health professional.",
    },
    {
        "name": "Back and muscle pain",
        "keywords": ["back pain", "backache", "muscle pain", "body ache", "body pain", "neck pain", "joint pain", "sprain", "muscle cramp"],
        "severity": "LOW",
        "explanation": "Back and muscle pain commonly come from poor posture, long periods of sitting, muscle strain or overexertion.",
        "advice": "Stay gently active, avoid sitting for long stretches, improve your posture and try a warm compress.",
        "see_doctor": "See a doctor if the pain is severe, follows an injury, spreads down the leg, or comes with numbness, weakness or loss of bladder control.",
    },
    {
        "name": "Diabetes",
        "keywords": ["diabetes", "diabetic", "blood sugar", "sugar level", "high sugar"],
        "severity": "MODERATE",
        "explanation": "Diabetes is a condition where blood sugar stays too high, and it is managed through diet, activity, regular checks and medication when prescribed.",
        "advice": "Eat balanced meals with less sugar and refined carbohydrates, stay active and keep up regular check-ups.",
        "see_doctor": "Always follow your doctor's plan, and see a doctor if you notice extreme thirst, frequent urination, unexplained weight loss or blurry vision.",
    },
    {
        "name": "Blood pressure",
        "keywords": ["blood pressure", "bp", "hypertension", "high bp", "low bp"],
        "severity": "MODERATE",
        "explanation": "Blood pressure is the force of blood on your artery walls; it is influenced by salt intake, weight, stress and activity.",
        "advice": "Reduce salt, stay active, manage stress, avoid smoking, and have your blood pressure checked regularly.",
        "see_doctor": "See a doctor for repeated high or low readings, and get urgent help for a severe headache, chest pain or fainting.",
    },
    {
        "name": "Healthy diet",
        "keywords": ["diet", "nutrition", "healthy food", "weight loss", "lose weight", "balanced diet", "protein", "vitamin", "healthy eating"],
        "severity": "LOW",
        "explanation": "A balanced diet includes vegetables, fruit, whole grains, protein and healthy fats in sensible portions.",
        "advice": "Eat regular meals, limit sugary and fried foods, drink enough water, and avoid crash diets.",
        "see_doctor": "A doctor or dietitian can suggest a plan that fits you, especially if you have a medical condition.",
    },
    {
        "name": "Exercise",
        "keywords": ["exercise", "workout", "fitness", "gym", "yoga", "walking"],
        "severity": "LOW",
        "explanation": "Regular physical activity supports the heart, mood, sleep and healthy weight.",
        "advice": "Aim for around 150 minutes of moderate activity a week, such as brisk walking, and build up gradually.",
        "see_doctor": "Check with a doctor before starting hard exercise if you have a heart, lung or joint condition.",
    },
    {
        "name": "Hydration",
        "keywords": ["water intake", "hydration", "dehydrated", "dehydration", "thirsty", "drink water", "drinking water", "how much water", "enough water"],
        "severity": "LOW",
        "explanation": "Water helps regulate temperature, digestion and energy, and your needs rise in hot weather or when exercising.",
        "advice": "Sip water through the day; pale-yellow urine is a good sign that you are drinking enough.",
        "see_doctor": "Get medical help for signs of severe dehydration such as confusion, very dark urine, no urination or fainting.",
    },
    {
        "name": "Period pain",
        "keywords": ["period pain", "menstrual", "menstruation", "period cramps", "periods", "irregular periods"],
        "severity": "LOW",
        "explanation": "Period cramps are caused by the uterus contracting and are common, especially in the first days.",
        "advice": "A warm compress, light exercise, rest and staying hydrated can ease the discomfort.",
        "see_doctor": "See a doctor if the pain is severe, periods are very heavy or irregular, or the pain disrupts your daily life.",
    },
    {
        "name": "Minor cuts and burns",
        "keywords": ["minor cut", "cut my", "wound", "minor burn", "burned my", "burnt my", "scald", "bruise"],
        "severity": "LOW",
        "explanation": "Minor cuts, bruises and burns can usually be treated at home with basic first aid.",
        "advice": "Rinse a cut with clean running water and cover it with a clean bandage; cool a minor burn under cool running water for several minutes.",
        "see_doctor": "Get medical care for deep or bleeding wounds, large or blistering burns, or signs of infection such as spreading redness or pus.",
    },
    {
        "name": "Skin problems",
        "keywords": ["acne", "pimple", "pimples", "rash", "skin", "dandruff"],
        "severity": "LOW",
        "explanation": "Skin problems such as acne or rashes are often related to hormones, hygiene, allergies or irritation.",
        "advice": "Wash gently, avoid squeezing pimples, use mild products, and avoid scratching a rash.",
        "see_doctor": "See a doctor or dermatologist if it spreads, is painful, keeps returning, or comes with fever.",
    },
    {
        "name": "Toothache",
        "keywords": ["toothache", "tooth pain", "dental", "gum pain", "gums"],
        "severity": "LOW",
        "explanation": "Tooth pain is commonly due to cavities, gum problems or sensitivity.",
        "advice": "Rinse with warm salt water, brush gently, and avoid very hot or very cold foods.",
        "see_doctor": "See a dentist soon, especially if there is swelling, fever, or pain lasting more than a day or two.",
    },
    {
        "name": "Tiredness",
        "keywords": ["tired", "tiredness", "fatigue", "weakness", "low energy", "weak"],
        "severity": "LOW",
        "explanation": "Tiredness is often caused by poor sleep, stress, an unbalanced diet, low iron or an ongoing infection.",
        "advice": "Keep regular sleep hours, eat balanced meals, drink water and stay lightly active.",
        "see_doctor": "See a doctor if tiredness lasts for weeks or comes with weight change, dizziness or shortness of breath.",
    },
    {
        "name": "Dizziness",
        "keywords": ["dizzy", "dizziness", "lightheaded", "light headed", "vertigo"],
        "severity": "MODERATE",
        "explanation": "Dizziness can happen from dehydration, low blood sugar, standing up too quickly, or inner-ear problems.",
        "advice": "Sit or lie down, sip some water, and get up slowly.",
        "see_doctor": "Get urgent help if dizziness comes with chest pain, fainting, weakness, slurred speech or a severe headache.",
    },
    {
        "name": "Eye strain",
        "keywords": ["eye strain", "eyestrain", "dry eyes", "watery eyes", "red eyes", "eye pain", "blurred vision", "screen time"],
        "severity": "LOW",
        "explanation": "Eye strain and dryness are common with long hours of screen use.",
        "advice": "Follow the 20-20-20 rule - every 20 minutes, look at something 20 feet away for 20 seconds - and blink often.",
        "see_doctor": "See an eye doctor for sudden vision changes, eye pain or persistent redness.",
    },
]

# Words/phrases that suggest the situation may be more serious than usual.
HIGH_FLAGS = [
    "blood in", "bloody", "coughing blood", "vomiting blood", "black stool",
    "worst headache", "stiff neck", "high fever", "can't keep", "cannot keep",
    "confused", "confusion", "unbearable",
]
MODERATE_FLAGS = [
    "severe", "getting worse", "worse", "for days", "for a week", "for weeks",
    "more than a week", "persistent", "keeps coming back", "not improving",
]

# Brand / alternative names that map to a medicine in the database seed data.
MEDICINE_ALIASES = {
    "acetaminophen": "Paracetamol",
    "crocin": "Paracetamol",
    "dolo": "Paracetamol",
    "brufen": "Ibuprofen",
    "zyrtec": "Cetirizine",
    "ors": "Oral Rehydration Salts",
    "vitamin d": "Vitamin D3",
    "ventolin": "Salbutamol",
}

# Clear dosage wording - always refused.
_DOSAGE_STRONG = re.compile(
    r"\b(dose|doses|dosage|milligrams?|\d+\s?(?:mg|ml)|mg|ml|how many (?:tablets?|pills?|capsules?))\b"
)
# Vaguer wording ("how much", "how often") only counts as a dosage question
# when a medicine is mentioned - "how much water should I drink?" is fine.
_DOSAGE_WEAK = re.compile(r"\b(how much|how often|how frequently|how long can i take)\b")
_MEDICINE_WORDS = re.compile(r"\b(medicine|medicines|medication|tablet|tablets|pill|pills|capsule|capsules|syrup)\b")
_GREETING_PATTERN = re.compile(r"^\s*(hi|hello|hey|hii+|good (?:morning|afternoon|evening)|namaste)\b")
_THANKS_PATTERN = re.compile(r"\b(thanks|thank you|thx)\b")
_BYE_PATTERN = re.compile(r"\b(bye|goodbye|see you)\b")
_ABOUT_PATTERN = re.compile(r"\b(who are you|what can you do|help me|what do you do)\b")


# ---------------------------------------------------------------------------
# Matching helpers
# ---------------------------------------------------------------------------

def match_topics(text: str, limit: int = 2) -> List[Dict]:
    """
    Return up to `limit` topics whose keywords appear in `text`.
    Topics with more keyword hits come first; ties are ordered by where the
    topic first appears in the user's sentence.
    """
    normalized = (text or "").lower()
    scored = []
    for topic in TOPICS:
        hits = 0
        first_pos = len(normalized) + 1
        for kw in topic["keywords"]:
            match = re.search(r"\b" + re.escape(kw) + r"(?:s|es|ing)?\b", normalized)
            if match:
                hits += 1
                first_pos = min(first_pos, match.start())
        if hits:
            scored.append((-hits, first_pos, topic))
    scored.sort(key=lambda item: (item[0], item[1]))
    return [topic for _, _, topic in scored[:limit]]


def find_medicine(text: str) -> Optional[Dict]:
    """Return the seed-data record of a medicine mentioned in `text`, if any."""
    normalized = (text or "").lower()
    for alias, real_name in MEDICINE_ALIASES.items():
        if re.search(r"\b" + re.escape(alias) + r"\b", normalized):
            normalized += " " + real_name.lower()
    for medicine in SAMPLE_MEDICINES:
        if re.search(r"\b" + re.escape(medicine["name"].lower()) + r"\b", normalized):
            return medicine
    return None


def red_flag_level(text: str) -> Optional[str]:
    """Return 'HIGH', 'MODERATE' or None depending on warning words in `text`."""
    normalized = (text or "").lower()
    if any(flag in normalized for flag in HIGH_FLAGS):
        return "HIGH"
    if any(flag in normalized for flag in MODERATE_FLAGS):
        return "MODERATE"
    return None


# ---------------------------------------------------------------------------
# Reply builders
# ---------------------------------------------------------------------------

def _medicine_reply(medicine: Dict) -> str:
    return (
        f"{medicine['name']} - general information\n"
        f"- Common uses: {medicine['common_uses']}\n"
        f"- Precautions: {medicine['precautions']}\n"
        f"- Possible side effects: {medicine['side_effects']}\n"
        f"- Warnings: {medicine['warnings']}\n"
        f"- {medicine['seek_professional_advice']}\n\n"
        "I can't tell you how much to take or how often - please follow the "
        "label or your doctor's prescription. " + REMINDER
    )


def build_chat_reply(user_message: str, profile_context: Optional[str] = None) -> Optional[str]:
    """
    Build a reply from the knowledge base, or return None if nothing matches
    (the caller then shows a generic 'tell me more' message).
    """
    text = (user_message or "").lower()
    medicine = find_medicine(text)

    # 1. Dosage questions are never answered - safety rule of the project.
    is_dosage_question = bool(_DOSAGE_STRONG.search(text)) or (
        bool(_DOSAGE_WEAK.search(text)) and (medicine is not None or bool(_MEDICINE_WORDS.search(text)))
    )
    if is_dosage_question:
        who = f" for {medicine['name']}" if medicine else ""
        return (
            f"I'm not able to recommend doses{who}, or how much or how often to "
            "take any medicine, because the right amount depends on your age, "
            "weight, health conditions and other medicines. Please follow the "
            "instructions on the label or your doctor's prescription, or ask a "
            "pharmacist. " + REMINDER
        )

    # 2. Questions about a medicine stored in our database.
    if medicine:
        reply = _medicine_reply(medicine)
        if profile_context:
            reply += (
                "\n\nSince your health profile lists allergies, conditions or "
                "current medications, please check with a doctor or pharmacist "
                "before using any medicine."
            )
        return reply

    # 3. Health topics.
    topics = match_topics(text)
    if topics:
        blocks = []
        for topic in topics:
            blocks.append(
                f"{topic['name']}: {topic['explanation']} {topic['advice']} {topic['see_doctor']}"
            )
        reply = "\n\n".join(blocks)

        level = red_flag_level(text)
        if level == "HIGH":
            reply = (
                "Some of the details you mentioned can be warning signs, so "
                "please see a doctor soon rather than waiting it out.\n\n" + reply
            )
        return reply + "\n\n" + REMINDER

    # 4. Small talk.
    if _GREETING_PATTERN.search(text):
        return (
            "Hello! I'm your AI Health Assistant. You can tell me how you're "
            "feeling (for example \"I have a headache and mild fever\"), ask "
            "about a common medicine, or ask for general health tips."
        )
    if _THANKS_PATTERN.search(text):
        return "You're welcome! Take care, and let me know if you have any other health questions."
    if _BYE_PATTERN.search(text):
        return "Goodbye! Stay healthy, and see a doctor if you ever feel unwell for long."
    if _ABOUT_PATTERN.search(text):
        return (
            "I'm an AI Health Assistant that shares general health information. "
            "I can talk about common symptoms (fever, cold, headache, stomach "
            "problems and more), explain common medicines, and give everyday "
            "health tips on sleep, diet, exercise and hydration. I can't "
            "diagnose illnesses or prescribe medicines."
        )

    return None


def build_symptom_analysis(symptoms: List[str]) -> Optional[Dict]:
    """
    Rule-based symptom analysis. Returns the same dict shape as the AI path
    (severity / possible_explanations / advice / professional_attention_recommended),
    or None when none of the symptoms are recognised.
    """
    combined = ", ".join(symptoms).lower()
    topics = match_topics(combined, limit=3)
    if not topics:
        return None

    severity = "LOW"
    for topic in topics:
        if SEVERITY_ORDER[topic["severity"]] > SEVERITY_ORDER[severity]:
            severity = topic["severity"]

    # Several symptoms together deserve a bit more caution.
    if len(topics) >= 2 and severity == "LOW":
        severity = "MODERATE"

    level = red_flag_level(combined)
    if level and SEVERITY_ORDER[level] > SEVERITY_ORDER[severity]:
        severity = level

    explanation = " ".join(topic["explanation"] for topic in topics)
    advice = " ".join(topic["advice"] for topic in topics)
    see_doctor = topics[0]["see_doctor"]
    if severity == "HIGH":
        see_doctor = (
            "Some details you listed can be warning signs - please see a doctor "
            "soon. " + see_doctor
        )

    return {
        "severity": severity,
        "possible_explanations": explanation,
        "advice": advice + " " + see_doctor,
        "professional_attention_recommended": severity != "LOW",
    }
