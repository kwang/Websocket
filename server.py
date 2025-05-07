import os
import whisper
import asyncio
from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import tempfile
import json
from datetime import datetime
import base64
import io
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load Whisper model
model = whisper.load_model("base")

# Store active connections and their conversation states
active_connections = {}
conversation_history = {}
used_questions = {}  # Track used questions for each client
current_question_types = {}  # Track current question type for each client

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

def text_to_speech(text):
    """Convert text to speech using OpenAI's TTS API and return as base64 encoded audio"""
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        audio_data = response.content
        return base64.b64encode(audio_data).decode('utf-8')
    except Exception as e:
        print(f"Error in text_to_speech: {e}")
        return None

def generate_follow_up(question_type, response, client_id):
    """Generate a contextual follow-up question based on the candidate's response"""
    if client_id not in used_questions:
        used_questions[client_id] = set()
    
    # Check if the user wants to move to the next question
    if "next question" in response.lower():
        # Move to the next question type
        question_types = list(INTERVIEW_QUESTIONS.keys())
        current_index = question_types.index(question_type)
        next_type = question_types[(current_index + 1) % len(question_types)]
        next_question = INTERVIEW_QUESTIONS[next_type]["question"]
        used_questions[client_id].add(next_question)
        current_question_types[client_id] = next_type
        return next_question
    
    # Check if the response is too short or unclear
    if len(response.split()) < 10:
        return "Could you please elaborate more on that? I'd like to understand your perspective better."
    
    # Get all available follow-ups for this question type
    follow_ups = INTERVIEW_QUESTIONS[question_type]["follow_ups"]
    
    # Filter out already used follow-ups
    available_follow_ups = [q for q in follow_ups if q not in used_questions[client_id]]
    
    # If no more follow-ups available, move to next topic
    if not available_follow_ups:
        # Move to the next question type
        question_types = list(INTERVIEW_QUESTIONS.keys())
        current_index = question_types.index(question_type)
        next_type = question_types[(current_index + 1) % len(question_types)]
        next_question = INTERVIEW_QUESTIONS[next_type]["question"]
        used_questions[client_id].add(next_question)
        current_question_types[client_id] = next_type
        return next_question
    
    # Use the first available follow-up
    follow_up = available_follow_ups[0]
    used_questions[client_id].add(follow_up)
    return follow_up

def analyze_response(response):
    """Analyze the candidate's response and provide feedback"""
    # Simple analysis based on response length and content
    words = response.split()
    if len(words) < 10:
        return {
            "feedback": "Your response was quite brief. Could you provide more details?",
            "next_question": "Let's explore this topic further."
        }
    elif len(words) > 100:
        return {
            "feedback": "Thank you for the detailed response.",
            "next_question": "Let's move on to another aspect."
        }
    else:
        return {
            "feedback": "Thank you for your response.",
            "next_question": "Let's continue with our discussion."
        }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = str(datetime.now().timestamp())
    active_connections[client_id] = websocket
    conversation_history[client_id] = []
    used_questions[client_id] = set()  # Initialize used questions for this client
    current_question_types[client_id] = "introduction"  # Start with introduction
    
    try:
        # Send initial greeting
        greeting = INTERVIEW_QUESTIONS["introduction"]["question"]
        used_questions[client_id].add(greeting)  # Mark initial question as used
        audio_data = text_to_speech(greeting)
        
        await websocket.send_json({
            "type": "greeting",
            "message": greeting,
            "audio": audio_data
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
                
                # Generate follow-up using current question type
                current_type = current_question_types[client_id]
                follow_up = generate_follow_up(current_type, transcription, client_id)
                
                # Convert follow-up to speech
                audio_data = text_to_speech(follow_up)
                
                # Send follow-up
                await websocket.send_json({
                    "type": "follow_up",
                    "message": follow_up,
                    "audio": audio_data
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
        if client_id in used_questions:
            del used_questions[client_id]
        if client_id in current_question_types:
            del current_question_types[client_id]

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            # Transcribe using Whisper
            result = model.transcribe(temp_file.name)
            
            # Clean up
            os.unlink(temp_file.name)
            
            return {"transcription": result["text"]}
    except Exception as e:
        print(f"Transcription error: {e}")
        return {"error": str(e)}

@app.get("/interview-questions")
async def get_interview_questions():
    return {"questions": [q["question"] for q in INTERVIEW_QUESTIONS.values()]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 