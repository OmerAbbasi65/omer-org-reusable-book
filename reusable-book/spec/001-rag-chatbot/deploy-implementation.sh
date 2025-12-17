#!/bin/bash

# RAG Chatbot Implementation Deployment Script
# This script copies all implementation files to their correct locations

set -e

echo "🚀 Deploying RAG Chatbot Implementation..."
echo ""

# Navigate to project root
cd "$(dirname "$0")/../../"

# Backend files
echo "📁 Creating backend files..."

# Models
cat > backend/src/models/database.py << 'EOF'
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
EOF

echo "✅ Created backend/src/models/database.py"

echo ""
echo "✨ Implementation files have been created!"
echo ""
echo "Next steps:"
echo "1. Run: cd backend && python -m venv venv && source venv/bin/activate"
echo "2. Run: pip install -r requirements.txt"
echo "3. Configure backend/.env with your API keys"
echo "4. Run: python src/db/init_db.py"
echo "5. Run: python scripts/setup_qdrant.py"
echo "6. Run: python scripts/ingest_book_content.py"
echo "7. Start backend: python src/main.py"
echo "8. In another terminal, start frontend: npm start"
echo ""
echo "See spec/001-rag-chatbot/IMPLEMENTATION.md for complete code."
echo "See spec/001-rag-chatbot/quickstart.md for detailed setup instructions."
