from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import uuid

from .config import settings
from .database import get_db, init_db
from .schemas import (
    ChatMessageRequest,
    ChatResponse
)
from .simple_chat_service import simple_chat_service
from . import models

# Initialize FastAPI app
app = FastAPI(
    title="Physical AI & Humanoid Robotics Simple Chatbot API",
    description="Simple chatbot powered by Claude (Anthropic)",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("Database initialized")
    print("Claude (Anthropic) configured")
    print("Simple Chatbot API is ready")

@app.get("/")
async def root():
    return {
        "message": "Physical AI & Humanoid Robotics Simple Chatbot API",
        "version": "1.0.0",
        "status": "operational",
        "mode": "Simple Chat (No RAG)"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "mode": "simple_chat"}

# ============================================================================
# CHAT ENDPOINTS
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Main chat endpoint using Claude.
    Supports:
    - General questions about robotics and AI
    - Context-specific questions on selected text
    """
    try:
        # Get or create session
        if request.session_id:
            session = db.query(models.ChatSession).filter(
                models.ChatSession.session_id == request.session_id
            ).first()
            if not session:
                session = models.ChatSession(session_id=request.session_id)
                db.add(session)
                db.commit()
        else:
            session_id = str(uuid.uuid4())
            session = models.ChatSession(session_id=session_id)
            db.add(session)
            db.commit()

        # Get conversation history
        history_messages = db.query(models.ChatMessage).filter(
            models.ChatMessage.session_id == session.id
        ).order_by(models.ChatMessage.created_at).limit(10).all()

        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in history_messages
        ]

        # Generate response using Claude
        chat_response = simple_chat_service.generate_response(
            query=request.message,
            selected_text=request.selected_text,
            conversation_history=conversation_history
        )

        # Save user message
        user_message = models.ChatMessage(
            session_id=session.id,
            role="user",
            content=request.message,
            context=request.selected_text
        )
        db.add(user_message)

        # Save assistant response
        assistant_message = models.ChatMessage(
            session_id=session.id,
            role="assistant",
            content=chat_response["response"],
            extra_metadata={
                "sources": chat_response["sources"],
                "confidence": chat_response["confidence"]
            }
        )
        db.add(assistant_message)
        db.commit()

        return ChatResponse(
            response=chat_response["response"],
            session_id=session.session_id,
            sources=chat_response["sources"],
            confidence=chat_response["confidence"]
        )

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )

@app.get("/api/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get chat history for a session"""
    session = db.query(models.ChatSession).filter(
        models.ChatSession.session_id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.query(models.ChatMessage).filter(
        models.ChatMessage.session_id == session.id
    ).order_by(models.ChatMessage.created_at).all()

    return {
        "session_id": session_id,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "context": msg.context,
                "metadata": msg.extra_metadata,
                "created_at": msg.created_at
            }
            for msg in messages
        ]
    }

@app.delete("/api/chat/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Clear chat history for a session"""
    session = db.query(models.ChatSession).filter(
        models.ChatSession.session_id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Delete all messages for this session
    db.query(models.ChatMessage).filter(
        models.ChatMessage.session_id == session.id
    ).delete()
    db.commit()

    return {
        "status": "success",
        "message": f"Cleared chat history for session {session_id}"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
