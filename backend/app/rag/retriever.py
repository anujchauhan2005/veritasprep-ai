"""
rag/retriever.py
------------------
Given a question, finds the most relevant resume chunks.
This is the "R" (Retrieval) step in RAG.
"""

from app.vectorstore.chroma_client import get_or_create_collection
from app.core.config import settings


def retrieve_relevant_chunks(question: str, collection_name: str = "resume", top_k: int = None):
    top_k = top_k or settings.TOP_K
    collection = get_or_create_collection(collection_name)

    results = collection.query(query_texts=[question], n_results=top_k)
    return results["documents"][0] if results["documents"] else []
