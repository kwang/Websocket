# AI Interview Agent with Audio Recording

A Python-based AI interview system that conducts voice interviews, records audio responses, and provides contextual follow-up questions using OpenAI's Chat API.

- 🎤 **Voice Recording**: Record high-quality audio responses
- 🗣️ **AI Voice Synthesis**: OpenAI-powered text-to-speech with natural AI voices
- 🤖 **OpenAI Integration**: Contextual interview questions using GPT-3.5/GPT-4
- 📝 **Audio Transcription**: Automatic speech-to-text using OpenAI Whisper
- 💾 **Session Management**: Save and organize interview recordings
- 🔄 **Audio Conversion**: Automatic WebM to MP3 conversion for compatibility
- 🎵 **Combined Audio**: Automatic creation of complete interview MP3 files
- 📊 **Recording Management**: View and manage interview sessions

## Prerequisites

- Python 3.9+
- ffmpeg (for audio conversion and combining)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Websocket
   ```

2. **Install Python dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Install ffmpeg** (if not already installed):
   ```bash
   # macOS (using Homebrew)
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg
   
   # Windows (using Chocolatey)
   choco install ffmpeg
   ```

4. **Configure OpenAI API**:
   ```bash
   # Copy the example config
   cp config.example.py config.py
   
   # Edit config.py and add your OpenAI API key
   # Or set environment variable:
   export OPENAI_API_KEY="your-api-key-here"
   ```

## Quick Start

### Option 1: Using the Service Manager (Recommended)

The easiest way to start and manage the system:

```bash
# Start all services
python3 manage_services.py start

# Check status
python3 manage_services.py status

# Stop all services
python3 manage_services.py stop

# Restart services
python3 manage_services.py restart

# Clean up any stuck processes
python3 manage_services.py clean
```

### Option 2: Manual Start

1. **Start the server** (in one terminal):
   ```bash
   python3 server.py
   ```

2. **Start the client** (in another terminal):
   ```bash
   python3 client.py
   ```

3. **Open your browser** and go to: `http://localhost:8080`

## Usage

1. **Open the web interface** at `http://localhost:8080`
2. **Select an AI voice** from the dropdown menu
3. **Test the speech synthesis** by clicking "Test Speech"
4. **Start an interview** by clicking "Start Recording"
5. **Speak your response** when prompted
6. **Stop recording** to process your response
7. **View recordings** in the "Recordings" tab

## Features

### Voice Recording
- High-quality audio recording using browser MediaRecorder API
- Automatic WebM to MP3 conversion for compatibility
- Session-based recording organization

### AI Interview Questions
- Contextual questions based on your responses
- OpenAI GPT-3.5/GPT-4 integration for natural conversation
- Fallback to predefined questions if OpenAI is unavailable

### Text-to-Speech
- OpenAI TTS with 6 different AI voices (Alloy, Echo, Fable, Onyx, Nova, Shimmer)
- Browser speech synthesis fallback
- Voice selection and testing

### Recording Management
- Automatic session creation and management
- Separate storage of interviewer and candidate audio
- Combined interview MP3 files
- Metadata storage for each session
- Web interface for browsing recordings

## Configuration

Edit `config.py` to customize:

- **OpenAI Settings**: API key, model, temperature, max tokens
- **Audio Settings**: Format (MP3/WAV), quality, bitrate
- **Server Settings**: Ports, CORS origins, file paths
- **Whisper Settings**: Model size, language detection

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the ports
lsof -ti:8000,8080

# Kill processes on those ports
python3 manage_services.py clean
```

#### 2. Client do_GET Error
This usually means there's a syntax error or import issue:
```bash
# Check for syntax errors
python3 -m py_compile client.py

# Restart services
python3 manage_services.py restart
```

#### 3. Server Crashes with Semaphore Warnings
This can happen with rapid restarts:
```bash
# Clean up and restart
python3 manage_services.py clean
python3 manage_services.py start
```

#### 4. OpenAI API Key Issues
```bash
# Check if API key is set
echo $OPENAI_API_KEY

# Or check config.py
cat config.py | grep OPENAI_API_KEY
```

#### 5. Audio Recording Issues
- Ensure microphone permissions are granted in browser
- Check that ffmpeg is installed: `ffmpeg -version`
- Try refreshing the browser page

### Testing

Use the provided test scripts to verify functionality:

```bash
# Test system status
python3 test_system_status.py

# Test OpenAI integration
python3 test_openai_integration.py

# Test TTS functionality
python3 test_tts.py

# Test audio conversion
python3 test_mp3_conversion.py

# Test full workflow
python3 test_full_workflow.py
```

## Project Structure

```
├── server.py              # FastAPI backend server
├── client.py              # Web client and HTTP server
├── config.py              # Configuration settings
├── config.example.py      # Example configuration
├── requirements.txt       # Python dependencies
├── manage_services.py     # Service management script
├── test_system_status.py  # System status testing
├── recordings/            # Saved interview recordings
│   └── session_id/        # Individual session directories
│       ├── response_*.mp3 # Candidate responses (MP3)
│       ├── interviewer_*.mp3 # Interviewer speech (MP3)
│       ├── combined_interview.mp3 # Complete interview (MP3)
│       └── metadata_*.json # Session metadata
├── test_*.py             # Test scripts
└── README.md             # This file
```

## API Endpoints

- `GET /recordings` - List all recording sessions
- `GET /recordings/{session_id}` - Get specific session details
- `POST /transcribe` - Transcribe audio file
- `POST /tts` - Convert text to speech
- `WebSocket /ws` - Real-time communication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
