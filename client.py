import http.server
import socketserver
import websockets
import asyncio
import json
import os
from pathlib import Path

# HTML content for the web interface
HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
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
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Interview Agent</h1>
        <div class="tabs">
            <div class="tab active" onclick="showTab('interview')">Interview</div>
            <div class="tab" onclick="showTab('recordings')">Recordings</div>
        </div>
        
        <div id="interview-tab" class="tab-content active">
            <div class="session-info" id="sessionInfo" style="display: none;">
                <strong>Session ID:</strong> <span id="sessionId"></span>
            </div>
            <div class="status" id="status">Connecting to server... Auto-recording will start when interview begins.</div>
            
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
        </div>
        
        <div id="recordings-tab" class="tab-content">
            <h2>Interview Recordings</h2>
            <button onclick="loadRecordings()">Refresh Recordings</button>
            <div class="recordings-list" id="recordingsList"></div>
            <div id="sessionDetails" style="display:none;"></div>
        </div>
    </div>

    <script>
        let mediaRecorder;
        let audioRecorder;
        let videoRecorder;
        let audioChunks = [];
        let videoChunks = [];
        let ws;
        let isConnected = false;
        let currentSessionId = null;
        let mediaStream = null;
        let desktopStream = null;
        let isRecording = false;
        let audioContext = null;
        let microphoneSource = null;
        let desktopSource = null;
        let ttsSource = null;
        let mixedAudioDestination = null;
        let ttsAudioQueue = [];
        let isPlayingTTS = false;
        let autoRecordingEnabled = true;
        let recordingStarted = false;

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
            
            // Load recordings if switching to recordings tab
            if (tabName === 'recordings') {
                loadRecordings();
            }
        }

        async function loadRecordings() {
            try {
                const response = await fetch('http://localhost:8000/recordings');
                const data = await response.json();
                
                const recordingsList = document.getElementById('recordingsList');
                recordingsList.innerHTML = '';
                
                if (data.recordings && data.recordings.length > 0) {
                    // Sort recordings by date (newest first)
                    data.recordings.sort((a, b) => {
                        // Extract date from session_id (format: interview_YYYYMMDD_HHMMSS_XXXXXX)
                        const dateA = a.session_id.split('_')[1] + a.session_id.split('_')[2];
                        const dateB = b.session_id.split('_')[1] + b.session_id.split('_')[2];
                        return dateB.localeCompare(dateA); // Descending order
                    });
                    
                    data.recordings.forEach(recording => {
                        const recordingDiv = document.createElement('div');
                        recordingDiv.className = 'recording-item';
                        
                        // Extract date from session_id for display
                        const dateParts = recording.session_id.split('_');
                        const dateStr = dateParts[1] + '-' + dateParts[2];
                        const timeStr = dateParts[2];
                        const displayDate = `${dateStr.substring(0,4)}-${dateStr.substring(4,6)}-${dateStr.substring(6,8)} ${timeStr.substring(0,2)}:${timeStr.substring(2,4)}:${timeStr.substring(4,6)}`;
                        
                        recordingDiv.innerHTML = `
                            <div class="recording-header">
                                <h3>${displayDate}</h3>
                                <p>Session: ${recording.session_id}</p>
                                <p>Files: ${recording.audio_files.length} audio, ${recording.video_files ? recording.video_files.length : 0} video, ${recording.metadata_files.length} metadata</p>
                                ${recording.combined_audio ? `<p><strong>Combined Audio Available</strong></p>` : ''}
                                ${recording.combined_video ? `<p><strong>Combined Video Available</strong></p>` : ''}
                            </div>
                            <div class="recording-actions">
                                <button onclick="viewSessionDetails('${recording.session_id}')" class="btn btn-primary">View Details</button>
                                ${recording.combined_audio ? `<button onclick="playCombinedAudio('${recording.session_id}', '${recording.combined_audio}')" class="btn btn-success">Play Combined Audio</button>` : ''}
                                ${recording.combined_video ? `<button onclick="playCombinedVideo('${recording.session_id}', '${recording.combined_video}')" class="btn btn-success">Play Combined Video</button>` : ''}
                            </div>
                        `;
                        recordingsList.appendChild(recordingDiv);
                    });
                } else {
                    recordingsList.innerHTML = '<p>No recordings found.</p>';
                }
            } catch (error) {
                console.error('Error loading recordings:', error);
                document.getElementById('recordingsList').innerHTML = '<p>Error loading recordings.</p>';
            }
        }

        function playCombinedAudio(sessionId, filename) {
            const audioUrl = `http://localhost:8000/recordings/${sessionId}/${filename}`;
            const audio = new Audio(audioUrl);
            audio.play().catch(error => {
                console.error('Error playing audio:', error);
                alert('Error playing audio. Please try again.');
            });
        }

        function playCombinedVideo(sessionId, filename) {
            const videoUrl = `http://localhost:8000/recordings/${sessionId}/${filename}`;
            const video = document.createElement('video');
            video.src = videoUrl;
            video.controls = true;
            video.style.width = '100%';
            video.style.maxWidth = '640px';
            
            // Create a modal or popup to show the video
            const modal = document.createElement('div');
            modal.style.position = 'fixed';
            modal.style.top = '0';
            modal.style.left = '0';
            modal.style.width = '100%';
            modal.style.height = '100%';
            modal.style.backgroundColor = 'rgba(0,0,0,0.8)';
            modal.style.display = 'flex';
            modal.style.justifyContent = 'center';
            modal.style.alignItems = 'center';
            modal.style.zIndex = '1000';
            
            const closeBtn = document.createElement('button');
            closeBtn.textContent = 'Close';
            closeBtn.style.position = 'absolute';
            closeBtn.style.top = '20px';
            closeBtn.style.right = '20px';
            closeBtn.style.padding = '10px 20px';
            closeBtn.style.backgroundColor = '#dc3545';
            closeBtn.style.color = 'white';
            closeBtn.style.border = 'none';
            closeBtn.style.borderRadius = '4px';
            closeBtn.style.cursor = 'pointer';
            
            closeBtn.onclick = () => document.body.removeChild(modal);
            modal.onclick = (e) => {
                if (e.target === modal) document.body.removeChild(modal);
            };
            
            modal.appendChild(video);
            modal.appendChild(closeBtn);
            document.body.appendChild(modal);
        }

        async function viewSessionDetails(sessionId) {
            try {
                const response = await fetch(`http://localhost:8000/recordings/${sessionId}`);
                const data = await response.json();
                
                if (data.error) {
                    alert('Error loading session details:::: ' + data.error + " sessionId: " + sessionId);
                    return;
                }
                
                const detailsDiv = document.getElementById('sessionDetails');
                if (detailsDiv == null) {
                    alert('Session details panel not found.');
                    return;
                }
                detailsDiv.style.display = '';
                detailsDiv.innerHTML = `
                    <h2>Session: ${data.session_id}</h2>
                    <div class="audio-section">
                        <h3>Interviewer Audio Files</h3>
                        ${data.interviewer_files.length > 0 ? 
                            data.interviewer_files.map(file => `
                                <div class="audio-item">
                                    <span>${file}</span>
                                    <button onclick="playAudio('${sessionId}', '${file.replace(/'/g, "\\'")}')" class="btn btn-sm btn-primary">Play</button>
                                </div>
                            `).join('') : '<p>No interviewer audio files</p>'
                        }
                    </div>
                    <div class="audio-section">
                        <h3>Candidate Audio Files</h3>
                        ${data.candidate_files.length > 0 ? 
                            data.candidate_files.map(file => `
                                <div class="audio-item">
                                    <span>${file}</span>
                                    <button onclick="playAudio('${sessionId}', '${file.replace(/'/g, "\\'")}')" class="btn btn-sm btn-primary">Play</button>
                                </div>
                            `).join('') : '<p>No candidate audio files</p>'
                        }
                    </div>
                    ${data.video_files && data.video_files.length > 0 ? `
                        <div class="audio-section">
                            <h3>Video Files</h3>
                            ${data.video_files.map(file => `
                                <div class="audio-item">
                                    <span>${file}</span>
                                    <button onclick="playVideo('${sessionId}', '${file.replace(/'/g, "\\'")}')" class="btn btn-sm btn-primary">Play</button>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                    ${data.combined_audio ? `
                        <div class="audio-section">
                            <h3>Combined Audio</h3>
                            <div class="audio-item">
                                <span>${data.combined_audio}</span>
                                <button onclick="playAudio('${sessionId}', '${data.combined_audio.replace(/'/g, "\\'")}')" class="btn btn-sm btn-success">Play Combined</button>
                            </div>
                        </div>
                    ` : ''}
                    ${data.combined_video ? `
                        <div class="audio-section">
                            <h3>Combined Video</h3>
                            <div class="audio-item">
                                <span>${data.combined_video}</span>
                                <button onclick="playVideo('${sessionId}', '${data.combined_video.replace(/'/g, "\\'")}')" class="btn btn-sm btn-success">Play Combined</button>
                            </div>
                        </div>
                    ` : ''}
                    <div class="metadata-section">
                        <h3>Metadata Files</h3>
                        ${data.metadata_files.length > 0 ? 
                            data.metadata_files.map(file => `<p>${file}</p>`).join('') : '<p>No metadata files</p>'
                        }
                    </div>
                    <button onclick="hideSessionDetails()" class="btn btn-secondary">Back to Recordings</button>
                `;
                // Hide the recordings list while showing details
                document.getElementById('recordingsList').style.display = 'none';
                detailsDiv.scrollIntoView({behavior: 'smooth'});
            } catch (error) {
                console.error('Error loading session details.', error, sessionId);
                alert('Error loading session details.' + sessionId);
            }
        }

        function hideSessionDetails() {
            document.getElementById('sessionDetails').style.display = 'none';
            document.getElementById('recordingsList').style.display = '';
        }

        function playAudio(sessionId, filename) {
            if (!filename || filename === 'undefined') {
                console.error('Invalid filename:', filename);
                alert('Invalid audio file');
                return;
            }
            
            const audioUrl = `http://localhost:8000/recordings/${sessionId}/${encodeURIComponent(filename)}`;
            const audio = new Audio(audioUrl);
            audio.play().catch(error => {
                console.error('Error playing audio:', error);
                alert('Error playing audio. Please try again.');
            });
        }

        function playVideo(sessionId, filename) {
            if (!filename || filename === 'undefined') {
                console.error('Invalid filename:', filename);
                alert('Invalid video file');
                return;
            }
            
            const videoUrl = `http://localhost:8000/recordings/${sessionId}/${encodeURIComponent(filename)}`;
            const video = document.createElement('video');
            video.src = videoUrl;
            video.controls = true;
            video.style.width = '100%';
            video.style.maxWidth = '640px';
            
            // Create a modal or popup to show the video
            const modal = document.createElement('div');
            modal.style.position = 'fixed';
            modal.style.top = '0';
            modal.style.left = '0';
            modal.style.width = '100%';
            modal.style.height = '100%';
            modal.style.backgroundColor = 'rgba(0,0,0,0.8)';
            modal.style.display = 'flex';
            modal.style.justifyContent = 'center';
            modal.style.alignItems = 'center';
            modal.style.zIndex = '1000';
            
            const closeBtn = document.createElement('button');
            closeBtn.textContent = 'Close';
            closeBtn.style.position = 'absolute';
            closeBtn.style.top = '20px';
            closeBtn.style.right = '20px';
            closeBtn.style.padding = '10px 20px';
            closeBtn.style.backgroundColor = '#dc3545';
            closeBtn.style.color = 'white';
            closeBtn.style.border = 'none';
            closeBtn.style.borderRadius = '4px';
            closeBtn.style.cursor = 'pointer';
            
            closeBtn.onclick = () => document.body.removeChild(modal);
            modal.onclick = (e) => {
                if (e.target === modal) document.body.removeChild(modal);
            };
            
            modal.appendChild(video);
            modal.appendChild(closeBtn);
            document.body.appendChild(modal);
        }

        function addMessage(content, role) {
            const conversation = document.getElementById('conversation');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            messageDiv.textContent = content;
            conversation.appendChild(messageDiv);
            conversation.scrollTop = conversation.scrollHeight;
            
            // Speak the message if it's from the interviewer
            if (role === 'interviewer') {
                // Get the currently selected voice from the dropdown
                const selectedVoice = document.getElementById('voiceSelect')?.value || 'alloy';
                speakWithOpenAI(content, selectedVoice);
            }
        }

        function updateStatus(message) {
            document.getElementById('status').textContent = message;
        }

        async function connectWebSocket() {
            try {
                ws = new WebSocket('ws://localhost:8000/ws');
                
                ws.onopen = function() {
                    isConnected = true;
                    updateStatus('Connected to server');
                };
                
                ws.onmessage = async function(event) {
                    const data = JSON.parse(event.data);
                    if (data.type === 'greeting' || data.type === 'follow_up') {
                        addMessage(data.message, 'interviewer');
                        
                        // Capture session_id if provided
                        if (data.session_id) {
                            currentSessionId = data.session_id;
                            document.getElementById('sessionId').textContent = data.session_id;
                            document.getElementById('sessionInfo').style.display = 'block';
                        }
                        
                        // Auto-start recording on first greeting if not already recording
                        if (autoRecordingEnabled && !recordingStarted && data.type === 'greeting') {
                            await startAutoRecording();
                        }
                    }
                };

                ws.onclose = function() {
                    isConnected = false;
                    updateStatus('Connection lost. Reconnecting...');
                    setTimeout(connectWebSocket, 1000);
                };

                ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                    updateStatus('Connection error. Please refresh the page.');
                };
            } catch (error) {
                console.error('WebSocket connection error:', error);
                updateStatus('Failed to connect. Please refresh the page.');
            }
        }

        async function startRecording() {
            // Manual recording start (override for auto-recording)
            if (autoRecordingEnabled && !recordingStarted) {
                await startAutoRecording();
            } else if (!autoRecordingEnabled) {
                // Original manual recording logic
                try {
                    const enableVideo = document.getElementById('enableVideo').checked;
                    const enableAudio = document.getElementById('enableAudio').checked;
                    
                    if (!enableVideo && !enableAudio) {
                        alert('Please enable at least audio or video recording.');
                        return;
                    }

                    // Initialize Web Audio API for mixing audio
                    if (enableVideo) {
                        audioContext = new (window.AudioContext || window.webkitAudioContext)();
                        mixedAudioDestination = audioContext.createMediaStreamDestination();
                    }

                    const constraints = {};
                    if (enableAudio) {
                        constraints.audio = {
                            sampleRate: 44100,
                            channelCount: 1,
                            echoCancellation: true,
                            noiseSuppression: true
                        };
                    }
                    if (enableVideo) {
                        constraints.video = {
                            width: { ideal: 1280 },
                            height: { ideal: 720 },
                            frameRate: { ideal: 30 }
                        };
                    }

                    mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
                    
                    // Capture desktop audio if video recording is enabled
                    if (enableVideo) {
                        const enableDesktopAudio = document.getElementById('enableDesktopAudio').checked;
                        if (enableDesktopAudio) {
                            await captureDesktopAudio();
                        }
                    }
                    
                    // Set up video preview
                    if (enableVideo) {
                        const videoPreview = document.getElementById('videoPreview');
                        videoPreview.srcObject = mediaStream;
                    }
                    
                    // Create separate recorders for audio and video
                    if (enableAudio) {
                        const audioStream = new MediaStream(mediaStream.getAudioTracks());
                        const audioMimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') 
                            ? 'audio/webm;codecs=opus' 
                            : 'audio/webm';
                        
                        audioRecorder = new MediaRecorder(audioStream, { mimeType: audioMimeType });
                        
                        audioRecorder.ondataavailable = (event) => {
                            audioChunks.push(event.data);
                        };

                        audioRecorder.onstop = async () => {
                            const audioBlob = new Blob(audioChunks, { type: audioMimeType });
                            const formData = new FormData();
                            formData.append('file', audioBlob, 'recording.webm');
                            
                            if (currentSessionId) {
                                formData.append('session_id', currentSessionId);
                                formData.append('client_id', currentSessionId);
                            }

                            try {
                                const response = await fetch('http://localhost:8000/transcribe', {
                                    method: 'POST',
                                    body: formData
                                });
                                const data = await response.json();
                                
                                addMessage(data.transcription, 'candidate');
                                
                                if (ws && isConnected) {
                                    ws.send(JSON.stringify({
                                        transcription: data.transcription
                                    }));
                                }
                            } catch (error) {
                                console.error('Error:', error);
                                updateStatus('Error processing audio. Please try again.');
                            }

                            audioChunks = [];
                        };
                        
                        audioRecorder.start();
                    }
                    
                    if (enableVideo) {
                        // Set up audio mixing for video recording
                        await setupAudioMixing();
                        
                        // Create combined stream with video and mixed audio
                        const videoTracks = mediaStream.getVideoTracks();
                        const mixedAudioTracks = mixedAudioDestination.stream.getAudioTracks();
                        const combinedStream = new MediaStream([...videoTracks, ...mixedAudioTracks]);
                        
                        const videoMimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9,opus') 
                            ? 'video/webm;codecs=vp9,opus' 
                            : MediaRecorder.isTypeSupported('video/webm;codecs=vp8,opus')
                            ? 'video/webm;codecs=vp8,opus'
                            : 'video/webm';
                        
                        videoRecorder = new MediaRecorder(combinedStream, { mimeType: videoMimeType });
                        
                        videoRecorder.ondataavailable = (event) => {
                            videoChunks.push(event.data);
                            // Don't save chunks during recording - only collect them
                            console.log('Video chunk collected, total chunks:', videoChunks.length);
                        };

                        videoRecorder.onstop = async () => {
                            // Only save video when the interview is actually finished
                            // Don't save during continuous recording restarts
                            if (!isRecording) {
                                // Interview is finished, save the complete video
                                if (videoChunks.length > 0) {
                                    const videoBlob = new Blob(videoChunks, { type: videoMimeType });
                                    const formData = new FormData();
                                    formData.append('file', videoBlob, 'recording.webm');
                                    
                                    if (currentSessionId) {
                                        formData.append('session_id', currentSessionId);
                                        formData.append('client_id', currentSessionId);
                                    }

                                    try {
                                        const response = await fetch('http://localhost:8000/save-video', {
                                            method: 'POST',
                                            body: formData
                                        });
                                        const data = await response.json();
                                        
                                        if (data.success) {
                                            console.log('Final video saved successfully');
                                            updateStatus('Video saved successfully');
                                        } else {
                                            console.error('Error saving final video:', data.error);
                                            updateStatus('Error saving video: ' + data.error);
                                        }
                                    } catch (error) {
                                        console.error('Error saving final video:', error);
                                        updateStatus('Error saving video');
                                    }
                                }
                            } else {
                                // This is just a restart for continuous recording, don't save
                                console.log('Video recording restarted for continuous mode, chunks preserved');
                            }
                            
                            // Don't clear chunks during continuous recording
                            if (!isRecording) {
                                videoChunks = [];
                            }
                        };
                        
                        // Set timeslice to 1 second for continuous recording
                        videoRecorder.start(1000);
                    }

                    isRecording = true;
                    recordingStarted = true;
                    document.getElementById('startRecording').disabled = true;
                    document.getElementById('stopRecording').disabled = false;
                    document.querySelector('.recording-indicator').style.display = 'inline-block';
                    updateStatus('Recording...');
                } catch (error) {
                    console.error('Error accessing media devices:', error);
                    updateStatus('Error accessing camera/microphone. Please check permissions.');
                }
            }
        }

        function stopRecording() {
            // For continuous recording, we don't actually stop - we just pause and restart
            if (autoRecordingEnabled && isRecording) {
                // Restart recording for continuous mode
                if (audioRecorder && audioRecorder.state !== 'inactive') {
                    audioRecorder.stop(); // This will trigger onstop which restarts
                }
                if (videoRecorder && videoRecorder.state !== 'inactive') {
                    videoRecorder.stop(); // This will trigger onstop which restarts
                }
                updateStatus('Recording restarted for continuous mode...');
            } else {
                // Complete stop for manual mode
                if (audioRecorder && audioRecorder.state !== 'inactive') {
                    audioRecorder.stop();
                }
                
                if (videoRecorder && videoRecorder.state !== 'inactive') {
                    videoRecorder.stop();
                }
                
                // Stop media stream
                if (mediaStream) {
                    mediaStream.getTracks().forEach(track => track.stop());
                    mediaStream = null;
                }
                
                // Clean up audio context
                if (audioContext) {
                    if (microphoneSource) {
                        microphoneSource.disconnect();
                        microphoneSource = null;
                    }
                    if (desktopSource) {
                        desktopSource.disconnect();
                        desktopSource = null;
                    }
                    if (ttsSource) {
                        ttsSource.disconnect();
                        ttsSource = null;
                    }
                    audioContext.close();
                    audioContext = null;
                }
                
                // Stop desktop stream
                if (desktopStream) {
                    desktopStream.getTracks().forEach(track => track.stop());
                    desktopStream = null;
                }
                
                // Clear video preview
                const videoPreview = document.getElementById('videoPreview');
                videoPreview.srcObject = null;
                
                isRecording = false;
                recordingStarted = false;
                document.getElementById('startRecording').disabled = false;
                document.getElementById('stopRecording').disabled = true;
                document.querySelector('.recording-indicator').style.display = 'none';
                updateStatus('Recording stopped.');
            }
        }

        function toggleAutoRecording() {
            autoRecordingEnabled = !autoRecordingEnabled;
            const toggleBtn = document.getElementById('toggleAutoRecording');
            if (autoRecordingEnabled) {
                toggleBtn.textContent = 'Disable Auto-Recording';
                toggleBtn.className = 'btn btn-warning';
                updateStatus('Auto-recording enabled. Recording will start automatically when interview begins.');
            } else {
                toggleBtn.textContent = 'Enable Auto-Recording';
                toggleBtn.className = 'btn btn-success';
                updateStatus('Manual recording mode. Click "Start Recording" to begin.');
            }
        }

        function speak(text) {
            if (text.trim() === '') return;
            
            // Always try OpenAI TTS first for better quality
            if (window.openaiTTSEnabled !== false) {
                speakWithOpenAI(text);
            } else {
                console.log('OpenAI TTS disabled, using browser speech synthesis');
                speakWithBrowser(text);
            }
        }
        
        async function speakWithOpenAI(text, voice = null) {
            try {
                const formData = new FormData();
                formData.append('text', text);
                
                // Use the provided voice or the selected voice from the dropdown
                const selectedVoice = voice || window.openaiVoice || document.getElementById('voiceSelect')?.value || 'alloy';
                formData.append('voice', selectedVoice);
                
                // Include session_id if available to save interviewer speech
                if (currentSessionId) {
                    formData.append('session_id', currentSessionId);
                }
                
                const response = await fetch('http://localhost:8000/tts', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(`TTS request failed: ${response.status}`);
                }
                
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                
                const audio = new Audio(audioUrl);
                
                // If video recording is active, mix the TTS audio into the video recording
                if (isRecording && audioContext && mixedAudioDestination) {
                    try {
                        console.log('Attempting to mix TTS audio into video recording...');
                        
                        // Ensure audio context is running
                        if (audioContext.state === 'suspended') {
                            await audioContext.resume();
                        }
                        
                        // Create a new audio element for mixing
                        const mixingAudio = new Audio(audioUrl);
                        mixingAudio.muted = true; // Don't play through speakers
                        
                        // Wait for audio to be loaded before creating stream
                        await new Promise((resolve, reject) => {
                            mixingAudio.onloadeddata = resolve;
                            mixingAudio.onerror = reject;
                            mixingAudio.load();
                        });
                        
                        // Create a media stream source from the audio element
                        const audioStream = mixingAudio.captureStream();
                        const ttsAudioSource = audioContext.createMediaStreamSource(audioStream);
                        ttsAudioSource.connect(mixedAudioDestination);
                        
                        // Start playing the audio to capture it
                        await mixingAudio.play();
                        
                        // Clean up when audio finishes
                        mixingAudio.onended = () => {
                            ttsAudioSource.disconnect();
                            URL.revokeObjectURL(audioUrl);
                            console.log('TTS audio mixing completed');
                        };
                        
                        console.log('TTS audio mixed into video recording successfully');
                    } catch (error) {
                        console.error('Error mixing TTS audio:', error);
                        // Fallback: try to play audio normally so it might be captured by microphone
                        console.log('Falling back to normal audio playback for microphone capture');
                    }
                } else {
                    console.log('TTS mixing conditions not met:', {
                        isRecording,
                        hasAudioContext: !!audioContext,
                        hasMixedDestination: !!mixedAudioDestination
                    });
                }
                
                audio.onended = () => {
                    URL.revokeObjectURL(audioUrl);
                };
                audio.onerror = (e) => {
                    console.error('OpenAI TTS error:', e);
                    URL.revokeObjectURL(audioUrl);
                    // Fallback to browser speech synthesis
                    speakWithBrowser(text);
                };
                
                await audio.play();
                
            } catch (error) {
                console.error('OpenAI TTS failed, falling back to browser speech:', error);
                window.openaiTTSEnabled = false; // Disable OpenAI TTS for this session
                speakWithBrowser(text);
            }
        }
        
        function speakWithBrowser(text) {
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 0.9;
                utterance.pitch = 1.0;
                utterance.volume = 1.0;
                
                // Try to find a good voice
                const voices = speechSynthesis.getVoices();
                const preferredVoice = voices.find(voice => 
                    voice.lang.includes('en') && voice.name.includes('Google')
                ) || voices.find(voice => 
                    voice.lang.includes('en')
                ) || voices[0];
                
                if (preferredVoice) {
                    utterance.voice = preferredVoice;
                }
                
                speechSynthesis.speak(utterance);
            } else {
                console.error('Speech synthesis not supported');
            }
        }

        function testSpeech() {
            const testText = "Hello! This is a test of the speech synthesis system. How are you today?";
            speak(testText);
        }

        function changeVoice() {
            const selectedVoice = document.getElementById('voiceSelect').value;
            window.openaiVoice = selectedVoice;
            console.log('Voice changed to:', selectedVoice);
        }

        async function captureDesktopAudio() {
            try {
                // Request desktop capture with audio
                const desktopMedia = await navigator.mediaDevices.getDisplayMedia({
                    video: false,
                    audio: {
                        echoCancellation: false,
                        noiseSuppression: false,
                        autoGainControl: false
                    }
                });
                
                // Extract only the audio tracks
                const audioTracks = desktopMedia.getAudioTracks();
                if (audioTracks.length > 0) {
                    desktopStream = new MediaStream(audioTracks);
                    console.log('Desktop audio captured successfully');
                    return true;
                } else {
                    console.log('No audio tracks found in desktop capture');
                    return false;
                }
            } catch (error) {
                console.error('Error capturing desktop audio:', error);
                return false;
            }
        }

        async function setupAudioMixing() {
            if (!audioContext) {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                mixedAudioDestination = audioContext.createMediaStreamDestination();
            }

            // Connect microphone audio
            if (mediaStream && mediaStream.getAudioTracks().length > 0) {
                microphoneSource = audioContext.createMediaStreamSource(mediaStream);
                microphoneSource.connect(mixedAudioDestination);
                console.log('Microphone audio connected to mixer');
            }

            // Connect desktop audio
            const enableDesktopAudio = document.getElementById('enableDesktopAudio').checked;
            if (enableDesktopAudio && desktopStream && desktopStream.getAudioTracks().length > 0) {
                desktopSource = audioContext.createMediaStreamSource(desktopStream);
                desktopSource.connect(mixedAudioDestination);
                console.log('Desktop audio connected to mixer');
            }
        }

        async function finishInterview() {
            // Stop all recording completely when finishing
            if (isRecording) {
                // Force complete stop for finish
                if (audioRecorder && audioRecorder.state !== 'inactive') {
                    audioRecorder.stop();
                }
                if (videoRecorder && videoRecorder.state !== 'inactive') {
                    videoRecorder.stop();
                }
                
                // Stop media stream
                if (mediaStream) {
                    mediaStream.getTracks().forEach(track => track.stop());
                    mediaStream = null;
                }
                
                // Clean up audio context
                if (audioContext) {
                    if (microphoneSource) {
                        microphoneSource.disconnect();
                        microphoneSource = null;
                    }
                    if (desktopSource) {
                        desktopSource.disconnect();
                        desktopSource = null;
                    }
                    if (ttsSource) {
                        ttsSource.disconnect();
                        ttsSource = null;
                    }
                    audioContext.close();
                    audioContext = null;
                }
                
                // Stop desktop stream
                if (desktopStream) {
                    desktopStream.getTracks().forEach(track => track.stop());
                    desktopStream = null;
                }
                
                // Clear video preview
                const videoPreview = document.getElementById('videoPreview');
                videoPreview.srcObject = null;
                
                isRecording = false;
                recordingStarted = false;
                document.getElementById('startRecording').disabled = false;
                document.getElementById('stopRecording').disabled = true;
                document.querySelector('.recording-indicator').style.display = 'none';
            }
            
            if (currentSessionId) {
                try {
                    const response = await fetch('http://localhost:8000/finish-session', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            session_id: currentSessionId
                        })
                    });
                    
                    const data = await response.json();
                    if (data.success) {
                        updateStatus('Interview finished. Audio and video files have been combined.');
                        addMessage('Interview completed successfully!', 'system');
                    } else {
                        updateStatus('Error finishing interview: ' + data.error);
                    }
                } catch (error) {
                    console.error('Error finishing interview:', error);
                    updateStatus('Error finishing interview. Please try again.');
                }
            } else {
                updateStatus('No active session to finish.');
            }
        }

        async function startAutoRecording() {
            try {
                const enableVideo = document.getElementById('enableVideo').checked;
                const enableAudio = document.getElementById('enableAudio').checked;
                
                if (!enableVideo && !enableAudio) {
                    console.log('No recording enabled, skipping auto-recording');
                    return;
                }

                console.log('Starting automatic recording...');

                // Initialize Web Audio API for mixing audio
                if (enableVideo) {
                    audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    mixedAudioDestination = audioContext.createMediaStreamDestination();
                }

                const constraints = {};
                if (enableAudio) {
                    constraints.audio = {
                        sampleRate: 44100,
                        channelCount: 1,
                        echoCancellation: true,
                        noiseSuppression: true
                    };
                }
                if (enableVideo) {
                    constraints.video = {
                        width: { ideal: 1280 },
                        height: { ideal: 720 },
                        frameRate: { ideal: 30 }
                    };
                }

                mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
                
                // Capture desktop audio if video recording is enabled
                if (enableVideo) {
                    const enableDesktopAudio = document.getElementById('enableDesktopAudio').checked;
                    if (enableDesktopAudio) {
                        await captureDesktopAudio();
                    }
                }
                
                // Set up video preview
                if (enableVideo) {
                    const videoPreview = document.getElementById('videoPreview');
                    videoPreview.srcObject = mediaStream;
                }
                
                // Create separate recorders for audio and video
                if (enableAudio) {
                    const audioStream = new MediaStream(mediaStream.getAudioTracks());
                    const audioMimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') 
                        ? 'audio/webm;codecs=opus' 
                        : 'audio/webm';
                    
                    audioRecorder = new MediaRecorder(audioStream, { mimeType: audioMimeType });
                    
                    audioRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };

                    audioRecorder.onstop = async () => {
                        const audioBlob = new Blob(audioChunks, { type: audioMimeType });
                        const formData = new FormData();
                        formData.append('file', audioBlob, 'recording.webm');
                        
                        if (currentSessionId) {
                            formData.append('session_id', currentSessionId);
                            formData.append('client_id', currentSessionId);
                        }

                        try {
                            const response = await fetch('http://localhost:8000/transcribe', {
                                method: 'POST',
                                body: formData
                            });
                            const data = await response.json();
                            
                            addMessage(data.transcription, 'candidate');
                            
                            if (ws && isConnected) {
                                ws.send(JSON.stringify({
                                    transcription: data.transcription
                                }));
                            }
                        } catch (error) {
                            console.error('Error:', error);
                            updateStatus('Error processing audio. Please try again.');
                        }

                        audioChunks = [];
                        
                        // Restart audio recording immediately for continuous recording
                        if (isRecording && audioRecorder) {
                            audioRecorder.start();
                        }
                    };
                    
                    audioRecorder.start();
                }
                
                if (enableVideo) {
                    // Set up audio mixing for video recording
                    await setupAudioMixing();
                    
                    // Create combined stream with video and mixed audio
                    const videoTracks = mediaStream.getVideoTracks();
                    const mixedAudioTracks = mixedAudioDestination.stream.getAudioTracks();
                    const combinedStream = new MediaStream([...videoTracks, ...mixedAudioTracks]);
                    
                    const videoMimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9,opus') 
                        ? 'video/webm;codecs=vp9,opus' 
                        : MediaRecorder.isTypeSupported('video/webm;codecs=vp8,opus')
                        ? 'video/webm;codecs=vp8,opus'
                        : 'video/webm';
                    
                    videoRecorder = new MediaRecorder(combinedStream, { mimeType: videoMimeType });
                    
                    videoRecorder.ondataavailable = (event) => {
                        videoChunks.push(event.data);
                        // Don't save chunks during recording - only collect them
                        console.log('Video chunk collected, total chunks:', videoChunks.length);
                    };

                    videoRecorder.onstop = async () => {
                        // Only save video when the interview is actually finished
                        // Don't save during continuous recording restarts
                        if (!isRecording) {
                            // Interview is finished, save the complete video
                            if (videoChunks.length > 0) {
                                const videoBlob = new Blob(videoChunks, { type: videoMimeType });
                                const formData = new FormData();
                                formData.append('file', videoBlob, 'recording.webm');
                                
                                if (currentSessionId) {
                                    formData.append('session_id', currentSessionId);
                                    formData.append('client_id', currentSessionId);
                                }

                                try {
                                    const response = await fetch('http://localhost:8000/save-video', {
                                        method: 'POST',
                                        body: formData
                                    });
                                    const data = await response.json();
                                    
                                    if (data.success) {
                                        console.log('Final video saved successfully');
                                        updateStatus('Video saved successfully');
                                    } else {
                                        console.error('Error saving final video:', data.error);
                                        updateStatus('Error saving video: ' + data.error);
                                    }
                                } catch (error) {
                                    console.error('Error saving final video:', error);
                                    updateStatus('Error saving video');
                                }
                            }
                        } else {
                            // This is just a restart for continuous recording, don't save
                            console.log('Video recording restarted for continuous mode, chunks preserved');
                        }
                        
                        // Don't clear chunks during continuous recording
                        if (!isRecording) {
                            videoChunks = [];
                        }
                    };
                    
                    // Set timeslice to 1 second for continuous recording
                    videoRecorder.start(1000);
                }

                isRecording = true;
                recordingStarted = true;
                document.getElementById('startRecording').disabled = true;
                document.getElementById('stopRecording').disabled = false;
                document.querySelector('.recording-indicator').style.display = 'inline-block';
                updateStatus('Recording automatically started...');
                console.log('Automatic recording started successfully');
            } catch (error) {
                console.error('Error starting automatic recording:', error);
                updateStatus('Error starting automatic recording. Please check permissions.');
            }
        }

        // Initialize the application
        document.addEventListener('DOMContentLoaded', function() {
            connectWebSocket();
            
            // Set up recording button event listeners
            document.getElementById('startRecording').addEventListener('click', startRecording);
            document.getElementById('stopRecording').addEventListener('click', stopRecording);
        });
    </script>
</body>
</html>
"""

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode())
        else:
            super().do_GET()

def run_server():
    PORT = 8080
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server() 