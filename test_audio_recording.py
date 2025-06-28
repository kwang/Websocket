#!/usr/bin/env python3
"""
Test script for the AI Interview Agent audio recording functionality
"""

import asyncio
import aiohttp
import json
import tempfile
import os
import wave
import struct
from pathlib import Path

def create_valid_wav_file(filename, duration_seconds=1, sample_rate=16000):
    """Create a valid WAV file with silence"""
    with wave.open(filename, 'w') as wav_file:
        # Set parameters
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Generate silence
        num_frames = int(sample_rate * duration_seconds)
        silence_data = struct.pack('<h', 0) * num_frames
        wav_file.writeframes(silence_data)

async def test_audio_recording():
    """Test the audio recording functionality"""
    print("Testing AI Interview Agent Audio Recording...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("1. Checking server status...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/interview-questions") as response:
                if response.status == 200:
                    print("   ✓ Server is running")
                else:
                    print("   ✗ Server returned status:", response.status)
                    return
    except Exception as e:
        print("   ✗ Cannot connect to server:", e)
        print("   Please make sure the server is running with: python3 server.py")
        return
    
    # Test 2: Check recordings directory
    print("\n2. Checking recordings directory...")
    recordings_dir = Path("recordings")
    if recordings_dir.exists():
        print("   ✓ Recordings directory exists")
    else:
        print("   ✗ Recordings directory not found")
        return
    
    # Test 3: Test recordings API
    print("\n3. Testing recordings API...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/recordings") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✓ Recordings API working ({len(data.get('recordings', []))} sessions)")
                else:
                    print("   ✗ Recordings API failed:", response.status)
    except Exception as e:
        print("   ✗ Recordings API error:", e)
    
    # Test 4: Test file upload (simulate audio recording)
    print("\n4. Testing audio upload...")
    try:
        # Create a valid WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            create_valid_wav_file(temp_file.name, duration_seconds=1)
            
            async with aiohttp.ClientSession() as session:
                data = aiohttp.FormData()
                data.add_field('file', open(temp_file.name, 'rb'), filename='test.wav')
                data.add_field('client_id', 'test_client_123')
                
                async with session.post("http://localhost:8000/transcribe", data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("   ✓ Audio upload working")
                        print(f"   Transcription: {result.get('transcription', 'No transcription')}")
                    else:
                        print("   ✗ Audio upload failed:", response.status)
                        error_text = await response.text()
                        print("   Error:", error_text)
        
        # Clean up
        os.unlink(temp_file.name)
        
    except Exception as e:
        print("   ✗ Audio upload error:", e)
    
    # Test 5: Check if test recording was saved
    print("\n5. Checking if test recording was saved...")
    test_session_dir = recordings_dir / "test_client_123"
    if test_session_dir.exists():
        audio_files = list(test_session_dir.glob("*.wav"))
        metadata_files = list(test_session_dir.glob("*.json"))
        print(f"   ✓ Test recording saved ({len(audio_files)} audio files, {len(metadata_files)} metadata files)")
    else:
        print("   ✗ Test recording not found")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_audio_recording()) 