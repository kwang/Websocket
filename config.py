"""
Configuration settings for the AI Interview Agent with Audio Recording
"""

import os
from pathlib import Path

# Recording settings
RECORDINGS_DIR = Path(os.getenv("RECORDINGS_DIR", "recordings"))
MAX_RECORDING_SIZE_MB = int(os.getenv("MAX_RECORDING_SIZE_MB", "50"))
AUDIO_FORMAT = os.getenv("AUDIO_FORMAT", "mp3")
AUDIO_QUALITY = os.getenv("AUDIO_QUALITY", "high")  # high, medium, low

# Session settings
SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
AUTO_CLEANUP_DAYS = int(os.getenv("AUTO_CLEANUP_DAYS", "30"))

# Whisper settings
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")  # tiny, base, small, medium, large

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Metadata settings
SAVE_TRANSCRIPTION = os.getenv("SAVE_TRANSCRIPTION", "True").lower() == "true"
SAVE_AUDIO_DURATION = os.getenv("SAVE_AUDIO_DURATION", "True").lower() == "true"
SAVE_AUDIO_QUALITY = os.getenv("SAVE_AUDIO_QUALITY", "True").lower() == "true"

# File naming patterns
AUDIO_FILENAME_PATTERN = os.getenv("AUDIO_FILENAME_PATTERN", "response_{timestamp}.{ext}")
METADATA_FILENAME_PATTERN = os.getenv("METADATA_FILENAME_PATTERN", "metadata_{timestamp}.json")
SESSION_ID_PATTERN = os.getenv("SESSION_ID_PATTERN", "interview_{date}_{time}_{client_suffix}")

# Combined audio settings
CREATE_COMBINED_AUDIO = os.getenv("CREATE_COMBINED_AUDIO", "False").lower() == "true"  # Manual audio combining via Finish button
COMBINED_AUDIO_FILENAME = os.getenv("COMBINED_AUDIO_FILENAME", "combined_interview.mp3")

# Backup settings
AUTO_BACKUP = os.getenv("AUTO_BACKUP", "False").lower() == "true"
BACKUP_DIR = Path(os.getenv("BACKUP_DIR", "backups"))
BACKUP_INTERVAL_HOURS = int(os.getenv("BACKUP_INTERVAL_HOURS", "24"))

# Security settings
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
REQUIRE_AUTHENTICATION = os.getenv("REQUIRE_AUTHENTICATION", "False").lower() == "true"
API_KEY = os.getenv("API_KEY", None)

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")  # Replace with your actual API key
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "150"))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
USE_OPENAI_FOR_INTERVIEW = os.getenv("USE_OPENAI_FOR_INTERVIEW", "True").lower() == "true"

# OpenAI TTS settings
USE_OPENAI_TTS = os.getenv("USE_OPENAI_TTS", "True").lower() == "true"
OPENAI_TTS_VOICE = os.getenv("OPENAI_TTS_VOICE", "alloy")  # alloy, echo, fable, onyx, nova, shimmer
OPENAI_TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "tts-1")  # tts-1, tts-1-hd 