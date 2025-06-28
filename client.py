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
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .conversation {
            margin: 20px 0;
            max-height: 400px;
            overflow-y: auto;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 4px;
        }
        .interviewer {
            background-color: #e9ecef;
            margin-right: 20%;
        }
        .candidate {
            background-color: #007bff;
            color: white;
            margin-left: 20%;
        }
        .controls {
            margin: 20px 0;
            display: flex;
            gap: 10px;
        }
        button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            flex: 1;
        }
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        button:hover:not(:disabled) {
            background-color: #0056b3;
        }
        .status {
            margin: 10px 0;
            padding: 10px;
            border-radius: 4px;
            background-color: #f8f9fa;
        }
        .session-info {
            background-color: #e3f2fd;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
        .recordings-list {
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
        }
        .recording-item {
            padding: 10px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
        }
        .recording-item:hover {
            background-color: #f5f5f5;
        }
        .recording-item:last-child {
            border-bottom: none;
        }
        .tabs {
            display: flex;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            cursor: pointer;
            border-radius: 4px 4px 0 0;
        }
        .tab.active {
            background-color: white;
            border-bottom: 1px solid white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .control-group {
            margin-bottom: 10px;
        }
        .control-group label {
            display: block;
            margin-bottom: 5px;
        }
        .control-group select {
            width: 100%;
            padding: 5px;
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
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
            
            if (tabName === 'recordings') {
                loadRecordings();
            }
        }

        function addMessage(content, role) {
            const conversation = document.getElementById('conversation');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            messageDiv.textContent = content;
            conversation.appendChild(messageDiv);
            conversation.scrollTop = conversation.scrollHeight;
        }

        function updateStatus(message) {
            document.getElementById('status').textContent = message;
        }

        async function loadRecordings() {
            try {
                const response = await fetch('http://localhost:8000/recordings');
                const data = await response.json();
                
                const recordingsList = document.getElementById('recordingsList');
                recordingsList.innerHTML = '';
                
                if (data.recordings.length === 0) {
                    recordingsList.innerHTML = '<p>No recordings found.</p>';
                    return;
                }
                
                data.recordings.forEach(recording => {
                    const item = document.createElement('div');
                    item.className = 'recording-item';
                    
                    // Get detailed info for this session
                    fetch(`http://localhost:8000/recordings/${recording.session_id}`)
                        .then(response => response.json())
                        .then(sessionData => {
                            if (!sessionData.error) {
                                let combinedAudioInfo = '';
                                if (sessionData.combined_audio) {
                                    combinedAudioInfo = `<br><strong>🎵 Combined:</strong> ${sessionData.combined_audio}`;
                                }
                                
                                item.innerHTML = `
                                    <strong>Session:</strong> ${recording.session_id}<br>
                                    <strong>Interviewer:</strong> ${sessionData.interviewer_files.length} files<br>
                                    <strong>Candidate:</strong> ${sessionData.candidate_files.length} files${combinedAudioInfo}<br>
                                    <strong>Total:</strong> ${sessionData.audio_files.length + sessionData.metadata_files.length} files
                                `;
                            } else {
                                item.innerHTML = `
                                    <strong>Session:</strong> ${recording.session_id}<br>
                                    <strong>Audio Files:</strong> ${recording.audio_files.length}<br>
                                    <strong>Metadata Files:</strong> ${recording.metadata_files.length}
                                `;
                            }
                        })
                        .catch(() => {
                            item.innerHTML = `
                                <strong>Session:</strong> ${recording.session_id}<br>
                                <strong>Audio Files:</strong> ${recording.audio_files.length}<br>
                                <strong>Metadata Files:</strong> ${recording.metadata_files.length}
                            `;
                        });
                    
                    item.onclick = () => showSessionDetails(recording.session_id);
                    recordingsList.appendChild(item);
                });
            } catch (error) {
                console.error('Error loading recordings:', error);
                document.getElementById('recordingsList').innerHTML = '<p>Error loading recordings.</p>';
            }
        }

        async function showSessionDetails(sessionId) {
            try {
                const response = await fetch(`http://localhost:8000/recordings/${sessionId}`);
                const data = await response.json();
                
                if (data.error) {
                    alert('Session not found');
                    return;
                }
                
                let details = `<h3>Session: ${sessionId}</h3>`;
                details += `<p><strong>Total Files:</strong> ${data.audio_files.length + data.metadata_files.length}</p>`;
                
                if (data.combined_audio) {
                    details += `<h4>🎵 Combined Audio:</h4>`;
                    details += `<p><strong>${data.combined_audio}</strong> (Complete interview)</p>`;
                }
                
                if (data.interviewer_files.length > 0) {
                    details += `<h4>Interviewer Speech (${data.interviewer_files.length} files):</h4>`;
                    data.interviewer_files.forEach(audio => {
                        details += `<p>🎤 ${audio}</p>`;
                    });
                }
                
                if (data.candidate_files.length > 0) {
                    details += `<h4>Candidate Responses (${data.candidate_files.length} files):</h4>`;
                    data.candidate_files.forEach(audio => {
                        details += `<p>🎙️ ${audio}</p>`;
                    });
                }
                
                if (data.metadata_files.length > 0) {
                    details += `<h4>Metadata Files (${data.metadata_files.length} files):</h4>`;
                    data.metadata_files.forEach(meta => {
                        details += `<p>📄 ${meta}</p>`;
                    });
                }
                
                alert(details);
            } catch (error) {
                console.error('Error loading session details:', error);
                alert('Error loading session details');
            }
        }

        async function connectWebSocket() {
            try {
                ws = new WebSocket('ws://localhost:8000/ws');
                
                ws.onopen = function() {
                    isConnected = true;
                    updateStatus('Connected to server');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    if (data.type === 'greeting' || data.type === 'follow_up') {
                        addMessage(data.message, 'interviewer');
                        
                        // Ensure voices are loaded before speaking
                        if (window.speechSynthesis.getVoices().length === 0) {
                            window.speechSynthesis.onvoiceschanged = () => {
                                speak(data.message);
                            };
                        } else {
                            speak(data.message);
                        }
                        
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
                        
                        if (data.error) {
                            console.error('Transcription error:', data.error);
                            updateStatus('Error: ' + data.error);
                            return;
                        }
                        
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
            
            // Always try OpenAI TTS first for interviews
            speakWithOpenAI(testText).then(() => {
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