# backend/services/tts_service.py
import os
import uuid
from typing import Dict, Optional, Tuple, List
from groq import Groq
from backend.models.tts import TranscribeResult
import backend.config as config
import logging

logger = logging.getLogger(__name__)

class TextToSpeechService:
    def __init__(self, api_key: str):
        """Initialize the service with the required API key."""
        self.client = Groq(api_key=api_key)
        self.temp_files: Dict[str, str] = {}
        
        # Create a directory for audio files if it doesn't exist
        self.audio_dir = config.AUDIO_DIR
        os.makedirs(self.audio_dir, exist_ok=True)
        
        self.default_texts: List[str] = [
            "This is a temporary audio message. You can provide your own text to hear it spoken.",
            "Welcome to the text-to-speech demo. Enter some text to hear it converted to speech.",
            "Hello there! This is an example of the text-to-speech capabilities. Try entering your own text.",
            "No text was provided, so I've generated this temporary message instead. Feel free to enter your own text.",
            "This is GROQ's PlayAI text-to-speech service speaking. Enter text in the input field to try it yourself."
        ]
    
    async def text_to_speech(self, 
                            text: str, 
                            voice: str = "Fritz-PlayAI", 
                            transcribe: bool = True,
                            filename: Optional[str] = None) -> TranscribeResult:
        """
        Convert text to speech, optionally transcribe it back.
        
        Args:
            text: The text to convert to speech
            voice: The voice to use for synthesis
            transcribe: Whether to transcribe the generated audio
            filename: Optional custom filename base (without extension)
            
        Returns:
            TranscribeResult object containing original text, audio ID and optional transcription
        """
        # Handle empty text case
        is_default_text = False
        if not text or not text.strip():
            # Choose a random default text from the list
            import random
            text = random.choice(self.default_texts)
            is_default_text = True
        
        # Create a file in the current directory structure
        file_id = str(uuid.uuid4())
        
        # Use custom filename if provided, otherwise use the UUID
        if filename:
            file_basename = f"{filename}_{file_id[-8:]}"
        else:
            file_basename = f"{file_id}_speech"
        
        file_path = os.path.join(self.audio_dir, f"{file_basename}.wav")
        
        # Get the audio response from GROQ and write directly to file
        response = self.client.audio.speech.create(
            model="playai-tts",
            voice=voice,
            input=text,
            response_format="wav"
        )
        
        # Use the proper write_to_file method
        response.write_to_file(file_path)
        
        # Store the file path in memory
        self.temp_files[file_id] = file_path
        
        result = TranscribeResult(
            original_text=text,
            audio_id=file_id,
            used_default_text=is_default_text
        )
        
        # Step 2 (Optional): Transcribe the generated audio
        if transcribe:
            try:
                with open(file_path, "rb") as file:
                    transcription = self.client.audio.transcriptions.create(
                        file=file,
                        model="whisper-large-v3-turbo",
                        response_format="text",
                        language="en",
                        temperature=0.0
                    )
                    
                    # The transcription is already a string when response_format="text"
                    result.transcribed_text = transcription
            except Exception as e:
                logger.error(f"Transcription error: {str(e)}")
                result.transcribed_text = "Transcription failed"
        
        return result
    
    def get_audio_file(self, file_id: str) -> Tuple[bytes, bool]:
        """
        Retrieve the audio file content by ID.
        
        Args:
            file_id: The ID of the audio file to retrieve
            
        Returns:
            Tuple of (file_content, success_status)
        """
        if file_id not in self.temp_files:
            return None, False
        
        file_path = self.temp_files[file_id]
        
        try:
            with open(file_path, "rb") as file:
                content = file.read()
            return content, True
        except Exception as e:
            logger.error(f"Error reading audio file: {str(e)}")
            return None, False