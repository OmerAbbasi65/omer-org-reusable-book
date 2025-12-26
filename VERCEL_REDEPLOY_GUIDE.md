# 🚀 Vercel Redeployment Guide

## What Was Fixed

✅ **Backend CORS Updated**: Added your Vercel domain to allowed origins
✅ **Frontend Code**: Already has the API endpoint fixes
✅ **HF Space**: CORS updated to allow Vercel domain
✅ **GitHub**: All changes pushed

## 🔄 Trigger Vercel Redeployment

Vercel needs to rebuild with the updated frontend code. Here's how:

### **Option 1: Automatic Deployment (Recommended)**

If Vercel is connected to your GitHub repo, it should automatically deploy when you push.

**Check if auto-deploy is working:**
1. Go to: https://vercel.com/dashboard
2. Find your project: `omer-org-reusable-book`
3. Look for a new deployment in progress (triggered by the latest push)
4. Wait 2-3 minutes for build to complete

### **Option 2: Manual Redeploy**

If auto-deploy didn't trigger:

1. Go to: https://vercel.com/dashboard
2. Click your project: `omer-org-reusable-book`
3. Click **"Deployments"** tab
4. Find the latest deployment
5. Click the **three dots (...)** → **"Redeploy"**
6. Click **"Redeploy"** to confirm
7. Wait 2-3 minutes for build

### **Option 3: Commit Trigger**

Force a redeploy by making a small commit:

```bash
# Make a trivial change
echo "# Trigger redeploy" >> reusable-book/README.md

# Commit and push
git add reusable-book/README.md
git commit -m "chore: Trigger Vercel redeploy"
git push origin main
```

Vercel will detect the push and auto-deploy.

---

## ✅ Verify Deployment

Once Vercel finishes deploying:

### 1. Check Deployment Status
- Go to: https://vercel.com/dashboard
- Project should show: **"Ready"** or **"Success"**

### 2. Test Live Website

Open: **https://omer-org-reusable-book.vercel.app**

1. Click the chatbot button (bottom-right)
2. Send a test message: "What is ROS 2?"
3. **Should work now!** ✅

### 3. Check Browser Console

Press **F12** → **Console** tab

- ❌ **Before**: "Failed to fetch" errors
- ✅ **After**: No errors, chatbot works!

---

## 🐛 Still Getting Errors?

### Error: "Failed to fetch"

**Cause**: CORS issue or HF Space not restarted

**Solution**:
1. Wait 2-3 minutes for HF Space to restart with new CORS settings
2. Check HF Space is running: https://huggingface.co/spaces/joseph8071/robotics-rag-backend
3. Test backend directly:
   ```bash
   curl https://joseph8071-robotics-rag-backend.hf.space/health
   ```

### Error: Still using old code

**Cause**: Vercel cache

**Solution**:
1. Go to Vercel deployment settings
2. Clear build cache
3. Redeploy

### CORS Error in Console

**Cause**: HF Space CORS not updated

**Solution**:
1. Go to: https://huggingface.co/spaces/joseph8071/robotics-rag-backend/settings
2. Variables and secrets
3. Update `CORS_ORIGINS` to include:
   ```
   http://localhost:3000,http://localhost:8000,https://omer-org-reusable-book.vercel.app
   ```

---

## 📋 What Changed

### Backend (HF Space)
- ✅ CORS now allows: `https://omer-org-reusable-book.vercel.app`
- ✅ API endpoints fixed
- ✅ Multi-model support added

### Frontend (Vercel)
- ✅ Fixed API calls to use `/api/chat` endpoint
- ✅ Fixed session management
- ✅ Backend URL configured correctly

---

## 🎯 Expected Behavior After Redeploy

1. ✅ Open https://omer-org-reusable-book.vercel.app
2. ✅ Click chatbot button
3. ✅ Type a message
4. ✅ Get a response from Claude 3.5 Sonnet
5. ✅ No errors in console

---

## ⏱️ Timeline

- **Vercel Deploy**: 2-3 minutes
- **HF Space Restart**: 2-3 minutes (for CORS update)
- **Total Wait Time**: ~5 minutes from now

---

## 🔍 Debug Commands

```bash
# Test backend health
curl https://joseph8071-robotics-rag-backend.hf.space/health

# Test model info
curl https://joseph8071-robotics-rag-backend.hf.space/api/model-info

# Test chat endpoint
curl -X POST https://joseph8071-robotics-rag-backend.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test"}'
```

---

**Your chatbot will work on the live site after Vercel redeploys!** 🎉
