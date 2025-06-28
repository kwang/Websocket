#!/usr/bin/env python3
"""
Test script to verify audio conversion functionality
"""

import subprocess
import tempfile
import os
from pathlib import Path

def test_ffmpeg_conversion():
    """Test if ffmpeg can convert WebM to WAV"""
    print("Testing ffmpeg conversion...")
    
    # Check if ffmpeg is available
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ ffmpeg not found or not working")
            return False
        print("✅ ffmpeg is available")
    except Exception as e:
        print(f"❌ Error checking ffmpeg: {e}")
        return False
    
    # Create a test WebM file (or use existing one)
    test_webm = "recordings/interview_20250627_160345_938548/response_20250627_160408.wav"
    if os.path.exists(test_webm):
        print(f"Using existing file: {test_webm}")
        
        # Create output WAV file
        output_wav = "test_output.wav"
        
        # Convert WebM to WAV
        cmd = [
            'ffmpeg', '-i', test_webm,
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            '-ac', '1',
            '-y',  # Overwrite output file
            output_wav
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Conversion successful!")
            print(f"Output file: {output_wav}")
            
            # Check the output file
            if os.path.exists(output_wav):
                file_info = subprocess.run(['file', output_wav], capture_output=True, text=True)
                print(f"File type: {file_info.stdout.strip()}")
                
                # Check file size
                size = os.path.getsize(output_wav)
                print(f"File size: {size} bytes ({size/1024:.1f} KB)")
                
                return True
            else:
                print("❌ Output file not created")
                return False
        else:
            print(f"❌ Conversion failed: {result.stderr}")
            return False
    else:
        print(f"❌ Test file not found: {test_webm}")
        return False

def test_whisper_with_converted_audio():
    """Test if Whisper can transcribe the converted audio"""
    print("\nTesting Whisper with converted audio...")
    
    wav_file = "test_output.wav"
    if not os.path.exists(wav_file):
        print(f"❌ Converted audio file not found: {wav_file}")
        return False
    
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(wav_file)
        print(f"✅ Transcription successful: '{result['text']}'")
        return True
    except Exception as e:
        print(f"❌ Whisper transcription failed: {e}")
        return False

if __name__ == "__main__":
    print("Audio Conversion Test")
    print("=" * 50)
    
    if test_ffmpeg_conversion():
        test_whisper_with_converted_audio()
    else:
        print("❌ Audio conversion test failed") 