# PhishScope Web UI - Quick Start Guide

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ and npm installed
- Git repository cloned

## Step 1: Install Python Package (Required)

The package must be installed in editable mode for the API to work:

```bash
# From the project root directory
cd /Users/itzhakch/Research/PhishScope

# Install the package in editable mode
pip install -e .

# Or if you want dev dependencies too:
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium
```

## Step 2: Configure Environment (Optional)

Create a `.env` file for LLM configuration (optional - works without AI):

```bash
cp .env.example .env
# Edit .env with your LLM provider settings if needed
```

## Step 3: Start Backend API

```bash
# Terminal 1 - Start FastAPI backend
cd /Users/itzhakch/Research/PhishScope
uvicorn src.phishscope.api.main:app --host 0.0.0.0 --port 8070 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8070 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Step 4: Start Frontend Dev Server

```bash
# Terminal 2 - Start React frontend
cd /Users/itzhakch/Research/PhishScope/frontend

# First time only - install dependencies
npm install

# Start dev server
npm run dev
```

You should see:
```
  VITE v5.4.2  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

## Step 5: Access the Web UI

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8070/docs (FastAPI Swagger UI)
- **Health Check**: http://localhost:8070/health

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'phishscope'"

**Solution**: Install the package in editable mode:
```bash
pip install -e .
```

### Error: "Port 8070 already in use"

**Solution**: Kill the existing process or use a different port:
```bash
# Find and kill process on port 8070
lsof -ti:8070 | xargs kill -9

# Or use a different port
uvicorn src.phishscope.api.main:app --host 0.0.0.0 --port 8071 --reload
# Then update frontend/vite.config.js proxy target to match
```

### Frontend can't connect to API

**Solution**: Check that:
1. Backend is running on port 8070
2. Vite proxy is configured correctly in `frontend/vite.config.js`
3. No CORS errors in browser console

## Production Build

To build the frontend for production:

```bash
cd frontend
npm run build
# Output will be in frontend/dist/
```

To serve the production build:

```bash
npm run preview
# Or use any static file server
```

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  React Frontend │ ──────> │  FastAPI Backend │
│  (Port 3000)    │  Proxy  │  (Port 8070)     │
└─────────────────┘         └──────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  LangGraph      │
                            │  Workflow       │
                            │  (Async)        │
                            └─────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  Playwright     │
                            │  Browser        │
                            └─────────────────┘
```

## Features

✅ Real-time URL analysis with polling
✅ Screenshot capture and display
✅ DOM/JavaScript/Network findings
✅ AI-powered analysis (optional)
✅ Markdown report generation
✅ Analysis history dashboard
✅ Responsive design with TailwindCSS

## Next Steps

- Configure LLM provider in `.env` for AI analysis
- Customize frontend styling in `frontend/src/index.css`
- Add authentication if deploying publicly
- Set up production deployment with Docker