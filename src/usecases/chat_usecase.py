import json
import re
from fastapi import WebSocket
from pydantic_ai.messages import (
    ModelResponse,
    TextPart,
    ToolCallPart,
)

from src.agent.agent import create_agent
from src.agent.context import AgentContext
from src.schemas.session_schemas.ask_response_model import AskResponseModel
from src.schemas.session_schemas.tool_calls import ToolCall
from src.services.dataset_service import DatasetService
from src.services.session_service import SessionService


class ChatUseCase:
    def __init__(
        self,
        dataset_service: DatasetService,
        session_service: SessionService,
    ) -> None:
        self._dataset_service = dataset_service
        self._session_service = session_service

    async def stream_ask(self, web_socket: WebSocket, session_id: str):
        """Stream question answer with the agent for the chat."""
        while True:
            data = await web_socket.receive_json()
            question = data.get("question")
            if not question:
                continue
            response = await self.ask(session_id, question)
            await web_socket.send_json(
                {
                    "answer": response.answer,
                    "thinking": response.thinking,
                    "tool_calls": [tc.dict() for tc in response.tool_calls],
                }
            )

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
