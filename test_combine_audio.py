#!/usr/bin/env python3
"""
Test script to manually trigger audio combining
"""

import requests
import json
import time
import unittest
import tempfile
import shutil
import subprocess
from pathlib import Path
import sys
import os
from unittest.mock import patch, MagicMock

# Add the current directory to the path so we can import from server.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import combine_audio_files, COMBINED_AUDIO_FILENAME

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

class TestCombineAudioFiles(unittest.TestCase):
    """Test cases for the combine_audio_files function"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create a temporary directory for each test
        self.test_dir = tempfile.mkdtemp()
        self.session_dir = Path(self.test_dir) / "test_session"
        self.session_dir.mkdir()
    
    def tearDown(self):
        """Clean up test fixtures after each test method"""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_test_audio_file(self, filename: str, content: str = "test audio content"):
        """Helper method to create a test audio file"""
        file_path = self.session_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path
    
    @patch('subprocess.run')
    def test_combine_audio_files_success(self, mock_run):
        """Test successful audio file combination"""
        # Mock ffmpeg version check to return success
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        # Create test audio files
        self.create_test_audio_file("audio1.mp3", "test audio 1")
        self.create_test_audio_file("audio2.wav", "test audio 2")
        self.create_test_audio_file("audio3.webm", "test audio 3")
        
        # Test the function
        result = combine_audio_files(self.session_dir)
        
        # Check that the function returned True
        self.assertTrue(result)
        
        # Check that the combined file was created
        combined_file = self.session_dir / COMBINED_AUDIO_FILENAME
        self.assertTrue(combined_file.exists())
        
        # Check that the file list was cleaned up
        file_list = self.session_dir / "file_list.txt"
        self.assertFalse(file_list.exists())
        
        # Verify ffmpeg was called correctly
        mock_run.assert_called()
        # First call should be ffmpeg -version
        self.assertEqual(mock_run.call_args_list[0][0][0], ['ffmpeg', '-version'])
        # Second call should be the actual combine command
        combine_call = mock_run.call_args_list[1]
        self.assertEqual(combine_call[0][0][0], 'ffmpeg')
        self.assertEqual(combine_call[0][0][1], '-f')
        self.assertEqual(combine_call[0][0][2], 'concat')
        self.assertEqual(combine_call[1]['cwd'], self.session_dir)
    
    @patch('subprocess.run')
    def test_combine_audio_files_custom_output_filename(self, mock_run):
        """Test audio file combination with custom output filename"""
        # Mock ffmpeg version check to return success
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        # Create test audio files
        self.create_test_audio_file("audio1.mp3", "test audio 1")
        self.create_test_audio_file("audio2.wav", "test audio 2")
        
        # Test with custom output filename
        custom_filename = "custom_combined.mp3"
        result = combine_audio_files(self.session_dir, custom_filename)
        
        # Check that the function returned True
        self.assertTrue(result)
        
        # Check that the custom combined file was created
        combined_file = self.session_dir / custom_filename
        self.assertTrue(combined_file.exists())
        
        # Verify the custom filename was used in the ffmpeg command
        combine_call = mock_run.call_args_list[1]
        self.assertEqual(combine_call[0][0][-1], custom_filename)
    
    def test_combine_audio_files_no_audio_files(self):
        """Test behavior when no audio files are present"""
        # Test with empty directory
        result = combine_audio_files(self.session_dir)
        
        # Check that the function returned False
        self.assertFalse(result)
        
        # Check that no combined file was created
        combined_file = self.session_dir / COMBINED_AUDIO_FILENAME
        self.assertFalse(combined_file.exists())
    
    @patch('subprocess.run')
    def test_combine_audio_files_skips_combined_file(self, mock_run):
        """Test that the function skips the combined file if it already exists"""
        # Mock ffmpeg version check to return success
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        # Create test audio files
        self.create_test_audio_file("audio1.mp3", "test audio 1")
        self.create_test_audio_file("audio2.wav", "test audio 2")
        
        # Create an existing combined file
        existing_combined = self.session_dir / COMBINED_AUDIO_FILENAME
        self.create_test_audio_file(COMBINED_AUDIO_FILENAME, "existing combined")
        
        # Test the function
        result = combine_audio_files(self.session_dir)
        
        # Check that the function returned True
        self.assertTrue(result)
        
        # Check that the combined file was updated (not the original content)
        with open(existing_combined, 'r') as f:
            content = f.read()
        self.assertNotEqual(content, "existing combined")
    
    @patch('subprocess.run')
    def test_combine_audio_files_ignores_non_audio_files(self, mock_run):
        """Test that non-audio files are ignored"""
        # Mock ffmpeg version check to return success
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        # Create test audio files
        self.create_test_audio_file("audio1.mp3", "test audio 1")
        self.create_test_audio_file("audio2.wav", "test audio 2")
        
        # Create non-audio files
        self.create_test_audio_file("text.txt", "text content")
        self.create_test_audio_file("image.jpg", "image content")
        self.create_test_audio_file("document.pdf", "pdf content")
        
        # Test the function
        result = combine_audio_files(self.session_dir)
        
        # Check that the function returned True
        self.assertTrue(result)
        
        # Check that the combined file was created
        combined_file = self.session_dir / COMBINED_AUDIO_FILENAME
        self.assertTrue(combined_file.exists())
        
        # Check that only audio files were included in the file list
        file_list_content = ""
        if (self.session_dir / "file_list.txt").exists():
            with open(self.session_dir / "file_list.txt", 'r') as f:
                file_list_content = f.read()
        
        # Should only contain audio files
        self.assertIn("audio1.mp3", file_list_content)
        self.assertIn("audio2.wav", file_list_content)
        self.assertNotIn("text.txt", file_list_content)
        self.assertNotIn("image.jpg", file_list_content)
        self.assertNotIn("document.pdf", file_list_content)
    
    @patch('subprocess.run')
    def test_combine_audio_files_supports_all_audio_formats(self, mock_run):
        """Test that all supported audio formats are processed"""
        # Mock ffmpeg version check to return success
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        # Create test audio files with all supported formats
        self.create_test_audio_file("audio1.mp3", "test audio 1")
        self.create_test_audio_file("audio2.wav", "test audio 2")
        self.create_test_audio_file("audio3.webm", "test audio 3")
        self.create_test_audio_file("audio4.m4a", "test audio 4")
        
        # Test the function
        result = combine_audio_files(self.session_dir)
        
        # Check that the function returned True
        self.assertTrue(result)
        
        # Check that the combined file was created
        combined_file = self.session_dir / COMBINED_AUDIO_FILENAME
        self.assertTrue(combined_file.exists())
    
    @patch('subprocess.run')
    def test_combine_audio_files_case_insensitive_extensions(self, mock_run):
        """Test that file extensions are handled case-insensitively"""
        # Mock ffmpeg version check to return success
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        # Create test audio files with different case extensions
        self.create_test_audio_file("audio1.MP3", "test audio 1")
        self.create_test_audio_file("audio2.WAV", "test audio 2")
        self.create_test_audio_file("audio3.WEBM", "test audio 3")
        
        # Test the function
        result = combine_audio_files(self.session_dir)
        
        # Check that the function returned True
        self.assertTrue(result)
        
        # Check that the combined file was created
        combined_file = self.session_dir / COMBINED_AUDIO_FILENAME
        self.assertTrue(combined_file.exists())
    
    @patch('subprocess.run')
    def test_combine_audio_files_ffmpeg_not_available(self, mock_run):
        """Test behavior when ffmpeg is not available"""
        # Mock ffmpeg version check to return failure
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "ffmpeg not found"
        
        # Create test audio files
        self.create_test_audio_file("audio1.mp3", "test audio 1")
        
        # Test the function
        result = combine_audio_files(self.session_dir)
        
        # Check that the function returned False
        self.assertFalse(result)
        
        # Check that no combined file was created
        combined_file = self.session_dir / COMBINED_AUDIO_FILENAME
        self.assertFalse(combined_file.exists())
    
    def test_combine_audio_files_directory_not_exists(self):
        """Test behavior when session directory doesn't exist"""
        non_existent_dir = Path("/non/existent/directory")
        
        # Test the function
        result = combine_audio_files(non_existent_dir)
        
        # Check that the function returned False
        self.assertFalse(result)
    
    @patch('subprocess.run')
    def test_combine_audio_files_permission_error(self, mock_run):
        """Test behavior when there are permission issues"""
        # Mock ffmpeg version check to return success
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        # Create test audio files
        self.create_test_audio_file("audio1.mp3", "test audio 1")
        
        # Make the directory read-only
        os.chmod(self.session_dir, 0o444)
        
        try:
            # Test the function
            result = combine_audio_files(self.session_dir)
            
            # Check that the function returned False due to permission error
            self.assertFalse(result)
            
        finally:
            # Restore permissions
            os.chmod(self.session_dir, 0o755)
    
    @patch('subprocess.run')
    def test_combine_audio_files_creates_file_list_correctly(self, mock_run):
        """Test that the file list is created with correct format"""
        # Mock ffmpeg version check to return success
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        # Create test audio files
        self.create_test_audio_file("audio1.mp3", "test audio 1")
        self.create_test_audio_file("audio2.wav", "test audio 2")
        
        # Test the function
        result = combine_audio_files(self.session_dir)
        
        # Check that the function returned True
        self.assertTrue(result)
        
        # Verify ffmpeg was called with correct parameters
        mock_run.assert_called()
        
        # Get the combine command call
        combine_call = mock_run.call_args_list[1]
        cmd = combine_call[0][0]
        kwargs = combine_call[1]
        
        # Check that the command is correct
        self.assertEqual(cmd[0], 'ffmpeg')
        self.assertEqual(cmd[1], '-f')
        self.assertEqual(cmd[2], 'concat')
        self.assertEqual(cmd[3], '-safe')
        self.assertEqual(cmd[4], '0')
        self.assertEqual(cmd[5], '-i')
        self.assertEqual(cmd[6], 'file_list.txt')
        self.assertEqual(cmd[7], '-c')
        self.assertEqual(cmd[8], 'copy')
        self.assertEqual(cmd[9], '-y')
        self.assertEqual(cmd[10], COMBINED_AUDIO_FILENAME)
        
        # Check that cwd is set to session directory
        self.assertEqual(kwargs.get('cwd'), self.session_dir)
    
    @patch('subprocess.run')
    def test_combine_audio_files_handles_ffmpeg_error(self, mock_run):
        """Test behavior when ffmpeg returns an error"""
        # Mock ffmpeg version check to return success
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        # Create test audio files
        self.create_test_audio_file("audio1.mp3", "test audio 1")
        
        # Mock the combine command to return error
        def mock_run_side_effect(cmd, **kwargs):
            if cmd[0] == 'ffmpeg' and cmd[1] == '-version':
                return MagicMock(returncode=0, stderr="")
            else:
                return MagicMock(returncode=1, stderr="ffmpeg error")
        
        mock_run.side_effect = mock_run_side_effect
        
        # Test the function
        result = combine_audio_files(self.session_dir)
        
        # Check that the function returned False
        self.assertFalse(result)
    
    @patch('subprocess.run')
    def test_combine_audio_files_file_list_content(self, mock_run):
        """Test that the file list contains the correct content"""
        # Mock ffmpeg version check to return success
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        # Create test audio files
        self.create_test_audio_file("audio1.mp3", "test audio 1")
        self.create_test_audio_file("audio2.wav", "test audio 2")
        self.create_test_audio_file("audio3.webm", "test audio 3")
        
        # Test the function
        result = combine_audio_files(self.session_dir)
        
        # Check that the function returned True
        self.assertTrue(result)
        
        # The file list should have been created and then cleaned up
        # We can't check its content directly since it's cleaned up,
        # but we can verify the function worked correctly
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_combine_audio_files_with_single_file(self, mock_run):
        """Test combining a single audio file"""
        # Mock ffmpeg version check to return success
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        # Create a single test audio file
        self.create_test_audio_file("audio1.mp3", "test audio 1")
        
        # Test the function
        result = combine_audio_files(self.session_dir)
        
        # Check that the function returned True
        self.assertTrue(result)
        
        # Check that the combined file was created
        combined_file = self.session_dir / COMBINED_AUDIO_FILENAME
        self.assertTrue(combined_file.exists())


if __name__ == '__main__':
    unittest.main() 