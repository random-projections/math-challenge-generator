from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from problem_generator import generate_word_problem
import os
from pathlib import Path

app = FastAPI()

# Add this near the top
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

def debug_log(message):
    if DEBUG:
        print(message)

# Define models first
class AnswerRequest(BaseModel):
    problem_id: int
    user_answer: float  # Changed to float for more complex answers

# In-memory store for active problems and their explanations
active_problems = {}
problem_explanations = {}

# Get the absolute path to the frontend build directory
FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "build"
debug_log(f"Frontend directory path: {FRONTEND_DIR}")  # Debug print

# Only mount static files if the directory exists
if (FRONTEND_DIR / "static").exists():
    print("Static directory found")  # Debug print
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")
else:
    print(f"Static directory not found at {FRONTEND_DIR / 'static'}")  # Debug print

# API routes should come BEFORE the catch-all frontend route
@app.get("/api/problem")
def get_problem():
    problem = generate_word_problem()
    problem_id = len(active_problems) + 1000
    
    active_problems[problem_id] = problem["answer"]
    problem_explanations[problem_id] = problem["explanation"]
    
    return {
        "problem_id": problem_id,
        "question": problem["question"]
    }

@app.post("/api/check_answer")
def check_answer(answer_request: AnswerRequest):
    correct_answer = active_problems.get(answer_request.problem_id, None)
    if correct_answer is None:
        return {"status": "error", "message": "Invalid problem ID"}
    
    # Allow for small floating-point differences
    is_correct = abs(answer_request.user_answer - correct_answer) < 0.01
    
    return {
        "correct": is_correct,
        "correct_answer": correct_answer,
        "explanation": problem_explanations.get(answer_request.problem_id, "No explanation available")
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "message": "Math Challenge Generator API is running"}

# Frontend routes should come AFTER API routes
@app.get("/")
async def root():
    return await serve_frontend("")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    print(f"Requested path: {full_path}")  # Debug print
    
    # If it's an API route, don't try to serve frontend files
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404)
    
    # If frontend isn't built, return a helpful message
    if not FRONTEND_DIR.exists():
        print(f"Frontend directory does not exist: {FRONTEND_DIR}")  # Debug print
        return {"message": "Frontend not built. Please run 'cd frontend && npm install && npm run build'"}
    
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        print(f"index.html not found at {index_file}")  # Debug print
        return {"message": "Frontend build incomplete. Missing index.html"}
    
    print(f"Serving index.html from {index_file}")  # Debug print
    return FileResponse(str(index_file))
