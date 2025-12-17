"""Pydantic models for API request/response validation."""
from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional, Literal


class ChatSessionCreate(BaseModel):
    """Request model for creating a new chat session."""
    metadata: Optional[dict] = {}


class ChatSessionResponse(BaseModel):
    """Response model for chat session."""
    session_id: UUID4
    created_at: datetime
    metadata: dict

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Request model for creating a message."""
    content: str
    role: Literal["user", "assistant", "system"] = "user"
    metadata: Optional[dict] = {}


class MessageResponse(BaseModel):
    """Response model for a message."""
    id: int
    session_id: UUID4
    role: str
    content: str
    timestamp: datetime
    metadata: dict

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Request model for sending a chat message."""
    message: str
    selected_text: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat completion."""
    session_id: UUID4
    user_message: MessageResponse
    assistant_message: MessageResponse


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    timestamp: datetime
