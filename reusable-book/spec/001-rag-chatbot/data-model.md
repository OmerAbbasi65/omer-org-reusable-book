# Data Model: RAG Chatbot

**Feature**: Integrated RAG Chatbot
**Date**: 2025-12-17
**Database**: Neon Serverless Postgres

## Overview

This document defines the database schema for chat session and message persistence. The system uses Neon Serverless Postgres for relational data and Qdrant Cloud for vector embeddings (not covered in this schema).

## Entity Relationship Diagram

```
┌─────────────────┐
│  chat_sessions  │
│                 │
│ - session_id    │◄──────┐
│ - created_at    │       │
│ - metadata      │       │ 1:N
└─────────────────┘       │
                          │
                    ┌─────────────┐
                    │  messages   │
                    │             │
                    │ - id        │
                    │ - session_id│──┐
                    │ - role      │
                    │ - content   │
                    │ - timestamp │
                    │ - metadata  │
                    └─────────────┘
```

## Tables

### 1. chat_sessions

Stores metadata for each chat session. Sessions are ephemeral from the user's perspective (no cross-session history) but persisted for potential analytics.

**Schema**:

```sql
CREATE TABLE chat_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Indexes
    CONSTRAINT pk_chat_sessions PRIMARY KEY (session_id)
);

CREATE INDEX idx_chat_sessions_created_at ON chat_sessions(created_at DESC);
CREATE INDEX idx_chat_sessions_metadata ON chat_sessions USING GIN(metadata);
```

**Fields**:

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `session_id` | UUID | NO | Primary key, auto-generated UUID |
| `created_at` | TIMESTAMP WITH TIME ZONE | NO | Session creation timestamp |
| `closed_at` | TIMESTAMP WITH TIME ZONE | YES | Session close timestamp (optional) |
| `metadata` | JSONB | YES | Flexible field for future extensions (e.g., user preferences, source page) |

**Constraints**:
- `session_id` must be unique (enforced by PRIMARY KEY)
- `created_at` defaults to current timestamp

**Metadata Examples**:
```json
{
  "source_page": "/docs/chapter-1/introduction",
  "user_agent": "Mozilla/5.0...",
  "initial_context": "text selection"
}
```

---

### 2. messages

Stores all messages exchanged in chat sessions. Includes both user questions and chatbot responses.

**Schema**:

```sql
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Indexes
    CONSTRAINT pk_messages PRIMARY KEY (id),
    CONSTRAINT fk_messages_session FOREIGN KEY (session_id)
        REFERENCES chat_sessions(session_id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp DESC);
CREATE INDEX idx_messages_session_timestamp ON messages(session_id, timestamp);
```

**Fields**:

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | BIGSERIAL | NO | Auto-incrementing primary key |
| `session_id` | UUID | NO | Foreign key to `chat_sessions.session_id` |
| `role` | VARCHAR(20) | NO | Message role: 'user', 'assistant', or 'system' |
| `content` | TEXT | NO | Message content (question or answer) |
| `timestamp` | TIMESTAMP WITH TIME ZONE | NO | Message creation timestamp |
| `metadata` | JSONB | YES | Additional context (e.g., selected text, retrieved chunks) |

**Constraints**:
- `session_id` must exist in `chat_sessions` (foreign key)
- `role` must be one of: 'user', 'assistant', 'system'
- Messages are deleted when parent session is deleted (CASCADE)

**Role Values**:
- **user**: Message from the reader
- **assistant**: Response from the chatbot
- **system**: System messages (e.g., context injection, currently unused but reserved)

**Metadata Examples**:

User message with selected text:
```json
{
  "selected_text": "Inverse kinematics is the process of determining joint angles...",
  "selection_source": "chapter-3-kinematics"
}
```

Assistant message with RAG context:
```json
{
  "retrieved_chunks": [
    {"chunk_id": "chunk_123", "score": 0.89},
    {"chunk_id": "chunk_456", "score": 0.85}
  ],
  "response_time_ms": 1234
}
```

---

## Vector Store (Qdrant Cloud)

While not a relational database, Qdrant stores the embedded book content for semantic search.

**Collection**: `book-content`

**Vector Configuration**:
- **Dimensions**: 1536 (OpenAI text-embedding-3-small)
- **Distance metric**: Cosine

**Payload Schema**:

```json
{
  "chunk_id": "string (UUID)",
  "text": "string (original chunk text, ~500 tokens)",
  "chapter": "string (e.g., 'Chapter 1: Introduction')",
  "section": "string (e.g., '1.2 Humanoid Robotics Overview')",
  "page_url": "string (relative URL to book page)",
  "token_count": "integer",
  "created_at": "ISO timestamp"
}
```

