from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str
    software_background: Optional[str] = None
    hardware_background: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    software_background: Optional[str] = None
    hardware_background: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Chat Schemas
class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    selected_text: Optional[str] = None  # For text selection-based Q&A
    chapter_id: Optional[str] = None

class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    context: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    session_id: str

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: List[Dict[str, Any]] = []
    confidence: Optional[float] = None

# Document Schemas
class DocumentChunk(BaseModel):
    title: str
    content: str
    chapter_id: str
    metadata: Optional[Dict[str, Any]] = None

class DocumentIngest(BaseModel):
    documents: List[DocumentChunk]

class DocumentResponse(BaseModel):
    id: int
    title: str
    chapter_id: str
    url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Bookmark Schemas
class BookmarkCreate(BaseModel):
    chapter_id: str
    page_url: str
    note: Optional[str] = None

class BookmarkResponse(BaseModel):
    id: int
    chapter_id: str
    page_url: str
    note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Search Schemas
class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    chapter_filter: Optional[str] = None

class SearchResult(BaseModel):
    title: str
    content: str
    chapter_id: str
    score: float
    metadata: Optional[Dict[str, Any]] = None
