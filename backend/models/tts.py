# backend/models/tts.py
from typing import Dict, Optional, List, Any
from pydantic import BaseModel

class TranscribeResult(BaseModel):
    original_text: str
    audio_id: str
    transcribed_text: Optional[str] = None
    used_default_text: Optional[bool] = False


class TextToSpeechRequest(BaseModel):
    text: Optional[str] = None
    voice: Optional[str] = "Celeste-PlayAI"
    transcribe: Optional[bool] = True


class CourseTTSRequest(BaseModel):
    course_id: str
    voice: Optional[str] = "Celeste-PlayAI"


class CourseFromFileRequest(BaseModel):
    course_directory: str
    voice: Optional[str] = "Celeste-PlayAI"


class CourseTTSResponse(BaseModel):
    request_id: str
    status: str
    message: str


class CourseTTSStatusResponse(BaseModel):
    request_id: str
    status: str
    audio_course: Optional[Dict[str, Any]] = None


class StartRequest(BaseModel):
    voice: Optional[str] = "Celeste-PlayAI"