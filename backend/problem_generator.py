from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import logging

load_dotenv()

logger = logging.getLogger(__name__)

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
    if not api_key:
        logger.error("OpenAI API key not found")
        return get_fallback_problem()

    try:
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
        {
            "question": "In an enclosure there is a group of kangaroos. If you add up the ages of all kangaroos you get 36 years. In two
                        years all the kangaroos together will be 60 years old.
                        How many kangaroos are in the enclosure?",
            "answer": 12,
            "explanation": "1. Let x be the number of kangaroos\n2. If you add up the ages of all kangaroos you get 36 years\n3. In two years all the kangaroos together will be 60 years old\n4. Solve: 36 + 2x = 60\n5. 2x = 24\n6. x = 12\nTherefore, there are 12 kangaroos in the enclosure"
        }
        {
            "question": "The six smallest odd natural numbers are written on the sides of a die. Toni rolls the die three times and adds the
                        numbers. Which sum will Toni not be able to make? The choices are: 3, 19, 21, 29, 35",
            "answer": 33,
            "explanation": "1. The six smallest odd natural numbers are 1, 3, 5, 7, 9, 11\n2. The possible sums of three numbers from this set are: 9, 11, 13, 15, 17, 19, 21\n3. The sum 15 is possible\n4. The sum 17 is possible\n5. The sum 19 is possible\n6. The sum 21 is possible\n7. 29 can be 11 + 9 + 9. But 35 is not possible since the maximum from 3 rolls is 33 (11 + 11 + 11)."
        }
        {
            "question": "In a witch’s garden there are 30 animals: dogs, cats and mice. The witch changes 6 dogs into 6 cats and then 5
                        cats into 5 mice. Now there is an equal number of dogs, cats and mice.
                        How many cats were there to start with?",
            "answer": 8,
            "explanation": "d + c + m = 30. d - 6 = c + 6, d - c = 12; c - m = 4;  d + d - 12 + d + 8 = 30; 3d = 42; d = 14; c = 8; m = 4 "
        }
        """

        # First, list available models to verify
        models = client.models.list()
        available_models = [model.id for model in models]
        print(f"Available models: {available_models}")  # This will show all models you have access to
        
        model_name = "gpt-4"  # or whatever model you want to use
        if model_name not in available_models:
            print(f"Warning: {model_name} not available. Available models: {available_models}")
            return get_fallback_problem()

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": """Generate a math word problem with these requirements:
        1. Suitable for grades 5-8, should be interesting and challenging puzzles
        2. Assume the kid is a talented math student and is seeking acceleration
        3. Do not hallucinate, the answer should be a number
        4. Do not hallucinate. Make sure your answer is correct."""}
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        # Add model verification to the response logging
        print(f"Used model: {response.model}")  # This will show which model was actually used
        
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
        logger.error(f"Error initializing OpenAI client: {str(e)}")
        return get_fallback_problem() 
    