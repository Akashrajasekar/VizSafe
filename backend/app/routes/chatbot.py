# app/routes/chatbot.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from typing import Optional
import traceback
from groq import Groq

router = APIRouter()

class ChatbotRequest(BaseModel):
    message: str
    model: Optional[str] = "llama-3.3-70b-versatile"
    temperature: Optional[float] = 0.5
    system_message: Optional[str] = "You are a helpful assistant."

class ChatbotResponse(BaseModel):
    response: str

# Function to register routes
def register_chatbot_routes(app):
    # Get GROQ API key from environment
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ API key not found in environment variables. Please set 'GROQ_API_KEY'.")
    
    # Initialize GROQ client
    groq_client = Groq(api_key=api_key)
    
    @router.post("/message", response_model=ChatbotResponse)
    async def send_message(request: ChatbotRequest):
        try:
            # Create chat completion with GROQ
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    # System message sets the behavior of the assistant
                    {
                        "role": "system",
                        "content": request.system_message
                    },
                    # User message for the assistant to respond to
                    {
                        "role": "user",
                        "content": request.message,
                    }
                ],
                # The model to use
                model=request.model,
                # Controls randomness: lower is more deterministic
                temperature=request.temperature,
                # Maximum tokens to generate in the response
                max_completion_tokens=1024,
                # Control diversity via nucleus sampling
                top_p=1,
            )
            
            # Extract the assistant's response
            response_text = chat_completion.choices[0].message.content
            
            return ChatbotResponse(response=response_text)
        
        except Exception as e:
            error_detail = f"Error: {str(e)}\n{traceback.format_exc()}"
            print(error_detail)
            raise HTTPException(status_code=500, detail=error_detail)
    
    # Include router in the app
    app.include_router(router, prefix="/api/chatbot", tags=["chatbot"])