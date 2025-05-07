# AI Interview Agent

This is a client-server application that uses OpenAI's Whisper for speech-to-text conversion and provides an AI-powered interview experience.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python server.py
```

4. Open the client interface in your browser:
```bash
python client.py
```

## Features

- Real-time speech-to-text conversion using OpenAI's Whisper
- Web-based interview interface
- Server-side processing for better performance
- WebSocket communication for real-time updates

## Requirements

- Python 3.8+
- FFmpeg (for audio processing)
- Sufficient disk space for Whisper model 