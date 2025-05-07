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
client = OpenAI()  # Will use OPENAI_API_KEY from environment variable

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
            "What was your most challenging project?",
            "How did you handle difficult situations in your previous roles?",
            "What skills did you develop from these experiences?"
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

# Add response caching
response_cache = {}
MAX_CACHE_SIZE = 100

def get_cached_response(key):
    """Get a cached response if available"""
    return response_cache.get(key)

def cache_response(key, response):
    """Cache a response, maintaining max cache size"""
    if len(response_cache) >= MAX_CACHE_SIZE:
        # Remove oldest item
        response_cache.pop(next(iter(response_cache)))
    response_cache[key] = response

def text_to_speech(text):
    """Convert text to speech using OpenAI's TTS API and return as base64 encoded audio"""
    # Check cache first
    cache_key = f"tts_{text}"
    cached = get_cached_response(cache_key)
    if cached:
        return cached

    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        audio_data = base64.b64encode(response.content).decode('utf-8')
        cache_response(cache_key, audio_data)
        return audio_data
    except Exception as e:
        print(f"Error in text_to_speech: {e}")
        return None

def generate_initial_greeting():
    """Generate a unique greeting using OpenAI"""
    cache_key = "greeting"
    cached = get_cached_response(cache_key)
    if cached:
        return cached

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """You are a friendly and professional AI interviewer. Generate a brief greeting that:
                1. Introduces yourself in one sentence
                2. Asks a simple question
                Keep it under 3 sentences total."""},
                {"role": "user", "content": "Generate a brief, friendly greeting to start an interview."}
            ],
            temperature=0.7,
            max_tokens=50
        )
        greeting = response.choices[0].message.content
        cache_response(cache_key, greeting)
        return greeting
    except Exception as e:
        print(f"Error generating greeting: {e}")
        return "Hi! I'm your AI interviewer. Could you tell me about yourself?"

def generate_follow_up(question_type, response, client_id):
    """Generate a contextual follow-up question based on the candidate's response"""
    if client_id not in used_questions:
        used_questions[client_id] = set()
    
    # Generate a summary of the response
    try:
        # Check cache for similar responses
        cache_key = f"summary_{response[:100]}"  # Use first 100 chars as key
        cached = get_cached_response(cache_key)
        if cached:
            summary = cached
        else:
            summary_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """You are a friendly and professional AI interviewer. Summarize what the person said in one sentence, using 'You' instead of 'The candidate'. 
                    Make your summary:
                    1. Brief and to the point
                    2. Focus on key points only
                    3. Use natural language
                    Keep it to one sentence."""},
                    {"role": "user", "content": f"Person's response: {response}\nProvide a brief summary."}
                ],
                temperature=0.7,
                max_tokens=50
            )
            summary = summary_response.choices[0].message.content
            cache_response(cache_key, summary)
    except Exception as e:
        print(f"Error generating summary: {e}")
        summary = "Thanks for sharing that."
    
    # Check for various ways the user might ask to move to the next question
    skip_phrases = [
        "next question",
        "move on",
        "let's move on",
        "next topic",
        "different question",
        "don't ask that again",
        "stop asking",
        "change the question",
        "ask something else"
    ]
    
    if any(phrase in response.lower() for phrase in skip_phrases):
        try:
            # Check cache for similar questions
            cache_key = f"next_question_{question_type}"
            cached = get_cached_response(cache_key)
            if cached:
                next_question = cached
            else:
                system_prompt = f"""You are a friendly and professional AI interviewer. Generate a brief follow-up question about {question_type}. 
                The question should be:
                1. One sentence only
                2. Clear and direct
                3. Easy to answer
                Keep it concise."""
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Generate a brief follow-up question about {question_type}."}
                    ],
                    temperature=0.7,
                    max_tokens=50
                )
                next_question = response.choices[0].message.content
                cache_response(cache_key, next_question)
            
            used_questions[client_id].add(next_question)
            current_question_types[client_id] = question_type
            return f"{summary}\n\n{next_question}"
        except Exception as e:
            print(f"Error generating follow-up: {e}")
            # Fallback to predefined questions if OpenAI fails
            question_types = list(INTERVIEW_QUESTIONS.keys())
            current_index = question_types.index(question_type)
            next_type = question_types[(current_index + 1) % len(question_types)]
            next_question = INTERVIEW_QUESTIONS[next_type]["question"]
            used_questions[client_id].add(next_question)
            current_question_types[client_id] = next_type
            return f"{summary}\n\n{next_question}"
    
    # Check if the response is too short or unclear
    if len(response.split()) < 10:
        return f"{summary}\n\nCould you elaborate a bit more?"
    
    try:
        # Check cache for similar follow-ups
        cache_key = f"follow_up_{response[:100]}"  # Use first 100 chars as key
        cached = get_cached_response(cache_key)
        if cached:
            follow_up = cached
        else:
            system_prompt = """You are a friendly and professional AI interviewer. Generate a brief follow-up question based on the candidate's response. 
            The question should be:
            1. One sentence only
            2. Direct and relevant
            3. Easy to understand
            Keep it concise."""
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Candidate's response: {response}\nGenerate a brief follow-up question."}
                ],
                temperature=0.7,
                max_tokens=50
            )
            follow_up = response.choices[0].message.content
            cache_response(cache_key, follow_up)
        
        used_questions[client_id].add(follow_up)
        return f"{summary}\n\n{follow_up}"
    except Exception as e:
        print(f"Error generating follow-up: {e}")
        # Fallback to predefined questions if OpenAI fails
        follow_ups = INTERVIEW_QUESTIONS[question_type]["follow_ups"]
        available_follow_ups = [q for q in follow_ups if q not in used_questions[client_id]]
        
        if not available_follow_ups:
            question_types = list(INTERVIEW_QUESTIONS.keys())
            current_index = question_types.index(question_type)
            next_type = question_types[(current_index + 1) % len(question_types)]
            next_question = INTERVIEW_QUESTIONS[next_type]["question"]
            used_questions[client_id].add(next_question)
            current_question_types[client_id] = next_type
            return f"{summary}\n\n{next_question}"
        
        follow_up = available_follow_ups[0]
        used_questions[client_id].add(follow_up)
        return f"{summary}\n\n{follow_up}"

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
        greeting = generate_initial_greeting()
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