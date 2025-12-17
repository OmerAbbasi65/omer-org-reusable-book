# Complete Implementation Code: RAG Chatbot

This document contains all the code files needed to implement the RAG chatbot feature. Follow the quickstart.md for setup instructions, then use this document to create the implementation files.

## Backend Implementation

### 1. Database Models

**File: `backend/src/models/database.py`**

```python
"""SQLAlchemy ORM models for database tables."""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, BigInteger, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..db.base import Base


class ChatSession(Base):
    """Chat session model."""
    __tablename__ = "chat_sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    metadata = Column(JSONB, default={}, nullable=False)

    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    """Message model."""
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), CheckConstraint("role IN ('user', 'assistant', 'system')"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata = Column(JSONB, default={}, nullable=False)

    session = relationship("ChatSession", back_populates="messages")
```

**File: `backend/src/models/chat.py`**

```python
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
```

### 2. Services

**File: `backend/src/utils/embeddings.py`**

```python
"""Utilities for text embedding with OpenAI."""
from typing import List
from openai import OpenAI
from ..config.settings import settings

client = OpenAI(api_key=settings.openai_api_key)


async def embed_text(text: str) -> List[float]:
    """Embed a single text string using OpenAI embeddings."""
    response = client.embeddings.create(
        model=settings.embedding_model,
        input=text
    )
    return response.data[0].embedding


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed multiple text strings in batch."""
    response = client.embeddings.create(
        model=settings.embedding_model,
        input=texts
    )
    return [item.embedding for item in response.data]
```

**File: `backend/src/services/vector_service.py`**

```python
"""Vector search service using Qdrant."""
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, SearchParams
from ..config.settings import settings
from ..utils.embeddings import embed_text


class VectorService:
    """Service for vector similarity search operations."""

    def __init__(self):
        """Initialize Qdrant client."""
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key
        )
        self.collection_name = settings.qdrant_collection_name

    async def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Search for similar text chunks in the vector store."""
        if top_k is None:
            top_k = settings.top_k_retrieval

        query_vector = await embed_text(query)

        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            search_params=SearchParams(exact=False)
        )

        results = []
        for point in search_result:
            results.append({
                "chunk_id": point.id,
                "text": point.payload.get("text", ""),
                "chapter": point.payload.get("chapter", ""),
                "section": point.payload.get("section", ""),
                "page_url": point.payload.get("page_url", ""),
                "score": point.score
            })

        return results


vector_service = VectorService()
```

**File: `backend/src/services/rag_service.py`**

```python
"""RAG (Retrieval-Augmented Generation) service."""
from typing import List, Dict, Any, Optional
from .vector_service import vector_service


class RAGService:
    """Service for retrieving relevant context for RAG."""

    async def retrieve_context(
        self,
        query: str,
        selected_text: Optional[str] = None,
        top_k: int = None
    ) -> Dict[str, Any]:
        """Retrieve relevant book content for a user query."""
        chunks = await vector_service.search(query, top_k=top_k)

        context_parts = []

        if selected_text:
            context_parts.append(f"Selected Text:\n{selected_text}\n")

        if chunks:
            context_parts.append("Relevant Book Content:")
            for idx, chunk in enumerate(chunks, 1):
                chapter = chunk.get("chapter", "Unknown")
                section = chunk.get("section", "")
                text = chunk.get("text", "")
                context_parts.append(
                    f"\n[{idx}] From {chapter}" +
                    (f" - {section}" if section else "") +
                    f":\n{text}"
                )

        formatted_context = "\n".join(context_parts)

        return {
            "chunks": chunks,
            "formatted_context": formatted_context,
            "has_relevant_content": len(chunks) > 0
        }


rag_service = RAGService()
```

**File: `backend/src/services/chatbot_service.py`**

