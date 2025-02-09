from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

def get_fallback_problem():
    """Return a pre-generated problem when API is unavailable"""
    problems = [
        {
            "question": "A store sells notebooks for $2.50 each. If you have $15, how many notebooks can you buy?",
            "answer": 6,
            "explanation": "1. Money available = $15\n2. Cost per notebook = $2.50\n3. Number of notebooks = $15 ÷ $2.50 = 6"
        },
        {
            "question": "If a train travels 120 miles in 2 hours, what is its average speed in miles per hour?",
            "answer": 60,
            "explanation": "1. Speed = Distance ÷ Time\n2. Distance = 120 miles\n3. Time = 2 hours\n4. Speed = 120 ÷ 2 = 60 mph"
        },
        {
            "question": "A rectangle has a length of 8 inches and a width of 5 inches. What is its area in square inches?",
            "answer": 40,
            "explanation": "1. Area of rectangle = length × width\n2. Area = 8 × 5 = 40 square inches"
        }
    ]
    import random
    return random.choice(problems)

def sanitize_json_string(s):
    """Clean up the string to make it valid JSON"""
    # Remove markdown code block indicators
    s = s.replace('```json', '').replace('```', '')
    
    # Remove any control characters
    import re
    s = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', s)
    
    # Ensure proper quote usage
    s = s.replace('"', '"').replace('"', '"')
    
    # Remove any leading/trailing whitespace
    s = s.strip()
    
    print("Sanitized content:", s)  # Debug print
    return s

def generate_word_problem():
    """Generate a math word problem using OpenAI"""
    api_key = os.getenv('OPENAI_API_KEY')
    print("Using API Key:", api_key[:10] + "..." if api_key else "No API key found")
    
    if not api_key:
        return get_fallback_problem()

    client = OpenAI(api_key=api_key)

    prompt = """Generate a math word problem with these requirements:
    1. Suitable for grades 5-8, should be interesting and challenging puzzles
    2. Assume the kid is a talented math student and is seeking acceleration
    3. Do not hallucinate, the answer should be a number
    4. Do not hallucinate. Make sure your answer is correct.
    5. Return the response in this JSON format:
    {
        "question": "the word problem text",
        "answer": numerical answer only,
        "explanation": "step by step solution"
    }
    
    Example:
    {
        "question": "Sam is twice the age of Max. In 4 years, he will be 1.5 times his age. How old is Max now?",
        "answer": 8,
        "explanation": "1. Let x be Max's current age\n2. Sam's age is 2x\n3. In 4 years: (2x + 4) = 1.5(x + 4)\n4. Solve: 2x + 4 = 1.5x + 6\n5. 0.5x = 2\n6. x = 4\nTherefore, Max is 8 years old"
    }
    """

    try:
        response = client.chat.completions.create(
            model="chatgpt-4o-latest",
            messages=[
                {"role": "system", "content": "You are a math teacher creating word problems."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # Add debug logging
        content = response.choices[0].message.content
        print("Raw response:", content)
        
        # Sanitize and parse the response
        sanitized_content = sanitize_json_string(content)
        try:
            result = json.loads(sanitized_content)
            # Validate the required fields
            if all(key in result for key in ["question", "answer", "explanation"]):
                return result
            else:
                print("Missing required fields in response")
                return get_fallback_problem()
        except json.JSONDecodeError as je:
            print(f"JSON parsing error: {je}")
            print(f"Attempted to parse: {sanitized_content}")
            return get_fallback_problem()
        
    except Exception as e:
        print(f"Error generating problem: {str(e)}")
        import traceback
        traceback.print_exc()
        return get_fallback_problem() 
    