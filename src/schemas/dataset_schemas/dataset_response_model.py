from pydantic import BaseModel


class DatasetResponseModel(BaseModel):
    name: str
    rows: int
    columns: int
    column_names: list[str]
