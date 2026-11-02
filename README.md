# AI Health Assistant

A full-stack web application that gives **general health information** using an AI chat assistant,
a symptom checker, a medicine information library and a personal health profile with activity history.
Built as a TYBSc Computer Science mini project.

> **Disclaimer:** This project provides general, educational health information only. It is **not** a
> substitute for professional medical advice, diagnosis or treatment, and must not be used for real
> medical decisions.

## Features

- Sign up / log in with JWT authentication and bcrypt password hashing
- AI health chat with a rule-based **emergency detector** that runs before every AI call
- Symptom checker with severity (LOW / MODERATE / HIGH) and advice
- Medicine information for 20 common medicines (search by name, no dosages given)
- Personal health profile (height, weight, allergies, conditions, emergency contact)
- Health history of chats, symptom checks and profile updates
- Works without a paid API key: a built-in health knowledge base answers when no AI key is set

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, React Router, Vite |
| Backend | Python, FastAPI, Uvicorn |
| Database | SQLite with SQLAlchemy ORM |
| Validation / Auth | Pydantic, JWT (python-jose), Passlib + bcrypt |
| AI | Any OpenAI-compatible API (optional) |
| Testing | pytest + httpx (42 automated tests) |

## Project Structure

```
ai-health-assistant/
├── backend/      FastAPI REST API, database models, tests  (see backend/README.md)
├── frontend/     React web app                              (see frontend/README.md)
├── docs/         Report, user manual and screenshots
└── README.md
```

## Getting Started

### Prerequisites
Python 3.10+, Node.js 18+, Git

### 1. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env         # Mac/Linux: cp .env.example .env
python run.py
```
API: http://localhost:8000  |  Swagger docs: http://localhost:8000/docs

`AI_API_KEY` in `.env` is optional. Leave it empty to run in demo mode with the built-in knowledge base.

### 2. Frontend
```bash
cd frontend
npm install
copy .env.example .env         # Mac/Linux: cp .env.example .env
npm run dev
```
App: http://localhost:5173

### 3. Run the tests
```bash
cd backend
pytest tests/ -v
```

## API Overview

| Area | Endpoints |
|---|---|
| Auth | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/logout` |
| Health profile | `POST` / `GET` / `PUT /api/health/profile` |
| AI chat | `POST /api/chat` |
| Symptom checker | `POST /api/symptoms/check` |
| Medicines | `GET /api/medicines`, `GET /api/medicines/{name}` |
| History | `GET /api/history`, `GET /api/history/{id}` |

Full details and examples: [backend/README.md](backend/README.md).

## Screenshots

Add screenshots to `docs/screenshots/` and link them here.

## Author

**[Your Name]** - TYBSc Computer Science, [Your College], 2026
