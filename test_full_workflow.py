#!/usr/bin/env python3
"""
Full workflow test for the AI Interview Agent with Audio Recording
"""

import asyncio
import aiohttp
import json
import tempfile
import os
import wave
import struct
import websockets
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

async def test_full_workflow():
    """Test the complete interview workflow with audio recording"""
    print("Testing Full AI Interview Workflow...")
    print("=" * 50)
    
    # Test 1: WebSocket connection and session creation
    print("1. Testing WebSocket connection...")
    try:
        async with websockets.connect('ws://localhost:8000/ws') as websocket:
            # Wait for greeting message
            greeting = await websocket.recv()
            greeting_data = json.loads(greeting)
            
            if greeting_data.get('type') == 'greeting':
                print("   ✓ WebSocket connected and received greeting")
                session_id = greeting_data.get('session_id')
                if session_id:
                    print(f"   ✓ Session ID: {session_id}")
                else:
                    print("   ✗ No session ID received")
                    return
            else:
                print("   ✗ Unexpected greeting format")
                return

            # Test 2: Audio recording and transcription (keep WebSocket open)
            print("\n2. Testing audio recording and transcription...")
            try:
                # Create a valid WAV file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    create_valid_wav_file(temp_file.name, duration_seconds=2)
                    
                    async with aiohttp.ClientSession() as session:
                        data = aiohttp.FormData()
                        data.add_field('file', open(temp_file.name, 'rb'), filename='test_response.wav')
                        data.add_field('session_id', session_id)
                        
                        async with session.post("http://localhost:8000/transcribe", data=data) as response:
                            if response.status == 200:
                                result = await response.json()
                                print("   ✓ Audio transcription successful")
                                print(f"   Transcription: '{result.get('transcription', '')}'")
                            else:
                                print(f"   ✗ Transcription failed: {response.status}")
                                error_text = await response.text()
                                print(f"   Error: {error_text}")
                                return
                
                # Clean up
                os.unlink(temp_file.name)
                
            except Exception as e:
                print(f"   ✗ Audio recording test failed: {e}")
                return

            # Test 3: Check if recording was saved (while WebSocket is still open)
            print("\n3. Checking if recording was saved...")
            recordings_dir = Path("recordings")
            session_dir = recordings_dir / session_id
            
            if session_dir.exists():
                audio_files = list(session_dir.glob("*.wav"))
                metadata_files = list(session_dir.glob("*.json"))
                print(f"   ✓ Recording saved successfully")
                print(f"   Audio files: {len(audio_files)}")
                print(f"   Metadata files: {len(metadata_files)}")
                
                # Show metadata content
                if metadata_files:
                    with open(metadata_files[0], 'r') as f:
                        metadata = json.load(f)
                        print(f"   Session ID: {metadata.get('session_id')}")
                        print(f"   File size: {metadata.get('file_size_mb', 0)}MB")
                        print(f"   Audio format: {metadata.get('audio_format')}")
            else:
                print("   ✗ Recording not found")
                return

            # Test 4: Test recordings API
            print("\n4. Testing recordings API...")
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:8000/recordings") as response:
                        if response.status == 200:
                            data = await response.json()
                            recordings = data.get('recordings', [])
                            print(f"   ✓ Recordings API working ({len(recordings)} sessions)")
                            
                            # Check if our session is listed
                            session_found = any(r.get('session_id') == session_id for r in recordings)
                            if session_found:
                                print("   ✓ Our session is listed in recordings")
                            else:
                                print("   ✗ Our session not found in recordings list")
                        else:
                            print(f"   ✗ Recordings API failed: {response.status}")
            except Exception as e:
                print(f"   ✗ Recordings API error: {e}")

            print("\n" + "=" * 50)
            print("Full workflow test completed!")
            print(f"Session ID: {session_id}")
            print("You can view the recording in the web interface at http://localhost:8080")

    except Exception as e:
        print(f"   ✗ WebSocket connection failed: {e}")
        return

if __name__ == "__main__":
    asyncio.run(test_full_workflow()) 