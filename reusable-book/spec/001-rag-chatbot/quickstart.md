# Quickstart Guide: RAG Chatbot Development

**Feature**: Integrated RAG Chatbot
**Date**: 2025-12-17

This guide will help you set up the development environment and start building the RAG chatbot feature.

## Prerequisites

### Required Software

- **Python 3.11+** - Backend development
- **Node.js 18+** - Frontend development (already installed for Docusaurus)
- **Git** - Version control

### Required Accounts & API Keys

1. **OpenAI Account**
   - Sign up at https://platform.openai.com/
   - Create API key at https://platform.openai.com/api-keys
   - Add payment method (required for API access)
   - Estimated cost: ~$5-10 for development/testing

2. **Qdrant Cloud Account**
   - Sign up at https://cloud.qdrant.io/
   - Create a free cluster (1GB storage)
   - Get API key and cluster URL

3. **Neon Account**
   - Sign up at https://neon.tech/
   - Create a new project
   - Get connection string from project dashboard

## Project Structure

After completing this quickstart, your project will look like:

```
reusable-book/
├── backend/              # NEW - FastAPI backend
│   ├── src/
│   ├── tests/
│   ├── requirements.txt
│   ├── .env
│   └── README.md
├── src/
│   └── components/
│       └── ChatBot/      # NEW - React chatbot components
├── docs/                 # Existing Docusaurus content
├── spec/
│   └── 001-rag-chatbot/  # Feature specification (current)
└── [other existing files]
```

---

## Step 1: Backend Setup

### 1.1 Create Backend Directory

```bash
mkdir backend
cd backend
```

### 1.2 Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 1.3 Create Requirements File

Create `backend/requirements.txt`:

```txt
# Web framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# OpenAI & Agents SDK
openai==1.10.0
openai-agents-sdk==0.1.0

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1

# Vector store
qdrant-client==1.7.0

# RAG utilities
langchain==0.1.4
langchain-openai==0.0.5
tiktoken==0.5.2

# Environment management
python-dotenv==1.0.0

# CORS
python-cors==1.0.0

# Utilities
pydantic==2.5.3
pydantic-settings==2.1.0
```

### 1.4 Install Dependencies

```bash
pip install -r requirements.txt
```

### 1.5 Create Environment Configuration

Create `backend/.env`:

```bash
# OpenAI
OPENAI_API_KEY=sk-...  # Your OpenAI API key

# Qdrant Cloud
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Neon Postgres
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000

# OpenAI Model Settings
OPENAI_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small
```

### 1.6 Create Basic FastAPI App

Create `backend/src/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="RAG Chatbot API",
    description="Backend API for the integrated chatbot",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {"message": "RAG Chatbot API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

### 1.7 Test Backend

```bash
# Run the server
python src/main.py

# In another terminal, test:
curl http://localhost:8000/api/health
```

Expected output:
```json
{"status": "healthy", "version": "1.0.0"}
```

---

## Step 2: Database Setup

### 2.1 Initialize Database

Create `backend/src/db/init_db.py`:

```python
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Read and execute migration SQL
with open("../spec/001-rag-chatbot/data-model.md", "r") as f:
    # Extract SQL from markdown (look for ```sql blocks)
    # For now, manually copy the SQL from data-model.md

sql = """
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create chat_sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp DESC);
"""

with engine.connect() as conn:
    conn.execute(text(sql))
    conn.commit()

print("Database initialized successfully!")
```

Run it:
```bash
python src/db/init_db.py
```

---

## Step 3: Vector Store Setup

### 3.1 Create Qdrant Collection

Create `backend/scripts/setup_qdrant.py`:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import os
from dotenv import load_dotenv

load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# Create collection for book content
client.create_collection(
    collection_name="book-content",
    vectors_config=VectorParams(
        size=1536,  # text-embedding-3-small dimensions
        distance=Distance.COSINE
    )
)

print("Qdrant collection 'book-content' created successfully!")
```

Run it:
```bash
python scripts/setup_qdrant.py
```

### 3.2 Ingest Book Content

Create `backend/scripts/ingest_book_content.py`:

