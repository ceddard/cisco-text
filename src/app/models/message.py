from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    message: str = Field(..., description="The message sent by the user")
    user_id: Optional[str] = Field(None, description="User identifier")


class ChatResponse(BaseModel):
    response: str = Field(..., description="The response from the chatbot")
    timestamp: datetime = Field(default_factory=datetime.now)


class MessageHistory(BaseModel):
    messages: List[dict] = Field(default_factory=list)
    user_id: str
