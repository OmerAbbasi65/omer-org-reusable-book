# 📤 Manual Upload to HuggingFace Space

Git push had conflicts, so let's manually update the files on HF Space. This is actually faster!

## 🚀 Quick Upload Steps (5 minutes)

### Step 1: Go to Your HF Space
Open: https://huggingface.co/spaces/joseph8071/robotics-rag-backend

### Step 2: Update These 4 Files

Click **"Files and versions"** tab, then update each file:

---

## File 1: `app/config.py`

1. Click `app/config.py`
2. Click **"Edit file"** button (pencil icon)
3. **Replace entire content** with:

```python
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # OpenRouter (for LLM chat)
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "anthropic/claude-3.5-sonnet"

    # Model Selection (claude or cohere)
    active_model: str = "claude"  # Options: "claude" or "cohere"

    # Available Models Configuration
    claude_model: str = "anthropic/claude-3.5-sonnet"
    cohere_model: str = "cohere/command-r-plus"  # Excellent for RAG tasks

    # Database
    database_url: str

    # Qdrant Cloud
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = "rag-chatbot"

    # HuggingFace Embeddings (free, runs locally)
    embedding_model: str = "all-MiniLM-L6-v2"

    # Application
    environment: str = "development"
    debug: bool = True
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @property
    def current_model(self) -> str:
        """Get the currently active model based on active_model setting"""
        if self.active_model.lower() == "cohere":
            return self.cohere_model
        else:
            return self.claude_model

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

settings = Settings()
```

4. Add commit message: `fix: Add multi-model support config`
5. Click **"Commit changes to main"**

---

## File 2: `app/main.py`

1. Click `app/main.py`
2. Click **"Edit file"**
3. Find the `@app.get("/health")` function (around line 53-55)
4. **Add this NEW endpoint** RIGHT AFTER the health check:

```python
@app.get("/api/model-info")
async def get_model_info():
    """Get information about the currently active AI model"""
    return {
        "active_model": settings.active_model,
        "model_name": settings.current_model,
        "available_models": {
            "claude": settings.claude_model,
            "cohere": settings.cohere_model
        },
        "description": f"Currently using {settings.active_model.upper()} model for chat responses"
    }
```

5. Commit message: `fix: Add model info endpoint`
6. Click **"Commit changes to main"**

---

## File 3: `app/simple_chat_service.py`

1. Click `app/simple_chat_service.py`
2. Click **"Edit file"**
3. Find the `__init__` method (around lines 6-14)
4. **Replace it** with:

```python
    def __init__(self):
        # Use OpenRouter with OpenAI-compatible API
        self.client = OpenAI(
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
        )
        # Use current_model which switches between Claude and Cohere
        self.model = settings.current_model
        self.max_tokens = 1024
        self.active_model_type = settings.active_model
```

5. Commit message: `fix: Use dynamic model selection`
6. Click **"Commit changes to main"**

---

## File 4: `app/rag_service.py`

1. Click `app/rag_service.py`
2. Click **"Edit file"**
3. Find the `__init__` method (around lines 7-15)
4. **Replace it** with:

```python
    def __init__(self):
        # Use OpenRouter with OpenAI-compatible API
        self.client = OpenAI(
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
        )
        # Use current_model which switches between Claude and Cohere
        self.model = settings.current_model
        self.active_model_type = settings.active_model
        self.max_context_chars = 24000  # Approximate character limit for context
```

5. Commit message: `fix: Use dynamic model in RAG service`
6. Click **"Commit changes to main"**

---

## Step 3: Update Environment Variables

1. Go to: https://huggingface.co/spaces/joseph8071/robotics-rag-backend/settings
2. Click **"Variables and secrets"**
3. Click **"New secret"** for each:

**Add these NEW variables:**
```
Name: ACTIVE_MODEL
Value: claude

Name: CLAUDE_MODEL
Value: anthropic/claude-3.5-sonnet

Name: COHERE_MODEL
Value: cohere/command-r-plus
```

**Make sure you already have these:**
- OPENROUTER_API_KEY
- DATABASE_URL
- QDRANT_URL
- QDRANT_API_KEY
- SECRET_KEY
- CORS_ORIGINS (should include: https://omer-org-reusable-book.vercel.app,http://localhost:3000)

---

## Step 4: Wait for Build (3-5 minutes)

1. After last commit, HF Space will **automatically rebuild**
2. Go to **"Logs"** tab
3. Watch for: `"Running on local URL:  http://0.0.0.0:7860"`
4. Wait until it says **"Running"**

---

## Step 5: Test Deployment

Once running, test these endpoints:

```bash
# Test health
curl https://joseph8071-robotics-rag-backend.hf.space/health

# Test NEW model-info endpoint
curl https://joseph8071-robotics-rag-backend.hf.space/api/model-info

# Test chat
curl -X POST https://joseph8071-robotics-rag-backend.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is ROS 2?", "session_id": "test-123"}'
```

Expected response from model-info:
```json
{
  "active_model": "claude",
  "model_name": "anthropic/claude-3.5-sonnet",
  "available_models": {
    "claude": "anthropic/claude-3.5-sonnet",
    "cohere": "cohere/command-r-plus"
  },
  "description": "Currently using CLAUDE model for chat responses"
}
```

---

## Step 6: Test Your Frontend Chatbot

1. Open: https://omer-org-reusable-book.vercel.app
2. Click chatbot button (bottom-right)
3. Send a test message
4. **Should work now!** ✅

---

## ✅ Summary

You're updating 4 files to fix:
- ✅ API endpoint mismatch
- ✅ Add multi-model support (Claude + Cohere)
- ✅ Add model selection configuration
- ✅ Add new /api/model-info endpoint

**Total time: ~5 minutes**

---

## 🔄 Switch to Cohere Later

To use Cohere instead of Claude:
1. Go to HF Space Settings → Variables and secrets
2. Change `ACTIVE_MODEL` from `claude` to `cohere`
3. Space will auto-restart with Cohere!

---

**Let me know when you're done uploading and I'll help you test!** 🚀
