from pydantic import BaseModel

from src.schemas.session_schemas.tool_calls import ToolCall


class AskResponseModel(BaseModel):
    session_id: str
    thinking: list[str]
    tool_calls: list[ToolCall]
    answer: str
