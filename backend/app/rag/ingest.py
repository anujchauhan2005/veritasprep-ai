"""
rag/ingest.py
--------------
Takes a resume PDF, breaks it into chunks, and stores those chunks
(as embeddings) in the vector database. This is the "indexing" step
that happens once per uploaded resume.
"""

from pypdf import PdfReader
from app.vectorstore.chroma_client import reset_collection
from app.core.config import settings


def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    return full_text


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list[str]:
    chunk_size = chunk_size or settings.CHUNK_SIZE
    overlap = overlap or settings.CHUNK_OVERLAP

    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks


def build_resume_index(pdf_path: str, collection_name: str = "resume"):
    """Full pipeline: PDF -> text -> chunks -> embeddings -> stored in ChromaDB."""
    collection = reset_collection(collection_name)

    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)
    ids = [f"chunk_{i}" for i in range(len(chunks))]

    collection.add(documents=chunks, ids=ids)
    return len(chunks)
