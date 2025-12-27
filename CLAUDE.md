# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Math Challenge Generator is a full-stack web application that generates AI-powered math word problems for grades 5-8 students. The application uses OpenAI's GPT-4o model to create challenging, age-appropriate math puzzles with step-by-step explanations.

## Architecture

### Backend (FastAPI + Python)
- **challenge_server.py**: Main FastAPI server that handles API routes and serves the React frontend
  - `/api/problem`: GET endpoint that generates a new math problem via OpenAI
  - `/api/check_answer`: POST endpoint that validates user answers (allows 0.01 floating-point tolerance)
  - `/api/health`: Health check endpoint
  - In-memory storage for active problems and explanations (no database)
  - Serves static frontend files from `frontend/build/`

- **problem_generator.py**: OpenAI integration for generating math problems
  - Uses GPT-4o model (configurable via model_name variable)
  - Temperature set to 0.7 for balanced creativity/consistency
  - Includes fallback problems when OpenAI API is unavailable
  - Returns JSON with `question`, `answer` (numeric), and `explanation` (step-by-step solution)
  - Validates model availability before making requests

### Frontend (React + Tailwind CSS)
- **App.js**: Root component that wraps MathChallenge component
- **MathChallenge.jsx**: Main UI component
  - Fetches problems from `/api/problem`
  - Submits answers to `/api/check_answer`
  - Shows success/failure feedback with optional step-by-step explanations
  - Uses same-origin API calls (no CORS needed)

### Key Design Decisions
1. **In-memory storage**: Problems are stored in dictionaries (`active_problems`, `problem_explanations`) keyed by problem_id. This means server restarts clear all active problems.
2. **Single-page application**: FastAPI serves the React build at root and catches all non-API routes to support client-side routing.
3. **Fallback problems**: When OpenAI API fails, the system serves pre-generated problems to maintain availability.
4. **Model flexibility**: The code checks available OpenAI models at runtime and falls back to pre-generated problems if the specified model isn't available.

## Development Commands

### Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server (from backend/ directory)
cd backend
uvicorn challenge_server:app --reload --host 0.0.0.0 --port 8000

# Run tests
cd backend
pytest tests/

# Run single test
cd backend
pytest tests/test_challenge_server.py::test_get_problem

# Enable debug logging
DEBUG=true uvicorn challenge_server:app --reload
```

### Frontend
```bash
# Install dependencies (from frontend/ directory)
cd frontend
npm install

# Run development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Full Stack (from root)
```bash
# Start frontend dev server
npm start

# Build frontend
npm build
```

## Environment Setup

### Required Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for generating problems (required for problem generation, falls back to static problems if missing)
- `DEBUG`: Set to "true" to enable debug logging (optional)

### .env file (backend/)
```
OPENAI_API_KEY=your_api_key_here
DEBUG=false
```

## Deployment

The project uses Railway for automatic deployment:
- **Deployment trigger**: Committing and pushing to GitHub automatically triggers deployment via Railway
- **Build process** (see railway.json):
  - Build command: Installs frontend dependencies and builds React app
  - Start command: Installs backend dependencies and starts uvicorn server on port 8000
- The FastAPI server serves both the API and the built frontend
- Environment variables (OPENAI_API_KEY) must be configured in Railway dashboard

## Testing

Backend tests use pytest with FastAPI's TestClient. Tests currently assume simple addition problems, but the actual implementation uses OpenAI-generated word problems. When modifying tests, account for:
- The dynamic nature of AI-generated problems
- Floating-point answer tolerance (0.01)
- Problem ID management in the in-memory store

## Model Configuration

To change the OpenAI model (problem_generator.py:99):
- Current: `gpt-4o`
- The code validates model availability before use
- Falls back to pre-generated problems if model is unavailable
- Temperature is set to 0.7 for balanced creativity
