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
    result = await db.execute(select(ChatSession).where(ChatSession.session_id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

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

    user_message = Message(
        session_id=session_id,
        role="user",
        content=chat_request.message,
        metadata={"selected_text": chat_request.selected_text} if chat_request.selected_text else {}
    )
    db.add(user_message)

    try:
        response_data = await chatbot_service.generate_response(
            message=chat_request.message,
            selected_text=chat_request.selected_text,
            conversation_history=conversation_history
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

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
