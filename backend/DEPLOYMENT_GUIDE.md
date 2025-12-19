# Hugging Face Spaces Deployment Guide

This guide provides step-by-step instructions for deploying the Physical AI & Humanoid Robotics RAG backend to Hugging Face Spaces.

## Prerequisites

Before deploying, ensure you have:

1. **Hugging Face Account**: Sign up at [huggingface.co](https://huggingface.co)
2. **OpenRouter API Key**: Get one from [openrouter.ai](https://openrouter.ai)
3. **Qdrant Cloud Account**: Sign up for free tier at [cloud.qdrant.io](https://cloud.qdrant.io)
4. **Neon Database**: Create a free database at [neon.tech](https://neon.tech)

## Quick Deployment Steps

### 1. Set Up External Services

#### A. Create Qdrant Collection

1. Log in to [Qdrant Cloud](https://cloud.qdrant.io)
2. Create a new cluster (free tier available)
3. Note your:
   - Cluster URL (e.g., `https://xxxxx.cloud.qdrant.io`)
   - API Key
4. Create a collection named `rag-chatbot` with:
   - Vector size: 384 (for all-MiniLM-L6-v2 embeddings)
   - Distance: Cosine

#### B. Create Neon Database

1. Log in to [Neon](https://neon.tech)
2. Create a new project
3. Copy the connection string from the dashboard
4. Format: `postgresql://user:password@host:5432/database?sslmode=require`

#### C. Get OpenRouter API Key

1. Sign up at [OpenRouter](https://openrouter.ai)
2. Navigate to Keys section
3. Create a new API key
4. Note the key (starts with `sk-or-...`)

### 2. Create Hugging Face Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Fill in the details:
   - **Owner**: Your username or organization
   - **Space name**: Choose a descriptive name (e.g., `robotics-rag-backend`)
   - **License**: Choose appropriate license (e.g., MIT)
   - **Select the Space SDK**: Choose **Docker**
   - **Space hardware**: Start with **CPU basic** (free tier)
   - **Visibility**: Choose **Public** or **Private**
4. Click **"Create Space"**

### 3. Configure Environment Variables

1. In your new Space, click **Settings** (top right)
2. Scroll to **Repository secrets**
3. Add the following secrets one by one:

#### Required Secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | `sk-or-v1-...` |
| `DATABASE_URL` | Neon Postgres connection string | `postgresql://user:pass@host:5432/db?sslmode=require` |
| `QDRANT_URL` | Qdrant cluster URL | `https://xxxxx.cloud.qdrant.io` |
| `QDRANT_API_KEY` | Qdrant API key | `your-qdrant-key` |
| `SECRET_KEY` | Random secret for JWT | Generate: `openssl rand -hex 32` |

#### Optional Secrets:

| Secret Name | Default Value | Description |
|-------------|---------------|-------------|
| `OPENROUTER_MODEL` | `anthropic/claude-3.5-sonnet` | LLM model to use |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | OpenRouter API base URL |
| `QDRANT_COLLECTION_NAME` | `rag-chatbot` | Qdrant collection name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace embedding model |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:8000` | Allowed CORS origins (comma-separated) |
| `ENVIRONMENT` | `production` | Environment type |
| `DEBUG` | `False` | Debug mode |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT expiration time |

### 4. Push Code to Space

#### Option A: Using Git (Recommended)

```bash
# Navigate to backend directory
cd backend

# Initialize git if not already done
git init

# Add the Hugging Face Space as a remote
git remote add space https://huggingface.co/spaces/YOUR-USERNAME/YOUR-SPACE-NAME

# Add all files
git add .

# Commit
git commit -m "Initial deployment to Hugging Face Spaces"

# Push to space
git push space main
```

#### Option B: Using the Web Interface

1. In your Space, click **Files** > **Add file** > **Upload files**
2. Upload the following files from the `backend` directory:
   - `Dockerfile`
   - `README.md`
   - `requirements.txt`
   - `.dockerignore`
   - `.env.example`
   - All files in the `app/` directory
   - `Procfile`
3. Commit the changes

### 5. Monitor Deployment

1. After pushing, Hugging Face will automatically start building your Docker container
2. Go to your Space page
3. Click the **App** tab to see build progress
4. The build typically takes 5-10 minutes
5. Check the **Logs** section for any errors

### 6. Verify Deployment

Once the build completes and the app is running:

#### Test Health Endpoint

```bash
curl https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/health
```

Expected response:
```json
{
  "status": "healthy",
  "mode": "rag_chat"
}
```

#### Test Root Endpoint

```bash
curl https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/
```

Expected response:
```json
{
  "message": "Physical AI & Humanoid Robotics Simple Chatbot API",
  "version": "1.0.0",
  "status": "operational",
  "mode": "Simple Chat (No RAG)"
}
```

#### Test Chat Endpoint

```bash
curl -X POST https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, can you help me learn about robotics?",
    "session_id": "test-session-123"
  }'
```

### 7. Ingest Documents

After deployment, you need to populate the Qdrant database with your document content.

#### Option 1: Local Ingestion (Recommended)

1. Set up your local environment with the same credentials
2. Run the ingestion script locally:

```bash
cd backend
cp .env.example .env
# Edit .env with your credentials
python ingest_documents.py
```

This will populate Qdrant, which your deployed app can then access.

#### Option 2: API Ingestion

Use the `/api/documents/ingest` endpoint to upload documents via API:

```python
import requests

url = "https://YOUR-USERNAME-YOUR-SPACE-NAME.hf.space/api/documents/ingest"
payload = {
    "documents": [
        {
            "title": "Introduction to ROS 2",
            "content": "ROS 2 is the next generation of the Robot Operating System...",
            "chapter_id": "module1-ros2",
            "metadata": {
                "file_path": "docs/module1/ros2.md"
            }
        }
    ]
}

response = requests.post(url, json=payload)
print(response.json())
```

## Troubleshooting

### Build Fails

**Problem**: Docker build fails during pip install

**Solution**:
- Check the logs for specific package errors
- Ensure all dependencies in `requirements.txt` are compatible
- Try increasing Space hardware tier if memory issues

### App Won't Start

**Problem**: Container builds but app doesn't start

**Solution**:
1. Check environment variables are set correctly
2. Verify database connection strings
3. Check logs for specific error messages
4. Ensure port 7860 is exposed in Dockerfile

### Database Connection Errors

**Problem**: "Database connection failed"

**Solutions**:
- Verify `DATABASE_URL` format is correct
- Ensure `?sslmode=require` is appended for Neon
- Check that Neon database is accessible (not paused)
- Verify database credentials

### Qdrant Connection Errors

**Problem**: "Failed to connect to Qdrant"

**Solutions**:
- Verify `QDRANT_URL` and `QDRANT_API_KEY` are correct
- Ensure collection exists in Qdrant Cloud
- Check collection name matches `QDRANT_COLLECTION_NAME`

### CORS Errors

**Problem**: Frontend can't access the API due to CORS

**Solution**:
- Update `CORS_ORIGINS` secret in Space settings
- Add your frontend domain to the comma-separated list
- Example: `https://your-frontend.com,https://www.your-frontend.com`

### Rate Limiting

**Problem**: Too many requests to OpenRouter

**Solutions**:
- Check your OpenRouter usage and limits
- Consider upgrading OpenRouter plan
- Implement rate limiting in your frontend
- Use a cheaper model for testing (e.g., `google/gemini-2.0-flash-exp:free`)

## Updating Your Deployment

### Update Code

```bash
cd backend
git add .
git commit -m "Update: description of changes"
git push space main
```

The Space will automatically rebuild with your changes.

### Update Environment Variables

1. Go to Space Settings > Repository secrets
2. Update the value of any secret
3. Click "Restart this Space" for changes to take effect

## Scaling and Performance

### Upgrade Hardware

If you need better performance:

1. Go to Space Settings
2. Under "Space hardware", select a higher tier:
   - **CPU basic** (free): Good for testing
   - **CPU upgrade** (paid): Better performance
   - **GPU** (paid): If you need GPU acceleration

### Database Optimization

For better performance with Neon:
- Upgrade to Neon Pro for better connection pooling
- Add indexes to frequently queried columns
- Consider connection pooling with pgBouncer

### Qdrant Optimization

For better vector search:
- Upgrade Qdrant cluster size
- Adjust search parameters (`limit`, filters)
- Use quantization for faster searches

## Security Best Practices

1. **Never commit `.env` files**: Always use Space secrets
2. **Rotate API keys regularly**: Update OpenRouter and Qdrant keys periodically
3. **Use strong SECRET_KEY**: Generate with `openssl rand -hex 32`
4. **Limit CORS origins**: Only allow trusted domains
5. **Monitor usage**: Check OpenRouter and Qdrant usage regularly
6. **Use Private Spaces**: For sensitive applications

## Cost Estimation

### Free Tier Setup:
- Hugging Face Space (CPU basic): $0/month
- Neon Database (Free tier): $0/month (with limits)
- Qdrant Cloud (Free tier): $0/month (1GB storage)
- OpenRouter: Pay-per-use (varies by model)

### Estimated Monthly Costs:
- **Light usage** (testing): $5-10/month
- **Medium usage** (small app): $20-50/month
- **Heavy usage** (production): $100+/month

Most costs come from OpenRouter API calls. Use cheaper models for development:
- `google/gemini-2.0-flash-exp:free` - Free
- `google/gemini-flash-1.5` - $0.075 per 1M tokens
- `anthropic/claude-3.5-sonnet` - $3.00 per 1M tokens

## Support

For issues:
- **Hugging Face Spaces**: [docs.huggingface.co/spaces](https://huggingface.co/docs/hub/spaces)
- **OpenRouter**: [openrouter.ai/docs](https://openrouter.ai/docs)
- **Qdrant**: [qdrant.tech/documentation](https://qdrant.tech/documentation/)
- **Neon**: [neon.tech/docs](https://neon.tech/docs/introduction)

## Next Steps

After successful deployment:

1. **Test thoroughly**: Verify all endpoints work correctly
2. **Set up monitoring**: Use Hugging Face Analytics
3. **Configure frontend**: Update frontend to use your Space URL
4. **Add authentication**: Implement user authentication if needed
5. **Optimize costs**: Monitor and optimize API usage
6. **Set up CI/CD**: Automate deployments with GitHub Actions
