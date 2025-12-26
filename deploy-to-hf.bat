@echo off
REM Deploy Backend to HuggingFace Space (Windows)
REM Usage: deploy-to-hf.bat YOUR_HF_TOKEN

if "%1"=="" (
    echo ❌ Error: Please provide your HuggingFace token
    echo Usage: deploy-to-hf.bat YOUR_HF_TOKEN
    echo.
    echo Get your token from: https://huggingface.co/settings/tokens
    exit /b 1
)

set HF_TOKEN=%1

echo 🚀 Deploying to HuggingFace Space...
echo.

REM Remove old remote if exists
git remote remove hf-space 2>nul

REM Add remote with token
echo 📡 Setting up remote...
git remote add hf-space https://joseph8071:%HF_TOKEN%@huggingface.co/spaces/joseph8071/robotics-rag-backend

REM Push to HF Space
echo ⬆️  Pushing changes...
git push hf-space main --force

echo.
echo ✅ Deployment initiated!
echo.
echo 📋 Next steps:
echo 1. Go to: https://huggingface.co/spaces/joseph8071/robotics-rag-backend
echo 2. Watch the 'Logs' tab for build progress (3-5 minutes)
echo 3. Update environment variables in Settings if needed
echo 4. Test: curl https://joseph8071-robotics-rag-backend.hf.space/api/model-info
echo.