```python
"""Chatbot service using OpenAI for conversation management."""
from typing import Optional, Dict, Any, List
from openai import OpenAI
from ..config.settings import settings
from .rag_service import rag_service


class ChatbotService:
    """Service for managing chatbot conversations with RAG."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.chat_model
        self.system_prompt = """You are a helpful assistant for the Physical AI & Humanoid Robotics book.
Your primary role is to answer questions about the book's content, using the provided book excerpts.

When answering:
1. Prioritize information from the provided book content
2. If the book content doesn't contain the answer, use your general knowledge about Physical AI and Humanoid Robotics
3. Clarify when you're using general knowledge vs. book content
4. Be concise but thorough
5. If asked for simpler explanations, break down complex concepts into accessible language
6. When asked about relationships between topics, reference specific chapters/sections when possible
7. For homework help, explain concepts but don't provide direct answers

Always be helpful, accurate, and educational."""

    async def generate_response(
        self,
        message: str,
        selected_text: Optional[str] = None,
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """Generate a chatbot response using RAG."""
        rag_context = await rag_service.retrieve_context(message, selected_text)

        messages = [{"role": "system", "content": self.system_prompt}]

        if conversation_history:
            messages.extend(conversation_history)

        user_content = f"""{rag_context['formatted_context']}

User Question: {message}"""

        messages.append({"role": "user", "content": user_content})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

            assistant_message = response.choices[0].message.content

            return {
                "response": assistant_message,
                "retrieved_chunks": rag_context["chunks"],
                "has_book_content": rag_context["has_relevant_content"],
                "model": self.model
            }
        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")


chatbot_service = ChatbotService()
```

### 3. API Endpoints

**File: `backend/src/api/health.py`**

```python
"""Health check endpoint."""
from fastapi import APIRouter
from datetime import datetime
from ..models.chat import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now()
    )
```

**File: `backend/src/api/chat.py`**

```python
"""Chat API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from ..db.session import get_db
from ..models.database import ChatSession, Message
from ..models.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatRequest,
    ChatResponse,
    MessageResponse
)
from ..services.chatbot_service import chatbot_service

router = APIRouter(prefix="/chat")


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    session_data: ChatSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat session."""
    new_session = ChatSession(metadata=session_data.metadata)
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session


@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: UUID,
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send a message and get chatbot response."""
    # Verify session exists
    result = await db.execute(select(ChatSession).where(ChatSession.session_id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get conversation history
    history_result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.timestamp)
    )
    history = history_result.scalars().all()

    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in history
    ]

    # Save user message
    user_message = Message(
        session_id=session_id,
        role="user",
        content=chat_request.message,
        metadata={"selected_text": chat_request.selected_text} if chat_request.selected_text else {}
    )
    db.add(user_message)

    # Generate response
    try:
        response_data = await chatbot_service.generate_response(
            message=chat_request.message,
            selected_text=chat_request.selected_text,
            conversation_history=conversation_history
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    # Save assistant message
    assistant_message = Message(
        session_id=session_id,
        role="assistant",
        content=response_data["response"],
        metadata={
            "retrieved_chunks": [
                {"chunk_id": str(c.get("chunk_id")), "score": c.get("score")}
                for c in response_data.get("retrieved_chunks", [])
            ]
        }
    )
    db.add(assistant_message)

    await db.commit()
    await db.refresh(user_message)
    await db.refresh(assistant_message)

    return ChatResponse(
        session_id=session_id,
        user_message=MessageResponse.model_validate(user_message),
        assistant_message=MessageResponse.model_validate(assistant_message)
    )


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all messages in a session."""
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.timestamp)
    )
    messages = result.scalars().all()
    return [MessageResponse.model_validate(msg) for msg in messages]
```

### 4. Main Application

**File: `backend/src/main.py`**

```python
"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config.settings import settings
from .api import health, chat

app = FastAPI(
    title="RAG Chatbot API",
    description="Backend API for the integrated chatbot",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])


@app.get("/")
async def root():
    return {"message": "RAG Chatbot API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

## Frontend Implementation

### React Components

**File: `src/components/ChatBot/index.tsx`**

```typescript
import React, { useState } from 'react';
import ChatButton from './ChatButton';
import ChatPanel from './ChatPanel';
import useChatBot from './hooks/useChatBot';
import useTextSelection from './hooks/useTextSelection';
import TextSelector from './TextSelector';

export default function ChatBot() {
  const [isOpen, setIsOpen] = useState(false);
  const { selectedText, selectionPosition, clearSelection } = useTextSelection();
  const chatBot = useChatBot();

  const handleOpenWithSelection = () => {
    if (selectedText) {
      chatBot.setSelectedText(selectedText);
      clearSelection();
    }
    setIsOpen(true);
  };

  const handleClose = () => {
    setIsOpen(false);
    chatBot.resetSession();
  };

  return (
    <>
      {selectedText && selectionPosition && !isOpen && (
        <TextSelector
          position={selectionPosition}
          onAsk={handleOpenWithSelection}
          onDismiss={clearSelection}
        />
      )}

      <ChatButton onClick={() => setIsOpen(!isOpen)} isOpen={isOpen} />

      {isOpen && <ChatPanel chatBot={chatBot} onClose={handleClose} />}
    </>
  );
}
```

**File: `src/components/ChatBot/ChatButton.tsx`**

```typescript
import React from 'react';
import styles from './styles.module.css';

