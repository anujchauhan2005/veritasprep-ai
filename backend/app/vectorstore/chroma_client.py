"""
vectorstore/chroma_client.py
-----------------------------
Single shared connection to ChromaDB (the vector database) and the
embedding model. Every other file that needs to store or search
resume chunks imports from here, instead of each creating its own
connection.
"""

import chromadb
from chromadb.utils import embedding_functions
from app.core.config import settings

chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PATH)

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=settings.EMBEDDING_MODEL
)


def get_or_create_collection(name: str = "resume"):
    """Returns the collection, creating it if it doesn't exist yet."""
    return chroma_client.get_or_create_collection(
        name=name, embedding_function=embedding_fn
    )


def reset_collection(name: str = "resume"):
    """Deletes and recreates a collection -- used when a new resume is uploaded."""
    existing = [c.name for c in chroma_client.list_collections()]
    if name in existing:
        chroma_client.delete_collection(name)
    return chroma_client.create_collection(name=name, embedding_function=embedding_fn)
