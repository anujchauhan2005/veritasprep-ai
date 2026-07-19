# 🧭 VeritasPrep AI

**A resume-grounded interview coach that shows its work.**

Most AI interview prep tools give generic advice and hope it's accurate.
VeritasPrep AI retrieves answers directly from your real resume (RAG),
remembers the conversation, and **measures its own reliability** with
retrieval and answer-quality metrics — the part most student RAG projects skip.

## Problem it solves
- Generic interview prep tools ignore your actual background.
- Most AI tools give no way to check whether an answer is trustworthy or hallucinated.
- Most chat tools don't remember earlier turns in the conversation.

## Architecture
```
                        ┌──────────────┐
                        │   Frontend    │   Streamlit UI
                        │  (frontend/)  │
                        └──────┬───────┘
                               │ HTTP
                        ┌──────▼───────┐
                        │   FastAPI     │   backend/app/main.py
                        │   Backend     │
                        └──┬────────┬───┘
              ┌────────────┘        └────────────┐
       ┌──────▼──────┐                    ┌───────▼──────┐
       │  RAG engine  │                    │  Evaluation   │
       │ ingest /     │                    │ retrieval +   │
       │ retriever /  │                    │ answer metrics│
       │ generator    │                    └───────┬──────┘
       └──────┬──────┘                             │
       ┌──────▼──────┐                      ┌───────▼──────┐
       │  ChromaDB    │                      │  PostgreSQL/  │
       │ (vector store)│                     │  SQLite       │
       └─────────────┘                       │ (chat + eval  │
                                              │  logs)        │
                                              └──────────────┘
```

## Folder structure
```
veritasprep-ai-full/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entrypoint
│   │   ├── api/
│   │   │   ├── chat.py          # /chat and /chat/stream endpoints
│   │   │   ├── upload.py        # /upload endpoint
│   │   │   └── eval.py          # /eval/history and /eval/retrieval endpoints
│   │   ├── core/
│   │   │   ├── config.py        # centralized settings
│   │   │   └── memory.py        # conversation memory manager
│   │   ├── rag/
│   │   │   ├── ingest.py        # PDF -> chunks -> embeddings -> ChromaDB
│   │   │   ├── retriever.py     # vector search
│   │   │   └── generator.py     # LLM calls (streaming + non-streaming)
│   │   ├── evaluation/
│   │   │   ├── retrieval_metrics.py   # precision@k, recall@k, MRR
│   │   │   └── answer_metrics.py      # groundedness, answer relevance
│   │   ├── db/
│   │   │   ├── models.py        # SQLAlchemy models (chat history, eval logs)
│   │   │   └── session.py       # DB connection setup
│   │   └── vectorstore/
│   │       └── chroma_client.py # shared ChromaDB connection
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── app.py                   # Streamlit UI (calls the backend API)
│   ├── requirements.txt
│   └── Dockerfile
├── eval_data/
│   └── eval_dataset.json        # labeled Q&A pairs for retrieval evaluation
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Setup (running locally, without Docker)

**1. Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt
copy .env.example .env           # then edit .env and add your real GROQ_API_KEY
uvicorn app.main:app --reload
```
Backend runs at `http://localhost:8000`. Visit `http://localhost:8000/docs` to see
the interactive API documentation FastAPI generates automatically.

**2. Frontend (in a second terminal):**
```bash
cd frontend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```
Frontend opens at `http://localhost:8501`.

## Running with Docker instead
```bash
docker-compose up --build
```
This starts both the backend and frontend containers together.

## Running the evaluation suite
Once the backend is running and a resume has been uploaded:
```bash
curl -X POST http://localhost:8000/eval/retrieval
```
This runs the labeled questions in `eval_data/eval_dataset.json` against
the retriever and returns precision@k, recall@k, and MRR.

To see how every past answer scored on groundedness and relevance:
```bash
curl http://localhost:8000/eval/history
```

## What makes this project resume-worthy
- **Real backend/frontend separation** — a FastAPI service any client could call, not a single monolithic script.
- **Streaming responses** — `/chat/stream` streams tokens like a production chat app.
- **Persistent memory** — conversation history and evaluation scores are stored in a real database, not just in-session variables.
- **A genuine evaluation framework** — retrieval metrics (precision/recall/MRR) AND answer-quality metrics (groundedness, relevance), the exact thing companies hiring for AI roles screen for in 2026.

## Next upgrades (roadmap)
- Swap the word-overlap heuristics in `evaluation/answer_metrics.py` for the **RAGAS** library for more rigorous faithfulness/relevance scoring.
- Track chunk IDs properly through retrieval so `/eval/retrieval` compares IDs instead of raw text.
- Replace the Streamlit frontend with a React app for a more polished UI.
- Deploy the backend on Render/Railway and the frontend on Streamlit Community Cloud or Vercel.
