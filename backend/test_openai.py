from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def test_api_key():
    api_key = os.getenv('OPENAI_API_KEY')
    print("API Key found:", api_key[:10] + "..." if api_key else "No API key found")
    
    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello"}],
            temperature=0.7
        )
        print("API Key is working!")
        print("Response:", response.choices[0].message.content)
    except Exception as e:
        print("Error testing API key:", str(e))

if __name__ == "__main__":
    test_api_key() 