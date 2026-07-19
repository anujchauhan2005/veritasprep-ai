"""
core/memory.py
---------------
Manages conversation memory per session, so follow-up questions
("tell me more about that project") resolve correctly.

This is a simple in-memory version (a Python dictionary). It resets if
the server restarts. Upgrading this to persist in the database (see
db/models.py -> ChatMessage) is a natural next step once this works.
"""

from typing import Dict, List


class MemoryManager:
    def __init__(self):
        # Maps session_id -> list of {"role": ..., "content": ...} messages
        self._sessions: Dict[str, List[dict]] = {}

    def get_history(self, session_id: str) -> List[dict]:
        return self._sessions.get(session_id, [])

    def add_turn(self, session_id: str, role: str, content: str):
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append({"role": role, "content": content})

    def clear(self, session_id: str):
        self._sessions[session_id] = []


# One shared instance used across the whole app
memory_manager = MemoryManager()
