import pytest
from fastapi.testclient import TestClient
from challenge_server import app, active_problems

client = TestClient(app)

def test_get_problem():
    response = client.get("/problem")
    assert response.status_code == 200
    
    data = response.json()
    assert "problem_id" in data
    assert "question" in data
    
    # Verify problem format (should be "X + Y")
    question = data["question"]
    parts = question.split(" + ")
    assert len(parts) == 2
    assert all(part.isdigit() for part in parts)
    assert 1 <= int(parts[0]) <= 10
    assert 1 <= int(parts[1]) <= 10

def test_check_correct_answer():
    # First get a problem
    problem_response = client.get("/problem")
    problem_data = problem_response.json()
    problem_id = problem_data["problem_id"]
    
    # Calculate correct answer from the question
    question = problem_data["question"]
    num1, num2 = map(int, question.split(" + "))
    correct_answer = num1 + num2
    
    # Submit correct answer
    response = client.post("/check_answer", json={
        "problem_id": problem_id,
        "user_answer": correct_answer
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is True
    assert data["correct_answer"] == correct_answer

def test_check_wrong_answer():
    # Get a problem
    problem_response = client.get("/problem")
    problem_data = problem_response.json()
    problem_id = problem_data["problem_id"]
    
    # Calculate correct answer and submit wrong answer
    question = problem_data["question"]
    num1, num2 = map(int, question.split(" + "))
    correct_answer = num1 + num2
    wrong_answer = correct_answer + 1
    
    response = client.post("/check_answer", json={
        "problem_id": problem_id,
        "user_answer": wrong_answer
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is False
    assert data["correct_answer"] == correct_answer

def test_invalid_problem_id():
    response = client.post("/check_answer", json={
        "problem_id": 99999,  # Non-existent problem ID
        "user_answer": 42
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "Invalid problem ID"

@pytest.fixture(autouse=True)
def clear_active_problems():
    """Clear active_problems before each test"""
    active_problems.clear()
    yield 