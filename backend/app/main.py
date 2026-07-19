"""
main.py
--------
The FastAPI application entrypoint. Run with:
    uvicorn app.main:app --reload

This wires together all the API routers (upload, chat, eval) and
creates the database tables on startup.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import upload, chat, eval as eval_router
from app.db.session import engine
from app.db.models import init_db

app = FastAPI(title="VeritasPrep AI API")

# Allow the frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, tags=["upload"])
app.include_router(chat.router, tags=["chat"])
app.include_router(eval_router.router, tags=["evaluation"])


@app.on_event("startup")
def on_startup():
    init_db(engine)


@app.get("/")
def health_check():
    return {"status": "VeritasPrep AI backend is running"}
