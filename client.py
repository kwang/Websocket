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
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Interview Agent</h1>
        <div class="status" id="status">Connecting to server...</div>
        <div class="conversation" id="conversation"></div>
        <div class="controls">
            <button id="startRecording">Start Recording</button>
            <button id="stopRecording" disabled>Stop Recording</button>
        </div>
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        let ws;
        let isConnected = false;
        let audioContext;

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

        async function playAudio(base64Audio) {
            try {
                // Convert base64 to ArrayBuffer
                const binaryString = window.atob(base64Audio);
                const len = binaryString.length;
                const bytes = new Uint8Array(len);
                for (let i = 0; i < len; i++) {
                    bytes[i] = binaryString.charCodeAt(i);
                }

                // Create audio context if it doesn't exist
                if (!audioContext) {
                    audioContext = new (window.AudioContext || window.webkitAudioContext)();
                }

                // Decode and play the audio
                const audioBuffer = await audioContext.decodeAudioData(bytes.buffer);
                const source = audioContext.createBufferSource();
                source.buffer = audioBuffer;
                source.connect(audioContext.destination);
                source.start(0);
            } catch (error) {
                console.error('Error playing audio:', error);
            }
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
                        if (data.audio) {
                            await playAudio(data.audio);
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
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                
                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const formData = new FormData();
                    formData.append('file', audioBlob);

                    try {
                        const response = await fetch('http://localhost:8000/transcribe', {
                            method: 'POST',
                            body: formData
                        });
                        const data = await response.json();
                        
                        if (data.error) {
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