import pytest
from unittest.mock import patch, AsyncMock
from src.schemas.session_schemas.ask_response_model import AskResponseModel


class TestAskRoute:
    @patch("src.routes.session_routes.ChatUseCase")
    # @pytest.mark.skip(reason="Should be mocked but I won't take the risk to nail my plan suscription.")
    @pytest.mark.asyncio
    async def test_ask_route(self, mock_chat_usecase, client):
        create_session_return_id = client.post("/api/sessions/")
        session_id = create_session_return_id.json()["session_id"]
        fake_response = AskResponseModel(
            session_id=session_id, thinking=[], tool_calls=[], answer="42"
        )
        instance = mock_chat_usecase.return_value
        instance.ask = AsyncMock(return_value=fake_response)
        response = client.post(
            f"/api/sessions/{session_id}/ask/", json={"question": "Hello"}
        )
        assert response.status_code == 200
