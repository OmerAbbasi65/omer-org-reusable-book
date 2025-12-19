---
title: Physical AI & Humanoid Robotics RAG Backend
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
app_port: 7860
---

# Physical AI & Humanoid Robotics - RAG Backend

This is the FastAPI backend for the RAG (Retrieval-Augmented Generation) chatbot integrated into the Physical AI & Humanoid Robotics textbook.

## Hugging Face Spaces Deployment

This application is configured to run on Hugging Face Spaces using Docker. The API will be available at port 7860.

## Features

- **RAG Chatbot**: Answers questions about the textbook using OpenAI GPT-4
- **Vector Search**: Semantic search using Qdrant Cloud
- **Text Selection Q&A**: Answer questions based on user-selected text
- **Chat History**: Persistent conversation storage
- **Document Management**: Automated ingestion of markdown content

## Tech Stack

- **FastAPI**: Modern Python web framework
- **OpenRouter**: Access to multiple LLMs (Claude, GPT-4, Gemini, etc.)
- **HuggingFace Embeddings**: Free local embeddings (all-MiniLM-L6-v2)
- **Qdrant Cloud**: Vector database for semantic search
- **Neon Serverless Postgres**: Relational database for chat history
- **SQLAlchemy**: ORM for database operations

## Setup Instructions

### 1. Prerequisites

- Python 3.11+
- OpenRouter API key (supports multiple LLM providers)
- Qdrant Cloud account (free tier available)
- Neon Serverless Postgres database (free tier available)

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
# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Qdrant Cloud
QDRANT_URL=https://xxxxx.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=rag-chatbot

# Neon Postgres
DATABASE_URL=postgresql://user:password@ep-xxxxx.us-east-2.aws.neon.tech/database?sslmode=require

# HuggingFace Embeddings (free, runs locally)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Application Settings
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=https://your-frontend-url.com,https://another-allowed-origin.com

# Security
SECRET_KEY=generate_with_openssl_rand_hex_32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
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
3. Create embeddings using HuggingFace
4. Store vectors in Qdrant
5. Save metadata in Postgres

## Deploying to Hugging Face Spaces

### Step 1: Create a New Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Choose a name for your space
4. Select **Docker** as the SDK
5. Choose **Public** or **Private** visibility
6. Click "Create Space"

### Step 2: Push Your Code

From the backend directory, initialize git and push to your space:

```bash
cd backend
git init
git remote add space https://huggingface.co/spaces/YOUR-USERNAME/YOUR-SPACE-NAME
git add .
git commit -m "Initial commit"
git push space main
```

### Step 3: Configure Environment Variables

In your Hugging Face Space settings, add the following secrets:

1. Go to your Space's Settings > Repository secrets
2. Add each environment variable:

**Required Variables:**
- `OPENROUTER_API_KEY` - Your OpenRouter API key from [openrouter.ai](https://openrouter.ai)
- `DATABASE_URL` - Your Neon Postgres connection string
- `QDRANT_URL` - Your Qdrant Cloud URL
- `QDRANT_API_KEY` - Your Qdrant API key
- `SECRET_KEY` - Generate with: `openssl rand -hex 32`

**Optional Variables:**
- `OPENROUTER_MODEL` - Default: `anthropic/claude-3.5-sonnet`
- `QDRANT_COLLECTION_NAME` - Default: `rag-chatbot`
- `EMBEDDING_MODEL` - Default: `all-MiniLM-L6-v2`
- `CORS_ORIGINS` - Comma-separated list of allowed origins
- `ENVIRONMENT` - Default: `production`
- `DEBUG` - Default: `False`

### Step 4: Wait for Build

Hugging Face Spaces will automatically build your Docker container. This may take 5-10 minutes. You can monitor the build logs in the "Logs" tab.

### Step 5: Test Your API

Once deployed, your API will be available at:
```
https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space
```

Test the health endpoint:
```bash
curl https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/health
```

Test the chat endpoint:
```bash
curl -X POST https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is ROS 2?",
    "session_id": "test-session"
  }'
```

### Step 6: Ingest Documents (Optional)

If you need to ingest documents into Qdrant, you can either:

1. **Run locally then deploy**: Ingest documents on your local machine with the same Qdrant credentials, then deploy
2. **Use the API endpoint**: Use the `/api/documents/ingest` endpoint to upload documents via API

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
