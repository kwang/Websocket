#!/usr/bin/env python3
"""
Test script to verify system status
"""

import requests
import json
import time

def test_server_status():
    """Test if the server is responding properly"""
    try:
        # Test recordings endpoint
        response = requests.get('http://localhost:8000/recordings', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is running and responding")
            print(f"📁 Found {len(data.get('recordings', []))} recording sessions")
            return True
        else:
            print(f"❌ Server responded with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Server connection failed: {e}")
        return False

def test_client_status():
    """Test if the client is responding properly"""
    try:
        response = requests.get('http://localhost:8080/', timeout=5)
        if response.status_code == 200:
            if 'AI Interview Agent' in response.text:
                print("✅ Client is running and serving the web interface")
                return True
            else:
                print("❌ Client is running but not serving the expected content")
                return False
        else:
            print(f"❌ Client responded with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Client connection failed: {e}")
        return False

def test_openai_integration():
    """Test if OpenAI integration is working"""
    try:
        response = requests.get('http://localhost:8000/interview-questions', timeout=5)
        if response.status_code == 200:
            print("✅ Interview questions endpoint is working")
            return True
        else:
            print(f"❌ Interview questions endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Interview questions endpoint failed: {e}")
        return False

def main():
    print("🔍 Testing AI Interview Agent System Status")
    print("=" * 50)
    
    # Test server
    print("\n1. Testing Server (port 8000)...")
    server_ok = test_server_status()
    
    # Test client
    print("\n2. Testing Client (port 8080)...")
    client_ok = test_client_status()
    
    # Test OpenAI integration
    print("\n3. Testing OpenAI Integration...")
    openai_ok = test_openai_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SYSTEM STATUS SUMMARY:")
    print(f"   Server: {'✅ RUNNING' if server_ok else '❌ FAILED'}")
    print(f"   Client: {'✅ RUNNING' if client_ok else '❌ FAILED'}")
    print(f"   OpenAI: {'✅ WORKING' if openai_ok else '❌ FAILED'}")
    
    if server_ok and client_ok:
        print("\n🎉 System is ready for use!")
        print("   🌐 Open http://localhost:8080 in your browser")
        print("   📝 The system supports:")
        print("      - Voice recording and transcription")
        print("      - AI-powered interview questions")
        print("      - OpenAI text-to-speech")
        print("      - Session recording and playback")
    else:
        print("\n⚠️  System has issues that need to be resolved")
        if not server_ok:
            print("   - Check if server.py is running on port 8000")
        if not client_ok:
            print("   - Check if client.py is running on port 8080")

if __name__ == "__main__":
    main() 