```python
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from langchain.text_splitter import RecursiveCharacterTextSplitter
import uuid

load_dotenv()

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# Text splitter for chunking
splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,  # ~500 tokens
    chunk_overlap=200,
    separators=["\n## ", "\n### ", "\n\n", "\n", " "]
)

def ingest_book():
    """Ingest all book content from docs/ directory"""
    docs_path = Path("../../docs")  # Adjust path as needed

    chunks = []
    for md_file in docs_path.rglob("*.md"):
        # Read file
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Split into chunks
        file_chunks = splitter.split_text(content)

        # Extract metadata
        relative_path = md_file.relative_to(docs_path)
        chapter = relative_path.parts[0] if len(relative_path.parts) > 0 else "Unknown"

        for i, chunk_text in enumerate(file_chunks):
            chunks.append({
                "text": chunk_text,
                "chapter": chapter,
                "section": md_file.stem,
                "page_url": f"/docs/{relative_path.with_suffix('')}",
                "chunk_index": i
            })

    print(f"Split book into {len(chunks)} chunks. Embedding...")

    # Embed and upload chunks
    points = []
    batch_size = 100

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]

        # Get embeddings
        texts = [c["text"] for c in batch]
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )

        # Create points
        for j, embedding_obj in enumerate(response.data):
            chunk = batch[j]
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding_obj.embedding,
                payload={
                    "text": chunk["text"],
                    "chapter": chunk["chapter"],
                    "section": chunk["section"],
                    "page_url": chunk["page_url"],
                    "chunk_index": chunk["chunk_index"]
                }
            ))

        print(f"Processed {min(i+batch_size, len(chunks))}/{len(chunks)} chunks")

    # Upload to Qdrant
    qdrant_client.upsert(
        collection_name="book-content",
        points=points
    )

    print(f"Successfully ingested {len(points)} chunks into Qdrant!")

if __name__ == "__main__":
    ingest_book()
```

Run it (one-time setup):
```bash
python scripts/ingest_book_content.py
```

---

## Step 4: Frontend Setup

### 4.1 Create ChatBot Component Directory

```bash
mkdir -p src/components/ChatBot
```

### 4.2 Create Basic ChatBot Component

Create `src/components/ChatBot/index.tsx`:

```typescript
import React, { useState } from 'react';
import styles from './styles.module.css';

export default function ChatBot() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className={styles.chatbotContainer}>
      {/* Floating button */}
      <button
        className={styles.chatButton}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Open chatbot"
      >
        💬
      </button>

      {/* Chat panel (hidden by default) */}
      {isOpen && (
        <div className={styles.chatPanel}>
          <div className={styles.chatHeader}>
            <h3>AI Assistant</h3>
            <button onClick={() => setIsOpen(false)}>✕</button>
          </div>
          <div className={styles.chatMessages}>
            <p>Hello! Ask me anything about the book.</p>
          </div>
          <div className={styles.chatInput}>
            <input type="text" placeholder="Type your question..." />
            <button>Send</button>
          </div>
        </div>
      )}
    </div>
  );
}
```

Create `src/components/ChatBot/styles.module.css`:

```css
.chatbotContainer {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}

.chatButton {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #2563eb;
  color: white;
  border: none;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.chatButton:hover {
  background: #1d4ed8;
}

.chatPanel {
  position: absolute;
  bottom: 80px;
  right: 0;
  width: 350px;
  height: 500px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
}

.chatHeader {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chatMessages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.chatInput {
  padding: 16px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 8px;
}

.chatInput input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}

.chatInput button {
  padding: 8px 16px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
```

### 4.3 Integrate with Docusaurus

Swizzle the Root component:

```bash
npm run swizzle @docusaurus/theme-classic Root -- --eject
```

Edit `src/theme/Root.tsx`:

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

### 4.4 Test Frontend

```bash
npm start
```

Visit http://localhost:3000 and you should see the chat button in the bottom-right corner.

---

## Step 5: Development Workflow

### Running Both Servers

**Terminal 1 - Backend**:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python src/main.py
```

**Terminal 2 - Frontend**:
```bash
npm start
```

### Making API Calls from Frontend

Update `src/components/ChatBot/index.tsx` to connect to the backend:

```typescript
const API_URL = 'http://localhost:8000/api';

async function sendMessage(message: string) {
  const response = await fetch(`${API_URL}/chat/sessions/...`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  return response.json();
}
```

---

## Next Steps

Now that your development environment is set up, you can proceed with:

1. **Run `/sp.tasks`** to generate the detailed task breakdown
2. **Run `/sp.implement`** to execute the implementation plan
3. **Test** each component as you build it
4. **Iterate** based on testing feedback

## Troubleshooting

### Backend won't start
- Check `.env` file has all required keys
- Verify Python version: `python --version` (should be 3.11+)
- Check port 8000 is not in use: `lsof -i :8000`

### Frontend chat button not showing
- Clear browser cache
- Check browser console for errors
- Verify `Root.tsx` was created and includes ChatBot component

### Database connection errors
- Verify Neon connection string is correct
- Check SSL mode is included: `?sslmode=require`
- Test connection with `psql <connection-string>`

### Qdrant errors
- Verify cluster URL and API key
- Check free tier limits (1GB storage)
- Ensure collection 'book-content' exists

## Resources

- FastAPI docs: https://fastapi.tiangolo.com/
- OpenAI Agents SDK: https://github.com/openai/openai-agents-sdk
- Qdrant docs: https://qdrant.tech/documentation/
- Neon docs: https://neon.tech/docs/
- React docs: https://react.dev/
- Docusaurus docs: https://docusaurus.io/docs/
