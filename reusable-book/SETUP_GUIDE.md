# RAG Chatbot Setup Guide

Complete setup guide for the integrated RAG chatbot in the Physical AI & Humanoid Robotics book.

## Prerequisites

- **Python 3.11+** installed
- **Node.js 18+** installed
- **Git** installed
- **API Keys** ready:
  - OpenRouter API key (provided) OR OpenAI API key
  - Qdrant Cloud account and API key
  - Neon Serverless Postgres database

## Step 1: Environment Setup

### 1.1 Create Backend Environment File

```bash
cd backend
cp .env.example .env
```

### 1.2 Configure `.env` File

Open `backend/.env` and add your credentials:

```bash
# Use OpenRouter (recommended - key provided)
OPENROUTER_API_KEY=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
USE_OPENROUTER=true
OPENROUTER_MODEL=openai/gpt-4-turbo-preview

# OR use OpenAI directly (if you prefer)
# OPENAI_API_KEY=sk-...
# USE_OPENROUTER=false

# Qdrant Cloud (sign up at https://cloud.qdrant.io/)
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Neon Postgres (sign up at https://neon.tech/)
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000

# Model Settings
EMBEDDING_MODEL=text-embedding-3-small
```

## Step 2: Install Dependencies

### 2.1 Backend Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2.2 Frontend Dependencies

```bash
# From repo root
npm install
```

## Step 3: Set Up Databases

### 3.1 Initialize Postgres Database

```bash
cd backend
python scripts/init_db.py
```

Expected output:
```
✓ Created pgcrypto extension
✓ Created all tables
✓ Created indexes
✅ Database initialized successfully!
```

### 3.2 Set Up Qdrant Collection

```bash
python scripts/setup_qdrant.py
```

Expected output:
```
✅ Created Qdrant collection 'book-content'
   - Vector size: 1536 (text-embedding-3-small)
   - Distance metric: COSINE
```

### 3.3 Ingest Book Content

```bash
python scripts/ingest_book_content.py
```

This will:
- Read all Markdown files from `docs/`
- Split them into ~500-token chunks
- Embed each chunk using OpenAI embeddings
- Upload to Qdrant

Expected output:
```
✓ Split book into XXX chunks
  Processed XXX/XXX chunks
✅ Successfully ingested XXX chunks into Qdrant!
```

**Note**: This is a one-time setup. If you update book content, re-run this script.

## Step 4: Run the Application

### 4.1 Start Backend Server

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python src/main.py
```

Backend runs on: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

### 4.2 Start Frontend (Docusaurus)

```bash
# From repo root
npm start
```

Frontend runs on: http://localhost:3000

## Step 5: Test the Chatbot

1. Open http://localhost:3000 in your browser
2. Look for the blue chat button (💬) in the bottom-right corner
3. Click the button to open the chatbot
4. Try asking: "What is inverse kinematics?"
5. Try selecting text and clicking "Ask about this"

### Test Checklist

- [ ] Chat button appears on all pages
- [ ] Click button → chat panel opens
- [ ] Ask a question → receive answer within 5 seconds
- [ ] Close and reopen chat → fresh session starts
- [ ] Select text → "Ask about this" popup appears
- [ ] Click popup → chat opens with selected text shown
- [ ] Ask follow-up questions → maintains context
- [ ] Responsive on mobile (test at 375px width)

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
- **Solution**: Activate virtual environment and install dependencies
  ```bash
  source venv/bin/activate
  pip install -r requirements.txt
  ```

**Error**: `sqlalchemy.exc.OperationalError`
- **Solution**: Check DATABASE_URL in `.env` is correct
- Verify Neon database is running and accessible

**Error**: `openai.AuthenticationError`
- **Solution**: Verify OPENROUTER_API_KEY or OPENAI_API_KEY in `.env`
- Make sure USE_OPENROUTER is set correctly (true/false)

### Qdrant errors

**Error**: `QdrantException: Unauthorized`
- **Solution**: Check QDRANT_API_KEY in `.env`

**Error**: Collection not found
- **Solution**: Run `python scripts/setup_qdrant.py`

### Frontend errors

**Error**: Chat button doesn't appear
- **Solution**: Verify `src/theme/Root.tsx` exists and includes ChatBot
- Clear browser cache
- Check browser console for errors

**Error**: CORS errors in browser console
- **Solution**: Verify CORS_ORIGINS in backend `.env` includes http://localhost:3000
- Restart backend server

**Error**: "Failed to create session"
- **Solution**: Verify backend is running at http://localhost:8000
- Check backend logs for errors
- Test health endpoint: http://localhost:8000/api/health

### Embedding/Ingestion errors

**Error**: "Rate limit exceeded" during ingestion
- **Solution**: OpenRouter/OpenAI rate limits
- Wait a few minutes and retry
- Reduce batch size in `ingest_book_content.py` (change batch_size from 100 to 50)

**Error**: No chunks ingested
- **Solution**: Verify `docs/` directory contains Markdown files
- Check file paths in script output

## Development Tips

### Updating Book Content

If you modify book content in `docs/`:

```bash
cd backend
python scripts/ingest_book_content.py
```

This will re-embed and update Qdrant with new content.

### Viewing API Documentation

While backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Monitoring Logs

Backend logs show:
- Incoming API requests
- RAG retrieval results
- Errors and warnings

Set `LOG_LEVEL=DEBUG` in `.env` for more detailed logs.

### Testing Different Models

Edit `.env` to try different models:

```bash
# For OpenRouter
OPENROUTER_MODEL=anthropic/claude-3-sonnet
# or
OPENROUTER_MODEL=google/gemini-pro
# or
OPENROUTER_MODEL=openai/gpt-4-turbo-preview
```

## Production Deployment

### Backend Deployment

Recommended platforms (all have free tiers):
- **Render**: https://render.com/
- **Railway**: https://railway.app/
- **Fly.io**: https://fly.io/

Deploy checklist:
- [ ] Set environment variables in platform
- [ ] Configure DATABASE_URL for production
- [ ] Set CORS_ORIGINS to production domain
- [ ] Run database migrations
- [ ] Run ingestion script
- [ ] Test health endpoint

### Frontend Deployment

Docusaurus builds to static files:

```bash
npm run build
```

Deploy `build/` directory to:
- **Vercel**
- **Netlify**
- **GitHub Pages**
- **Cloudflare Pages**

Update `API_URL` in `src/components/ChatBot/hooks/useChatBot.ts` to production backend URL.

## Support

For issues, check:
1. This troubleshooting guide
2. Backend logs (console output)
3. Browser console (F12 → Console tab)
4. Spec documentation in `spec/001-rag-chatbot/`

## Next Steps

Once everything is working:
1. Customize chatbot styling in `src/components/ChatBot/styles.module.css`
2. Adjust RAG parameters in `backend/src/services/rag_service.py`
3. Modify system prompts in `backend/src/services/chatbot_service.py`
4. Add more book content and re-run ingestion
5. Monitor usage and optimize performance
