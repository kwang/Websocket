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
            <div class="status" id="status">Connecting to server...</div>
            <div class="conversation" id="conversation"></div>
            <div class="controls">
                <button id="startRecording">Start Recording</button>
                <button id="stopRecording" disabled>Stop Recording</button>
                <button id="testSpeech" onclick="testSpeech()">Test Speech</button>
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
        </div>
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        let ws;
        let isConnected = false;
        let currentSessionId = null;

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
                                <p>Files: ${recording.audio_files.length} audio, ${recording.metadata_files.length} metadata</p>
                                ${recording.combined_audio ? `<p><strong>Combined Audio Available</strong></p>` : ''}
                            </div>
                            <div class="recording-actions">
                                <button onclick="viewSessionDetails('${recording.session_id}')" class="btn btn-primary">View Details</button>
                                ${recording.combined_audio ? `<button onclick="playCombinedAudio('${recording.session_id}', '${recording.combined_audio}')" class="btn btn-success">Play Combined</button>` : ''}
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

        async function viewSessionDetails(sessionId) {
            try {
                const response = await fetch(`http://localhost:8000/recordings/${sessionId}`);
                const data = await response.json();
                
                if (data.error) {
                    alert('Error loading session details: ' + data.error);
                    return;
                }
                
                const detailsDiv = document.getElementById('sessionDetails');
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
                    
                    ${data.combined_audio ? `
                        <div class="audio-section">
                            <h3>Combined Audio</h3>
                            <div class="audio-item">
                                <span>${data.combined_audio}</span>
                                <button onclick="playAudio('${sessionId}', '${data.combined_audio.replace(/'/g, "\\'")}')" class="btn btn-sm btn-success">Play Combined</button>
                            </div>
                        </div>
                    ` : ''}
                    
                    <div class="metadata-section">
                        <h3>Metadata Files</h3>
                        ${data.metadata_files.length > 0 ? 
                            data.metadata_files.map(file => `<p>${file}</p>`).join('') : '<p>No metadata files</p>'
                        }
                    </div>
                    
                    <button onclick="showTab('recordings')" class="btn btn-secondary">Back to Recordings</button>
                `;
                
                showTab('sessionDetails');
            } catch (error) {
                console.error('Error loading session details:', error);
                alert('Error loading session details.');
            }
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
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        sampleRate: 44100,
                        channelCount: 1,
                        echoCancellation: true,
                        noiseSuppression: true
                    }
                });
                
                // Use the correct MIME type that MediaRecorder supports
                const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') 
                    ? 'audio/webm;codecs=opus' 
                    : 'audio/webm';
                
                mediaRecorder = new MediaRecorder(stream, { mimeType });
                
                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = async () => {
                    // Create blob with the correct MIME type
                    const audioBlob = new Blob(audioChunks, { type: mimeType });
                    const formData = new FormData();
                    formData.append('file', audioBlob, 'recording.webm');
                    
                    // Add both client_id and session_id if available
                    if (currentSessionId) {
                        formData.append('session_id', currentSessionId);
                        // Also send as client_id for backward compatibility
                        formData.append('client_id', currentSessionId);
                    }

                    try {
                        const response = await fetch('http://localhost:8000/transcribe', {
                            method: 'POST',
                            body: formData
                        });
                        const data = await response.json();
                        
                        // Add the transcription to the conversation
                        addMessage(data.transcription, 'candidate');
                        
                        // Send the transcription to the WebSocket server
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

                mediaRecorder.start();
                document.getElementById('startRecording').disabled = true;
                document.getElementById('stopRecording').disabled = false;
                updateStatus('Recording...');
            } catch (error) {
                console.error('Error accessing microphone:', error);
                updateStatus('Error accessing microphone. Please check permissions.');
            }
        }

        function stopRecording() {
            mediaRecorder.stop();
            document.getElementById('startRecording').disabled = false;
            document.getElementById('stopRecording').disabled = true;
            updateStatus('Processing your response...');
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
                // Cancel any ongoing speech
                window.speechSynthesis.cancel();
                
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'en-US';
                utterance.rate = 0.9; // Slightly slower for clarity
                utterance.pitch = 1.0;
                utterance.volume = 1.0;
                
                // Try to select a good voice
                const voices = window.speechSynthesis.getVoices();
                const preferredVoice = voices.find(voice => 
                    voice.lang.startsWith('en') && 
                    (voice.name.includes('Female') || voice.name.includes('Samantha') || voice.name.includes('Alex'))
                );
                if (preferredVoice) {
                    utterance.voice = preferredVoice;
                }
                
                utterance.onstart = () => {
                    console.log('Speaking:', text);
                };
                
                utterance.onend = () => {
                    console.log('Finished speaking');
                };
                
                utterance.onerror = (event) => {
                    console.error('Speech synthesis error:', event);
                };
                
                window.speechSynthesis.speak(utterance);
            } else {
                console.error('Speech synthesis not supported');
            }
        }

        function testSpeech() {
            const testText = "Hello! I'm your AI interviewer. This is a test of the OpenAI text-to-speech system.";
            updateStatus('Testing OpenAI TTS...');
            
            // Get the currently selected voice from the dropdown
            const selectedVoice = document.getElementById('voiceSelect')?.value || 'alloy';
            
            // Always try OpenAI TTS first for interviews
            speakWithOpenAI(testText, selectedVoice).then(() => {
                updateStatus('OpenAI TTS test completed successfully!');
            }).catch((error) => {
                console.error('OpenAI TTS test failed:', error);
                updateStatus('OpenAI TTS failed, testing browser speech synthesis...');
                speakWithBrowser(testText);
            });
        }

        function changeVoice() {
            const voiceSelect = document.getElementById('voiceSelect');
            const selectedVoice = voiceSelect.value;
            
            // Update the voice setting
            window.openaiVoice = selectedVoice;
            
            // Test the new voice
            const testText = `Voice changed to ${selectedVoice}. This is how I will sound for your interview.`;
            updateStatus(`Testing new voice: ${selectedVoice}...`);
            
            speakWithOpenAI(testText, selectedVoice).then(() => {
                updateStatus(`Voice changed to ${selectedVoice} successfully!`);
            }).catch((error) => {
                console.error('Voice change test failed:', error);
                updateStatus('Voice change failed, using default voice');
            });
        }

        document.getElementById('startRecording').addEventListener('click', startRecording);
        document.getElementById('stopRecording').addEventListener('click', stopRecording);

        // Initialize
        connectWebSocket();
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