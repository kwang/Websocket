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

## Project Structure

```
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
