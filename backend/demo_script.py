import uvicorn
import asyncio
import httpx
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any

async def demo_client():
    """Demonstrates client interaction with the math challenge server"""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Get a new problem
        print("\n1. Requesting a new math problem...")
        response = await client.get("/problem")
        problem_data = response.json()
        
        problem_id = problem_data["problem_id"]
        question = problem_data["question"]
        print(f"Received problem #{problem_id}: {question}")
        
        # Calculate answer (for demo purposes)
        num1, num2 = map(int, question.split(" + "))
        correct_answer = num1 + num2
        
        # First, submit correct answer
        print("\n2. Submitting correct answer...")
        response = await client.post("/check_answer", json={
            "problem_id": problem_id,
            "user_answer": correct_answer
        })
        print(f"Server response: {response.json()}")
        
        # Then, submit wrong answer
        print("\n3. Submitting wrong answer...")
        response = await client.post("/check_answer", json={
            "problem_id": problem_id,
            "user_answer": correct_answer + 1
        })
        print(f"Server response: {response.json()}")
        
        # Try invalid problem ID
        print("\n4. Testing invalid problem ID...")
        response = await client.post("/check_answer", json={
            "problem_id": 99999,
            "user_answer": 42
        })
        print(f"Server response: {response.json()}")

def run_server():
    """Runs the FastAPI server"""
    uvicorn.run("challenge_server:app", host="127.0.0.1", port=8000)

async def main():
    # Start server in a separate thread
    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(run_server)
    
    # Wait for server to start
    print("Starting server...")
    time.sleep(2)
    
    # Run demo client
    print("Running demo client...")
    await demo_client()
    
    print("\nDemo completed! Press Ctrl+C to exit.")

if __name__ == "__main__":
    asyncio.run(main()) 