# 🚀 Quick Setup Guide - Physical AI & Humanoid Robotics Textbook

## Step-by-Step Setup Instructions

### 1. Get Your API Keys (5 minutes)

#### OpenAI API Key
1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. **Important**: Add $5-$10 credit to your account

#### Qdrant Cloud (Free Tier)
1. Go to [https://cloud.qdrant.io/](https://cloud.qdrant.io/)
2. Sign up for a free account
3. Click "Create Cluster" → Select "Free" tier
4. Copy your:
   - Cluster URL (e.g., `https://xxxxx.qdrant.io`)
   - API Key

#### Neon Serverless Postgres (Free Tier)
1. Go to [https://neon.tech/](https://neon.tech/)
2. Sign up and create a new project
3. Copy the connection string (looks like):
   ```
   postgresql://user:password@ep-xxxxx.us-east-2.aws.neon.tech/database?sslmode=require
   ```

### 2. Clone and Install (3 minutes)

```bash
# Clone repository (replace with your repo URL)
git clone <your-repo-url>
cd book

# Install frontend
cd reusable-book
npm install

# Install backend
cd ../backend
pip install -r requirements.txt
```

### 3. Configure Backend (2 minutes)

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your favorite editor:

```env
# Paste your OpenAI API key
OPENAI_API_KEY=sk-your-key-here

# Paste your Qdrant credentials
QDRANT_URL=https://xxxxx.qdrant.io
QDRANT_API_KEY=your-qdrant-key-here
QDRANT_COLLECTION_NAME=physical_ai_robotics

# Paste your Neon Postgres connection string
DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=require

# Generate a secret key (or use this one for development)
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application settings
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 4. Start Backend Server (1 minute)

Open a new terminal:

```bash
cd backend
uvicorn app.main:app --reload
```

You should see:
```
✅ Database initialized
✅ Qdrant collection: physical_ai_robotics
🚀 API is ready
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Keep this terminal running!**

### 5. Ingest Book Content (2 minutes)

Open another new terminal:

```bash
cd backend
python ingest_documents.py
```

You should see:
```
🚀 Starting document ingestion...
📄 Found 5 markdown files
Processing: 01-introduction.md
  ✓ Created 3 chunks
...
✅ Success! Ingested 5 documents
✨ Ingestion complete!
```

### 6. Start Frontend (1 minute)

Open another new terminal:

```bash
cd reusable-book
npm start
```

Your browser will automatically open to `http://localhost:3000`

**Success! 🎉**

## Verification Checklist

### ✅ Backend Running
Visit: [http://localhost:8000/health](http://localhost:8000/health)

Should return:
```json
{"status": "healthy"}
```

### ✅ API Documentation
Visit: [http://localhost:8000/docs](http://localhost:8000/docs)

You should see the interactive API documentation.

### ✅ Documents Ingested
Visit: [http://localhost:8000/api/documents](http://localhost:8000/api/documents)

Should show your ingested chapters.

### ✅ Frontend Working
Visit: [http://localhost:3000](http://localhost:3000)

You should see the beautiful book homepage!

### ✅ Chatbot Working
1. Click the chat icon in the bottom right
2. Ask: "What is ROS 2?"
3. You should get an AI-generated answer with sources!

## Common Issues & Fixes

### Issue: "Connection refused" when chatting

**Fix**: Make sure backend is running on port 8000
```bash
# Check if backend is running
curl http://localhost:8000/health
```

### Issue: "Collection not found" error

**Fix**: The collection will be created automatically. Just restart the backend:
```bash
# Ctrl+C to stop, then:
uvicorn app.main:app --reload
```

### Issue: "Database connection error"

**Fix**: Check your `DATABASE_URL` in `.env`:
- Make sure you copied the entire connection string
- It should end with `?sslmode=require`
- No trailing spaces

### Issue: "OpenAI rate limit exceeded"

**Fix**: You need to add credits to your OpenAI account:
1. Go to [https://platform.openai.com/account/billing](https://platform.openai.com/account/billing)
2. Add $5-$10 credit
3. Wait a few minutes for it to activate

### Issue: Build fails with memory error

**Fix**: Increase Node memory:
```bash
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

## Testing the Features

### 1. Test General Questions

Click the chat widget and ask:
- "What is Physical AI?"
- "Explain ROS 2 nodes"
- "How do I simulate robots?"

### 2. Test Text Selection

1. Go to any chapter
2. Select some text (e.g., a code snippet)
3. The chatbot will show selected text
4. Ask: "Explain this code"

### 3. Test Search

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "humanoid robot simulation", "top_k": 3}'
```

### 4. Test Chat History

1. Have a conversation with the chatbot
2. Close and reopen the chat widget
3. Your conversation should still be there!

## Next Steps

### For Development

1. **Add more chapters**: Create new markdown files in `reusable-book/docs/`
2. **Re-ingest**: Run `python ingest_documents.py` to update the chatbot
3. **Customize UI**: Edit files in `reusable-book/src/`
4. **Improve RAG**: Modify `backend/app/rag_service.py`

### For Deployment

See the main README.md for deployment instructions to:
- GitHub Pages (Frontend)
- Vercel/Railway/Render (Backend)

## Need Help?

1. **Check logs**:
   - Backend: Look at the terminal running `uvicorn`
   - Frontend: Check browser console (F12)

2. **Test API manually**:
   - Visit http://localhost:8000/docs
   - Try endpoints directly

3. **Restart everything**:
   ```bash
   # Stop all terminals (Ctrl+C)
   # Then start again in order:
   # 1. Backend
   # 2. Frontend
   ```

## Congratulations! 🎉

You now have a fully functional AI-native textbook with:
- ✅ Comprehensive content on Physical AI
- ✅ RAG-powered chatbot
- ✅ Text selection Q&A
- ✅ Semantic search
- ✅ Chat history
- ✅ Beautiful UI

**Happy Learning! 🤖📚**

---

**Time to complete**: ~15 minutes
**Cost**: Free tier for Qdrant & Neon + ~$0.50-$1 for OpenAI credits
