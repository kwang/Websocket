import os
import whisper
import asyncio
from fastapi import FastAPI, WebSocket, UploadFile, File, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import tempfile
import json
from datetime import datetime
import aiofiles
from pathlib import Path
import subprocess
from config import *
import openai

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create recordings directory
RECORDINGS_DIR.mkdir(exist_ok=True)

# Load Whisper model
model = whisper.load_model(WHISPER_MODEL)

# Initialize OpenAI client if API key is available
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
    print("✅ OpenAI API initialized")
else:
    print("⚠️  OpenAI API key not found. Using fallback interview questions.")

def convert_webm_to_wav(input_path: str, output_path: str):
    """Convert WebM audio to WAV format using ffmpeg"""
    try:
        # Check if ffmpeg is available
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Warning: ffmpeg not found. Audio conversion skipped.")
            return False
        
        # Convert WebM to WAV
        cmd = [
            'ffmpeg', '-i', input_path,
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            '-ac', '1',
            '-y',  # Overwrite output file
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully converted {input_path} to {output_path}")
            return True
        else:
            print(f"Error converting audio: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error during audio conversion: {e}")
        return False

def convert_to_mp3(input_path: str, output_path: str):
    """Convert any audio format to MP3 using ffmpeg"""
    try:
        # Check if ffmpeg is available
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Warning: ffmpeg not found. Audio conversion skipped.")
            return False
        
        # Convert to MP3
        cmd = [
            'ffmpeg', '-i', input_path,
            '-acodec', 'mp3',
            '-ab', '128k',  # 128 kbps bitrate
            '-ar', '44100',
            '-ac', '1',
            '-y',  # Overwrite output file
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully converted {input_path} to {output_path}")
            return True
        else:
            print(f"Error converting audio: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error during audio conversion: {e}")
        return False

def combine_audio_files(session_dir: Path, output_filename: str = None):
    """Combine all audio files in a session directory into a single MP3 file"""
    if output_filename is None:
        output_filename = COMBINED_AUDIO_FILENAME
    
    try:
        # Check if ffmpeg is available
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Warning: ffmpeg not found. Audio combining skipped.")
            return False
        
        # Get all audio files in the session directory
        audio_files = []
        for file in session_dir.iterdir():
            if file.suffix.lower() in ['.mp3', '.wav', '.webm', '.m4a']:
                audio_files.append(str(file))
        
        if not audio_files:
            print("No audio files found to combine")
            return False
        
        # Sort files by timestamp (assuming they have timestamps in filenames)
        audio_files.sort()
        
        # Create a file list for ffmpeg
        file_list_path = session_dir / "file_list.txt"
        with open(file_list_path, 'w') as f:
            for audio_file in audio_files:
                f.write(f"file '{audio_file}'\n")
        
        # Combine audio files
        output_path = session_dir / output_filename
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(file_list_path),
            '-c', 'copy',
            '-y',  # Overwrite output file
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up file list
        if file_list_path.exists():
            file_list_path.unlink()
        
        if result.returncode == 0:
            print(f"Successfully combined audio files into {output_path}")
            return True
        else:
            print(f"Error combining audio files: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error during audio combining: {e}")
        return False

# Store active connections and their conversation states
active_connections = {}
conversation_history = {}
interview_sessions = {}

# Interview questions and follow-up prompts
INTERVIEW_QUESTIONS = {
    "introduction": {
        "question": "Hello! I'm your AI interviewer today. Could you please introduce yourself?",
        "follow_ups": [
            "That's interesting! Could you tell me more about your background?",
            "What made you interested in this field?",
            "What are your main career goals?"
        ]
    },
    "experience": {
        "question": "Could you tell me about your relevant experience?",
        "follow_ups": [
            "What was your most challenging project?",
            "How did you handle difficult situations in your previous roles?",
            "What skills did you develop from these experiences?"
        ]
    },
    "skills": {
        "question": "What are your key technical skills?",
        "follow_ups": [
            "How do you stay updated with new technologies?",
            "Can you give an example of how you applied these skills?",
            "What areas are you looking to improve?"
        ]
    },
    "problem_solving": {
        "question": "How do you approach problem-solving in your work?",
        "follow_ups": [
            "Can you share a specific example?",
            "What was the outcome?",
            "What did you learn from that experience?"
        ]
    },
    "future": {
        "question": "Where do you see yourself in the next 5 years?",
        "follow_ups": [
            "What steps are you taking to achieve these goals?",
            "How does this role align with your career path?",
            "What are you most excited about in your career?"
        ]
    }
}

async def generate_openai_response(conversation_history: list, candidate_response: str = None):
    """Generate interview response using OpenAI Chat API"""
    if not OPENAI_API_KEY:
        return None
    
    try:
        # Build the conversation context
        messages = [
            {
                "role": "system",
                "content": """You are a professional AI interviewer conducting a job interview. Your role is to:
1. Ask relevant, contextual questions based on the candidate's responses
2. Provide natural, conversational follow-up questions
3. Keep responses concise (1-2 sentences)
4. Be professional but friendly
5. Adapt your questions based on the candidate's background and responses
6. Focus on understanding the candidate's experience, skills, and fit for the role

Start with an introduction if this is the first interaction."""
            }
        ]
        
        # Add conversation history
        for msg in conversation_history:
            if msg["role"] == "interviewer":
                messages.append({"role": "assistant", "content": msg["content"]})
            elif msg["role"] == "candidate":
                messages.append({"role": "user", "content": msg["content"]})
        
        # Add current candidate response if provided
        if candidate_response:
            messages.append({"role": "user", "content": candidate_response})
        
        # Generate response using new OpenAI API format
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=OPENAI_MAX_TOKENS,
            temperature=OPENAI_TEMPERATURE
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Error generating OpenAI response: {e}")
        return None

def generate_follow_up(question_type, response):
    """Generate a contextual follow-up question based on the candidate's response"""
    follow_ups = INTERVIEW_QUESTIONS[question_type]["follow_ups"]
    # For now, we'll just cycle through follow-ups
    # In a real implementation, this could use NLP to generate contextual follow-ups
    return follow_ups[0]

def analyze_response(response):
    """Analyze the candidate's response and provide feedback"""
    # This is a simple implementation
    # In a real system, this could use NLP to analyze response quality
    return {
        "feedback": "Thank you for your response.",
        "next_question": "Let's move on to the next topic."
    }

async def save_audio_file(client_id: str, audio_data: bytes, session_info: dict):
    """Save audio file with metadata"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = session_info.get("session_id", client_id)
    
    # Create session directory
    session_dir = RECORDINGS_DIR / session_id
    session_dir.mkdir(exist_ok=True)
    
    # Save audio file
    audio_filename = AUDIO_FILENAME_PATTERN.format(timestamp=timestamp, ext=AUDIO_FORMAT)
    audio_path = session_dir / audio_filename
    
    async with aiofiles.open(audio_path, 'wb') as f:
        await f.write(audio_data)
    
    # Calculate file size
    file_size = len(audio_data)
    
    # Save metadata
    metadata = {
        "timestamp": timestamp,
        "audio_file": audio_filename,
        "session_id": session_id,
        "client_id": client_id,
        "interview_question": session_info.get("current_question", "Unknown"),
        "response_number": session_info.get("response_count", 0),
        "file_size_bytes": file_size,
        "file_size_mb": round(file_size / (1024 * 1024), 2),
        "audio_format": AUDIO_FORMAT,
        "audio_quality": AUDIO_QUALITY,
        "whisper_model": WHISPER_MODEL
    }
    
    # Add transcription if enabled
    if SAVE_TRANSCRIPTION and "transcription" in session_info:
        metadata["transcription"] = session_info["transcription"]
    
    metadata_filename = METADATA_FILENAME_PATTERN.format(timestamp=timestamp)
    metadata_path = session_dir / metadata_filename
    
    async with aiofiles.open(metadata_path, 'w') as f:
        await f.write(json.dumps(metadata, indent=2))
    
    return str(audio_path), metadata

def create_session_info(client_id: str):
    """Create a new interview session"""
    session_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{client_id[-6:]}"
    return {
        "session_id": session_id,
        "start_time": datetime.now().isoformat(),
        "current_question": "introduction",
        "response_count": 0,
        "audio_files": []
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = str(datetime.now().timestamp())
    active_connections[client_id] = websocket
    conversation_history[client_id] = []
    interview_sessions[client_id] = create_session_info(client_id)
    session_id = interview_sessions[client_id]["session_id"]
    
    try:
        # Generate initial greeting using OpenAI or fallback
        if USE_OPENAI_FOR_INTERVIEW and OPENAI_API_KEY:
            initial_message = await generate_openai_response(conversation_history[client_id])
            if not initial_message:
                initial_message = INTERVIEW_QUESTIONS["introduction"]["question"]
        else:
            initial_message = INTERVIEW_QUESTIONS["introduction"]["question"]
        
        # Send initial greeting
        await websocket.send_json({
            "type": "greeting",
            "message": initial_message,
            "session_id": session_id
        })
        
        # Add to conversation history
        conversation_history[client_id].append({
            "role": "interviewer",
            "content": initial_message
        })
        
        while True:
            data = await websocket.receive_text()
            response_data = json.loads(data)
            
            # Process the response
            if "transcription" in response_data:
                transcription = response_data["transcription"]
                conversation_history[client_id].append({
                    "role": "candidate",
                    "content": transcription
                })
                
                # Update session info
                interview_sessions[client_id]["response_count"] += 1
                
                # Generate follow-up using OpenAI or fallback
                if USE_OPENAI_FOR_INTERVIEW and OPENAI_API_KEY:
                    follow_up = await generate_openai_response(conversation_history[client_id], transcription)
                    if not follow_up:
                        # Fallback to predefined questions
                        current_question = conversation_history[client_id][-2]["content"] if len(conversation_history[client_id]) > 1 else "introduction"
                        follow_up = generate_follow_up("introduction", transcription)
                else:
                    # Use fallback questions
                    current_question = conversation_history[client_id][-2]["content"] if len(conversation_history[client_id]) > 1 else "introduction"
                    follow_up = generate_follow_up("introduction", transcription)
                
                # Send follow-up
                await websocket.send_json({
                    "type": "follow_up",
                    "message": follow_up,
                    "session_id": session_id
                })
                
                conversation_history[client_id].append({
                    "role": "interviewer",
                    "content": follow_up
                })
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if client_id in active_connections:
            del active_connections[client_id]
        if client_id in conversation_history:
            del conversation_history[client_id]
        if client_id in interview_sessions:
            del interview_sessions[client_id]

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...), client_id: str = Form(None), session_id: str = Form(None)):
    # Check file size
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    
    if file_size_mb > MAX_RECORDING_SIZE_MB:
        return {"error": f"File too large. Maximum size is {MAX_RECORDING_SIZE_MB}MB"}
    
    # Determine file extension based on content type and filename
    file_extension = "webm"  # Default for MediaRecorder
    if file.content_type:
        if "webm" in file.content_type:
            file_extension = "webm"
        elif "wav" in file.content_type:
            file_extension = "wav"
        elif "mp4" in file.content_type:
            file_extension = "mp4"
    
    # Also check filename for extension
    if file.filename:
        if file.filename.endswith('.webm'):
            file_extension = "webm"
        elif file.filename.endswith('.wav'):
            file_extension = "wav"
        elif file.filename.endswith('.mp4'):
            file_extension = "mp4"
    
    print(f"Detected file type: {file_extension}, content_type: {file.content_type}, filename: {file.filename}")
    
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
        temp_file.write(content)
        temp_file.flush()
        temp_file_path = temp_file.name
        
        try:
            # Convert to WAV if needed
            wav_file_path = None
            if file_extension != "wav":
                wav_file_path = temp_file_path.replace(f".{file_extension}", ".wav")
                print(f"Converting {temp_file_path} to {wav_file_path}")
                if convert_webm_to_wav(temp_file_path, wav_file_path):
                    # Use the converted WAV file for transcription
                    transcription_file = wav_file_path
                    print(f"Using converted WAV file: {transcription_file}")
                else:
                    # Fall back to original file
                    transcription_file = temp_file_path
                    print(f"Conversion failed, using original file: {transcription_file}")
            else:
                transcription_file = temp_file_path
                print(f"Using original WAV file: {transcription_file}")
            
            # Transcribe using Whisper
            result = model.transcribe(transcription_file)
            transcription = result["text"]
            print(f"Transcription: {transcription}")
            
        except Exception as e:
            # Clean up temp files
            os.unlink(temp_file_path)
            if wav_file_path and os.path.exists(wav_file_path):
                os.unlink(wav_file_path)
            return {"error": f"Failed to transcribe audio: {str(e)}"}
        
        # Find the session to save to
        target_session = None
        target_client_id = None
        
        if session_id:
            # Look for session by session_id
            for client_key, session_info in interview_sessions.items():
                if session_info.get("session_id") == session_id:
                    target_session = session_info
                    target_client_id = client_key
                    break
        elif client_id:
            # Look for session by client_id
            if client_id in interview_sessions:
                target_session = interview_sessions[client_id]
                target_client_id = client_id
            else:
                # Try to find by session_id if client_id looks like a session_id
                for client_key, session_info in interview_sessions.items():
                    if session_info.get("session_id") == client_id:
                        target_session = session_info
                        target_client_id = client_key
                        break
        
        # Save audio file if session found
        if target_session:
            try:
                target_session["transcription"] = transcription
                
                # Convert to MP3 for saving
                mp3_file_path = temp_file_path.replace(f".{file_extension}", ".mp3")
                if convert_to_mp3(temp_file_path, mp3_file_path):
                    # Save the converted MP3 file
                    with open(mp3_file_path, 'rb') as mp3_file:
                        mp3_content = mp3_file.read()
                    audio_path, metadata = await save_audio_file(target_client_id or client_id or "unknown", mp3_content, target_session)
                    print(f"Saved converted MP3 file: {audio_path}")
                    
                    # Clean up MP3 temp file
                    if os.path.exists(mp3_file_path):
                        os.unlink(mp3_file_path)
                else:
                    # Fall back to original file
                    audio_path, metadata = await save_audio_file(target_client_id or client_id or "unknown", content, target_session)
                    print(f"Saved original file: {audio_path}")
                
                target_session["audio_files"].append(metadata)
                print(f"Audio saved successfully for session: {target_session['session_id']}")
                
                # Create combined audio file
                session_dir = RECORDINGS_DIR / target_session['session_id']
                if CREATE_COMBINED_AUDIO:
                    combine_audio_files(session_dir)
                    
            except Exception as e:
                print(f"Error saving audio file: {e}")
                # Continue even if saving fails
        else:
            print(f"No active session found for client_id: {client_id}, session_id: {session_id}")
            print(f"Available sessions: {list(interview_sessions.keys())}")
        
        # Clean up temp files
        os.unlink(temp_file_path)
        if wav_file_path and os.path.exists(wav_file_path):
            os.unlink(wav_file_path)
        
        return {"transcription": transcription}

@app.get("/recordings")
async def list_recordings():
    """List all interview recordings"""
    recordings = []
    for session_dir in RECORDINGS_DIR.iterdir():
        if session_dir.is_dir():
            session_info = {
                "session_id": session_dir.name,
                "audio_files": [],
                "metadata_files": [],
                "interviewer_files": [],
                "candidate_files": [],
                "combined_audio": None
            }
            
            for file_path in session_dir.iterdir():
                if file_path.suffix == ".mp3":
                    if file_path.name.startswith('interviewer_'):
                        session_info["interviewer_files"].append(file_path.name)
                    elif file_path.name == COMBINED_AUDIO_FILENAME:
                        session_info["combined_audio"] = file_path.name
                    else:
                        session_info["candidate_files"].append(file_path.name)
                    session_info["audio_files"].append(file_path.name)
                elif file_path.suffix == ".wav":
                    session_info["candidate_files"].append(file_path.name)
                    session_info["audio_files"].append(file_path.name)
                elif file_path.suffix == ".json":
                    session_info["metadata_files"].append(file_path.name)
            
            recordings.append(session_info)
    
    return {"recordings": recordings}

@app.get("/recordings/{session_id}")
async def get_session_recordings(session_id: str):
    """Get recordings for a specific session"""
    session_dir = RECORDINGS_DIR / session_id
    if not session_dir.exists():
        return {"error": "Session not found"}
    
    audio_files = []
    metadata_files = []
    interviewer_files = []
    candidate_files = []
    combined_audio = None
    
    for file in session_dir.iterdir():
        if file.suffix == '.mp3':
            if file.name.startswith('interviewer_'):
                interviewer_files.append(file.name)
            elif file.name == COMBINED_AUDIO_FILENAME:
                combined_audio = file.name
            else:
                candidate_files.append(file.name)
            audio_files.append(file.name)
        elif file.suffix == '.wav':
            candidate_files.append(file.name)
            audio_files.append(file.name)
        elif file.suffix == '.json':
            metadata_files.append(file.name)
    
    return {
        "session_id": session_id,
        "audio_files": sorted(audio_files),
        "metadata_files": sorted(metadata_files),
        "interviewer_files": sorted(interviewer_files),
        "candidate_files": sorted(candidate_files),
        "combined_audio": combined_audio
    }

@app.get("/interview-questions")
async def get_interview_questions():
    return {"questions": [q["question"] for q in INTERVIEW_QUESTIONS.values()]}

@app.post("/tts")
async def text_to_speech(text: str = Form(...), voice: str = Form(None), session_id: str = Form(None)):
    """Convert text to speech using OpenAI TTS and optionally save it"""
    if not USE_OPENAI_TTS or not OPENAI_API_KEY:
        return {"error": "OpenAI TTS not enabled or API key not configured"}
    
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Use the provided voice or default to config setting
        selected_voice = voice if voice else OPENAI_TTS_VOICE
        
        # Generate speech
        response = client.audio.speech.create(
            model=OPENAI_TTS_MODEL,
            voice=selected_voice,
            input=text
        )
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        response.stream_to_file(temp_file.name)
        
        # Read the file content
        with open(temp_file.name, "rb") as f:
            audio_content = f.read()
        
        # Save interviewer speech if session_id is provided
        if session_id:
            try:
                session_dir = RECORDINGS_DIR / session_id
                session_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate timestamp for the interviewer speech
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                interviewer_filename = f"interviewer_{timestamp}.mp3"
                interviewer_path = session_dir / interviewer_filename
                
                # Save the interviewer speech
                with open(interviewer_path, "wb") as f:
                    f.write(audio_content)
                
                # Save metadata for the interviewer speech
                metadata = {
                    "type": "interviewer_speech",
                    "timestamp": timestamp,
                    "text": text,
                    "voice": selected_voice,
                    "model": OPENAI_TTS_MODEL,
                    "filename": interviewer_filename,
                    "file_size": len(audio_content)
                }
                
                metadata_filename = f"interviewer_metadata_{timestamp}.json"
                metadata_path = session_dir / metadata_filename
                
                async with aiofiles.open(metadata_path, 'w') as f:
                    await f.write(json.dumps(metadata, indent=2))
                
                print(f"Saved interviewer speech: {interviewer_path}")
                
                # Create combined audio file
                if CREATE_COMBINED_AUDIO:
                    combine_audio_files(session_dir)
                
            except Exception as e:
                print(f"Error saving interviewer speech: {e}")
        
        # Clean up temp file
        os.unlink(temp_file.name)
        
        return Response(
            content=audio_content,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
        
    except Exception as e:
        print(f"Error generating TTS: {e}")
        return {"error": f"TTS generation failed: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run("server:app", host=HOST, port=PORT, reload=DEBUG) 