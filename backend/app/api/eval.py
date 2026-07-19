"""
api/eval.py
------------
GET /eval/history        -- view logged groundedness/relevance scores over time
POST /eval/retrieval      -- run retrieval precision/recall/MRR against a
                              labeled evaluation dataset (eval_data/eval_dataset.json)
"""

import json
import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import EvalLog
from app.rag.retriever import retrieve_relevant_chunks
from app.evaluation.retrieval_metrics import evaluate_retrieval

router = APIRouter()

EVAL_DATASET_PATH = os.path.join("eval_data", "eval_dataset.json")


@router.get("/eval/history")
def eval_history(db: Session = Depends(get_db)):
    logs = db.query(EvalLog).order_by(EvalLog.created_at.desc()).limit(50).all()
    return [
        {
            "question": log.question,
            "groundedness": log.groundedness,
            "answer_relevance": log.answer_relevance,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]


@router.post("/eval/retrieval")
def run_retrieval_eval():
    if not os.path.exists(EVAL_DATASET_PATH):
        return {"error": f"No eval dataset found at {EVAL_DATASET_PATH}. See README for format."}

    with open(EVAL_DATASET_PATH) as f:
        eval_dataset = json.load(f)

    def retrieve_fn(question: str):
        # NOTE: this simplified version compares retrieved chunk TEXT,
        # not database ids. Good enough for a first working version.
        return retrieve_relevant_chunks(question)

    results = evaluate_retrieval(eval_dataset, retrieve_fn)
    return results
