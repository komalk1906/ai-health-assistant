"""
seed_medicines.py
------------------
Inserts a small set of sample medicine records into the `medicines` table
so the /api/medicines/{name} endpoint has data to return out of the box.

Run automatically at startup (see app/main.py) — it only inserts medicines
that are not already in the table, so it's safe to run every time the app
starts without creating duplicates.

IMPORTANT: This information is intentionally general and educational only.
It is sample data for a college mini project, NOT verified medical
reference data, and must never be used for real medical decisions.
"""

from sqlalchemy.orm import Session
from app.database.models import Medicine

SAMPLE_MEDICINES = [
    {
        "name": "Paracetamol",
        "common_uses": "Relief of mild to moderate pain and reducing fever.",
        "precautions": "Avoid exceeding the recommended daily limit; use caution with liver conditions or alcohol use.",
        "side_effects": "Generally well tolerated; rare side effects include nausea or allergic skin reactions.",
        "warnings": "Overdose can cause serious liver damage. Do not combine multiple products containing paracetamol.",
        "seek_professional_advice": "Consult a doctor or pharmacist before use if pregnant, on other medications, or if symptoms persist beyond a few days.",
    },
    {
        "name": "Ibuprofen",
        "common_uses": "Relief of pain, inflammation, and fever (an NSAID).",
        "precautions": "Take with food; use caution with a history of stomach ulcers, kidney issues, or asthma.",
        "side_effects": "Stomach upset, heartburn, dizziness in some users.",
        "warnings": "Not recommended for long-term use without medical supervision; avoid in late pregnancy.",
        "seek_professional_advice": "Consult a doctor before use if you have kidney disease, heart conditions, or are on blood thinners.",
    },
    {
        "name": "Cetirizine",
        "common_uses": "Relief of allergy symptoms such as sneezing, itching, and runny nose.",
        "precautions": "May cause mild drowsiness in some people; use caution when driving.",
        "side_effects": "Drowsiness, dry mouth, headache.",
        "warnings": "Use caution in people with kidney impairment; consult a doctor for children's dosing.",
        "seek_professional_advice": "Consult a doctor or pharmacist if allergy symptoms are severe or persistent.",
    },
    {
        "name": "Amoxicillin",
        "common_uses": "An antibiotic used for certain bacterial infections (prescription only).",
        "precautions": "Only to be used exactly as prescribed by a doctor; complete the full course.",
        "side_effects": "Nausea, diarrhea, allergic skin reactions.",
        "warnings": "Do not use without a prescription. Serious allergic reactions are possible in penicillin-sensitive individuals.",
        "seek_professional_advice": "This is a prescription medicine — always consult a doctor before use; never self-prescribe antibiotics.",
    },
    {
        "name": "Omeprazole",
        "common_uses": "Reduces stomach acid; used for heartburn, acid reflux, and related conditions.",
        "precautions": "Best taken before a meal; long-term use should be supervised by a doctor.",
        "side_effects": "Headache, stomach pain, nausea.",
        "warnings": "Long-term use has been associated with certain nutrient deficiencies; discuss with a doctor for extended use.",
        "seek_professional_advice": "Consult a doctor if symptoms persist beyond two weeks of use.",
    },
    {
        "name": "Oral Rehydration Salts",
        "common_uses": "Replaces fluids and salts lost during diarrhoea, vomiting or heavy sweating.",
        "precautions": "Mix only with the amount of clean water stated on the packet and use the prepared solution within the time given on the pack.",
        "side_effects": "Rarely, nausea or bloating, especially if the solution is made too concentrated.",
        "warnings": "Do not add extra salt or sugar. It is not a substitute for medical care in severe dehydration.",
        "seek_professional_advice": "Seek medical help for persistent vomiting, blood in stool, extreme weakness or no improvement; take extra care with infants and older adults.",
    },
    {
        "name": "Aspirin",
        "common_uses": "Pain relief, fever reduction and, on a doctor's advice, lowering the risk of blood clots.",
        "precautions": "Take with food; avoid if you have stomach ulcers, bleeding disorders or asthma triggered by painkillers.",
        "side_effects": "Stomach irritation, heartburn, easy bruising.",
        "warnings": "Should not be given to children or teenagers with viral illness because of the risk of Reye's syndrome. Increases bleeding risk.",
        "seek_professional_advice": "Consult a doctor before use if you take blood thinners, have ulcers, are pregnant, or are planning surgery.",
    },
    {
        "name": "Loratadine",
        "common_uses": "Relief of allergy symptoms such as sneezing, runny nose and itchy eyes, usually with less drowsiness.",
        "precautions": "Use caution if you have liver or kidney problems.",
        "side_effects": "Headache, dry mouth, tiredness.",
        "warnings": "Not a treatment for severe allergic reactions (anaphylaxis), which need emergency care.",
        "seek_professional_advice": "Consult a pharmacist or doctor before use in children, during pregnancy, or if symptoms last more than a couple of weeks.",
    },
    {
        "name": "Azithromycin",
        "common_uses": "A prescription antibiotic for certain bacterial infections of the chest, throat, ear and skin.",
        "precautions": "Take exactly as prescribed and complete the course; tell your doctor about heart rhythm problems or other medicines you take.",
        "side_effects": "Nausea, loose stools, stomach pain.",
        "warnings": "Antibiotics do not work against viral infections such as colds and flu. Never self-medicate. Stop and seek help if a rash or swelling occurs.",
        "seek_professional_advice": "Prescription medicine - use only under a doctor's guidance.",
    },
    {
        "name": "Metformin",
        "common_uses": "A prescription medicine used to help control blood sugar in type 2 diabetes.",
        "precautions": "Take as prescribed, usually with meals; regular blood tests may be needed.",
        "side_effects": "Nausea, loose stools, metallic taste, stomach discomfort.",
        "warnings": "Rarely can cause a serious build-up of lactic acid; people with kidney problems or heavy alcohol use need medical supervision.",
        "seek_professional_advice": "Prescription medicine - never start, stop or change it without your doctor.",
    },
    {
        "name": "Pantoprazole",
        "common_uses": "Reduces stomach acid; used for acid reflux, heartburn and stomach ulcers.",
        "precautions": "Usually taken before a meal as directed; long-term use needs medical review.",
        "side_effects": "Headache, nausea, stomach discomfort, loose stools.",
        "warnings": "Long-term use may reduce absorption of some nutrients such as magnesium and vitamin B12.",
        "seek_professional_advice": "Consult a doctor if symptoms continue beyond two weeks, or if you have trouble swallowing, weight loss or black stools.",
    },
    {
        "name": "Salbutamol",
        "common_uses": "A reliever inhaler that opens the airways, used for asthma and wheezing.",
        "precautions": "Learn the correct inhaler technique from a doctor or pharmacist.",
        "side_effects": "Shaky hands, fast heartbeat, headache.",
        "warnings": "Needing it more often than usual can mean asthma is poorly controlled. Severe breathlessness is an emergency.",
        "seek_professional_advice": "Prescription use - see a doctor if you need your reliever more often than before.",
    },
    {
        "name": "Diclofenac",
        "common_uses": "Relief of pain and inflammation, for example in joint, muscle and back pain (an NSAID).",
        "precautions": "Take with food; use caution with stomach ulcers, or kidney, liver or heart problems.",
        "side_effects": "Stomach upset, heartburn, dizziness.",
        "warnings": "Not for long-term use without medical supervision; may raise heart and bleeding risks. Avoid in late pregnancy.",
        "seek_professional_advice": "Consult a doctor before use if you have heart disease, kidney disease, ulcers, or take blood thinners.",
    },
    {
        "name": "Dextromethorphan",
        "common_uses": "Temporary relief of a dry, irritating cough (a cough suppressant).",
        "precautions": "Not suitable for a cough with phlegm; check labels so you do not double up on cough and cold products.",
        "side_effects": "Drowsiness, dizziness, nausea.",
        "warnings": "Should not be combined with certain antidepressants (MAOIs). Misuse can be dangerous. Not for young children.",
        "seek_professional_advice": "Consult a doctor if the cough lasts more than a week, or comes with fever, rash or breathlessness.",
    },
    {
        "name": "Ondansetron",
        "common_uses": "A prescription medicine to prevent or reduce nausea and vomiting.",
        "precautions": "Tell your doctor about heart rhythm problems or other medicines you take.",
        "side_effects": "Headache, constipation, tiredness.",
        "warnings": "Can affect heart rhythm in some people. Vomiting that does not stop needs medical assessment.",
        "seek_professional_advice": "Prescription medicine - use only as directed by a doctor.",
    },
    {
        "name": "Loperamide",
        "common_uses": "Short-term relief of loose stools in simple diarrhoea in adults.",
        "precautions": "Drink plenty of fluids or oral rehydration solution alongside it.",
        "side_effects": "Constipation, bloating, dizziness.",
        "warnings": "Do not use if there is blood in the stool or a high fever, or in young children. It is not a replacement for rehydration.",
        "seek_professional_advice": "See a doctor if diarrhoea lasts more than 2 days, or if there is blood or fever.",
    },
    {
        "name": "Antacid",
        "common_uses": "Quick, short-term relief of heartburn, acidity and indigestion (for example aluminium or magnesium hydroxide).",
        "precautions": "Use as per the label, usually after meals; antacids can affect absorption of other medicines, so space them apart.",
        "side_effects": "Constipation or loose stools depending on the type, chalky taste.",
        "warnings": "Use caution with kidney problems. Needing antacids often should be checked by a doctor.",
        "seek_professional_advice": "See a doctor if you need antacids regularly, or have chest pain, trouble swallowing or weight loss.",
    },
    {
        "name": "Vitamin D3",
        "common_uses": "Supports bone and muscle health; used when vitamin D levels are low.",
        "precautions": "Take only as advised by a doctor, ideally after a blood test, because too much can be harmful.",
        "side_effects": "Usually none at normal levels; excess may cause nausea, constipation or high calcium.",
        "warnings": "Excess intake can lead to dangerously high calcium levels.",
        "seek_professional_advice": "Ask a doctor before taking supplements if you have kidney disease or take other medicines.",
    },
    {
        "name": "Amlodipine",
        "common_uses": "A prescription medicine used to lower high blood pressure and prevent certain types of chest pain.",
        "precautions": "Take at the same time each day; do not stop suddenly without medical advice.",
        "side_effects": "Ankle swelling, flushing, headache, tiredness.",
        "warnings": "Do not stop it on your own. Dizziness may occur when standing up quickly.",
        "seek_professional_advice": "Prescription medicine - blood pressure treatment should be guided by a doctor.",
    },
    {
        "name": "Atorvastatin",
        "common_uses": "A prescription medicine used to lower cholesterol and reduce the risk of heart disease.",
        "precautions": "Usually taken together with a healthy diet; periodic blood tests may be advised.",
        "side_effects": "Muscle aches, headache, stomach upset.",
        "warnings": "Report unexplained muscle pain, weakness or dark urine to your doctor. Not for use in pregnancy.",
        "seek_professional_advice": "Prescription medicine - use only under a doctor's supervision.",
    },
]


def seed_medicines(db: Session) -> None:
    """Insert any sample medicines that are not in the table yet.

    We check each medicine BY NAME (case-insensitive) instead of only checking
    whether the table is empty. That way, when new medicines are added to
    SAMPLE_MEDICINES later, an existing database receives them on the next
    startup, and medicines that are already present are never duplicated or
    overwritten.
    """
    existing_names = {name.lower() for (name,) in db.query(Medicine.name).all()}

    added = False
    for item in SAMPLE_MEDICINES:
        if item["name"].lower() not in existing_names:
            db.add(Medicine(**item))
            added = True

    if added:
        db.commit()
