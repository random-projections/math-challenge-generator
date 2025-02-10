from fastapi import FastAPI, StaticFiles, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from problem_generator import generate_word_problem
import os

app = FastAPI()

# Serve frontend static files
app.mount("/static", StaticFiles(directory="../frontend/build/static"), name="static")

# Serve the React app for all other routes
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404)
    return FileResponse("../frontend/build/index.html")

class AnswerRequest(BaseModel):
    problem_id: int
    user_answer: float  # Changed to float for more complex answers

# In-memory store for active problems and their explanations
active_problems = {}
problem_explanations = {}

@app.get("/api/problem")
def get_problem():
    problem = generate_word_problem()
    problem_id = len(active_problems) + 1000  # Simple ID generation
    
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
