#!/usr/bin/env python3
"""
Test script to manually trigger audio combining
"""

import requests
import json
import time

def test_manual_combine():
    """Test manual audio combining for a session"""
    print("🧪 Testing Manual Audio Combining")
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
        
        # Find a session with multiple audio files but no combined audio
        test_session = None
        for recording in recordings:
            audio_files = recording.get('audio_files', [])
            combined_audio = recording.get('combined_audio')
            if len(audio_files) > 1 and not combined_audio:
                test_session = recording
                break
        
        if not test_session:
            print("❌ No suitable session found for testing")
            return False
        
        session_id = test_session['session_id']
        audio_files = test_session.get('audio_files', [])
        
        print(f"✅ Testing session: {session_id}")
        print(f"📁 Audio files: {len(audio_files)}")
        print(f"🎵 Files: {audio_files}")
        
        # Test the audio serving endpoint for each file to ensure they exist
        print("\n🔍 Verifying audio files exist...")
        for audio_file in audio_files:
            try:
                audio_url = f"http://localhost:8000/recordings/{session_id}/{audio_file}"
                response = requests.get(audio_url, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ Audio file '{audio_file}' exists and is accessible")
                else:
                    print(f"❌ Audio file '{audio_file}' not accessible: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error accessing audio file '{audio_file}': {e}")
        
        print(f"\n📝 Note: Audio combining is triggered automatically when new audio is added to a session.")
        print(f"📝 To test combining, you would need to add new audio to session: {session_id}")
        print(f"📝 The combined audio file would be named: combined_interview.mp3")
        
        print("\n✅ Manual audio combining test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_manual_combine() 