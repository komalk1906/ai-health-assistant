# AI Health Assistant — Backend

A FastAPI backend for a **TYBSc Computer Science mini project**: an AI-powered
general health information assistant with user authentication, health
profiles, an AI chat assistant, a rule-based emergency detector, a symptom
checker, medicine information, and per-user health history.

> ⚠️ **Disclaimer:** This project provides *general health information* for
> educational purposes only. It is **not a substitute for professional
> medical advice, diagnosis, or treatment**, and must never be used for real
> medical decisions.

---

## 1. Project Description

The AI Health Assistant lets a registered user:

- Sign up / log in securely (JWT + bcrypt password hashing)
- Maintain a personal health profile (height, weight, allergies, etc.)
- Chat with an AI assistant about how they're feeling
- Run a structured symptom checker (severity + advice)
- Look up general information about common medicines
- View a history of all their AI/health activity

A **rule-based emergency detector** runs before every AI call so that
dangerous symptoms (e.g. "severe chest pain", "loss of consciousness") are
caught deterministically and always trigger a safe "seek emergency care"
message — regardless of what the AI model would have said.

---

## 2. Features

| Feature | Endpoint(s) |
|---|---|
| User registration & login (JWT) | `POST /api/auth/register`, `POST /api/auth/login` |
| Get current user / logout | `GET /api/auth/me`, `POST /api/auth/logout` |
| Health profile CRUD | `POST/GET/PUT /api/health/profile` |
| AI chat assistant | `POST /api/chat` |
| Symptom checker | `POST /api/symptoms/check` |
| Emergency detection | (internal safety layer used by chat + symptoms) |
| Medicine information | `GET /api/medicines` (list / `?search=`), `GET /api/medicines/{medicine_name}` |
| Health history | `GET /api/history`, `GET /api/history/{id}` |

---

## 3. Technology Stack

- **Python 3.10+**
- **FastAPI** — REST API framework
- **SQLite** — file-based database (via SQLAlchemy)
- **SQLAlchemy** — ORM
- **Pydantic v2** — request/response validation
- **python-jose** — JWT creation/verification
- **passlib + bcrypt** — password hashing
- **openai (Python SDK)** — talks to any OpenAI-compatible AI API
- **Uvicorn** — ASGI development server
- **pytest + httpx** — automated testing

---

## 4. System Architecture

```
Client (browser / Postman / frontend)
        │  HTTP + JSON (Bearer JWT)
        ▼
   FastAPI app (app/main.py)
        │
        ├── routes/        → HTTP endpoints, request/response only
        ├── schemas/        → Pydantic request/response validation
        ├── services/       → business logic (AI calls, emergency rules)
        ├── utils/          → security (JWT, bcrypt), shared dependencies
        └── database/       → SQLAlchemy models + SQLite connection
```

**Design principle:** routes stay thin (validate → call service/DB → return).
All AI logic lives in `services/ai_service.py`, and all emergency-keyword
logic lives in `services/emergency_detection.py` — this separation is what
makes the project modular and easy to explain in a viva.

### Request flow example — `POST /api/chat`

```
1. Client sends {"message": "..."} with Authorization: Bearer <token>
2. get_current_user dependency verifies the JWT → identifies the user
3. emergency_detection.check_emergency() scans the message
4.   if emergency  → return safe emergency message (no AI call)
5.   else          → build health-profile context → call ai_service.get_ai_response()
6. Save the exchange to `chat_messages`
7. Log a summary row to `health_history`
8. Return { ai_response, is_emergency, disclaimer }
```

---

## 5. Database Design

SQLite file: `health_assistant.db` (created automatically on first run).

| Table | Purpose |
|---|---|
| `users` | Account/login info (never stores plain-text passwords) |
| `health_profiles` | One-to-one extra health details per user |
| `chat_messages` | Every AI chat exchange |
| `symptom_checks` | Every symptom-checker request + result |
| `medicines` | Reference/sample medicine info (seeded on startup) |
| `health_history` | Unified activity log (chat / symptom check / profile update) |

### Relationships

```
User (1) ────── (1) HealthProfile
User (1) ────── (∞) ChatMessage
User (1) ────── (∞) SymptomCheck
User (1) ────── (∞) HealthHistory
Medicine        (independent lookup table, no FK to User)
```

All child tables reference `users.id` via a `ForeignKey`, and
`cascade="all, delete-orphan"` on the `User` relationships means deleting a
user cleans up all their related rows automatically.

---

## 6. Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Steps

```bash
# 1. Clone / unzip the project, then move into it
cd backend

# 2. (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env if you want to add a real AI_API_KEY (optional — see below)
```

---

## 7. Environment Variables

Copy `.env.example` to `.env` and adjust as needed:

```env
DATABASE_URL=sqlite:///./health_assistant.db
SECRET_KEY=replace-this-with-a-long-random-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

AI_API_KEY=
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini
```

- **`SECRET_KEY`** — used to sign JWT tokens. Generate a strong one with
  `openssl rand -hex 32`.
