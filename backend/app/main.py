"""
main.py
-------
The entry point of the FastAPI application.

Responsibilities of this file:
1. Create the FastAPI app instance (title, description shown in /docs).
2. Create all database tables on startup (via Base.metadata.create_all).
3. Seed sample medicine data on startup.
4. Register CORS middleware (so a frontend on a different port can call us).
5. Register all route modules (auth, health, chat, symptoms, medicines, history).
6. Define global exception handlers so errors always return clean JSON.

Run with:
    uvicorn app.main:app --reload
or simply:
    python run.py
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import engine, Base, SessionLocal
from app.database.seed_medicines import seed_medicines

# Import route modules
from app.routes import auth, health, chat, symptoms, medicines, history

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI Health Assistant API",
    description=(
        "Backend REST API for a college mini project: an AI-powered general "
        "health information assistant. This project provides general health "
        "information only and is NOT a substitute for professional medical "
        "advice, diagnosis, or treatment."
    ),
    version="1.0.0",
)

# Allow requests from any origin during development (e.g. a React/Postman
# frontend running on a different port). Restrict this in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Runs once when the app starts."""
    # Create all tables defined in app/database/models.py if they don't exist
    Base.metadata.create_all(bind=engine)

    # Insert sample medicine data if the table is empty
    db = SessionLocal()
    try:
        seed_medicines(db)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Register routers
# ---------------------------------------------------------------------------

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(symptoms.router)
app.include_router(medicines.router)
app.include_router(history.router)


# ---------------------------------------------------------------------------
# Global exception handlers -> always return clean, consistent JSON errors
# ---------------------------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Triggered when incoming request data fails Pydantic validation."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "details": exc.errors(),
        },
    )


@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    """Catches unexpected database errors so we never leak a raw traceback."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "A database error occurred. Please try again."},
    )


@app.get("/", tags=["Root"])
def root():
    """Simple health-check root endpoint."""
    return {
        "message": "AI Health Assistant API is running.",
        "docs": "/docs",
        "disclaimer": (
            "This AI Health Assistant provides general health information "
            "and is not a substitute for professional medical advice."
        ),
    }
