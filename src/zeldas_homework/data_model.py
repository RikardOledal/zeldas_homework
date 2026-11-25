from pydantic import BaseModel, Field
from typing import Literal

class Homework_data(BaseModel):
    index: int = Field(description="Index for data")
    kind: Literal["Words", "Sentences", "Grammar"] = Field(description="Kind of data")
    english: str = Field(description="English word or sentence")
    swedish: str = Field(description="Swedish word or sentence")

class Homework_List(BaseModel):
    homework_items: list[Homework_data] = Field(description="List of all extracted homework items from the PDF")