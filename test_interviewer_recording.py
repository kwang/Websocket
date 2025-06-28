#!/usr/bin/env python3
"""
Test script to verify interviewer speech recording functionality
"""

import requests
import time
import os
from datetime import datetime

def test_interviewer_recording():
    """Test that interviewer speech is saved when session_id is provided"""
    print("Testing Interviewer Speech Recording")
    print("=" * 50)
    
    # Test TTS with session_id
    test_text = "Hello! This is a test of the interviewer speech recording system."
    session_id = f"test_session_{int(time.time())}"
    
    try:
        print(f"Testing TTS with session_id: {session_id}")
        
        response = requests.post(
            "http://localhost:8000/tts",
            data={
                "text": test_text,
                "voice": "nova",
                "session_id": session_id
            },
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ TTS request successful")
            
            # Check if files were created
            session_dir = f"recordings/{session_id}"
            if os.path.exists(session_dir):
                files = os.listdir(session_dir)
                interviewer_files = [f for f in files if f.startswith('interviewer_') and f.endswith('.mp3')]
                metadata_files = [f for f in files if f.startswith('interviewer_metadata_') and f.endswith('.json')]
                
                print(f"✅ Session directory created: {session_dir}")
                print(f"✅ Interviewer audio files: {len(interviewer_files)}")
                print(f"✅ Interviewer metadata files: {len(metadata_files)}")
                
                if interviewer_files:
                    print(f"   Audio file: {interviewer_files[0]}")
                if metadata_files:
                    print(f"   Metadata file: {metadata_files[0]}")
                
                # Test session details endpoint
                print("\nTesting session details endpoint...")
                details_response = requests.get(f"http://localhost:8000/recordings/{session_id}")
                
                if details_response.status_code == 200:
                    details = details_response.json()
                    print(f"✅ Session details retrieved")
                    print(f"   Interviewer files: {details.get('interviewer_files', [])}")
                    print(f"   Candidate files: {details.get('candidate_files', [])}")
                    print(f"   Total files: {details.get('total_files', 0)}")
                else:
                    print(f"❌ Session details request failed: {details_response.status_code}")
                
                return True
            else:
                print(f"❌ Session directory not created: {session_dir}")
                return False
                
        else:
            print(f"❌ TTS request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_interviewer_recording_without_session():
    """Test that TTS still works without session_id (backward compatibility)"""
    print("\nTesting TTS without session_id (backward compatibility)")
    print("=" * 50)
    
    test_text = "This is a test without session_id for backward compatibility."
    
    try:
        response = requests.post(
            "http://localhost:8000/tts",
            data={"text": test_text, "voice": "echo"},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ TTS without session_id works correctly")
            return True
        else:
            print(f"❌ TTS without session_id failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success1 = test_interviewer_recording()
    success2 = test_interviewer_recording_without_session()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Interviewer speech recording is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.") 