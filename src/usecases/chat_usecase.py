import json
import re
from fastapi import WebSocket
from pydantic_ai import AgentRunResultEvent
from pydantic_ai.messages import (
    ModelResponse,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    PartDeltaEvent,
    TextPartDelta,
    ThinkingPartDelta,
)

from src.agent.agent import create_agent
from src.agent.context import AgentContext
from src.schemas.session_schemas.ask_response_model import AskResponseModel
from src.schemas.session_schemas.tool_calls import ToolCall
from src.services.dataset_service import DatasetService
from src.services.session_service import SessionService
from src.usecases.infrastructure.thinking_stream_parser import ThinkingStreamParser
from src.usecases.infrastructure.plotly_extractor import extract_plotly_json_from_html

_FILE_PATH_RE = re.compile(r"Saved to: (output/\S+)")


class ChatUseCase:
    def __init__(
        self,
        dataset_service: DatasetService,
        session_service: SessionService,
    ) -> None:
        self._dataset_service = dataset_service
        self._session_service = session_service

    async def stream_ask(self, ws: WebSocket, session_id: str) -> None:
        """Listen for questions on WebSocket and stream agent responses."""
        while True:
            data = await ws.receive_json()
            question = data.get("question")
            if not question:
                continue

            try:
                await self.stream_agent_response(ws, session_id, question)
            except Exception as e:
                await ws.send_json({"type": "error", "content": str(e)})

    async def stream_agent_response(
        self, ws: WebSocket, session_id: str, question: str
    ) -> None:
        history = self._session_service.get_history(session_id)
        context = AgentContext(
            datasets=self._dataset_service.datasets,
            dataset_info=self._dataset_service.dataset_info,
        )
        agent = create_agent(self._dataset_service.dataset_info)
        thinking_stream_parser = ThinkingStreamParser(ws)

        async for event in agent.run_stream_events(
            question, deps=context, message_history=history or None
        ):
            if isinstance(event, AgentRunResultEvent):
                await thinking_stream_parser.flush()
                self._session_service.save_history(session_id, event.result.all_messages())
                await ws.send_json({"type": "done"})

            elif isinstance(event, FunctionToolCallEvent):
                part = event.part
                args = (
                    part.args
                    if isinstance(part.args, dict)
                    else (json.loads(part.args) if isinstance(part.args, str) else {})
                )
                await ws.send_json({"type": "tool_call", "name": part.tool_name, "args": args})

            elif isinstance(event, FunctionToolResultEvent):
                result_part = event.result
                if isinstance(result_part, ToolReturnPart):
                    content = str(result_part.content)
                    ws_event = self._build_tool_result_event(result_part.tool_name, content)
                    await ws.send_json(ws_event)

            elif isinstance(event, PartDeltaEvent):
                delta = event.delta
                if isinstance(delta, TextPartDelta):
                    await thinking_stream_parser.feed(delta.content_delta)
                elif isinstance(delta, ThinkingPartDelta) and delta.content_delta:
                    await ws.send_json({"type": "thinking", "content": delta.content_delta})

    def _build_tool_result_event(self, tool_name: str, content: str) -> dict:
        """Build a tool_result WebSocket event, enriching with URLs and Plotly JSON."""
        event: dict = {
            "type": "tool_result",
            "name": tool_name,
            "result": content,
            "file_url": None,
        }

        file_match = _FILE_PATH_RE.search(content)
        if file_match:
            file_path = file_match.group(1)
            event["file_url"] = self._server_path_to_url(file_path)
            if file_path.endswith(".html"):
                event["plotly_json"] = extract_plotly_json_from_html(file_path)

        return event

    def _server_path_to_url(self, path: str) -> str:
        """Convert 'output/foo.html' to '/api/files/foo.html'."""
        filename = path.removeprefix("output/")
        return f"/api/files/{filename}"

    async def ask(self, session_id: str, question: str) -> AskResponseModel:
        """Ask a question to the agent in an existing session."""
        history = self._session_service.get_history(session_id)

        context = AgentContext(
            datasets=self._dataset_service.datasets,
            dataset_info=self._dataset_service.dataset_info,
        )
        agent = create_agent(self._dataset_service.dataset_info)

        result = await agent.run(
            question,
            deps=context,
            message_history=history,
        )
        all_msgs = result.all_messages()

        new_msgs = all_msgs[len(history) :]

        thinking_blocks, tool_calls = self._parse_messages(new_msgs)
        thinking_final, answer = self._parse_thinking(result.output)
        if thinking_final:
            thinking_blocks.append(thinking_final)

        self._session_service.save_history(session_id, all_msgs)

        return AskResponseModel(
            session_id=session_id,
            thinking=thinking_blocks,
            tool_calls=tool_calls,
            answer=answer,
        )

    @staticmethod
    def _parse_thinking(text: str) -> tuple[str, str]:
        """Extract <thinking> blocks and return (thinking_text, clean_text)."""
        pattern = re.compile(r"<thinking>(.*?)</thinking>", re.DOTALL)
        thinking_parts = pattern.findall(text)
        thinking = "\n".join(t.strip() for t in thinking_parts)
        clean_text = pattern.sub("", text).strip()
        return thinking, clean_text

    @staticmethod
    def _parse_messages(messages) -> tuple[list[str], list[ToolCall]]:
        """Extract thinking blocks and tool calls from agent messages."""
        thinking_blocks: list[str] = []
        tool_calls: list[ToolCall] = []

        for msg in messages:
            if isinstance(msg, ModelResponse):
                for part in msg.parts:
                    if isinstance(part, TextPart) and part.content.strip():
                        thinking, _ = ChatUseCase._parse_thinking(part.content)
                        if thinking:
                            thinking_blocks.append(thinking)
                    elif isinstance(part, ToolCallPart):
                        args = (
                            part.args
                            if isinstance(part.args, dict)
                            else (
                                json.loads(part.args)
                                if isinstance(part.args, str)
                                else {}
                            )
                        )
                        tool_calls.append(ToolCall(tool_name=part.tool_name, args=args))
        return thinking_blocks, tool_calls