interface ChatButtonProps {
  onClick: () => void;
  isOpen: boolean;
}

export default function ChatButton({ onClick, isOpen }: ChatButtonProps) {
  return (
    <button
      className={styles.chatButton}
      onClick={onClick}
      aria-label={isOpen ? "Close chatbot" : "Open chatbot"}
    >
      {isOpen ? '✕' : '💬'}
    </button>
  );
}
```

**File: `src/components/ChatBot/ChatPanel.tsx`**

```typescript
import React from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import styles from './styles.module.css';

interface ChatPanelProps {
  chatBot: any;
  onClose: () => void;
}

export default function ChatPanel({ chatBot, onClose }: ChatPanelProps) {
  return (
    <div className={styles.chatPanel}>
      <div className={styles.chatHeader}>
        <h3>AI Assistant</h3>
        <button onClick={onClose} className={styles.closeButton}>✕</button>
      </div>

      <MessageList messages={chatBot.messages} isLoading={chatBot.isLoading} />

      <MessageInput
        onSend={chatBot.sendMessage}
        disabled={chatBot.isLoading}
      />
    </div>
  );
}
```

**File: `src/components/ChatBot/MessageList.tsx`**

```typescript
import React, { useEffect, useRef } from 'react';
import styles from './styles.module.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export default function MessageList({ messages, isLoading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className={styles.chatMessages}>
      {messages.length === 0 && (
        <div className={styles.welcomeMessage}>
          <p>👋 Hello! I'm your AI assistant for the Physical AI & Humanoid Robotics book.</p>
          <p>Ask me anything about the book's content!</p>
        </div>
      )}

      {messages.map((message, index) => (
        <div
          key={index}
          className={`${styles.message} ${styles[message.role]}`}
        >
          <div className={styles.messageContent}>{message.content}</div>
        </div>
      ))}

      {isLoading && (
        <div className={`${styles.message} ${styles.assistant}`}>
          <div className={styles.messageContent}>
            <span className={styles.loadingDots}>Thinking</span>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
```

**File: `src/components/ChatBot/MessageInput.tsx`**

```typescript
import React, { useState } from 'react';
import styles from './styles.module.css';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
}

export default function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  return (
    <form className={styles.chatInput} onSubmit={handleSubmit}>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your question..."
        disabled={disabled}
      />
      <button type="submit" disabled={disabled || !input.trim()}>
        Send
      </button>
    </form>
  );
}
```

**File: `src/components/ChatBot/TextSelector.tsx`**

```typescript
import React from 'react';
import styles from './styles.module.css';

interface TextSelectorProps {
  position: { x: number; y: number };
  onAsk: () => void;
  onDismiss: () => void;
}

export default function TextSelector({ position, onAsk, onDismiss }: TextSelectorProps) {
  return (
    <div
      className={styles.textSelector}
      style={{
        left: `${position.x}px`,
        top: `${position.y + 10}px`,
      }}
    >
      <button onClick={onAsk}>Ask about this</button>
      <button onClick={onDismiss} className={styles.dismissButton}>✕</button>
    </div>
  );
}
```

### Hooks

**File: `src/components/ChatBot/hooks/useChatBot.ts`**

```typescript
import { useState, useCallback } from 'react';

