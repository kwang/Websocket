#!/usr/bin/env python3
"""
Test script to verify OpenAI integration
"""

import os
import asyncio
from config import *

async def test_openai_integration():
    """Test OpenAI integration"""
    print("Testing OpenAI Integration")
    print("=" * 50)
    
    # Check if OpenAI API key is configured
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your-openai-api-key-here":
        print("❌ OpenAI API key not configured")
        print("Please set OPENAI_API_KEY in your config.py or environment variables")
        print("Get your API key from: https://platform.openai.com/api-keys")
        return False
    
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        
        # Test basic API call
        print("Testing OpenAI API connection...")
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in one sentence."}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ OpenAI API working: {result}")
        
        # Test interview-specific response
        print("\nTesting interview response generation...")
        conversation_history = [
            {"role": "interviewer", "content": "Hello! I'm your AI interviewer today. Could you please introduce yourself?"},
            {"role": "candidate", "content": "Hi, I'm John and I have 5 years of experience in software development."}
        ]
        
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
        
        for msg in conversation_history:
            if msg["role"] == "interviewer":
                messages.append({"role": "assistant", "content": msg["content"]})
            elif msg["role"] == "candidate":
                messages.append({"role": "user", "content": msg["content"]})
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=OPENAI_MAX_TOKENS,
            temperature=OPENAI_TEMPERATURE
        )
        
        interview_response = response.choices[0].message.content.strip()
        print(f"✅ Interview response generated: {interview_response}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI integration test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_openai_integration()) 