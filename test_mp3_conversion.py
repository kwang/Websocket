#!/usr/bin/env python3
"""
Test script for MP3 conversion and audio combining functionality
"""

import requests
import json
import time
import os
from pathlib import Path

def test_mp3_conversion_and_combining():
    """Test MP3 conversion and audio combining functionality"""
    
    print("🧪 Testing MP3 Conversion and Audio Combining")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get("http://localhost:8000/recordings")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding properly")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the server first.")
        return
    
    # Test 2: Create a test session and record audio
    print("\n📝 Creating test session...")
    
    # Connect to WebSocket to get session ID
    import websocket
    import threading
    
    session_id = None
    
    def on_message(ws, message):
        global session_id
        data = json.loads(message)
        if data.get("type") in ["greeting", "follow_up"] and data.get("session_id"):
            session_id = data["session_id"]
            print(f"✅ Got session ID: {session_id}")
            ws.close()
    
    def on_error(ws, error):
        print(f"❌ WebSocket error: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print("🔌 WebSocket connection closed")
    
    def on_open(ws):
        print("🔗 WebSocket connected")
    
    # Connect to WebSocket
    ws = websocket.WebSocketApp("ws://localhost:8000/ws",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    
    # Wait for session ID
    timeout = 10
    start_time = time.time()
    while session_id is None and time.time() - start_time < timeout:
        time.sleep(0.1)
    
    if session_id is None:
        print("❌ Failed to get session ID")
        return
    
    # Test 3: Test TTS to create interviewer speech
    print(f"\n🎤 Testing TTS for session: {session_id}")
    
    tts_data = {
        "text": "Hello! This is a test of the MP3 conversion and combining functionality.",
        "voice": "alloy",
        "session_id": session_id
    }
    
    try:
        tts_response = requests.post("http://localhost:8000/tts", data=tts_data)
        if tts_response.status_code == 200:
            print("✅ TTS request successful")
            
            # Check if interviewer speech was saved
            session_response = requests.get(f"http://localhost:8000/recordings/{session_id}")
            if session_response.status_code == 200:
                session_data = session_response.json()
                if session_data.get("interviewer_files"):
                    print(f"✅ Interviewer speech saved: {len(session_data['interviewer_files'])} files")
                else:
                    print("❌ Interviewer speech not saved")
            else:
                print("❌ Failed to get session data")
        else:
            print(f"❌ TTS request failed: {tts_response.status_code}")
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
    
    # Test 4: Check for combined audio file
    print(f"\n🎵 Checking for combined audio file...")
    
    try:
        session_response = requests.get(f"http://localhost:8000/recordings/{session_id}")
        if session_response.status_code == 200:
            session_data = session_response.json()
            
            if session_data.get("combined_audio"):
                print(f"✅ Combined audio file created: {session_data['combined_audio']}")
            else:
                print("⚠️  Combined audio file not found (may be created after candidate response)")
            
            print(f"\n📊 Session Summary:")
            print(f"   - Interviewer files: {len(session_data.get('interviewer_files', []))}")
            print(f"   - Candidate files: {len(session_data.get('candidate_files', []))}")
            print(f"   - Combined audio: {session_data.get('combined_audio', 'None')}")
            print(f"   - Total files: {len(session_data.get('audio_files', []))}")
            
        else:
            print("❌ Failed to get session data")
    except Exception as e:
        print(f"❌ Session check failed: {e}")
    
    # Test 5: Check recordings directory structure
    print(f"\n📁 Checking recordings directory...")
    
    recordings_dir = Path("recordings")
    if recordings_dir.exists():
        session_dir = recordings_dir / session_id
        if session_dir.exists():
            print(f"✅ Session directory created: {session_dir}")
            
            # List all files in session directory
            files = list(session_dir.iterdir())
            print(f"   Files in session directory:")
            for file in files:
                file_type = "📄"
                if file.suffix == ".mp3":
                    if file.name.startswith("interviewer_"):
                        file_type = "🎤"
                    elif file.name == "combined_interview.mp3":
                        file_type = "🎵"
                    else:
                        file_type = "🎙️"
                elif file.suffix == ".json":
                    file_type = "📄"
                
                print(f"   {file_type} {file.name}")
        else:
            print(f"❌ Session directory not found: {session_dir}")
    else:
        print("❌ Recordings directory not found")
    
    print("\n" + "=" * 50)
    print("🎉 MP3 Conversion and Audio Combining Test Complete!")
    print("\nNext steps:")
    print("1. Open the client in your browser")
    print("2. Record a candidate response")
    print("3. Check that both candidate and interviewer audio are saved as MP3")
    print("4. Verify that a combined_interview.mp3 file is created")

if __name__ == "__main__":
    test_mp3_conversion_and_combining() 