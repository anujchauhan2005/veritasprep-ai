"""
core/config.py
---------------
Central place for all settings. Instead of scattering "os.getenv(...)"
calls across many files, everything reads its configuration from here.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    CHROMA_PATH: str = os.getenv("CHROMA_PATH", "chroma_db")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./veritasprep.db")
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    LLM_MODEL: str = "llama-3.1-8b-instant"
    CHUNK_SIZE: int = 300
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 3


settings = Settings()
