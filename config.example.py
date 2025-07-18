"""
Example configuration file for the AI Interview Agent with Audio Recording
Copy this file to config.py and modify the settings as needed.
"""

import os
from pathlib import Path

# Recording settings
RECORDINGS_DIR = Path("recordings")
MAX_RECORDING_SIZE_MB = 50
AUDIO_FORMAT = "mp3"  # Changed from wav to mp3 for consistency
AUDIO_QUALITY = "high"  # high, medium, low

# Session settings
SESSION_TIMEOUT_MINUTES = 60
AUTO_CLEANUP_DAYS = 30

# Whisper settings
WHISPER_MODEL = "base"  # tiny, base, small, medium, large

# Server settings
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# Metadata settings
SAVE_TRANSCRIPTION = True
SAVE_AUDIO_DURATION = True
SAVE_AUDIO_QUALITY = True

# File naming patterns
AUDIO_FILENAME_PATTERN = "response_{timestamp}.{ext}"
METADATA_FILENAME_PATTERN = "metadata_{timestamp}.json"
SESSION_ID_PATTERN = "interview_{date}_{time}_{client_suffix}"

# Combined audio settings
CREATE_COMBINED_AUDIO = False  # Manual audio combining via Finish button
COMBINED_AUDIO_FILENAME = "combined_interview.mp3"

# Backup settings
AUTO_BACKUP = False
BACKUP_DIR = Path("backups")
BACKUP_INTERVAL_HOURS = 24

# Security settings
ALLOWED_ORIGINS = "*"
REQUIRE_AUTHENTICATION = False
API_KEY = None

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")  # Replace with your actual API key
OPENAI_MODEL = "gpt-3.5-turbo"  # or "gpt-4" for better responses
OPENAI_MAX_TOKENS = 150
OPENAI_TEMPERATURE = 0.7
USE_OPENAI_FOR_INTERVIEW = True

# OpenAI TTS settings
USE_OPENAI_TTS = True  # Enable AI-powered voice synthesis
OPENAI_TTS_VOICE = "alloy"  # Options: alloy, echo, fable, onyx, nova, shimmer
OPENAI_TTS_MODEL = "tts-1"  # Options: tts-1, tts-1-hd (HD is higher quality but slower)

# Server settings
SERVER_HOST = "localhost"
SERVER_PORT = 8080

# Recording settings
RECORDING_DIR = "recordings"
MAX_RECORDING_DURATION = 300  # 5 minutes in seconds

# Audio settings
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1

# Video settings
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
VIDEO_FPS = 30

# TTS settings
TTS_VOICE = "alloy"  # Options: alloy, echo, fable, onyx, nova, shimmer
TTS_MODEL = "tts-1"

# Interview settings
INTERVIEW_QUESTIONS = [
    "Hello! I'm your AI interviewer today. Could you please introduce yourself?",
    "That's interesting! Could you elaborate on that?",
    "What are your strengths and weaknesses?",
    "Where do you see yourself in 5 years?",
    "Why are you interested in this position?"
]

# File upload settings
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB in bytes

# Logging settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Development settings
RELOAD_ON_CHANGE = True 