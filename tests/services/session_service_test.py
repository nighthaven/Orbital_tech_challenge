import pytest

from src.exceptions.session.session_not_found_exception import SessionNotFoundException
from src.services.session_service import SessionService


class TestSessionService:
    def setup_method(self):
        self.session_service = SessionService()

    def test_create_session_with_success(self):

        response = self.session_service.create_session()
        assert response is not None

    def test_delete_session_with_success(self):
        session_id = self.session_service.create_session()
        assert len(self.session_service.list_sessions()) == 1
        self.session_service.delete_session(session_id)
        list_session = self.session_service.list_sessions()
        assert not list_session

    def test_delete_session_with_invalid_session_id(self):
        session_id = "invalid_session_id"
        with pytest.raises(SessionNotFoundException) as exception_info:
            self.session_service.delete_session(session_id)

        assert (
            str(exception_info.value)
            == f"Session not found, session_id provided: {session_id}"
        )

    def test_list_sessions_with_success(self):
        self.session_service.create_session()
        response = self.session_service.list_sessions()
        assert response is not None
        assert len(response) > 0

    def test_get_history_with_success(self):
        session_id = self.session_service.create_session()
        message = ["Mankind was born on Earth. It was never meant to die here."]
        self.session_service.save_history(session_id, message)
        response = self.session_service.get_history(session_id)

        assert response == message

    def test_get_history_with_invalid_session(self):
        session_id = "invalid_session_id"
        with pytest.raises(SessionNotFoundException) as exception_info:
            self.session_service.get_history(session_id)
        assert (
            str(exception_info.value)
            == f"Session not found, session_id provided: {session_id}"
        )
