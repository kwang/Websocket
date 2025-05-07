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

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Whisper model
model = whisper.load_model("base")

# Store active connections and their conversation states
active_connections = {}
conversation_history = {}

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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = str(datetime.now().timestamp())
    active_connections[client_id] = websocket
    conversation_history[client_id] = []
    
    try:
        # Send initial greeting
        await websocket.send_json({
            "type": "greeting",
            "message": INTERVIEW_QUESTIONS["introduction"]["question"]
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
                
                # Generate follow-up
                current_question = conversation_history[client_id][-2]["content"] if len(conversation_history[client_id]) > 1 else "introduction"
                follow_up = generate_follow_up("introduction", transcription)
                
                # Send follow-up
                await websocket.send_json({
                    "type": "follow_up",
                    "message": follow_up
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

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
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

@app.get("/interview-questions")
async def get_interview_questions():
    return {"questions": [q["question"] for q in INTERVIEW_QUESTIONS.values()]}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True) 