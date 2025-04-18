# app/routes/audio.py
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
import os
from typing import Optional
import traceback

from app.services.tst_service import TextToSpeechService, TranscribeResult

router = APIRouter()

class TextToSpeechRequest(BaseModel):
    text: Optional[str] = None
    voice: Optional[str] = "Celeste-PlayAI"
    transcribe: Optional[bool] = True

# Function to register routes
def register_tst_routes(app):
    # Get GROQ API key from environment
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ API key not found in environment variables. Please set 'GROQ_API_KEY'.")
    
    # Initialize the service
    tst_service = TextToSpeechService(api_key=api_key)
    
    @router.post("/text-to-speech", response_model=TranscribeResult)
    async def text_to_speech_pipeline(request: TextToSpeechRequest):
        try:
            # Check if text is empty or None
            text_to_process = request.text
            if not text_to_process or not text_to_process.strip():
                # Use default text if no text is provided
                text_to_process = "This is a temporary audio message generated because no text was provided. You can replace this with your own text input."
            
            # Use the service to process the text-to-speech request
            result = await tst_service.text_to_speech(
                text=text_to_process,
                voice=request.voice,
                transcribe=request.transcribe
            )
            
            # If we used default text, note this in the result
            if not request.text or not request.text.strip():
                result.used_default_text = True
            
            return result
        
        except Exception as e:
            error_detail = f"Error: {str(e)}\n{traceback.format_exc()}"
            print(error_detail)
            raise HTTPException(status_code=500, detail=error_detail)
    
    @router.get("/audio/{file_id}")
    async def get_audio(file_id: str):
        # Use the service to retrieve the audio file
        content, success = tst_service.get_audio_file(file_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return Response(
            content=content,
            media_type="audio/wav"
        )
    
    # Include router in the app
    app.include_router(router, prefix="/api/tst", tags=["text-speech-text"])