class SessionNotFoundException(Exception):
    def __init__(self, session_id: str, message: str = "Session not found") -> None:
        super().__init__(f"{message}, session_id provided: {session_id}")