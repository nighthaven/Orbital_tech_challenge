from unittest.mock import AsyncMock, patch


class TestChatWebsocketRoute:

    @patch("src.usecases.chat_usecase.ChatUseCase.stream_ask", new_callable=AsyncMock)
    def test_chat_websocket(self, mock_stream_ask, client):

        async def fake_stream(websocket, session_id):
            await websocket.send_json(
                {
                    "answer": "fake answer",
                    "thinking": ["fake thinking"],
                    "tool_calls": [],
                }
            )

        mock_stream_ask.side_effect = fake_stream

        create_session_return_id = client.post("/api/sessions/")
        session_id = create_session_return_id.json()["session_id"]

        with client.websocket_connect(f"/api/sessions/{session_id}/chat") as web_socket:
            web_socket.send_json({"question": "Hello"})
            data = web_socket.receive_json()

            assert "answer" in data
            assert "thinking" in data
