#!/usr/bin/env python3
"""
Test script to verify OpenAI TTS functionality
"""

import requests
import os
from config import *

def test_tts():
    """Test OpenAI TTS functionality"""
    print("Testing OpenAI TTS Integration")
    print("=" * 50)
    
    # Check if OpenAI TTS is enabled
    if not USE_OPENAI_TTS:
        print("❌ OpenAI TTS is disabled in config")
        return False
    
    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-your-actual-openai-api-key-here":
        print("❌ OpenAI API key not configured")
        print("Please set OPENAI_API_KEY in your config.py")
        return False
    
    try:
        # Test TTS endpoint with default voice
        print("Testing TTS endpoint with default voice...")
        test_text = "Hello! This is a test of the OpenAI text-to-speech system."
        
        response = requests.post(
            "http://localhost:8000/tts",
            data={"text": test_text},
            timeout=30
        )
        
        if response.status_code == 200:
            # Save the audio file for testing
            with open("test_tts_output.mp3", "wb") as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"✅ TTS test successful!")
            print(f"   Generated audio file: test_tts_output.mp3")
            print(f"   File size: {file_size} bytes")
            print(f"   Voice: {OPENAI_TTS_VOICE}")
            print(f"   Model: {OPENAI_TTS_MODEL}")
            
            # Clean up test file
            os.remove("test_tts_output.mp3")
            
            # Test different voices
            voices_to_test = ["nova", "echo", "shimmer"]
            for voice in voices_to_test:
                print(f"\nTesting voice: {voice}...")
                response = requests.post(
                    "http://localhost:8000/tts",
                    data={"text": f"This is the {voice} voice speaking.", "voice": voice},
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"✅ {voice} voice test successful!")
                else:
                    print(f"❌ {voice} voice test failed: {response.status_code}")
            
            return True
            
        else:
            print(f"❌ TTS request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False

if __name__ == "__main__":
    test_tts() 