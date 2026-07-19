"""
api/upload.py
--------------
POST /upload -- accepts a resume PDF, saves it, and indexes it into
the vector database so questions can be answered against it.
"""

import os
from fastapi import APIRouter, UploadFile, File
from app.rag.ingest import build_resume_index

router = APIRouter()

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    file_path = os.path.join(DATA_DIR, "resume.pdf")
    with open(file_path, "wb") as f:
        f.write(await file.read())

    num_chunks = build_resume_index(file_path)
    return {"message": "Resume indexed successfully", "chunks": num_chunks}
