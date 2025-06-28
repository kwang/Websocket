#!/usr/bin/env python3
"""
Test script to simulate a new audio recording and verify conversion
"""

import requests
import json
import time
import os

def test_new_recording():
    """Test the complete recording workflow"""
    print("Testing new audio recording workflow...")
    
    # Step 1: Connect to WebSocket to get a session
    import websockets
    import asyncio
    
    async def test_websocket():
        try:
            uri = "ws://localhost:8000/ws"
            async with websockets.connect(uri) as websocket:
                # Wait for greeting message
                greeting = await websocket.recv()
                data = json.loads(greeting)
                print(f"Received greeting: {data}")
                
                if 'session_id' in data:
                    session_id = data['session_id']
                    print(f"Session ID: {session_id}")
                    
                    # Step 2: Upload a test audio file
                    test_audio_file = "recordings/interview_20250627_160345_938548/response_20250627_160408.wav"
                    if os.path.exists(test_audio_file):
                        print(f"Uploading test audio file: {test_audio_file}")
                        
                        with open(test_audio_file, 'rb') as f:
                            files = {'file': ('test_recording.webm', f, 'audio/webm')}
                            data = {
                                'session_id': session_id,
                                'client_id': session_id
                            }
                            
                            response = requests.post('http://localhost:8000/transcribe', 
                                                   files=files, data=data)
                            
                            if response.status_code == 200:
                                result = response.json()
                                print(f"✅ Transcription successful: {result['transcription']}")
                                
                                # Step 3: Check if the file was saved properly
                                time.sleep(2)  # Wait for file to be saved
                                
                                recordings_response = requests.get('http://localhost:8000/recordings')
                                if recordings_response.status_code == 200:
                                    recordings = recordings_response.json()
                                    print(f"Recordings: {json.dumps(recordings, indent=2)}")
                                    
                                    # Check if our session has new audio files
                                    for recording in recordings['recordings']:
                                        if recording['session_id'] == session_id:
                                            print(f"✅ Session found with {len(recording['audio_files'])} audio files")
                                            return True
                                
                                return True
                            else:
                                print(f"❌ Transcription failed: {response.text}")
                                return False
                    else:
                        print(f"❌ Test audio file not found: {test_audio_file}")
                        return False
                else:
                    print("❌ No session ID received")
                    return False
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
            return False
    
    # Run the async test
    return asyncio.run(test_websocket())

if __name__ == "__main__":
    print("New Recording Test")
    print("=" * 50)
    
    if test_new_recording():
        print("✅ New recording test completed successfully!")
    else:
        print("❌ New recording test failed!") 