- **`AI_API_KEY`** — your OpenAI-compatible API key. **If left empty, the
  project still runs fully** — `ai_service.py` returns safe, clearly-labeled
  fallback responses instead of calling a real AI model. This means you can
  demo and test the entire project (including the viva) without paying for
  API access.

**Never commit your real `.env` file.** Only `.env.example` (no real
secrets) should be committed to version control.

---

## 8. Running the Backend

```bash
uvicorn app.main:app --reload
```

or simply:

```bash
python run.py
```

The API will be available at:
- **Root:** http://127.0.0.1:8000/
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

On startup, the app automatically creates all tables and adds any missing
records to the `medicines` table (20 common medicines of general, educational
information; existing rows are never duplicated or overwritten).

---

## 9. API Endpoint List

### Authentication (`/api/auth`)
| Method | Path | Auth? | Description |
|---|---|---|---|
| POST | `/api/auth/register` | No | Create account, returns JWT |
| POST | `/api/auth/login` | No | Log in, returns JWT |
| GET | `/api/auth/me` | Yes | Get current user |
| POST | `/api/auth/logout` | Yes | Stateless logout notice |

### Health Profile (`/api/health`)
| Method | Path | Auth? | Description |
|---|---|---|---|
| POST | `/api/health/profile` | Yes | Create your health profile |
| GET | `/api/health/profile` | Yes | View your health profile |
| PUT | `/api/health/profile` | Yes | Update your health profile |

### AI Chat
| Method | Path | Auth? | Description |
|---|---|---|---|
| POST | `/api/chat` | Yes | Chat with the AI health assistant |

### Symptom Checker
| Method | Path | Auth? | Description |
|---|---|---|---|
| POST | `/api/symptoms/check` | Yes | Analyze a list of symptoms |

### Medicines
| Method | Path | Auth? | Description |
|---|---|---|---|
| GET | `/api/medicines` | Yes | List all medicines (A-Z); optional `?search=text` filters by name |
| GET | `/api/medicines/{name}` | Yes | General info about one medicine |

### History
| Method | Path | Auth? | Description |
|---|---|---|---|
| GET | `/api/history` | Yes | List your activity history |
| GET | `/api/history/{id}` | Yes | View one history entry |

All authenticated routes require the header:
```
Authorization: Bearer <your_jwt_access_token>
```

---

## 10. Example Requests & Responses

### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "full_name": "Asha Patil",
  "email": "asha@example.com",
  "password": "StrongPass123",
  "age": 21,
  "gender": "Female"
}
```
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "full_name": "Asha Patil",
    "email": "asha@example.com",
    "age": 21,
    "gender": "Female",
    "created_at": "2026-09-27T08:34:47"
  }
}
```

### Chat
```http
POST /api/chat
Authorization: Bearer <token>
Content-Type: application/json

{ "message": "I have a headache and mild fever." }
```
```json
{
  "ai_response": "Headaches with mild fever are often linked to common causes like viral infections or fatigue. Resting, staying hydrated, and monitoring your temperature can help. If symptoms worsen or persist beyond a couple of days, please see a doctor.",
  "is_emergency": false,
  "disclaimer": "This AI Health Assistant provides general health information and is not a substitute for professional medical advice."
}
```

### Symptom Checker (emergency case)
```http
POST /api/symptoms/check
Authorization: Bearer <token>
Content-Type: application/json

{ "symptoms": ["severe chest pain", "loss of consciousness"] }
```
```json
{
  "symptoms": ["severe chest pain", "loss of consciousness"],
  "possible_explanations": "The symptoms you described may indicate a medical emergency.",
  "severity": "HIGH",
  "advice": "Do not wait — seek emergency medical help immediately.",
  "professional_attention_recommended": true,
  "is_emergency": true,
  "emergency_message": "⚠️ Your message mentions symptoms that could be a medical emergency. Please seek immediate emergency medical assistance...",
  "disclaimer": "This result is general health information generated by an AI assistant. It is not a medical diagnosis."
}
```

### Error example — wrong password
```json
{ "detail": "Incorrect email or password." }
```

### Error example — validation failure
```json
{
  "error": "Validation error",
  "details": [
    { "loc": ["body", "symptoms"], "msg": "List should have at least 1 item", "type": "too_short" }
  ]
}
```

---

## 11. Testing

Tests use **pytest** + FastAPI's `TestClient`, against an isolated SQLite
test database (`test_health_assistant.db`), so they never touch your real
data.

```bash
pip install -r requirements.txt   # httpx & pytest already included
pytest tests/ -v
```

Test files:
- `test_auth.py` — registration, login, duplicate email, wrong password, protected routes
- `test_health_profile.py` — create/view/update profile, duplicate profile, not-found
- `test_chat.py` — normal chat, emergency detection, validation, auth requirement
- `test_symptoms.py` — normal check, emergency check, validation, auth requirement
- `test_medicines.py` — found, case-insensitive, not-found, auth requirement
- `test_history.py` — listing, not-found, and **cross-user access denial**
- `test_knowledge_base.py` — offline chat answers, medicine questions, dosage refusal, rule-based symptom severity, medicine list/search