**Indexing**:
- Qdrant handles vector indexing automatically (HNSW algorithm)
- Payload fields are filterable for hybrid queries (e.g., filter by chapter + semantic search)

**Example Payload**:
```json
{
  "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "Inverse kinematics (IK) is the mathematical process of calculating the joint angles needed to position an end effector...",
  "chapter": "Chapter 3: Robot Kinematics",
  "section": "3.2 Inverse Kinematics",
  "page_url": "/docs/chapter-3/kinematics#inverse-kinematics",
  "token_count": 487,
  "created_at": "2025-12-17T10:30:00Z"
}
```

---

## Pydantic Models (Python)

For type safety and validation in the FastAPI backend.

```python
from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional, Literal

class ChatSessionCreate(BaseModel):
    """Request model for creating a new chat session"""
    metadata: Optional[dict] = {}

class ChatSessionResponse(BaseModel):
    """Response model for chat session"""
    session_id: UUID4
    created_at: datetime
    metadata: dict

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    """Request model for creating a message"""
    content: str
    role: Literal["user", "assistant", "system"] = "user"
    metadata: Optional[dict] = {}

class MessageResponse(BaseModel):
    """Response model for a message"""
    id: int
    session_id: UUID4
    role: str
    content: str
    timestamp: datetime
    metadata: dict

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    """Request model for sending a chat message"""
    message: str
    selected_text: Optional[str] = None

class ChatResponse(BaseModel):
    """Response model for chat completion"""
    session_id: UUID4
    user_message: MessageResponse
    assistant_message: MessageResponse
```

---

## SQLAlchemy Models (Python)

ORM models for database interaction.

```python
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, BigInteger, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    metadata = Column(JSONB, default={}, nullable=False)

    # Relationship to messages
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), CheckConstraint("role IN ('user', 'assistant', 'system')"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSONB, default={}, nullable=False)

    # Relationship to session
    session = relationship("ChatSession", back_populates="messages")
```

---

## Database Initialization

Migration script for creating tables:

```sql
-- migrations/001_initial_schema.sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create chat_sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for chat_sessions
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_metadata ON chat_sessions USING GIN(metadata);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for messages
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_messages_session_timestamp ON messages(session_id, timestamp);

-- Comments for documentation
COMMENT ON TABLE chat_sessions IS 'Stores chat session metadata';
COMMENT ON TABLE messages IS 'Stores all messages exchanged in chat sessions';
COMMENT ON COLUMN messages.role IS 'Message sender role: user, assistant, or system';
```

---

## Cleanup Strategy

Since sessions are ephemeral from the user perspective, implement a cleanup job to remove old sessions:

```sql
-- Delete sessions older than 30 days
DELETE FROM chat_sessions
WHERE created_at < NOW() - INTERVAL '30 days';

-- Orphaned message cleanup (should not happen with CASCADE, but defensive)
DELETE FROM messages
WHERE session_id NOT IN (SELECT session_id FROM chat_sessions);
```

Recommended: Run this as a scheduled job (daily or weekly) to manage database size within free tier limits.

---

## Storage Estimates

**Assumptions**:
- Average message length: 200 characters
- Average session: 10 messages (5 user + 5 assistant)
- Expected usage: 100 sessions per day

**Storage per Session**:
- Session row: ~200 bytes (with metadata)
- Message rows: 10 × 300 bytes = 3KB
- Total per session: ~3.2KB

**Monthly Storage**:
- 100 sessions/day × 30 days = 3000 sessions
- 3000 × 3.2KB = 9.6MB

**Annual Storage**:
- 3000 sessions/month × 12 months = 36,000 sessions
- 36,000 × 3.2KB = ~115MB

**Conclusion**: Well within Neon free tier limit (0.5GB = 512MB). Could retain ~4 years of history at this usage level.

---

## Future Extensions

Potential schema additions for future features (currently out of scope):

1. **User Authentication**:
   ```sql
   ALTER TABLE chat_sessions ADD COLUMN user_id UUID REFERENCES users(id);
   ```

2. **Feedback/Ratings**:
   ```sql
   CREATE TABLE message_feedback (
       feedback_id UUID PRIMARY KEY,
       message_id BIGINT REFERENCES messages(id),
       rating INTEGER CHECK (rating BETWEEN 1 AND 5),
       comment TEXT
   );
   ```

3. **Conversation Sharing**:
   ```sql
   ALTER TABLE chat_sessions ADD COLUMN is_public BOOLEAN DEFAULT FALSE;
   ALTER TABLE chat_sessions ADD COLUMN share_token UUID UNIQUE;
   ```

These are noted for future consideration but not implemented initially per the spec requirements.
