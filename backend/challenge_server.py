from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from problem_generator import generate_word_problem
import os
from pathlib import Path
import logging
import sys
import traceback

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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting application...")
    logger.info(f"Frontend directory: {FRONTEND_DIR}")
    logger.info(f"Static files exist: {(FRONTEND_DIR / 'static').exists()}")
    logger.info(f"Index file exists: {(FRONTEND_DIR / 'index.html').exists()}")

# Add error handling middleware
@app.middleware("http")
async def catch_exceptions_middleware(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "error": str(e)}
        )

# API routes should come BEFORE the catch-all frontend route
@app.get("/api/problem")
def get_problem():
    problem = generate_word_problem()
    problem_id = len(active_problems) + 1000

    active_problems[problem_id] = problem["answer"]
    problem_explanations[problem_id] = problem["explanation"]

    return {
        "problem_id": problem_id,
        "question": problem["question"],
        "theme": problem.get("theme", "general"),
        "problem_type": problem.get("problem_type", "math"),
        "num_steps": problem.get("num_steps", 1)
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
    return {"status": "ok"}

# Frontend routes should come AFTER API routes
@app.get("/")
async def root():
    try:
        logger.info("Attempting to serve frontend")
        return await serve_frontend("")
    except Exception as e:
        logger.error(f"Error serving frontend: {str(e)}")
        return {"error": str(e)}

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    logger.info(f"Requested path: {full_path}")
    try:
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        
        # If frontend isn't built, return a helpful message
        if not FRONTEND_DIR.exists():
            logger.error(f"Frontend directory does not exist: {FRONTEND_DIR}")
            return {"message": "Frontend not built"}
        
        index_file = FRONTEND_DIR / "index.html"
        if not index_file.exists():
            logger.error(f"index.html not found at {index_file}")
            return {"message": "Frontend build incomplete"}
        
        logger.info(f"Serving index.html from {index_file}")
        return FileResponse(str(index_file))
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"error": str(e)}
