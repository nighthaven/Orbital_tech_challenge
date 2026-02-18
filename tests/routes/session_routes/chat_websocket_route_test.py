from unittest.mock import patch


class TestChatWebSocket:

    @patch("src.routes.session_routes.ChatUseCase")
    def test_sends_events_and_done_success(self, mock_chat_usecase, client):
        session_id = client.post("/api/sessions/").json()["session_id"]

        async def fake_stream(ws, sid):
            await ws.receive_json()
            await ws.send_json(
                {
                    "type": "tool_call",
                    "tool_name": "query_data",
                    "args": {"sql": "SELECT 1"},
                }
            )
            await ws.send_json(
                {
                    "type": "tool_result",
                    "tool_name": "query_data",
                    "content": "1 row",
                    "file": None,
                }
            )
            await ws.send_json({"type": "thinking", "content": "Analyzing..."})
            await ws.send_json({"type": "text_delta", "content": "The answer is "})
            await ws.send_json({"type": "text_delta", "content": "42."})
            await ws.send_json({"type": "done"})
            await ws.receive_json()

        mock_chat_usecase.return_value.stream_ask = fake_stream

        with client.websocket_connect(f"/api/sessions/{session_id}/chat") as ws:
            ws.send_json({"question": "What is the answer?"})

            events = []
            while True:
                event = ws.receive_json()
                events.append(event)
                if event["type"] == "done":
                    break

        types = [e["type"] for e in events]
        assert types == [
            "tool_call",
            "tool_result",
            "thinking",
            "text_delta",
            "text_delta",
            "done",
        ]
        assert events[0]["tool_name"] == "query_data"
        assert events[0]["args"] == {"sql": "SELECT 1"}
        assert events[1]["content"] == "1 row"
        assert events[2]["content"] == "Analyzing..."

    @patch("src.routes.session_routes.ChatUseCase")
    def test_error_event_on_exception(self, mock_chat_usecase, client):
        session_id = client.post("/api/sessions/").json()["session_id"]

        async def failing_stream(ws, sid):
            await ws.receive_json()
            raise RuntimeError("LLM API is down")

        mock_chat_usecase.return_value.stream_ask = failing_stream

        with client.websocket_connect(f"/api/sessions/{session_id}/chat") as ws:
            ws.send_json({"question": "Hello"})
            error = ws.receive_json()
            assert error["type"] == "error"
            assert "LLM API is down" in error["content"]

    def test_invalid_session(self, client):
        with client.websocket_connect("/api/sessions/nonexistent-id/chat") as ws:
            assert ws.receive_json() == {
                "type": "error",
                "content": "Session not found",
            }

    @patch("src.routes.session_routes.ChatUseCase")
    def test_multiple_questions_in_same_session(self, mock_chat_usecase, client):
        session_id = client.post("/api/sessions/").json()["session_id"]
        call_count = 0

        async def fake_stream(ws, sid):
            nonlocal call_count
            while True:
                await ws.receive_json()
                call_count += 1
                await ws.send_json(
                    {"type": "text_delta", "content": f"Answer {call_count}"}
                )
                await ws.send_json({"type": "done"})

        mock_chat_usecase.return_value.stream_ask = fake_stream

        with client.websocket_connect(f"/api/sessions/{session_id}/chat") as ws:
            ws.send_json({"question": "Q1"})
            assert ws.receive_json()["content"] == "Answer 1"
            assert ws.receive_json()["type"] == "done"

            ws.send_json({"question": "Q2"})
            assert ws.receive_json()["content"] == "Answer 2"
            assert ws.receive_json()["type"] == "done"

    @patch("src.routes.session_routes.ChatUseCase")
    def test_empty_question_is_ignored(self, mock_chat_usecase, client):
        session_id = client.post("/api/sessions/").json()["session_id"]

        async def fake_stream(ws, sid):
            while True:
                data = await ws.receive_json()
                question = data.get("question")
                if not question:
                    continue
                await ws.send_json({"type": "text_delta", "content": "Got it"})
                await ws.send_json({"type": "done"})
                await ws.receive_json()

        mock_chat_usecase.return_value.stream_ask = fake_stream

        with client.websocket_connect(f"/api/sessions/{session_id}/chat") as ws:
            ws.send_json({"question": ""})
            ws.send_json({"question": "Real question"})

            data = ws.receive_json()
            assert data["type"] == "text_delta"
            assert data["content"] == "Got it"
