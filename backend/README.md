# Physical AI & Humanoid Robotics - RAG Backend

This is the FastAPI backend for the RAG (Retrieval-Augmented Generation) chatbot integrated into the Physical AI & Humanoid Robotics textbook.

## Features

- **RAG Chatbot**: Answers questions about the textbook using OpenAI GPT-4
- **Vector Search**: Semantic search using Qdrant Cloud
- **Text Selection Q&A**: Answer questions based on user-selected text
- **Chat History**: Persistent conversation storage
- **Document Management**: Automated ingestion of markdown content

## Tech Stack

- **FastAPI**: Modern Python web framework
- **OpenAI API**: GPT-4 for responses, text-embedding-3-small for embeddings
- **Qdrant Cloud**: Vector database for semantic search
- **Neon Serverless Postgres**: Relational database for chat history
- **SQLAlchemy**: ORM for database operations

## Setup Instructions

### 1. Prerequisites

- Python 3.10+
- OpenAI API key
- Qdrant Cloud account (free tier)
- Neon Serverless Postgres database

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Qdrant Cloud
QDRANT_URL=https://xxxxx.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=physical_ai_robotics

# Neon Postgres
DATABASE_URL=postgresql://user:password@ep-xxxxx.us-east-2.aws.neon.tech/database?sslmode=require

# Security
SECRET_KEY=generate_with_openssl_rand_hex_32
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 5. Ingest Documents

After the server is running, ingest the textbook content:

```bash
python ingest_documents.py
```

This will:
1. Read all markdown files from `../reusable-book/docs/`
2. Chunk them appropriately
3. Create embeddings using OpenAI
4. Store vectors in Qdrant
5. Save metadata in Postgres

## API Endpoints

### Chat Endpoints

#### `POST /api/chat`

Main chat endpoint with RAG support.

**Request:**
```json
{
  "message": "What is ROS 2?",
  "session_id": "optional-session-id",
  "selected_text": "optional selected text for context",
  "chapter_id": "optional-chapter-filter"
}
```

**Response:**
```json
{
  "response": "ROS 2 (Robot Operating System 2) is...",
  "session_id": "session-id",
  "sources": [
    {
      "title": "Module 1 - The Robotic Nervous System",
      "chapter_id": "02-module1-ros2",
      "score": 0.89,
      "content": "..."
    }
  ],
  "confidence": 0.89
}
```

#### `GET /api/chat/history/{session_id}`

Get chat history for a session.

### Search Endpoints

#### `POST /api/search`

Semantic search across the textbook.

**Request:**
```json
{
  "query": "how do I simulate a humanoid robot",
  "top_k": 5,
  "chapter_filter": "03-module2-digital-twin"
}
```

### Document Management

#### `POST /api/documents/ingest`

Ingest new documents (used by `ingest_documents.py`).

#### `GET /api/documents`

List all ingested documents.

#### `DELETE /api/documents/chapter/{chapter_id}`

Delete all documents for a specific chapter.

### Utility Endpoints

#### `GET /api/chapters/{chapter_id}/summary`

Generate an AI summary of a chapter.

## Architecture

```
┌─────────────────────────────────────────┐
│           Docusaurus Frontend           │
│          (React Components)             │
└──────────────────┬──────────────────────┘
                   │ HTTP/REST
                   ▼
┌─────────────────────────────────────────┐
│          FastAPI Backend                │
│  ┌─────────────────────────────────┐   │
│  │       RAG Service               │   │
│  │  • Query Processing             │   │
│  │  • Context Building             │   │
│  │  • Response Generation          │   │
│  └──────────┬──────────────┬───────┘   │
│             │              │            │
│             ▼              ▼            │
│  ┌──────────────┐  ┌──────────────┐   │
│  │   Qdrant     │  │  PostgreSQL  │   │
│  │   Service    │  │   (Neon)     │   │
│  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────┘
         │                    │
         ▼                    ▼
┌──────────────┐    ┌──────────────┐
│Qdrant Cloud  │    │Neon Postgres │
│(Vectors)     │    │(Chat History)│
└──────────────┘    └──────────────┘
         │
         ▼
┌──────────────┐
│  OpenAI API  │
│• GPT-4       │
│• Embeddings  │
└──────────────┘
```

## Database Schema

### Users
- id
- email
- username
- hashed_password
- software_background
- hardware_background

### ChatSessions
- id
- user_id (optional)
- session_id (UUID)
- created_at

### ChatMessages
- id
- session_id
- role (user/assistant)
- content
- context (selected text)
- metadata (sources, confidence)

### Documents
- id
- title
- content
- chapter_id
- vector_id (Qdrant reference)

## Development

### Run Tests

```bash
pytest
```

### Database Migrations

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Code Formatting

```bash
black app/
isort app/
```

## Deployment

### Environment Variables

Set all required environment variables in your deployment platform.

### Database Setup

1. Create a Neon Serverless Postgres database
2. Copy the connection string to `DATABASE_URL`
3. Run migrations: `alembic upgrade head`

### Qdrant Setup

1. Create a free cluster at [qdrant.io](https://cloud.qdrant.io/)
2. Copy the cluster URL and API key
3. Collection will be created automatically on first run

### Start Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Troubleshooting

### "Collection not found"

Run the server once to auto-create the Qdrant collection, then run ingestion.

### "Database connection error"

Check your `DATABASE_URL` format:
```
postgresql://user:password@host:5432/database?sslmode=require
```

### "OpenAI rate limit"

Consider implementing request queuing or upgrading your OpenAI plan.

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## License

MIT License - See LICENSE file for details
