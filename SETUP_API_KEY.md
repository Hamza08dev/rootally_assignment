# API Key Setup Guide

## Quick Setup Steps

### 1. Create `.env` file

In the project root directory (`rootally/`), create a file named `.env` (no extension).

**Windows PowerShell:**
```powershell
New-Item -ItemType File -Path .env
```

**Windows Command Prompt:**
```cmd
type nul > .env
```

**Linux/Mac:**
```bash
touch .env
```

### 2. Add your API key

Open the `.env` file in a text editor and add one of the following:

**For Google Gemini (Recommended):**
```
GEMINI_API_KEY=your-actual-api-key-here
GEMINI_MODEL=gemini-2.5-flash
LLM_PROVIDER=gemini
```

**For OpenAI:**
```
OPENAI_API_KEY=sk-your-actual-api-key-here
LLM_PROVIDER=openai
```

**For Anthropic:**
```
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here
LLM_PROVIDER=anthropic
```

### 3. Get your API key

**Google Gemini (Recommended - Free tier available):**
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key" or "Get API Key"
4. Copy the API key
5. Paste it in your `.env` file as `GEMINI_API_KEY`

**OpenAI:**
1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (it starts with `sk-`)
5. Paste it in your `.env` file

**Anthropic:**
1. Go to https://console.anthropic.com/
2. Sign in or create an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (it starts with `sk-ant-`)
6. Paste it in your `.env` file

### 4. Verify setup

The `.env` file should look like this (with your actual key):

**For Gemini:**
```
GEMINI_API_KEY=AIzaSyCJ7DHsFLTHnDWPcQMm3sH_Q1yITnuEBjo
GEMINI_MODEL=gemini-2.5-flash
LLM_PROVIDER=gemini
```

**For OpenAI:**
```
OPENAI_API_KEY=sk-proj-abc123xyz789...
LLM_PROVIDER=openai
```

**Important:**
- Never commit the `.env` file to git (it's already in `.gitignore`)
- Keep your API key secret
- The `.env` file should be in the project root, same directory as `requirements.txt`

### 5. Test it

Run the demo to verify it works:
```bash
python src/demo.py
```

If you see "⚠️ Warning: No LLM API key found", double-check:
- The `.env` file exists in the project root
- The file name is exactly `.env` (not `.env.txt`)
- The API key is correct and not commented out
- You've restarted your terminal/IDE after creating the file

## Without API Key

The system will work with a fallback parser, but with limited natural language understanding. For best results, use an LLM API key.

