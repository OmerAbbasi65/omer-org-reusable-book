"""Initialize database schema"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.db import engine
from src.models.database import Base
from src.config import settings

def init_database():
    """Create all database tables"""
    print("Initializing database...")

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Created all tables")

    # Create indexes (works for both SQLite and PostgreSQL)
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at
                ON chat_sessions(created_at)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_messages_session_id
                ON messages(session_id)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_messages_timestamp
                ON messages(timestamp)
            """))
            conn.commit()
            print("✓ Created indexes")
    except Exception as e:
        print(f"⚠ Note: Some indexes may not be created: {e}")

    print("\n✅ Database initialized successfully!")
    print("Tables created: chat_sessions, messages")

if __name__ == "__main__":
    init_database()
