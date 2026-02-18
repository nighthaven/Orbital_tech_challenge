from pydantic import BaseModel


class AskQuery(BaseModel):
    question: str