const API_URL = 'http://localhost:8000/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function useChatBot() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState<string | null>(null);

  const createSession = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/chat/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ metadata: {} }),
      });
      const data = await response.json();
      setSessionId(data.session_id);
      return data.session_id;
    } catch (error) {
      console.error('Failed to create session:', error);
      return null;
    }
  }, []);

  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim()) return;

    let currentSessionId = sessionId;
    if (!currentSessionId) {
      currentSessionId = await createSession();
      if (!currentSessionId) return;
    }

    const userMessage: Message = {
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/chat/sessions/${currentSessionId}/messages`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message,
            selected_text: selectedText,
          }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.assistant_message.content,
        timestamp: new Date(data.assistant_message.timestamp),
      };

      setMessages(prev => [...prev, assistantMessage]);
      setSelectedText(null);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, selectedText, createSession]);

  const resetSession = useCallback(() => {
    setSessionId(null);
    setMessages([]);
    setSelectedText(null);
  }, []);

  return {
    messages,
    isLoading,
    sendMessage,
    resetSession,
    setSelectedText,
  };
}
```

**File: `src/components/ChatBot/hooks/useTextSelection.ts`**

```typescript
import { useState, useEffect } from 'react';

interface SelectionPosition {
  x: number;
  y: number;
}

export default function useTextSelection() {
  const [selectedText, setSelectedText] = useState<string>('');
  const [selectionPosition, setSelectionPosition] = useState<SelectionPosition | null>(null);

  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      const text = selection?.toString().trim() || '';

      if (text && text.length > 10) {
        setSelectedText(text);

        const range = selection!.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        setSelectionPosition({
          x: rect.left + rect.width / 2,
          y: rect.bottom + window.scrollY,
        });
      } else {
        setSelectedText('');
        setSelectionPosition(null);
      }
    };

    document.addEventListener('selectionchange', handleSelection);
    return () => document.removeEventListener('selectionchange', handleSelection);
  }, []);

  const clearSelection = () => {
    setSelectedText('');
    setSelectionPosition(null);
    window.getSelection()?.removeAllRanges();
  };

  return { selectedText, selectionPosition, clearSelection };
}
```

### Styles

**File: `src/components/ChatBot/styles.module.css`**

```css
.chatButton {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #2563eb;
  color: white;
  border: none;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  transition: all 0.3s ease;
}

.chatButton:hover {
  background: #1d4ed8;
  transform: scale(1.05);
}

.chatPanel {
  position: fixed;
  bottom: 90px;
  right: 20px;
  width: 400px;
  height: 600px;
  max-width: calc(100vw - 40px);
  max-height: calc(100vh - 120px);
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  overflow: hidden;
}

@media (max-width: 768px) {
  .chatPanel {
    width: calc(100vw - 40px);
    height: calc(100vh - 120px);
  }
}

.chatHeader {
  padding: 16px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chatHeader h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.closeButton {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.closeButton:hover {
  background: #e5e7eb;
}

.chatMessages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.welcomeMessage {
  text-align: center;
  color: #6b7280;
  padding: 20px;
}

.welcomeMessage p {
  margin: 8px 0;
}

.message {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 12px;
  word-wrap: break-word;
}

.message.user {
  align-self: flex-end;
  background: #2563eb;
  color: white;
  margin-left: auto;
}

.message.assistant {
  align-self: flex-start;
  background: #f3f4f6;
  color: #1f2937;
}

.messageContent {
  line-height: 1.5;
}

.loadingDots::after {
  content: '...';
  animation: dots 1.5s steps(4, end) infinite;
}

@keyframes dots {
  0%, 20% { content: '.'; }
  40% { content: '..'; }
  60%, 100% { content: '...'; }
}

.chatInput {
  padding: 16px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 8px;
}

.chatInput input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
}

.chatInput input:focus {
  border-color: #2563eb;
}

.chatInput button {
  padding: 10px 20px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.chatInput button:hover:not(:disabled) {
  background: #1d4ed8;
}

.chatInput button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.textSelector {
  position: absolute;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 8px;
  display: flex;
  gap: 8px;
  z-index: 999;
  transform: translateX(-50%);
}

.textSelector button {
  padding: 8px 16px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  white-space: nowrap;
}

.textSelector button:hover {
  background: #1d4ed8;
}

.dismissButton {
  background: #f3f4f6 !important;
  color: #6b7280 !important;
  padding: 8px 12px !important;
}

.dismissButton:hover {
  background: #e5e7eb !important;
}
```

## Integration

**File: `src/theme/Root.tsx`** (create via `npm run swizzle @docusaurus/theme-classic Root -- --eject`)

```typescript
import React from 'react';
import ChatBot from '@site/src/components/ChatBot';

export default function Root({children}) {
  return (
    <>
      {children}
      <ChatBot />
    </>
  );
}
```

## Next Steps

1. Copy all backend files to their respective locations
2. Copy all frontend files to their respective locations
3. Follow quickstart.md for environment setup
4. Run database migrations
5. Ingest book content
6. Start both backend and frontend servers
7. Test the chatbot functionality

Refer to tasks.md for the complete implementation checklist.
