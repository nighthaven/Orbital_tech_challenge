import pytest
from unittest.mock import patch
from src.services.dataset_service import DatasetService
from src.services.session_service import SessionService
from src.usecases.chat_usecase import ChatUseCase


class TestChatUsecase:
    def setup_method(self):
        self.session_service = SessionService()
        self.dataset_service = DatasetService()
        self.chat_usecase = ChatUseCase(self.dataset_service, self.session_service)

    # @pytest.mark.skip(reason="Should be mocked but I won't take the risk to nail my plan suscription.")
    @pytest.mark.asyncio
    @patch("src.usecases.chat_usecase.create_agent")
    async def test_chat_ask(self, mock_create_agent):
        class FakeResult:
            output = "<thinking>analysis</thinking>Hello"

            def all_messages(self):
                return []

        class FakeAgent:
            async def run(self, *args, **kwargs):
                return FakeResult()

        mock_create_agent.return_value = FakeAgent()

        session_id = self.session_service.create_session()
        question = "Hello how are you?"

        response = await self.chat_usecase.ask(session_id, question)
        assert response.answer == "Hello"
        assert "analysis" in response.thinking
