# RAG Chatbot Backend

FastAPI backend service for the Physical AI & Humanoid Robotics book chatbot featuring Retrieval-Augmented Generation (RAG).

## Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key
- Qdrant Cloud account (free tier)
- Neon Postgres database (free tier)

### Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and connection strings
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Ingest book content (one-time setup):
```bash
python scripts/ingest_book_content.py
```

6. Start the server:
```bash
uvicorn src.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── api/                 # API endpoints
│   ├── services/            # Business logic
│   ├── models/              # Pydantic & SQLAlchemy models
│   ├── db/                  # Database connection
│   ├── config/              # Configuration
│   └── utils/               # Utilities
├── scripts/                 # One-time setup scripts
├── tests/                   # Test suite
└── requirements.txt         # Python dependencies
```

## Environment Variables

See `.env.example` for required environment variables.

## Development

Run tests:
```bash
pytest
```

Run with auto-reload:
```bash
uvicorn src.main:app --reload
```

## Deployment

See `../spec/001-rag-chatbot/quickstart.md` for deployment instructions.
