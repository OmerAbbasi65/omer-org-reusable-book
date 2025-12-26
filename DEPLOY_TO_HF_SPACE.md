# 🚀 Deploy Backend Fixes to HuggingFace Space

## Quick Deployment Guide

### Step 1: Get HuggingFace Access Token

1. Go to: https://huggingface.co/settings/tokens
2. Click **"New token"**
3. Name: `backend-deployment`
4. Role: **Write**
5. Click **"Create"**
6. **Copy the token** (starts with `hf_...`)

### Step 2: Push Changes to HF Space

Run these commands (replace `YOUR_HF_TOKEN` with your actual token):

```bash
# Remove old remote
git remote remove hf-space

# Add remote with token authentication
git remote add hf-space https://joseph8071:YOUR_HF_TOKEN@huggingface.co/spaces/joseph8071/robotics-rag-backend

# Push to HF Space
git push hf-space main --force
```

**Example:**
```bash
git remote add hf-space https://joseph8071:hf_XxXxXxXxXxXxXxXxXxXx@huggingface.co/spaces/joseph8071/robotics-rag-backend
git push hf-space main --force
```

### Step 3: Update Environment Variables on HF Space

1. Go to: https://huggingface.co/spaces/joseph8071/robotics-rag-backend/settings
2. Click **"Variables and secrets"**
3. **Add/Update these variables:**

```
ACTIVE_MODEL=claude
CLAUDE_MODEL=anthropic/claude-3.5-sonnet
COHERE_MODEL=cohere/command-r-plus
OPENROUTER_API_KEY=<your-key>
DATABASE_URL=<your-neon-db-url>
QDRANT_URL=<your-qdrant-url>
QDRANT_API_KEY=<your-qdrant-key>
QDRANT_COLLECTION_NAME=rag-chatbot
EMBEDDING_MODEL=all-MiniLM-L6-v2
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=https://omer-org-reusable-book.vercel.app,http://localhost:3000
SECRET_KEY=<generate-with-openssl-rand-hex-32>
```

### Step 4: Wait for Build

1. HuggingFace Space will automatically rebuild (takes 3-5 minutes)
2. Watch the **"Logs"** tab to see build progress
3. Wait for message: **"Running on local URL:  http://0.0.0.0:7860"**

### Step 5: Verify Deployment

Once build completes, test:

```bash
# Check health
curl https://joseph8071-robotics-rag-backend.hf.space/health

# Check model info (NEW ENDPOINT)
curl https://joseph8071-robotics-rag-backend.hf.space/api/model-info

# Test chat
curl -X POST https://joseph8071-robotics-rag-backend.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is ROS 2?", "session_id": "test"}'
```

### Step 6: Test Frontend

1. Open your frontend: https://omer-org-reusable-book.vercel.app
2. Click chatbot button
3. Send a message
4. Should work now! ✅

---

## 📋 Files That Were Updated

1. **backend/app/config.py** - Added multi-model support
2. **backend/app/main.py** - Added /api/model-info endpoint
3. **backend/app/simple_chat_service.py** - Dynamic model selection
4. **backend/app/rag_service.py** - Dynamic model selection
5. **backend/.env.example** - Updated with new variables
6. **reusable-book/src/components/ChatBot/hooks/useChatBot.ts** - Fixed API endpoints

---

## 🔄 Alternative: Manual File Upload

If you prefer not to use git, manually update files on HF Space:

### Files to Update:

1. Go to: https://huggingface.co/spaces/joseph8071/robotics-rag-backend/tree/main

2. Click each file below and replace content:

#### **app/config.py**
- Click file → **"Edit file"**
- Replace entire content with updated version from your local `backend/app/config.py`
- Click **"Commit changes to main"**

#### **app/main.py**
- Add the new `/api/model-info` endpoint (lines 57-68 in local file)

#### **app/simple_chat_service.py**
- Update `__init__` method (lines 6-15)
- Update `_get_system_prompt` method (lines 52-80)

#### **app/rag_service.py**
- Update `__init__` method (lines 7-16)

---

## ✅ What Changed?

### Main Fixes:
- ✅ Fixed API endpoint mismatch (frontend now calls `/api/chat` correctly)
- ✅ Added support for Claude 3.5 Sonnet and Cohere Command R+ models
- ✅ Added `ACTIVE_MODEL` environment variable to switch between models
- ✅ Added `/api/model-info` endpoint to check active model
- ✅ Updated all chat services to use dynamic model selection

### Configuration:
- Default model: **Claude 3.5 Sonnet** (`ACTIVE_MODEL=claude`)
- Alternative: **Cohere Command R+** (set `ACTIVE_MODEL=cohere`)
- Easy toggle by changing one environment variable

---

## 🐛 Troubleshooting

### Build fails on HF Space
- Check **"Logs"** tab for error messages
- Verify all environment variables are set
- Make sure `requirements.txt` includes all dependencies

### 500 errors after deployment
- Check environment variables are set correctly
- Verify `OPENROUTER_API_KEY` has credits
- Check `DATABASE_URL` and `QDRANT_URL` are accessible

### Frontend still shows old errors
- Hard refresh browser (Ctrl+Shift+R)
- Clear browser cache
- Check browser console for new errors

---

## 📞 Next Steps After Deployment

1. Monitor HF Space build logs
2. Test all endpoints work
3. Test frontend chatbot
4. Switch to Cohere if desired (`ACTIVE_MODEL=cohere`)
5. Monitor API usage and costs

---

**Your chatbot will work perfectly after this deployment!** 🎉
