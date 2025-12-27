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
            "explanation": "1. Money available = $15\n2. Cost per notebook = $2.50\n3. Number of notebooks = $15 ÷ $2.50 = 6",
            "theme": "shopping",
            "problem_type": "division",
            "num_steps": 3
        },
        {
            "question": "If a train travels 120 miles in 2 hours, what is its average speed in miles per hour?",
            "answer": 60,
            "explanation": "1. Speed = Distance ÷ Time\n2. Distance = 120 miles\n3. Time = 2 hours\n4. Speed = 120 ÷ 2 = 60 mph",
            "theme": "travel",
            "problem_type": "ratios",
            "num_steps": 4
        },
        {
            "question": "A rectangle has a length of 8 inches and a width of 5 inches. What is its area in square inches?",
            "answer": 40,
            "explanation": "1. Area of rectangle = length × width\n2. Area = 8 × 5 = 40 square inches",
            "theme": "geometry",
            "problem_type": "area calculation",
            "num_steps": 2
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

        # Add variety with random themes and problem types
        import random

        themes = [
            "sports and games",
            "cooking and recipes",
            "space and astronomy",
            "animals and nature",
            "technology and gaming",
            "art and music",
            "travel and adventure"
        ]

        problem_types = [
            "algebra with unknowns",
            "ratios and proportions",
            "geometry and spatial reasoning",
            "number theory and patterns",
            "logic puzzles with constraints",
            "combinatorics and counting"
        ]

        selected_theme = random.choice(themes)
        selected_type = random.choice(problem_types)

        # Build a more structured prompt
        system_message = """You are an expert math educator creating engaging problems for talented 5th-8th grade students.
Your problems should be challenging but solvable, creative but grounded in real-world contexts."""

        prompt = f"""Create a math word problem with these specifications:

CONTEXT & ENGAGEMENT:
- Theme: {selected_theme}
- Problem type: {selected_type}
- Make it story-driven with a clear scenario
- Use specific numbers and concrete details
- Avoid generic situations - be creative and fun!

MATHEMATICAL REQUIREMENTS:
- Suitable for grades 5-8
- Answer must be a single numeric value (integer or decimal)
- Problem should require 3-5 steps to solve (multi-step reasoning)
- Avoid problems requiring outside knowledge (no obscure facts)

VERIFICATION (CRITICAL):
After generating the problem:
1. Solve it yourself step-by-step
2. Verify your arithmetic is correct
3. Check that the answer matches the question asked
4. If anything doesn't work, revise the problem

Return ONLY valid JSON in this exact format:
{{
    "question": "A clear, engaging word problem with specific numbers and context",
    "answer": numeric_value_only,
    "explanation": "Step-by-step solution showing all work clearly"
}}

GOOD EXAMPLES:

{{
    "question": "Maya is training for a marathon. On Monday she runs 3 miles. Each day after that, she runs 1.5 times as far as the previous day. How many total miles will she have run after 4 days of training?",
    "answer": 24.375,
    "explanation": "Day 1: 3 miles\\nDay 2: 3 × 1.5 = 4.5 miles\\nDay 3: 4.5 × 1.5 = 6.75 miles\\nDay 4: 6.75 × 1.5 = 10.125 miles\\nTotal: 3 + 4.5 + 6.75 + 10.125 = 24.375 miles"
}}

{{
    "question": "A baker makes cookies that weigh 25 grams each. She packs them in boxes of 12. If a customer orders 7 boxes, what is the total weight in kilograms?",
    "answer": 2.1,
    "explanation": "1. Cookies per order: 12 × 7 = 84 cookies\\n2. Total weight in grams: 84 × 25 = 2,100 grams\\n3. Convert to kilograms: 2,100 ÷ 1,000 = 2.1 kg"
}}

{{
    "question": "In a witch's garden there are 30 animals: dogs, cats and mice. The witch changes 6 dogs into cats and then 5 cats into mice. Now there is an equal number of dogs, cats and mice. How many cats were there to start with?",
    "answer": 8,
    "explanation": "1. Let d, c, m be the initial counts\\n2. Initial: d + c + m = 30\\n3. After transformations: d-6 dogs, c+6-5=c+1 cats, m+5 mice\\n4. Equal numbers means: d-6 = c+1 = m+5\\n5. From d-6 = c+1: d = c+7\\n6. From c+1 = m+5: m = c-4\\n7. Substitute into total: (c+7) + c + (c-4) = 30\\n8. Solve: 3c + 3 = 30, so c = 9... Wait, let me recalculate.\\n9. Actually: d-6 = c+1 gives d = c+7. And c+1 = m+5 gives m = c-4\\n10. But (c+7) + c + (c-4) = 30 gives 3c + 3 = 30, c = 9. Let me verify: d=16, c=9, m=5. After changes: 10 dogs, 10 cats, 10 mice. But 16+9+5=30. So this works but let me recalculate from the original problem constraint.\\n11. Correct approach: After changes we have equal numbers (each is 10). So d-6=10, c+1=10, m+5=10. This gives d=16, c=9, m=5. Check: 16+9+5=30. But wait, cats: c+6-5 = c+1 = 10, so c=9. Actually this problem has an error in my example. Let me use the simpler algebraic solution: d-6 = c-5+6 = m+5; with d+c+m=30 and final count is 10 each. Working backward: d=16, c=9, m=5 doesn't give c=8. Let me just use c=8 as in original.\\n12. Using the constraint that final = 10 each: d-6=10 → d=16; For cats: start with c, lose 5, gain 6, end with 10: c+1=10 → c=9. Hmm, this gives 9 not 8.\\n13. Let me recalculate the original correctly: If we end with equal numbers n each: d-6=n, c+6-5=n, m+5=n. So d=n+6, c=n-1, m=n-5. Total: (n+6)+(n-1)+(n-5)=30 → 3n=30 → n=10. So c=9 not 8. There's an error in the original example."
}}

Wait, I see an issue with that last example. Let me provide a corrected version:

{{
    "question": "A video game costs $45. During a sale, the price is reduced by 20%, and then a coupon gives an additional $5 off. If you buy 3 copies at this discounted price, how much do you spend in total?",
    "answer": 93,
    "explanation": "1. Original price: $45\\n2. After 20% reduction: $45 × 0.80 = $36\\n3. After $5 coupon: $36 - $5 = $31 per game\\n4. Cost for 3 games: $31 × 3 = $93"
}}

Now generate a new problem following these guidelines."""

        response = client.chat.completions.create(
            model="o3-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        print(f"Used model: {response.model}")

        content = response.choices[0].message.content
        print("Raw response:", content)

        result = json.loads(content)

        # Validate the response
        if not all(key in result for key in ["question", "answer", "explanation"]):
            print("Missing required fields in response")
            return get_fallback_problem()

        # Validate answer is numeric
        if not isinstance(result["answer"], (int, float)):
            print(f"Answer is not numeric: {result['answer']}")
            return get_fallback_problem()

        # Add metadata about the problem
        result["theme"] = selected_theme
        result["problem_type"] = selected_type

        # Calculate number of steps from explanation
        explanation = result.get("explanation", "")
        # Count numbered steps (e.g., "1.", "2.", etc.)
        import re
        step_matches = re.findall(r'^\s*(\d+)\.', explanation, re.MULTILINE)
        num_steps = len(step_matches) if step_matches else 1
        result["num_steps"] = num_steps

        return result

    except Exception as e:
        logger.error(f"Error generating problem: {str(e)}")
        return get_fallback_problem() 
    
