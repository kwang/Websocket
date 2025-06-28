# AI Interview Agent with Audio Recording

A Python-based AI interview system that conducts voice interviews, records audio responses, and provides contextual follow-up questions using OpenAI's Chat API.

## Features

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
- OpenAI API key (for intelligent interview responses)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Websocket
   ```

2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Install ffmpeg** (if not already installed):
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

4. **Configure OpenAI API** (optional but recommended):
   - Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Copy `config.example.py` to `config.py`
   - Update `OPENAI_API_KEY` in `config.py` with your API key

## Configuration

Copy `config.example.py` to `config.py` and customize the settings:

```python
# OpenAI settings (recommended)
OPENAI_API_KEY = "your-openai-api-key-here"
OPENAI_MODEL = "gpt-3.5-turbo"  # or "gpt-4" for better responses
USE_OPENAI_FOR_INTERVIEW = True

# OpenAI TTS settings
USE_OPENAI_TTS = True  # Enable AI-powered voice synthesis
OPENAI_TTS_VOICE = "alloy"  # Options: alloy, echo, fable, onyx, nova, shimmer
OPENAI_TTS_MODEL = "tts-1"  # Options: tts-1, tts-1-hd (HD is higher quality but slower)

# Audio settings
AUDIO_FORMAT = "mp3"  # All audio saved as MP3 for consistency
AUDIO_QUALITY = "high"

# Combined audio settings
CREATE_COMBINED_AUDIO = True  # Automatically create combined interview files
COMBINED_AUDIO_FILENAME = "combined_interview.mp3"

# Server settings
HOST = "0.0.0.0"
PORT = 8000
```

## Usage

1. **Start the server**: `python3 server.py`
2. **Start the client**: `python3 client.py`
3. **Open your browser**: Navigate to `http://localhost:8080`
4. **Test speech synthesis**: Click "Test Speech" to verify TTS is working
5. **Select AI Voice**: Choose your preferred voice from the dropdown menu
6. **Start recording**: Click "Start Recording" and speak your response
7. **View recordings**: Check the "Recordings" tab to see saved sessions

### Voice Selection
- **Alloy**: Neutral, balanced voice
- **Echo**: Male voice with clear pronunciation
- **Fable**: Male voice with warm tone
- **Onyx**: Male voice with deep resonance
- **Nova**: Female voice with bright tone
- **Shimmer**: Female voice with smooth delivery

You can change voices at any time during the interview using the dropdown menu.

## Features in Detail

### OpenAI Integration
- **Contextual Questions**: AI generates relevant follow-up questions based on your responses
- **Natural Conversation**: More human-like interview flow
- **Adaptive Responses**: Questions adapt to your background and experience
- **Fallback Support**: Uses predefined questions if OpenAI is unavailable

### AI Voice Synthesis
- **High-Quality Voices**: OpenAI TTS with natural-sounding AI voices
- **Multiple Voice Options**: Choose from 6 different AI voices (alloy, echo, fable, onyx, nova, shimmer)
- **Dynamic Voice Selection**: Change voices during interviews using the dropdown menu
- **HD Quality**: Optional HD model for even better audio quality
- **Automatic Fallback**: Falls back to browser speech synthesis if TTS fails
- **Real-time Generation**: Speech is generated on-demand for each question

### Audio Recording & MP3 Conversion
- **Complete Conversations**: Records both interviewer questions and candidate responses
- **MP3 Format**: All audio files saved as MP3 for consistency and compatibility
- **Interviewer Speech**: AI-generated questions are saved as MP3 files with metadata
- **Candidate Responses**: User audio responses are converted and saved as MP3 files
- **Session Organization**: All recordings organized by interview session
- **Metadata Tracking**: Detailed metadata for each recording including timestamps and voice settings

### Combined Audio Files
- **Automatic Combining**: Creates a single MP3 file containing the complete interview
- **Chronological Order**: Combines all audio files in timestamp order
- **Easy Sharing**: Single file for easy sharing or archiving of complete interviews
- **File Management**: Combined files are clearly labeled and easy to identify

### Speech Synthesis
- **Voice Selection**: Automatically selects the best available voice
- **Error Handling**: Graceful fallback if speech synthesis fails
- **Test Function**: Built-in test to verify speech is working

## API Endpoints

- `GET /recordings` - List all interview recordings
- `GET /recordings/{session_id}` - Get details of a specific session
- `POST /transcribe` - Transcribe uploaded audio
- `POST /tts` - Generate speech from text
- `WebSocket /ws` - Real-time interview communication

## Testing

Run the test scripts to verify functionality:

```bash
# Test MP3 conversion and combining
python3 test_mp3_conversion.py

# Test audio conversion
python3 test_audio_conversion.py

# Test OpenAI integration
python3 test_openai_integration.py

# Test TTS functionality
python3 test_tts.py

# Test interviewer speech recording
python3 test_interviewer_recording.py

# Test full workflow
python3 test_full_workflow.py
```

## Troubleshooting

### Audio Issues
- **Can't open MP3 files**: Ensure ffmpeg is installed
- **No audio recording**: Check browser microphone permissions
- **Poor audio quality**: Adjust `AUDIO_QUALITY` in config
- **Combined audio not created**: Check that `CREATE_COMBINED_AUDIO` is enabled

### OpenAI Issues
- **No contextual responses**: Check your OpenAI API key
- **API errors**: Verify your API key has sufficient credits
- **Slow responses**: Consider using GPT-3.5-turbo instead of GPT-4

### Speech Issues
- **No speech**: Click "Test Speech" button to debug
- **Browser compatibility**: Ensure your browser supports SpeechSynthesis

## File Structure

```
Websocket/
├── server.py              # FastAPI server with OpenAI integration
├── client.py              # Web client with speech synthesis
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── recordings/            # Saved interview recordings
│   └── session_id/        # Individual session directories
│       ├── response_*.mp3 # Candidate responses (MP3)
│       ├── interviewer_*.mp3 # Interviewer speech (MP3)
│       ├── combined_interview.mp3 # Complete interview (MP3)
│       └── metadata_*.json # Session metadata
├── test_*.py             # Test scripts
└── README.md             # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 