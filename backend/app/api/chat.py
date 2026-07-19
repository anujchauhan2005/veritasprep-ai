"""
api/chat.py
------------
POST /chat         -- ask a question, get a full answer back (with scores)
POST /chat/stream   -- same thing, but streams the answer token-by-token

Every turn is saved to the database (chat history + evaluation scores).
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.rag.retriever import retrieve_relevant_chunks
from app.rag.generator import generate_answer, generate_answer_stream
from app.evaluation.answer_metrics import evaluate_answer
from app.core.memory import memory_manager
from app.db.session import get_db
from app.db.models import ChatMessage, EvalLog

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str
    question: str


@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    history = memory_manager.get_history(request.session_id)

    chunks = retrieve_relevant_chunks(request.question)
    answer = generate_answer(request.question, chunks, history)
    scores = evaluate_answer(answer, request.question, chunks)

    # Update in-memory conversation history
    memory_manager.add_turn(request.session_id, "user", request.question)
    memory_manager.add_turn(request.session_id, "assistant", answer)

    # Persist to database
    db.add(ChatMessage(session_id=request.session_id, role="user", content=request.question))
    db.add(ChatMessage(session_id=request.session_id, role="assistant", content=answer))
    db.add(EvalLog(
        session_id=request.session_id,
        question=request.question,
        answer=answer,
        groundedness=scores["groundedness"],
        answer_relevance=scores["answer_relevance"],
    ))
    db.commit()

    return {
        "answer": answer,
        "retrieved_chunks": chunks,
        "scores": scores,
    }


@router.post("/chat/stream")
def chat_stream(request: ChatRequest):
    history = memory_manager.get_history(request.session_id)
    chunks = retrieve_relevant_chunks(request.question)

    def token_generator():
        full_answer = ""
        for token in generate_answer_stream(request.question, chunks, history):
            full_answer += token
            yield token
        # Once streaming finishes, save the full turn to memory
        memory_manager.add_turn(request.session_id, "user", request.question)
        memory_manager.add_turn(request.session_id, "assistant", full_answer)

    return StreamingResponse(token_generator(), media_type="text/plain")
