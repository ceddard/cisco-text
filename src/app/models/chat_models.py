from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class ChatType(str, Enum):
    INVENTOR = "inventor"
    TRANSLATOR = "translator"
    CURATOR = "curator"


class ChatRequest(BaseModel):
    prompt: Literal["inventor", "translator", "curator"] = Field(
        ..., description="The type of chat service to use"
    )
    query: str = Field(..., description="The message/query to send to the LLM")


class ChatResponse(BaseModel):
    response: str = Field(..., description="The response from the chatbot")
    chat_type: str = Field(..., description="The type of chat service used")
    image_url: Optional[str] = Field(None, description="URL to an image for the Dream Curator")
