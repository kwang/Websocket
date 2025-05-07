# AI Interviewer

An interactive AI interviewer that uses speech recognition and text-to-speech to conduct interviews.

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your-api-key-here
```

4. Start the server:
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

5. In a new terminal, start the client:
```bash
python client.py
```

6. Open your browser and navigate to:
```
http://localhost:8080
```

## Features

- Real-time speech recognition
- AI-powered interview questions
- Natural text-to-speech responses
- Dynamic follow-up questions
- Web-based interface

## Requirements

- Python 3.9+
- OpenAI API key
- ffmpeg (for audio processing)

## Troubleshooting

If you encounter port conflicts:
```bash
# Kill processes using ports 8000 and 8080
lsof -i :8000,8080 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

If you get ffmpeg errors:
```bash
# Install ffmpeg using Homebrew
brew install ffmpeg
``` 