#!/usr/bin/env python3
"""
Interview Recordings Manager

This script helps manage and download interview recordings from the AI Interview Agent.
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
import argparse

RECORDINGS_DIR = Path("recordings")

def list_recordings():
    """List all available interview recordings"""
    if not RECORDINGS_DIR.exists():
        print("No recordings directory found.")
        return
    
    print("Available Interview Recordings:")
    print("=" * 50)
    
    for session_dir in RECORDINGS_DIR.iterdir():
        if session_dir.is_dir():
            audio_files = list(session_dir.glob("*.wav"))
            metadata_files = list(session_dir.glob("*.json"))
            
            print(f"\nSession: {session_dir.name}")
            print(f"  Audio Files: {len(audio_files)}")
            print(f"  Metadata Files: {len(metadata_files)}")
            
            if metadata_files:
                # Read the first metadata file to get session info
                try:
                    with open(metadata_files[0], 'r') as f:
                        metadata = json.load(f)
                        print(f"  Start Time: {metadata.get('timestamp', 'Unknown')}")
                        print(f"  Client ID: {metadata.get('client_id', 'Unknown')}")
                except:
                    pass

def show_session_details(session_id):
    """Show detailed information about a specific session"""
    session_dir = RECORDINGS_DIR / session_id
    if not session_dir.exists():
        print(f"Session {session_id} not found.")
        return
    
    print(f"\nSession Details: {session_id}")
    print("=" * 50)
    
    audio_files = list(session_dir.glob("*.wav"))
    metadata_files = list(session_dir.glob("*.json"))
    
    print(f"Audio Files ({len(audio_files)}):")
    for audio_file in sorted(audio_files):
        size_kb = audio_file.stat().st_size / 1024
        created = datetime.fromtimestamp(audio_file.stat().st_ctime)
        print(f"  • {audio_file.name} ({size_kb:.1f}KB) - {created}")
    
    print(f"\nMetadata Files ({len(metadata_files)}):")
    for meta_file in sorted(metadata_files):
        try:
            with open(meta_file, 'r') as f:
                metadata = json.load(f)
                print(f"  • {meta_file.name}")
                print(f"    - Question: {metadata.get('interview_question', 'Unknown')}")
                print(f"    - Response #: {metadata.get('response_number', 'Unknown')}")
                print(f"    - Timestamp: {metadata.get('timestamp', 'Unknown')}")
        except Exception as e:
            print(f"  • {meta_file.name} (Error reading: {e})")

def download_session(session_id, output_dir=None):
    """Download a session's recordings to a specified directory"""
    session_dir = RECORDINGS_DIR / session_id
    if not session_dir.exists():
        print(f"Session {session_id} not found.")
        return
    
    if output_dir is None:
        output_dir = Path(f"downloads/{session_id}")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading session {session_id} to {output_dir}")
    
    # Copy all files
    for file_path in session_dir.iterdir():
        if file_path.is_file():
            shutil.copy2(file_path, output_dir / file_path.name)
            print(f"  Copied: {file_path.name}")
    
    print(f"Download complete! Files saved to: {output_dir}")

def create_session_archive(session_id, output_file=None):
    """Create a ZIP archive of a session's recordings"""
    session_dir = RECORDINGS_DIR / session_id
    if not session_dir.exists():
        print(f"Session {session_id} not found.")
        return
    
    if output_file is None:
        output_file = f"{session_id}_recordings.zip"
    
    print(f"Creating archive for session {session_id}")
    
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in session_dir.iterdir():
            if file_path.is_file():
                zipf.write(file_path, file_path.name)
                print(f"  Added: {file_path.name}")
    
    print(f"Archive created: {output_file}")

def cleanup_old_recordings(days_old=30):
    """Clean up recordings older than specified days"""
    cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
    
    if not RECORDINGS_DIR.exists():
        print("No recordings directory found.")
        return
    
    print(f"Cleaning up recordings older than {days_old} days...")
    
    removed_count = 0
    for session_dir in RECORDINGS_DIR.iterdir():
        if session_dir.is_dir():
            # Check if any file in the session is older than cutoff
            session_old = False
            for file_path in session_dir.iterdir():
                if file_path.stat().st_ctime < cutoff_date:
                    session_old = True
                    break
            
            if session_old:
                shutil.rmtree(session_dir)
                print(f"  Removed: {session_dir.name}")
                removed_count += 1
    
    print(f"Cleanup complete. Removed {removed_count} old sessions.")

def main():
    parser = argparse.ArgumentParser(description="Manage AI Interview Recordings")
    parser.add_argument("action", choices=["list", "show", "download", "archive", "cleanup"],
                       help="Action to perform")
    parser.add_argument("--session", "-s", help="Session ID for show/download/archive actions")
    parser.add_argument("--output", "-o", help="Output directory or file")
    parser.add_argument("--days", "-d", type=int, default=30, help="Days old for cleanup (default: 30)")
    
    args = parser.parse_args()
    
    if args.action == "list":
        list_recordings()
    elif args.action == "show":
        if not args.session:
            print("Please provide a session ID with --session")
            return
        show_session_details(args.session)
    elif args.action == "download":
        if not args.session:
            print("Please provide a session ID with --session")
            return
        download_session(args.session, args.output)
    elif args.action == "archive":
        if not args.session:
            print("Please provide a session ID with --session")
            return
        create_session_archive(args.session, args.output)
    elif args.action == "cleanup":
        cleanup_old_recordings(args.days)

if __name__ == "__main__":
    main() 