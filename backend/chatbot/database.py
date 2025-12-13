from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Replace with your Neon connection string
DATABASE_URL = "postgresql://user:password@host:port/database"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
