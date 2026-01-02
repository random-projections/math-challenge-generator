# Math Challenge Generator

An interactive web application that generates AI-powered math word problems for students in grades 1-8. The application uses OpenAI's o3-mini reasoning model to create challenging, age-appropriate math puzzles with step-by-step explanations.

## Features

- **AI-Generated Problems**: Uses OpenAI's o3-mini model to create unique, engaging math word problems
- **Grade Level Personalization**: Select difficulty levels for grades 1-2, 3-5, or 5-8
- **Diverse Content**: Problems cover 24+ themes (sports, cooking, space, etc.) and 30+ problem types
- **Step-by-Step Explanations**: Get detailed solution breakdowns when answers are incorrect
- **Answer Validation**: Automatic checking with floating-point tolerance
- **Fallback System**: Pre-generated problems ensure availability even when API is down

## Project Structure

1. `frontend/`: React application with Tailwind CSS
2. `backend/`: FastAPI server with OpenAI integration
3. `docs/`: Project documentation

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn challenge_server:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm start
```

### Environment Variables
Create a `.env` file in the `backend/` directory:
```
OPENAI_API_KEY=your_api_key_here
DEBUG=false
```

## Deployment

The application automatically deploys to Railway when pushed to GitHub. See `CLAUDE.md` for detailed documentation.

