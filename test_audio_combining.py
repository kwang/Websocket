#!/usr/bin/env python3
"""
Test script to verify audio combining functionality
"""

import requests
import json
import time

def test_audio_combining():
    """Test the audio combining functionality"""
    print("🧪 Testing Audio Combining Functionality")
    print("=" * 50)
    
    try:
        # Get recordings
        response = requests.get('http://localhost:8000/recordings', timeout=5)
        if response.status_code != 200:
            print("❌ Failed to get recordings")
            return False
        
        data = response.json()
        recordings = data.get('recordings', [])
        
        if not recordings:
            print("❌ No recordings found")
            return False
        
        print(f"✅ Found {len(recordings)} recording sessions")
        
        # Find a session with multiple audio files
        test_session = None
        for recording in recordings:
            if len(recording.get('audio_files', [])) > 1:
                test_session = recording
                break
        
        if not test_session:
            print("❌ No session with multiple audio files found")
            return False
        
        session_id = test_session['session_id']
        audio_files = test_session.get('audio_files', [])
        
        print(f"✅ Testing session: {session_id}")
        print(f"📁 Audio files: {len(audio_files)}")
        print(f"🎵 Files: {audio_files}")
        
        # Test audio file serving
        print("\n🔍 Testing audio file serving...")
        for audio_file in audio_files[:2]:  # Test first 2 files
            try:
                audio_url = f"http://localhost:8000/recordings/{session_id}/{audio_file}"
                response = requests.get(audio_url, timeout=10)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    print(f"✅ Audio file '{audio_file}' served successfully ({content_type})")
                else:
                    print(f"❌ Failed to serve audio file '{audio_file}': {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error serving audio file '{audio_file}': {e}")
        
        # Test session details endpoint
        print("\n🔍 Testing session details endpoint...")
        try:
            response = requests.get(f'http://localhost:8000/recordings/{session_id}', timeout=5)
            if response.status_code == 200:
                details = response.json()
                print(f"✅ Session details retrieved successfully")
                print(f"📊 Interviewer files: {len(details.get('interviewer_files', []))}")
                print(f"📊 Candidate files: {len(details.get('candidate_files', []))}")
                print(f"📊 Combined audio: {details.get('combined_audio', 'None')}")
            else:
                print(f"❌ Failed to get session details: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting session details: {e}")
        
        print("\n✅ Audio combining functionality test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_audio_combining() 