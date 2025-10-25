"""Session management utilities for the chat backend."""

from __future__ import annotations

import asyncio
from typing import Dict, List, Tuple
from uuid import uuid4

ChatMessage = Dict[str, str]


class UnknownSessionError(KeyError):
    """Raised when a session lookup fails."""


class SessionManager:
    """In-memory storage for chat sessions.

    This keeps track of conversation turns so the backend can supply the
    accumulated context to the language model. The implementation is simple and
    non-persistent on purpose; FastAPI runs with multiple workers should be
    configured with a more robust store (Redis, database, etc.).
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, List[ChatMessage]] = {}
        self._lock = asyncio.Lock()

    async def ensure_session(self, session_id: str | None = None) -> Tuple[str, bool]:
        """Return a valid session id, creating a new session when needed.

        Returns a tuple of the resolved session id and a boolean flag indicating
        whether a new session was created.
        """

        async with self._lock:
            if session_id and session_id in self._sessions:
                return session_id, False

            new_id = session_id or uuid4().hex
            self._sessions.setdefault(new_id, [])
            return new_id, True

    async def add_message(self, session_id: str, role: str, content: str) -> None:
        """Append a message to the session history."""

        message = {"role": role, "content": content}
        async with self._lock:
            if session_id not in self._sessions:
                raise UnknownSessionError(session_id)
            self._sessions[session_id].append(message)

    async def get_history(self, session_id: str) -> List[ChatMessage]:
        """Return a copy of the message history for the session."""

        async with self._lock:
            if session_id not in self._sessions:
                raise UnknownSessionError(session_id)
            # Return a shallow copy so callers cannot mutate internal state.
            return list(self._sessions[session_id])

    async def clear(self, session_id: str) -> None:
        """Remove all messages from the given session."""

        async with self._lock:
            if session_id not in self._sessions:
                raise UnknownSessionError(session_id)
            self._sessions[session_id].clear()


session_manager = SessionManager()
"""Default session manager used by the FastAPI application."""