All 42 tests should pass:
```
======================= 42 passed in ~12s =======================
```

---

## 12. Security Notes (for the viva)

- Passwords are hashed with **bcrypt** (`passlib`) — never stored in plain text.
- Login uses the **same error message** for "no such user" and "wrong
  password" to avoid leaking which emails are registered.
- **JWT** tokens are signed with `SECRET_KEY` (from `.env`) and expire after
  `ACCESS_TOKEN_EXPIRE_MINUTES`.
- Every protected route uses the `get_current_user` FastAPI dependency —
  there is no way to pass another user's ID, so **users can only ever
  access their own health data** (enforced at the query level with
  `WHERE user_id = current_user.id`).
- API keys and secrets are loaded from `.env` via `python-dotenv` — never
  hard-coded in source.
- Input is validated by Pydantic before it ever reaches business logic.
- A global exception handler catches validation and database errors and
  returns clean JSON instead of raw stack traces.

---

## 13. AI Safety Design

Two layers work together:

1. **Rule-based emergency detection** (`services/emergency_detection.py`) —
   a simple keyword list checked *before* any AI call. Deterministic and
   instant. Easily extendable — just add more strings to
   `EMERGENCY_KEYWORDS`.
2. **AI system prompt** (`services/ai_service.py`) — instructs the AI model
   to never diagnose with certainty, never prescribe medication, always
   recommend professional care when appropriate, and always include the
   safety disclaimer.

If no `AI_API_KEY` is configured, or the AI API call fails, the service
answers from a **built-in health knowledge base** instead of crashing —
this satisfies the "AI API failure" error-handling requirement and keeps
the project demoable without a paid API key.

### Built-in knowledge base (`services/health_knowledge.py`)

A keyword-based (no machine learning) module with ~25 common health topics
(fever, headache, cold, cough, stomach problems, acidity, sleep, stress,
diet, exercise, ...). For each topic it holds a short explanation, safe
self-care advice and "when to see a doctor" guidance. It is used to:

- answer **chat** messages (matching up to two topics per message);
- answer questions about any of the 20 **medicines** (brand names such as
  "Crocin" or "Dolo" map to Paracetamol);
- **refuse dosage questions** ("how many mg...") — the project never gives doses;
- power the **symptom checker** severity (LOW / MODERATE / HIGH), raised
  automatically when warning phrases such as "blood in stool" appear;
- reply with a generic "tell me more" message for anything it does not know.

Replies from this module end with a short "(Demo mode ...)" label so users can
tell they did not come from the external AI model. To hide it, set
`DEMO_LABEL = ""` in `services/ai_service.py`. To add a topic, append one
dictionary to `TOPICS` in `health_knowledge.py`.

---

## 14. Future Scope

- Add refresh tokens / token blocklist for true server-side logout
- Rate-limiting on `/api/chat` and `/api/symptoms/check`
- Move from SQLite to PostgreSQL for production
- Add a proper frontend (React/Flutter) consuming this API
- Expand the medicines table with a real, licensed drug database
- Add multi-language support for the AI assistant
- Add push/email reminders based on health history trends
- Add role-based access (e.g. a "doctor" role who can view flagged emergencies)

---

## 15. Project Structure

```
backend/
├── app/
│   ├── main.py                     # App entry point, routers, error handlers
│   ├── database/
│   │   ├── connection.py           # Engine, SessionLocal, get_db()
│   │   ├── models.py               # SQLAlchemy ORM models (tables)
│   │   └── seed_medicines.py       # 20 sample medicines (added by name on startup)
│   ├── schemas/
│   │   ├── user.py                 # Register/login/user response schemas
│   │   ├── health.py               # Health profile + history schemas
│   │   ├── chat.py                 # Chat + symptom checker schemas
│   │   └── medicine.py             # Medicine info schema
│   ├── routes/
│   │   ├── auth.py
│   │   ├── health.py
│   │   ├── chat.py
│   │   ├── symptoms.py
│   │   ├── medicines.py
│   │   └── history.py
│   ├── services/
│   │   ├── ai_service.py           # AI system prompt + OpenAI-compatible client
│   │   ├── health_knowledge.py     # Built-in knowledge base (offline chat + symptom rules)
│   │   ├── emergency_detection.py  # Modular keyword-based safety layer
│   │   └── history_service.py      # Shared helpers (profile context, logging)
│   └── utils/
│       ├── security.py             # bcrypt hashing + JWT create/decode
│       └── deps.py                 # get_current_user dependency
├── tests/
│   ├── conftest.py                 # Test fixtures + isolated test DB
│   ├── test_auth.py
│   ├── test_health_profile.py
│   ├── test_chat.py
│   ├── test_symptoms.py
│   ├── test_medicines.py
│   ├── test_history.py
│   └── test_knowledge_base.py
├── .env.example
├── requirements.txt
├── README.md
└── run.py
```
