"""
db/models.py
-------------
Defines the database tables (as Python classes, using SQLAlchemy's ORM).

Two tables:
1. ChatMessage -- stores every question/answer, so chat history can
   survive a server restart (instead of living only in memory).
2. EvalLog -- stores the evaluation scores (groundedness, relevance)
   for every answer generated, so you can track quality over time.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    role = Column(String)          # "user" or "assistant"
    content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class EvalLog(Base):
    __tablename__ = "eval_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    question = Column(Text)
    answer = Column(Text)
    groundedness = Column(Float)
    answer_relevance = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db(engine):
    """Creates all tables if they don't already exist. Call once at startup."""
    Base.metadata.create_all(bind=engine)
