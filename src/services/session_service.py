import uuid

from src.exceptions.session.session_not_found_exception import SessionNotFoundException


class SessionService:
    """In-memory store for conversation histories, keyed by session ID."""

    def __init__(self) -> None:
        self._sessions: dict[str, list] = {}

    def create_session(self) -> str:
        """Create a new session and return its ID."""
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = []
        return session_id

    def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        if session_id not in self._sessions:
            raise SessionNotFoundException(session_id)
        self._sessions.pop(session_id, None)
        return

    def list_sessions(self) -> list[str]:
        """Return all active session IDs."""
        return list(self._sessions.keys())