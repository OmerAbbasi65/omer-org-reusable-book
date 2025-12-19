# Hugging Face Spaces Deployment Checklist

Use this checklist to ensure a smooth deployment process.

## Pre-Deployment

- [ ] Create Hugging Face account at [huggingface.co](https://huggingface.co)
- [ ] Create OpenRouter account and get API key from [openrouter.ai](https://openrouter.ai)
- [ ] Create Qdrant Cloud account and cluster at [cloud.qdrant.io](https://cloud.qdrant.io)
- [ ] Create Neon database at [neon.tech](https://neon.tech)
- [ ] Have all credentials ready:
  - [ ] OpenRouter API key
  - [ ] Qdrant URL and API key
  - [ ] Neon database connection string
  - [ ] Generated SECRET_KEY (`openssl rand -hex 32`)

## Qdrant Setup

- [ ] Create new cluster in Qdrant Cloud
- [ ] Create collection named `rag-chatbot` with:
  - [ ] Vector size: 384
  - [ ] Distance metric: Cosine
- [ ] Copy cluster URL
- [ ] Copy API key

## Neon Database Setup

- [ ] Create new project in Neon
- [ ] Copy connection string
- [ ] Verify format: `postgresql://user:password@host:5432/database?sslmode=require`

## Hugging Face Space Creation

- [ ] Create new Space
- [ ] Choose Docker SDK
- [ ] Select appropriate visibility (Public/Private)
- [ ] Choose hardware tier (start with CPU basic)

## Environment Variables Configuration

Configure these secrets in Space Settings > Repository secrets:

**Required:**
- [ ] `OPENROUTER_API_KEY`
- [ ] `DATABASE_URL`
- [ ] `QDRANT_URL`
- [ ] `QDRANT_API_KEY`
- [ ] `SECRET_KEY`

**Optional (with defaults):**
- [ ] `OPENROUTER_MODEL` (default: `anthropic/claude-3.5-sonnet`)
- [ ] `QDRANT_COLLECTION_NAME` (default: `rag-chatbot`)
- [ ] `EMBEDDING_MODEL` (default: `all-MiniLM-L6-v2`)
- [ ] `CORS_ORIGINS` (update for your frontend)
- [ ] `ENVIRONMENT` (default: `production`)
- [ ] `DEBUG` (default: `False`)

## Code Deployment

- [ ] Navigate to backend directory: `cd backend`
- [ ] Add Space remote: `git remote add space https://huggingface.co/spaces/USERNAME/SPACE-NAME`
- [ ] Add files: `git add .`
- [ ] Commit: `git commit -m "Initial deployment"`
- [ ] Push: `git push space main`

## Post-Deployment Verification

- [ ] Wait for build to complete (check Logs tab)
- [ ] Verify app is running (green status)
- [ ] Test health endpoint: `curl https://USERNAME-SPACE-NAME.hf.space/health`
- [ ] Test root endpoint: `curl https://USERNAME-SPACE-NAME.hf.space/`
- [ ] Test chat endpoint (see DEPLOYMENT_GUIDE.md for curl command)

## Document Ingestion

Choose one method:

**Method 1: Local Ingestion (Recommended)**
- [ ] Copy `.env.example` to `.env` locally
- [ ] Add same credentials as Space secrets
- [ ] Run: `python ingest_documents.py`

**Method 2: API Ingestion**
- [ ] Use `/api/documents/ingest` endpoint
- [ ] Send document chunks via POST request

## Integration

- [ ] Update frontend to use Space URL: `https://USERNAME-SPACE-NAME.hf.space`
- [ ] Update CORS_ORIGINS secret to include frontend domain
- [ ] Restart Space if CORS was updated
- [ ] Test frontend integration

## Final Checks

- [ ] All endpoints responding correctly
- [ ] Chat functionality working
- [ ] RAG retrieval working (if documents ingested)
- [ ] CORS allowing frontend requests
- [ ] No errors in logs
- [ ] Monitor initial API costs

## Optional Enhancements

- [ ] Set up custom domain (Hugging Face Pro)
- [ ] Enable Space analytics
- [ ] Set up monitoring and alerts
- [ ] Implement rate limiting
- [ ] Add authentication if needed
- [ ] Upgrade hardware if needed

## Troubleshooting Resources

If issues arise, check:
- [ ] Space logs for errors
- [ ] Environment variables are set correctly
- [ ] Database is accessible
- [ ] Qdrant cluster is accessible
- [ ] OpenRouter API key is valid
- [ ] DEPLOYMENT_GUIDE.md troubleshooting section

## Success Criteria

Your deployment is successful when:
- ✅ Space shows green "Running" status
- ✅ Health endpoint returns `{"status": "healthy"}`
- ✅ Chat endpoint returns valid responses
- ✅ No critical errors in logs
- ✅ Frontend can communicate with backend (if applicable)

## Notes

Space URL format: `https://USERNAME-SPACE-NAME.hf.space`

Default port: 7860

Build time: 5-10 minutes (typical)

Free tier limitations:
- CPU basic tier
- Limited concurrent users
- May sleep after inactivity

---

**Deployment Date**: _______________

**Space URL**: _______________

**Deployed By**: _______________
