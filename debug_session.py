#!/usr/bin/env python3
"""
Debug script to test session tracking and audio saving
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
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        num_frames = int(sample_rate * duration_seconds)
        silence_data = struct.pack('<h', 0) * num_frames
        wav_file.writeframes(silence_data)

async def debug_session():
    """Debug session tracking and audio saving"""
    print("Debugging Session Tracking and Audio Saving...")
    print("=" * 60)
    
    # Step 1: Connect WebSocket and get session
    print("1. Connecting to WebSocket...")
    try:
        async with websockets.connect('ws://localhost:8000/ws') as websocket:
            greeting = await websocket.recv()
            greeting_data = json.loads(greeting)
            session_id = greeting_data.get('session_id')
            print(f"   ✓ Session ID: {session_id}")
            
            # Step 2: Check if session exists in recordings API
            print("\n2. Checking if session appears in recordings API...")
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8000/recordings") as response:
                    if response.status == 200:
                        data = await response.json()
                        recordings = data.get('recordings', [])
                        print(f"   Current recordings: {len(recordings)}")
                        
                        # Look for our session
                        session_found = any(r.get('session_id') == session_id for r in recordings)
                        if session_found:
                            print(f"   ✓ Our session {session_id} found in recordings")
                        else:
                            print(f"   ✗ Our session {session_id} NOT found in recordings")
            
            # Step 3: Create and upload audio while WebSocket is open
            print("\n3. Uploading audio file...")
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                create_valid_wav_file(temp_file.name, duration_seconds=1)
                
                async with aiohttp.ClientSession() as session:
                    data = aiohttp.FormData()
                    data.add_field('file', open(temp_file.name, 'rb'), filename='debug_test.wav')
                    data.add_field('session_id', session_id)
                    
                    print(f"   Uploading to session: {session_id}")
                    async with session.post("http://localhost:8000/transcribe", data=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            print(f"   ✓ Upload successful: {result.get('transcription', '')}")
                        else:
                            error_text = await response.text()
                            print(f"   ✗ Upload failed: {response.status} - {error_text}")
                
                os.unlink(temp_file.name)
            
            # Step 4: Check if recording was saved (while WebSocket still open)
            print("\n4. Checking if recording was saved...")
            recordings_dir = Path("recordings")
            session_dir = recordings_dir / session_id
            
            if session_dir.exists():
                audio_files = list(session_dir.glob("*.wav"))
                metadata_files = list(session_dir.glob("*.json"))
                print(f"   ✓ Recording saved! Audio: {len(audio_files)}, Metadata: {len(metadata_files)}")
                
                if metadata_files:
                    with open(metadata_files[0], 'r') as f:
                        metadata = json.load(f)
                        print(f"   Session ID in metadata: {metadata.get('session_id')}")
                        print(f"   File size: {metadata.get('file_size_mb', 0)}MB")
            else:
                print(f"   ✗ Recording directory not found: {session_dir}")
            
            # Step 5: Check recordings API again
            print("\n5. Checking recordings API after upload...")
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8000/recordings") as response:
                    if response.status == 200:
                        data = await response.json()
                        recordings = data.get('recordings', [])
                        print(f"   Total recordings now: {len(recordings)}")
                        
                        session_found = any(r.get('session_id') == session_id for r in recordings)
                        if session_found:
                            print(f"   ✓ Our session {session_id} now appears in recordings")
                        else:
                            print(f"   ✗ Our session {session_id} still NOT in recordings")
            
            print("\n" + "=" * 60)
            print("Debug completed!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_session()) 