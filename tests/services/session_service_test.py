from src.services.session_service import SessionService


class TestSessionService:
    def setup_method(self):
        self.session_service = SessionService()

    def test_create_session_with_success(self):

        response = self.session_service.create_session()
        assert response is not None
