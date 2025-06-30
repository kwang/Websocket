#!/usr/bin/env python3
"""
Java Web Client for Interview System

This client has exactly the same UI as the original client.py but connects to the Java gRPC server.
"""

import http.server
import socketserver
import grpc
import json
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any

# Import gRPC modules for Java server
try:
    import interview_pb2
    import interview_pb2_grpc
except ImportError:
    print("Warning: gRPC modules not found. Please generate them from your .proto files.")
    interview_pb2 = None
    interview_pb2_grpc = None


class JavaInterviewClient:
    """Client for connecting to the Java gRPC server"""
    
    def __init__(self, host: str = "localhost", port: int = 9090):
        self.host = host
        self.port = port
        self.channel = None
        self.interview_stub = None
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to the Java gRPC server"""
        try:
            self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
            self.interview_stub = interview_pb2_grpc.InterviewServiceStub(self.channel)
            self.connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to Java server: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the Java server"""
        if self.channel:
            self.channel.close()
        self.connected = False
    
    def start_interview(self, client_id: str = None) -> Dict[str, Any]:
        """Start a new interview session"""
        if not self.connected:
            if not self.connect():
                return {"success": False, "error": "Failed to connect to Java server"}
        
        try:
            if not client_id:
                client_id = f"client_{int(time.time())}"
            
            request = interview_pb2.StartInterviewRequest(client_id=client_id)
            response = self.interview_stub.StartInterview(request)
            
            return {
                "success": True,
                "session_id": response.session_id,
                "greeting_message": response.greeting_message,
                "client_id": client_id
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def process_audio(self, session_id: str, audio_data: bytes, audio_format: str = "mp3", client_id: str = None) -> Dict[str, Any]:
        """Process audio for transcription"""
        if not self.connected:
            if not self.connect():
                return {"success": False, "error": "Failed to connect to Java server"}
        
        try:
            request = interview_pb2.ProcessAudioRequest(
                audio_data=audio_data,
                session_id=session_id,
                client_id=client_id or "unknown",
                audio_format=audio_format
            )
            
            response = self.interview_stub.ProcessAudio(request)
            
            return {
                "success": response.success,
                "transcription": response.transcription,
                "follow_up_question": response.follow_up_question,
                "error_message": response.error_message if not response.success else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_speech(self, text: str, session_id: str = None, voice: str = "alloy") -> Dict[str, Any]:
        """Generate text-to-speech"""
        if not self.connected:
            if not self.connect():
                return {"success": False, "error": "Failed to connect to Java server"}
        
        try:
            request = interview_pb2.GenerateSpeechRequest(
                text=text,
                voice=voice,
                session_id=session_id or ""
            )
            
            response = self.interview_stub.GenerateSpeech(request)
            
            return {
                "success": response.success,
                "audio_data": response.audio_data,
                "audio_file_path": response.audio_file_path,
                "error_message": response.error_message if not response.success else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def finish_interview(self, session_id: str) -> Dict[str, Any]:
        """Finish an interview session"""
        if not self.connected:
            if not self.connect():
                return {"success": False, "error": "Failed to connect to Java server"}
        
        try:
            request = interview_pb2.FinishInterviewRequest(session_id=session_id)
            response = self.interview_stub.FinishInterview(request)
            
            return {
                "success": response.success,
                "audio_combined": response.audio_combined,
                "video_combined": response.video_combined,
                "error_message": response.error_message if not response.success else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# HTML content for the web interface (exact copy from client.py)
HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Interview Agent</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .tabs {
            display: flex;
            border-bottom: 2px solid #ddd;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 16px;
            color: #666;
        }
        .tab.active {
            color: #007bff;
            border-bottom: 2px solid #007bff;
            margin-bottom: -2px;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            margin: 2px;
        }
        .btn-primary {
            background-color: #007bff;
            color: white;
        }
        .btn-success {
            background-color: #28a745;
            color: white;
        }
        .btn-secondary {
            background-color: #6c757d;
            color: white;
        }
        .btn-outline-primary {
            background-color: transparent;
            color: #007bff;
            border: 1px solid #007bff;
        }
        .btn-outline-primary:hover {
            background-color: #007bff;
            color: white;
        }
        .btn-outline-success {
            background-color: transparent;
            color: #28a745;
            border: 1px solid #28a745;
        }
        .btn-outline-success:hover {
            background-color: #28a745;
            color: white;
        }
        .btn-danger {
            background-color: #dc3545;
            color: white;
        }
        .btn-warning {
            background-color: #ffc107;
            color: #212529;
        }
        .btn-sm {
            padding: 4px 8px;
            font-size: 12px;
        }
        h5 {
            font-size: 18px;
            font-weight: bold;
            margin: 0 0 10px 0;
        }
        h6 {
            font-size: 16px;
            font-weight: bold;
            margin: 0 0 8px 0;
        }
        .recording-item {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            background: #f9f9f9;
        }
        .recording-header h3 {
            margin: 0 0 10px 0;
            color: #333;
        }
        .recording-header p {
            margin: 5px 0;
            color: #666;
        }
        .recording-actions {
            margin-top: 10px;
        }
        .audio-section {
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #f9f9f9;
        }
        .audio-section h3 {
            margin: 0 0 15px 0;
            color: #333;
        }
        .audio-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            margin: 5px 0;
            background: white;
            border-radius: 4px;
            border: 1px solid #eee;
        }
        .audio-item span {
            font-family: monospace;
            font-size: 12px;
            color: #666;
        }
        .metadata-section {
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #f9f9f9;
        }
        .metadata-section h3 {
            margin: 0 0 15px 0;
            color: #333;
        }
        .metadata-section p {
            margin: 5px 0;
            font-family: monospace;
            font-size: 12px;
            color: #666;
        }
        #conversation {
            height: 300px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            margin: 10px 0;
            background: #f9f9f9;
        }
        .message {
            margin: 5px 0;
            padding: 8px;
            border-radius: 4px;
        }
        .message.interviewer {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
        }
        .message.candidate {
            background: #f3e5f5;
            border-left: 4px solid #9c27b0;
        }
        #status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            background: #e8f5e8;
            color: #2e7d32;
        }
        .controls {
            margin: 10px 0;
        }
        .voice-controls {
            margin: 10px 0;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: #f9f9f9;
        }
        .video-container {
            margin: 20px 0;
            text-align: center;
        }
        #videoPreview {
            width: 100%;
            max-width: 640px;
            height: auto;
            border: 2px solid #ddd;
            border-radius: 8px;
            background: #000;
        }
        .video-controls {
            margin: 10px 0;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: #f9f9f9;
        }
        .recording-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #dc3545;
            margin-right: 8px;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        select, input {
            padding: 8px;
            margin: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        #sessionInfo {
            display: none;
            padding: 10px;
            margin: 10px 0;
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            color: #856404;
        }
        .annotation-controls {
            margin: 20px 0;
        }
        .annotation-section {
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #f9f9f9;
        }
        .annotation-section h3 {
            margin: 0 0 15px 0;
            color: #333;
        }
        .annotation-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
        }
        .annotation-options label {
            display: flex;
            align-items: center;
            padding: 8px;
            background: white;
            border-radius: 4px;
            border: 1px solid #eee;
            cursor: pointer;
        }
        .annotation-options input[type="checkbox"] {
            margin-right: 8px;
        }
        .custom-text-section {
            margin-top: 15px;
            padding: 15px;
            background: white;
            border-radius: 4px;
            border: 1px solid #ddd;
        }
        .custom-text-section label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .custom-text-section input {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        #annotationResults {
            min-height: 100px;
            padding: 15px;
            background: white;
            border-radius: 4px;
            border: 1px solid #ddd;
        }
        .annotation-result {
            margin: 10px 0;
            padding: 10px;
            background: #e8f5e8;
            border: 1px solid #4caf50;
            border-radius: 4px;
            color: #2e7d32;
        }
        .annotation-error {
            background: #ffebee;
            border: 1px solid #f44336;
            color: #c62828;
        }
        
        /* Modal styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        .modal.show {
            display: block;
        }
        .modal-dialog {
            position: relative;
            width: 90%;
            max-width: 800px;
            margin: 50px auto;
        }
        .modal-content {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .modal-header {
            background-color: #007bff;
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .modal-title {
            margin: 0;
            font-size: 18px;
            font-weight: bold;
        }
        .close {
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .close:hover {
            background-color: rgba(255,255,255,0.2);
            border-radius: 4px;
        }
        .modal-body {
            padding: 20px;
            max-height: 70vh;
            overflow-y: auto;
        }
        .modal-footer {
            padding: 15px 20px;
            background-color: #f8f9fa;
            border-top: 1px solid #dee2e6;
            text-align: right;
        }
        .row {
            display: flex;
            flex-wrap: wrap;
            margin: 0 -10px;
        }
        .col-md-6 {
            flex: 0 0 50%;
            max-width: 50%;
            padding: 0 10px;
        }
        .col-12 {
            flex: 0 0 100%;
            max-width: 100%;
            padding: 0 10px;
        }
        .card {
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
        }
        .card-header {
            padding: 12px 15px;
            font-weight: bold;
            font-size: 14px;
        }
        .card-body {
            padding: 15px;
        }
        .bg-primary {
            background-color: #007bff !important;
        }
        .bg-info {
            background-color: #17a2b8 !important;
        }
        .bg-success {
            background-color: #28a745 !important;
        }
        .bg-secondary {
            background-color: #6c757d !important;
        }
        .text-white {
            color: white !important;
        }
        .text-primary {
            color: #007bff !important;
        }
        .text-success {
            color: #28a745 !important;
        }
        .text-muted {
            color: #6c757d !important;
        }
        .mb-0 {
            margin-bottom: 0 !important;
        }
        .mb-2 {
            margin-bottom: 8px !important;
        }
        .mt-3 {
            margin-top: 15px !important;
        }
        .p-2 {
            padding: 8px !important;
        }
        .py-3 {
            padding-top: 15px !important;
            padding-bottom: 15px !important;
        }
        .border {
            border: 1px solid #dee2e6 !important;
        }
        .border-rounded {
            border-radius: 4px !important;
        }
        .d-flex {
            display: flex !important;
        }
        .justify-content-between {
            justify-content: space-between !important;
        }
        .align-items-center {
            align-items: center !important;
        }
        .flex-grow-1 {
            flex-grow: 1 !important;
        }
        .text-center {
            text-align: center !important;
        }
        .alert {
            padding: 12px 15px;
            border-radius: 4px;
            margin-bottom: 15px;
        }
        .alert-danger {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .spinner-border {
            display: inline-block;
            width: 2rem;
            height: 2rem;
            border: 0.25em solid currentColor;
            border-right-color: transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }
        h5 {
            font-size: 18px;
            font-weight: bold;
            margin: 0 0 10px 0;
        }
        h6 {
            font-size: 16px;
            font-weight: bold;
            margin: 0 0 8px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Interview Agent</h1>
        <div class="tabs">
            <div class="tab active" onclick="showTab('interview')">Interview</div>
            <div class="tab" onclick="showTab('recordings')">Recordings</div>
            <div class="tab" onclick="showTab('annotations')">Video Annotations</div>
        </div>
        
        <div id="interview-tab" class="tab-content active">
            <div class="session-info" id="sessionInfo" style="display: none;">
                <strong>Session ID:</strong> <span id="sessionId"></span>
            </div>
            <div class="status" id="status">Connected to Java server. Click "Start Interview & Recording" to begin the interview.</div>
            
            <!-- Video Preview Section -->
            <div class="video-container">
                <video id="videoPreview" autoplay muted playsinline></video>
                <div class="video-controls">
                    <label>
                        <input type="checkbox" id="enableVideo" checked> Enable Video Recording
                    </label>
                    <label>
                        <input type="checkbox" id="enableAudio" checked> Enable Audio Recording
                    </label>
                    <label>
                        <input type="checkbox" id="enableDesktopAudio" checked> Enable Desktop Audio Capture
                    </label>
                </div>
            </div>
            
            <div class="conversation" id="conversation"></div>
            <div class="controls">
                <button id="toggleAutoRecording" class="btn btn-success" onclick="toggleAutoRecording()">Disable Auto-Recording</button>
                <button id="startRecording" class="btn btn-primary">
                    <span class="recording-indicator" style="display: none;"></span>
                    Start Recording (Manual)
                </button>
                <button id="stopRecording" class="btn btn-danger" disabled>Restart Recording</button>
                <button id="testSpeech" onclick="testSpeech()" class="btn btn-secondary">Test Speech</button>
                <button id="finishInterview" class="btn btn-success" onclick="finishInterview()">Finish</button>
            </div>
            <div class="control-group">
                <label for="voiceSelect">AI Voice:</label>
                <select id="voiceSelect" onchange="changeVoice()">
                    <option value="alloy">Alloy (Neutral)</option>
                    <option value="echo">Echo (Male)</option>
                    <option value="fable">Fable (Male)</option>
                    <option value="onyx">Onyx (Male)</option>
                    <option value="nova">Nova (Female)</option>
                    <option value="shimmer">Shimmer (Female)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="voiceSelect">Voice:</label>
                <select id="voiceSelect" class="form-control" onchange="changeVoice()">
                    <option value="alloy">Alloy</option>
                    <option value="echo">Echo</option>
                    <option value="fable">Fable</option>
                    <option value="onyx">Onyx</option>
                    <option value="nova">Nova</option>
                    <option value="shimmer">Shimmer</option>
                </select>
            </div>
            
            <button class="btn btn-info" onclick="testSpeech()">Test Speech</button>
            <button class="btn btn-warning" onclick="playTestTone()">Test Tone</button>
        </div>
        
        <div id="recordings-tab" class="tab-content">
            <h2>Interview Recordings</h2>
            <button onclick="loadRecordings()">Refresh Recordings</button>
            <div class="recordings-list" id="recordingsList"></div>
            <div id="sessionDetails" style="display:none;"></div>
        </div>
        
        <div id="annotations-tab" class="tab-content">
            <h2>Video Annotations</h2>
            <div class="annotation-controls">
                <div class="annotation-section">
                    <h3>Select Video to Annotate</h3>
                    <select id="annotationSessionSelect" onchange="loadSessionVideos()">
                        <option value="">Select a session...</option>
                    </select>
                    <select id="annotationVideoSelect" onchange="loadVideoDetails()">
                        <option value="">Select a video...</option>
                    </select>
                </div>
                
                <div class="annotation-section">
                    <h3>Annotation Options</h3>
                    <div class="annotation-options">
                        <label>
                            <input type="checkbox" id="showTimestamp" checked> Show Timestamp
                        </label>
                        <label>
                            <input type="checkbox" id="showProgressBar" checked> Show Progress Bar
                        </label>
                        <label>
                            <input type="checkbox" id="generateSubtitles" checked> Generate Subtitles
                        </label>
                        <label>
                            <input type="checkbox" id="addCustomText"> Add Custom Text
                        </label>
                        <label>
                            <input type="checkbox" id="addWatermark"> Add Watermark
                        </label>
                        <label>
                            <input type="checkbox" id="addSessionInfo" checked> Add Session Info
                        </label>
                    </div>
                    
                    <div class="custom-text-section" id="customTextSection" style="display: none;">
                        <label for="customTextInput">Custom Text:</label>
                        <input type="text" id="customTextInput" placeholder="Enter custom text to overlay...">
                    </div>
                    
                    <div class="custom-text-section" id="watermarkSection" style="display: none;">
                        <label for="watermarkInput">Watermark Text:</label>
                        <input type="text" id="watermarkInput" placeholder="Enter watermark text...">
                    </div>
                </div>
                
                <div class="annotation-section">
                    <h3>Actions</h3>
                    <button class="btn btn-primary" onclick="previewAnnotations()">Preview Annotations</button>
                    <button class="btn btn-success" onclick="createEnhancedVideo()">Create Enhanced Video</button>
                    <button class="btn btn-secondary" onclick="generateSubtitlesOnly()">Generate Subtitles Only</button>
                </div>
                
                <div class="annotation-section">
                    <h3>Results</h3>
                    <div id="annotationResults"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let isConnected = false;
        let currentSessionId = null;
        let interviewStarted = false;
        let recordingStarted = false;
        let autoRecordingEnabled = true;
        let isRecording = false;
        let audioChunks = [];
        let videoChunks = [];
        let mediaStream = null;
        let audioRecorder = null;
        let videoRecorder = null;
        let audioContext = null;
        let mixedAudioDestination = null;
        let currentVoice = 'alloy';

        function showTab(tabName) {
            // Hide all tab contents
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Remove active class from all tabs
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab content
            document.getElementById(tabName + '-tab').classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }

        function updateStatus(message) {
            document.getElementById('status').textContent = message;
        }

        async function connectToJavaServer() {
            try {
                console.log('Connecting to Java server...');
                updateStatus('Connecting to Java server...');
                
                // For Java server, we'll use HTTP endpoints instead of WebSocket
                isConnected = true;
                updateStatus('Connected to Java server. Click "Start Interview & Recording" to begin.');
                
                // Start interview with Java server
                console.log('Starting interview...');
                const response = await fetch('http://localhost:8080/java/start-interview', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        client_id: `client_${Date.now()}`
                    })
                });
                
                console.log('Interview response status:', response.status);
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('Interview response data:', data);
                    
                    if (data.success) {
                        currentSessionId = data.session_id;
                        console.log('Session ID set to:', currentSessionId);
                        document.getElementById('sessionId').textContent = data.session_id;
                        document.getElementById('sessionInfo').style.display = 'block';
                        addMessage(data.greeting_message, 'interviewer');
                        
                        // Generate initial interview question
                        console.log('Generating initial question...');
                        await generateInterviewQuestion();
                    } else {
                        console.error('Interview start failed:', data.error);
                        updateStatus('Failed to start interview: ' + data.error);
                    }
                } else {
                    console.error('Interview start HTTP error:', response.status);
                    updateStatus('Failed to start interview. HTTP error: ' + response.status);
                }
            } catch (error) {
                console.error('Java server connection error:', error);
                updateStatus('Failed to connect to Java server. Please check if the server is running.');
            }
        }

        async function generateInterviewQuestion() {
            console.log('generateInterviewQuestion called, sessionId:', currentSessionId);
            if (!currentSessionId) {
                console.error('No session ID available for question generation');
                return;
            }
            
            try {
                console.log('Sending generate-question request...');
                const response = await fetch('http://localhost:8080/java/generate-question', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        session_id: currentSessionId,
                        context: 'interview_start'
                    })
                });
                
                console.log('Generate question response status:', response.status);
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('Generate question response data:', data);
                    
                    if (data.success && data.question) {
                        console.log('Adding question to conversation:', data.question);
                        addMessage(data.question, 'interviewer');
                        speakWithJavaServer(data.question, currentVoice);
                    } else {
                        console.error('Question generation failed:', data.error);
                    }
                } else {
                    console.error('Generate question HTTP error:', response.status);
                }
            } catch (error) {
                console.error('Error generating question:', error);
            }
        }

        function addMessage(text, sender) {
            const conversation = document.getElementById('conversation');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            messageDiv.textContent = text;
            conversation.appendChild(messageDiv);
            conversation.scrollTop = conversation.scrollHeight;
        }

        async function startRecording() {
            if (!isConnected) {
                alert('Please connect to server first.');
                return;
            }

            interviewStarted = true;
            recordingStarted = true;
            
            // Speak any existing interviewer messages
            const conversation = document.getElementById('conversation');
            const interviewerMessages = conversation.querySelectorAll('.message.interviewer');
            if (interviewerMessages.length > 0) {
                const lastInterviewerMessage = interviewerMessages[interviewerMessages.length - 1];
                const messageText = lastInterviewerMessage.textContent;
                speakWithJavaServer(messageText, currentVoice);
            }

            try {
                const enableAudio = document.getElementById('enableAudio').checked;
                const enableVideo = document.getElementById('enableVideo').checked;
                
                if (!enableAudio && !enableVideo) {
                    alert('Please enable at least audio or video recording.');
                    return;
                }
                
                // Get media stream
                const constraints = {
                    audio: enableAudio,
                    video: enableVideo ? {
                        width: { ideal: 1280 },
                        height: { ideal: 720 },
                        frameRate: { ideal: 30 }
                    } : false
                };
                
                mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
                
                // Show video preview if video is enabled
                if (enableVideo) {
                    const videoPreview = document.getElementById('videoPreview');
                    videoPreview.srcObject = mediaStream;
                    videoPreview.style.display = 'block';
                }
                
                // Set up audio recording
                if (enableAudio) {
                    const audioStream = new MediaStream(mediaStream.getAudioTracks());
                    // Try to use more compatible audio formats for QuickTime
                    let audioMimeType = 'audio/webm;codecs=opus';
                    if (MediaRecorder.isTypeSupported('audio/mp4')) {
                        audioMimeType = 'audio/mp4';
                    } else if (MediaRecorder.isTypeSupported('audio/wav')) {
                        audioMimeType = 'audio/wav';
                    } else if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
                        audioMimeType = 'audio/webm;codecs=opus';
                    } else {
                        audioMimeType = 'audio/webm';
                    }
                    
                    console.log('Using audio format:', audioMimeType);
                    audioRecorder = new MediaRecorder(audioStream, { mimeType: audioMimeType });
                    
                    audioRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };

                    audioRecorder.onstop = async () => {
                        await processAudioRecording();
                    };
                    
                    audioRecorder.start();
                }
                
                // Set up video recording
                if (enableVideo) {
                    const videoStream = new MediaStream(mediaStream.getVideoTracks());
                    const combinedStream = new MediaStream([
                        ...mediaStream.getVideoTracks(),
                        ...mediaStream.getAudioTracks()
                    ]);
                    
                    // Try to use more compatible video formats
                    let videoMimeType = 'video/webm;codecs=vp9,opus';
                    if (MediaRecorder.isTypeSupported('video/mp4')) {
                        videoMimeType = 'video/mp4';
                    } else if (MediaRecorder.isTypeSupported('video/webm;codecs=vp9,opus')) {
                        videoMimeType = 'video/webm;codecs=vp9,opus';
                    } else if (MediaRecorder.isTypeSupported('video/webm;codecs=vp8,opus')) {
                        videoMimeType = 'video/webm;codecs=vp8,opus';
                    } else {
                        videoMimeType = 'video/webm';
                    }
                    
                    console.log('Using video format:', videoMimeType);
                    videoRecorder = new MediaRecorder(combinedStream, { mimeType: videoMimeType });
                    
                    videoRecorder.ondataavailable = (event) => {
                        videoChunks.push(event.data);
                        console.log('Video chunk collected, total chunks:', videoChunks.length);
                    };

                    videoRecorder.onstop = async () => {
                        await processVideoRecording();
                    };
                    
                    videoRecorder.start();
                }
                
                document.getElementById('startRecording').disabled = true;
                document.getElementById('stopRecording').disabled = false;
                document.querySelector('.recording-indicator').style.display = 'inline-block';
                updateStatus('Recording...');
                
            } catch (error) {
                console.error('Error starting recording:', error);
                updateStatus('Error starting recording. Please try again.');
            }
        }

        async function processAudioRecording() {
            console.log('processAudioRecording called, sessionId:', currentSessionId);
            const audioBlob = new Blob(audioChunks, { type: audioRecorder.mimeType });
            
            // Determine file extension based on MIME type
            let fileExtension = 'webm';
            if (audioRecorder.mimeType.includes('mp4')) {
                fileExtension = 'mp4';
            } else if (audioRecorder.mimeType.includes('wav')) {
                fileExtension = 'wav';
            } else if (audioRecorder.mimeType.includes('webm')) {
                fileExtension = 'webm';
            }
            
            const formData = new FormData();
            formData.append('file', audioBlob, `recording.${fileExtension}`);
            
            if (currentSessionId) {
                formData.append('session_id', currentSessionId);
                formData.append('client_id', currentSessionId);
            }

            try {
                console.log('Sending audio for processing...');
                const response = await fetch('http://localhost:8080/java/process-audio', {
                    method: 'POST',
                    body: formData
                });
                
                console.log('Process audio response status:', response.status);
                
                const data = await response.json();
                console.log('Process audio response data:', data);
                
                if (data.success && data.transcription) {
                    console.log('Adding transcription to conversation:', data.transcription);
                    addMessage(data.transcription, 'candidate');
                    
                    // Generate follow-up question based on the response
                    console.log('Generating follow-up question...');
                    await generateFollowUpQuestion(data.transcription);
                } else {
                    console.error('Audio processing failed:', data.error);
                    updateStatus('Error processing audio: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error:', error);
                updateStatus('Error processing audio. Please try again.');
            }

            audioChunks = [];
        }

        async function processVideoRecording() {
            console.log('processVideoRecording called, sessionId:', currentSessionId);
            if (videoChunks.length === 0) {
                console.log('No video chunks to process');
                return;
            }
            
            const videoBlob = new Blob(videoChunks, { type: videoRecorder.mimeType });
            
            // Determine file extension based on MIME type
            let fileExtension = 'webm';
            if (videoRecorder.mimeType.includes('mp4')) {
                fileExtension = 'mp4';
            } else if (videoRecorder.mimeType.includes('webm')) {
                fileExtension = 'webm';
            }
            
            const formData = new FormData();
            formData.append('file', videoBlob, `video_recording.${fileExtension}`);
            
            if (currentSessionId) {
                formData.append('session_id', currentSessionId);
                formData.append('client_id', currentSessionId);
            }

            try {
                console.log('Sending video for processing...');
                const response = await fetch('http://localhost:8080/java/process-video', {
                    method: 'POST',
                    body: formData
                });
                
                console.log('Process video response status:', response.status);
                
                const data = await response.json();
                console.log('Process video response data:', data);
                
                if (data.success) {
                    console.log('Video processed successfully');
                    updateStatus('Video processed successfully');
                } else {
                    console.error('Video processing failed:', data.error);
                    updateStatus('Error processing video: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error:', error);
                updateStatus('Error processing video. Please try again.');
            }

            videoChunks = [];
        }

        async function generateFollowUpQuestion(transcription) {
            console.log('generateFollowUpQuestion called, sessionId:', currentSessionId, 'transcription:', transcription);
            if (!currentSessionId) {
                console.error('No session ID available for follow-up generation');
                return;
            }
            
            try {
                console.log('Sending generate-followup request...');
                const response = await fetch('http://localhost:8080/java/generate-followup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        session_id: currentSessionId,
                        transcription: transcription,
                        context: 'follow_up'
                    })
                });
                
                console.log('Generate followup response status:', response.status);
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('Generate followup response data:', data);
                    
                    if (data.success && data.follow_up_question) {
                        console.log('Adding follow-up to conversation:', data.follow_up_question);
                        addMessage(data.follow_up_question, 'interviewer');
                        speakWithJavaServer(data.follow_up_question, currentVoice);
                    } else {
                        console.error('Follow-up generation failed:', data.error);
                    }
                } else {
                    console.error('Generate followup HTTP error:', response.status);
                }
            } catch (error) {
                console.error('Error generating follow-up:', error);
            }
        }

        function stopRecording() {
            if (audioRecorder && audioRecorder.state !== 'inactive') {
                audioRecorder.stop();
            }
            if (videoRecorder && videoRecorder.state !== 'inactive') {
                videoRecorder.stop();
            }
            
            if (mediaStream) {
                mediaStream.getTracks().forEach(track => track.stop());
            }
            
            document.getElementById('startRecording').disabled = false;
            document.getElementById('stopRecording').disabled = true;
            document.querySelector('.recording-indicator').style.display = 'none';
            updateStatus('Recording stopped.');
        }

        async function finishInterview() {
            console.log('finishInterview called, sessionId:', currentSessionId);
            if (!currentSessionId) {
                console.error('No active session to finish');
                alert('No active session to finish.');
                return;
            }

            stopRecording();
            
            try {
                console.log('Sending finish-interview request...');
                const response = await fetch('http://localhost:8080/java/finish-interview', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        session_id: currentSessionId
                    })
                });
                
                console.log('Finish interview response status:', response.status);
                
                const data = await response.json();
                console.log('Finish interview response data:', data);
                
                if (data.success) {
                    console.log('Interview finished successfully');
                    updateStatus('Interview finished successfully!');
                    currentSessionId = null;
                    document.getElementById('sessionId').textContent = '';
                    document.getElementById('sessionInfo').style.display = 'none';
                    interviewStarted = false;
                    recordingStarted = false;
                } else {
                    console.error('Finish interview failed:', data.error);
                    updateStatus('Error finishing interview: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error finishing interview:', error);
                updateStatus('Error finishing interview. Please try again.');
            }
        }

        async function speakWithJavaServer(text, voice) {
            try {
                console.log('Generating speech for text:', text, 'voice:', voice);
                const response = await fetch('http://localhost:8080/java/generate-speech', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        text: text,
                        voice: voice,
                        session_id: currentSessionId
                    })
                });
                
                console.log('Speech generation response status:', response.status);
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('Speech generation response data:', data);
                    console.log('Audio data length:', data.audio_data ? data.audio_data.length : 'null');
                    
                    if (data.success && data.audio_data) {
                        // Convert base64 audio data to blob
                        const audioData = data.audio_data;
                        console.log('Converting base64 audio data...');
                        
                        try {
                            const byteCharacters = atob(audioData);
                            const byteNumbers = new Array(byteCharacters.length);
                            for (let i = 0; i < byteCharacters.length; i++) {
                                byteNumbers[i] = byteCharacters.charCodeAt(i);
                            }
                            const byteArray = new Uint8Array(byteNumbers);
                            console.log('Byte array length:', byteArray.length);
                            
                            // Try different audio formats
                            const audioBlob = new Blob([byteArray], { type: 'audio/wav' });
                            const audioUrl = URL.createObjectURL(audioBlob);
                            
                            console.log('Playing audio from blob URL:', audioUrl);
                            const audio = new Audio(audioUrl);
                            
                            audio.onloadstart = () => console.log('Audio loading started');
                            audio.oncanplay = () => console.log('Audio can play');
                            audio.onplay = () => console.log('Audio started playing');
                            audio.onended = () => {
                                console.log('Audio finished playing');
                                URL.revokeObjectURL(audioUrl); // Clean up
                            };
                            audio.onerror = (e) => console.error('Audio error:', e);
                            
                            const playResult = await audio.play();
                            console.log('Audio play result:', playResult);
                            
                        } catch (decodeError) {
                            console.error('Error decoding audio data:', decodeError);
                            // Fallback: try to play a test tone
                            console.log('Trying fallback test tone...');
                            await playTestTone();
                        }
                    } else {
                        console.error('Speech generation failed:', data.error);
                        // Fallback: try to play a test tone
                        console.log('Trying fallback test tone...');
                        await playTestTone();
                    }
                } else {
                    console.error('Speech generation HTTP error:', response.status);
                    // Fallback: try to play a test tone
                    console.log('Trying fallback test tone...');
                    await playTestTone();
                }
            } catch (error) {
                console.error('Error generating speech:', error);
                // Fallback: try to play a test tone
                console.log('Trying fallback test tone...');
                await playTestTone();
            }
        }

        async function playTestTone() {
            try {
                // Generate a simple test tone using Web Audio API
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.frequency.setValueAtTime(440, audioContext.currentTime); // A4 note
                oscillator.type = 'sine';
                
                gainNode.gain.setValueAtTime(0.1, audioContext.currentTime); // Low volume
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 1);
                
                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + 1);
                
                console.log('Test tone played successfully');
            } catch (error) {
                console.error('Error playing test tone:', error);
            }
        }

        function testSpeech() {
            const testText = "Hello, this is a test of the text-to-speech system.";
            speakWithJavaServer(testText, currentVoice);
        }

        function changeVoice() {
            currentVoice = document.getElementById('voiceSelect').value;
        }

        function toggleAutoRecording() {
            autoRecordingEnabled = !autoRecordingEnabled;
            const button = document.getElementById('toggleAutoRecording');
            if (autoRecordingEnabled) {
                button.textContent = 'Disable Auto-Recording';
                button.className = 'btn btn-success';
            } else {
                button.textContent = 'Enable Auto-Recording';
                button.className = 'btn btn-warning';
            }
        }

        async function loadRecordings() {
            try {
                const response = await fetch('http://localhost:8080/java/list-recordings');
                
                if (response.ok) {
                    const data = await response.json();
                    displayRecordings(data.recordings || []);
                } else {
                    document.getElementById('recordingsList').innerHTML = '<p style="color: red;">Error loading recordings.</p>';
                }
            } catch (error) {
                console.error('Error loading recordings:', error);
                document.getElementById('recordingsList').innerHTML = '<p style="color: red;">Error loading recordings.</p>';
            }
        }

        function displayRecordings(recordings) {
            const recordingsList = document.getElementById('recordingsList');
            
            if (recordings.length === 0) {
                recordingsList.innerHTML = '<p>No recordings found.</p>';
                return;
            }
            
            let html = '';
            recordings.forEach(recording => {
                html += `
                    <div class="recording-item">
                        <div class="recording-header">
                            <h3>Session: ${recording.session_id}</h3>
                            <p>Audio files: ${recording.audio_files ? recording.audio_files.length : 0}</p>
                            <p>Video files: ${recording.video_files ? recording.video_files.length : 0}</p>
                        </div>
                        <div class="recording-actions">
                            <button class="btn btn-sm btn-primary" onclick="viewSession('${recording.session_id}')">View Details</button>
                        </div>
                    </div>
                `;
            });
            
            recordingsList.innerHTML = html;
        }

        function viewSession(sessionId) {
            // Show loading state
            showSessionDetailsLoading();
            
            // Fetch session details from the server
            fetch(`http://localhost:8080/java/session-details?session_id=${sessionId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        showSessionDetails(data.session);
                    } else {
                        showSessionDetailsError(data.error || 'Unknown error occurred');
                    }
                })
                .catch(error => {
                    console.error('Error fetching session details:', error);
                    showSessionDetailsError('Failed to load session details. Please try again.');
                });
        }

        function showSessionDetailsLoading() {
            const modalContent = `
                <div class="modal" id="sessionDetailsModal">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Loading Session Details...</h5>
                                <button type="button" class="close" onclick="closeModal()">
                                    <span>&times;</span>
                                </button>
                            </div>
                            <div class="modal-body text-center">
                                <div class="spinner-border" role="status">
                                    <span class="sr-only">Loading...</span>
                                </div>
                                <p class="mt-3">Loading session details...</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove existing modal if any
            const existingModal = document.getElementById('sessionDetailsModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // Add modal to page
            document.body.insertAdjacentHTML('beforeend', modalContent);
            
            // Show modal
            const modal = document.getElementById('sessionDetailsModal');
            modal.classList.add('show');
        }

        function showSessionDetailsError(errorMessage) {
            const modalContent = `
                <div class="modal" id="sessionDetailsModal">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Error Loading Session Details</h5>
                                <button type="button" class="close" onclick="closeModal()">
                                    <span>&times;</span>
                                </button>
                            </div>
                            <div class="modal-body">
                                <div class="alert alert-danger" role="alert">
                                    ⚠️ ${errorMessage}
                                </div>
                                <div class="text-center">
                                    <button type="button" class="btn btn-primary" onclick="closeModal()">Close</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove existing modal if any
            const existingModal = document.getElementById('sessionDetailsModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // Add modal to page
            document.body.insertAdjacentHTML('beforeend', modalContent);
            
            // Show modal
            const modal = document.getElementById('sessionDetailsModal');
            modal.classList.add('show');
        }

        function closeModal() {
            const modal = document.getElementById('sessionDetailsModal');
            if (modal) {
                modal.classList.remove('show');
                setTimeout(() => {
                    modal.remove();
                }, 300);
            }
        }

        // Add click outside to close functionality
        document.addEventListener('click', function(event) {
            const modal = document.getElementById('sessionDetailsModal');
            if (modal && event.target === modal) {
                closeModal();
            }
        });

        // Add escape key to close functionality
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                closeModal();
            }
        });

        // Add session details functionality
        function showSessionDetails(session) {
            // Create modal content with custom styling
            const modalContent = `
                <div class="modal" id="sessionDetailsModal">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">
                                    📁 Session Details: ${session.session_id}
                                </h5>
                                <button type="button" class="close" onclick="closeModal()">
                                    <span>&times;</span>
                                </button>
                            </div>
                            <div class="modal-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="card">
                                            <div class="card-header bg-info text-white">
                                                <h6 class="mb-0">
                                                    🎤 Audio Files (${session.audio_files ? session.audio_files.length : 0})
                                                </h6>
                                            </div>
                                            <div class="card-body">
                                                ${session.audio_files && session.audio_files.length > 0 ? 
                                                    session.audio_files.map(file => `
                                                        <div class="d-flex justify-content-between align-items-center mb-2 p-2 border border-rounded">
                                                            <div class="flex-grow-1">
                                                                🎵 <span style="margin-left: 8px;">${file}</span>
                                                            </div>
                                                            <button class="btn btn-primary" style="font-size: 12px; padding: 4px 8px;" onclick="playAudio('${session.session_id}', '${file}')">
                                                                ▶️ Play
                                                            </button>
                                                        </div>
                                                    `).join('') : 
                                                    '<div class="text-muted text-center py-3">ℹ️ No audio files found</div>'
                                                }
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="card">
                                            <div class="card-header bg-success text-white">
                                                <h6 class="mb-0">
                                                    🎥 Video Files (${session.video_files ? session.video_files.length : 0})
                                                </h6>
                                            </div>
                                            <div class="card-body">
                                                ${session.video_files && session.video_files.length > 0 ? 
                                                    session.video_files.map(file => `
                                                        <div class="d-flex justify-content-between align-items-center mb-2 p-2 border border-rounded">
                                                            <div class="flex-grow-1">
                                                                🎬 <span style="margin-left: 8px;">${file}</span>
                                                            </div>
                                                            <button class="btn btn-success" style="font-size: 12px; padding: 4px 8px;" onclick="playVideo('${session.session_id}', '${file}')">
                                                                ▶️ Play
                                                            </button>
                                                        </div>
                                                    `).join('') : 
                                                    '<div class="text-muted text-center py-3">ℹ️ No video files found</div>'
                                                }
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="row mt-3">
                                    <div class="col-12">
                                        <div class="card">
                                            <div class="card-header bg-secondary text-white">
                                                <h6 class="mb-0">
                                                    ℹ️ Session Information
                                                </h6>
                                            </div>
                                            <div class="card-body">
                                                <div class="row">
                                                    <div class="col-md-6">
                                                        <p><strong>Session ID:</strong> ${session.session_id}</p>
                                                        <p><strong>Total Files:</strong> ${(session.audio_files ? session.audio_files.length : 0) + (session.video_files ? session.video_files.length : 0)}</p>
                                                    </div>
                                                    <div class="col-md-6">
                                                        <p><strong>Audio Files:</strong> ${session.audio_files ? session.audio_files.length : 0}</p>
                                                        <p><strong>Video Files:</strong> ${session.video_files ? session.video_files.length : 0}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" onclick="closeModal()">
                                    ❌ Close
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Remove existing modal if any
            const existingModal = document.getElementById('sessionDetailsModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // Add modal to page
            document.body.insertAdjacentHTML('beforeend', modalContent);
            
            // Show modal
            const modal = document.getElementById('sessionDetailsModal');
            modal.classList.add('show');
        }

        function playAudio(sessionId, filename) {
            const audioUrl = `http://localhost:8080/java/audio/${sessionId}/${filename}`;
            const audio = new Audio(audioUrl);
            audio.play().catch(error => {
                console.error('Error playing audio:', error);
                alert('Error playing audio file');
            });
        }

        function playVideo(sessionId, filename) {
            const videoUrl = `http://localhost:8080/java/video/${sessionId}/${filename}`;
            window.open(videoUrl, '_blank');
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            // Auto-connect to Java server
            connectToJavaServer();
            
            // Set up recording button event listeners
            document.getElementById('startRecording').addEventListener('click', startRecording);
            document.getElementById('stopRecording').addEventListener('click', stopRecording);
            
            // Set up annotation event listeners
            document.getElementById('addCustomText').addEventListener('change', function() {
                document.getElementById('customTextSection').style.display = this.checked ? 'block' : 'none';
            });
            
            document.getElementById('addWatermark').addEventListener('change', function() {
                document.getElementById('watermarkSection').style.display = this.checked ? 'block' : 'none';
            });
        });
    </script>
</body>
</html>
"""


class JavaWebClient:
    """Backend handler for the Java web client"""
    
    def __init__(self):
        self.java_client = None
        if interview_pb2 and interview_pb2_grpc:
            self.java_client = JavaInterviewClient()
    
    def handle_java_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Java server requests through the web client"""
        if not self.java_client:
            return {"success": False, "error": "Java client not available"}
        
        try:
            if endpoint == "start-interview":
                return self.java_client.start_interview(data.get("client_id"))
            elif endpoint == "process-audio":
                # This would need to handle file upload
                return {"success": False, "error": "Audio processing not implemented in web mode"}
            elif endpoint == "generate-speech":
                return self.java_client.generate_speech(
                    data.get("text", ""),
                    data.get("session_id"),
                    data.get("voice", "alloy")
                )
            elif endpoint == "finish-interview":
                return self.java_client.finish_interview(data.get("session_id"))
            elif endpoint == "list-recordings":
                return {"success": True, "recordings": []}  # Placeholder
            elif endpoint == "generate-question":
                # Generate interview question using Java server
                return self._generate_question(data.get("session_id"), data.get("context", "interview_start"))
            elif endpoint == "generate-followup":
                # Generate follow-up question using Java server
                return self._generate_followup(data.get("session_id"), data.get("transcription", ""), data.get("context", "follow_up"))
            else:
                return {"success": False, "error": f"Unknown endpoint: {endpoint}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_question(self, session_id: str, context: str) -> Dict[str, Any]:
        """Generate an interview question"""
        try:
            # Use predefined questions for now, or call Java server if available
            questions = [
                "Hello! I'm your AI interviewer today. Could you please introduce yourself?",
                "Could you tell me about your relevant experience?",
                "What are your key technical skills?",
                "How do you approach problem-solving in your work?",
                "Where do you see yourself in the next 5 years?"
            ]
            
            import random
            question = random.choice(questions)
            
            return {
                "success": True,
                "question": question,
                "session_id": session_id
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_followup(self, session_id: str, transcription: str, context: str) -> Dict[str, Any]:
        """Generate a follow-up question based on the candidate's response"""
        try:
            # Simple follow-up logic - in a real implementation, this would use AI
            follow_ups = [
                "That's interesting! Could you elaborate on that?",
                "Thank you for sharing that. What was the outcome?",
                "How did you handle challenges in that situation?",
                "What did you learn from that experience?",
                "Can you give me a specific example?"
            ]
            
            import random
            follow_up = random.choice(follow_ups)
            
            return {
                "success": True,
                "follow_up_question": follow_up,
                "session_id": session_id
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.java_client = JavaWebClient()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode())
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path.startswith('/java/'):
            self.handle_java_request()
        else:
            self.send_response(404)
            self.end_headers()
    
    def handle_java_request(self):
        """Handle Java server requests"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            endpoint = self.path.replace('/java/', '')
            
            result = self.java_client.handle_java_request(endpoint, data)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())


def run_server():
    PORT = 8081
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Java web client serving at http://localhost:{PORT}")
        print("This client connects to the Java gRPC server (port 8080)")
        httpd.serve_forever()


if __name__ == "__main__":
    run_server() 