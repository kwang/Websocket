# AI Interview Agent with Audio Recording

A Python-based AI interview system that conducts voice interviews, records audio responses, and provides contextual follow-up questions using OpenAI's Chat API.

- 🎤 **Voice Recording**: Record high-quality audio responses
- 🗣️ **AI Voice Synthesis**: OpenAI-powered text-to-speech with natural AI voices
- 🤖 **OpenAI Integration**: Contextual interview questions using GPT-3.5/GPT-4
- 📝 **Audio Transcription**: Automatic speech-to-text using OpenAI Whisper
- 💾 **Session Management**: Save and organize interview recordings
- 🔄 **Audio Conversion**: Automatic WebM to MP3 conversion for compatibility
- 🎵 **Combined Audio**: Automatic creation of complete interview MP3 files
- 📊 **Recording Management**: View and manage all interview recordings
- 🎧 **Audio Playback**: Play individual and combined audio files in browser
- 📅 **Smart Sorting**: Recordings sorted by date (newest first)

## Features

### 🎤 Voice Recording & Transcription
- Record audio responses using browser microphone
- Automatic WebM to MP3 conversion for compatibility
- Real-time transcription using OpenAI Whisper
- Session-based audio file organization

### 🗣️ AI Voice Synthesis
- OpenAI Text-to-Speech (TTS) integration
- Multiple voice options (alloy, echo, fable, onyx, nova, shimmer)
- Professional-grade AI voices for interviewer
- Automatic interviewer speech recording

### 🤖 OpenAI Chat Integration
- Contextual interview questions based on responses
- Intelligent follow-up questions
- Conversation history tracking
- Fallback to predefined questions if API unavailable

### 📊 Recording Management
- **Browser Playback**: Play audio files directly in the browser
- **Individual Files**: Play separate interviewer and candidate audio
- **Combined Audio**: Automatic creation of complete interview MP3
- **Smart Organization**: Files organized by session with timestamps
- **Metadata Storage**: JSON metadata for each recording
- **Date Sorting**: Recordings displayed newest first

### 🎵 Audio Combining
- **Automatic Combining**: All session audio files combined into single MP3
- **Chronological Order**: Files combined in timestamp order
- **FFmpeg Integration**: Professional audio processing
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites
- Python 3.8+
- FFmpeg (for audio conversion and combining)
- OpenAI API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Websocket
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg**
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`
   - **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html)

4. **Configure OpenAI API**
   ```bash
   cp config.example.py config.py
   ```
   Edit `config.py` and add your OpenAI API key:
   ```python
   OPENAI_API_KEY = "your-api-key-here"
   ```

## Usage

### Quick Start

1. **Start the server**
   ```bash
   python3 server.py
   ```

2. **Start the client**
   ```bash
   python3 client.py
   ```

3. **Open your browser**
   Navigate to `http://localhost:8080`

### Using the Interface

1. **Interview Tab**
   - Select your preferred AI voice
   - Click "Start Interview" to begin
   - Record your responses using the microphone
   - View real-time transcription and AI responses

2. **Recordings Tab**
   - View all interview sessions sorted by date
   - Click "View Details" to see individual session files
   - Play individual audio files (interviewer/candidate)
   - Play combined audio files (complete interview)
   - Download audio files for offline use

3. **Voice Testing**
   - Test different AI voices before starting
   - Adjust voice settings as needed

### Audio Playback Features

- **Individual Files**: Play separate interviewer questions and candidate responses
- **Combined Audio**: Play complete interview as single MP3 file
- **Browser Integration**: No external players needed
- **Session Organization**: All files organized by interview session
- **Metadata Access**: View detailed information about each recording

## File Structure

```
recordings/
├── interview_YYYYMMDD_HHMMSS_XXXXXX/
│   ├── interviewer_YYYYMMDD_HHMMSS.mp3    # AI interviewer speech
│   ├── response_YYYYMMDD_HHMMSS.mp3       # Candidate response
│   ├── combined_interview.mp3             # Complete interview (auto-generated)
│   ├── metadata_YYYYMMDD_HHMMSS.json     # Response metadata
│   └── interviewer_metadata_YYYYMMDD_HHMMSS.json  # Interviewer metadata
```

## Configuration

### Server Configuration (`config.py`)

```python
# OpenAI Settings
OPENAI_API_KEY = "your-api-key"
OPENAI_MODEL = "gpt-4"
OPENAI_TTS_MODEL = "tts-1"
OPENAI_TTS_VOICE = "alloy"

# Audio Settings
AUDIO_FORMAT = "mp3"
CREATE_COMBINED_AUDIO = True
COMBINED_AUDIO_FILENAME = "combined_interview.mp3"

# Server Settings
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True
```

### Available AI Voices
- `alloy` - Neutral, professional
- `echo` - Warm, friendly
- `fable` - Storytelling, engaging
- `onyx` - Deep, authoritative
- `nova` - Bright, energetic
- `shimmer` - Soft, gentle

## API Endpoints

### Server Endpoints
- `GET /recordings` - List all recording sessions
- `GET /recordings/{session_id}` - Get session details
- `GET /recordings/{session_id}/{filename}` - Serve audio files
- `POST /transcribe` - Transcribe audio files
- `POST /tts` - Generate speech from text
- `WebSocket /ws` - Real-time interview communication

### Audio File Access
Audio files can be accessed directly via URL:
```
http://localhost:8000/recordings/{session_id}/{filename}
```

## Testing

### Run System Tests
```bash
python3 test_system_status.py
```

### Test Audio Functionality
```bash
python3 test_audio_combining.py
python3 test_combine_audio.py
```

### Test OpenAI Integration
```bash
python3 test_openai_integration.py
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   python3 manage_services.py restart
   ```

2. **Audio Not Playing**
   - Check browser permissions for audio
   - Verify FFmpeg is installed
   - Check audio file format compatibility

3. **OpenAI API Errors**
   - Verify API key is correct
   - Check API quota and billing
   - Ensure internet connection

4. **Audio Combining Fails**
   - Verify FFmpeg installation
   - Check file permissions
   - Ensure audio files are valid

### Service Management

Use the included service manager for easy control:
```bash
python3 manage_services.py start    # Start services
python3 manage_services.py stop     # Stop services
python3 manage_services.py restart  # Restart services
python3 manage_services.py status   # Check service status
```

## Development

### Project Structure
```
├── server.py              # FastAPI server
├── client.py              # Web client
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── recordings/            # Audio recordings
├── test_*.py             # Test scripts
└── manage_services.py    # Service management
```

### Adding New Features
1. Update server endpoints in `server.py`
2. Modify client interface in `client.py`
3. Add configuration options to `config.py`
4. Create test scripts for new functionality
5. Update documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review existing issues
3. Create a new issue with detailed information
4. Include system information and error logs
