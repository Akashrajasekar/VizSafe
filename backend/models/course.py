# backend/models/course.py
from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class CourseSubsection(BaseModel):
    title: str
    description: Optional[str] = ""


class CourseSection(BaseModel):
    title: str
    description: Optional[str] = ""
    subsections: Optional[List[CourseSubsection]] = []


class CourseOutline(BaseModel):
    course_title: str
    course_description: str
    learning_objectives: List[str]
    sections: List[CourseSection]


class CourseRequest(BaseModel):
    course_name: Optional[str] = None
    sections_count: Optional[int] = None
    difficulty_level: Optional[str] = None


class QuestionResponse(BaseModel):
    question: str
    response_text: Optional[str] = None


class CourseGeneratorResult(BaseModel):
    interaction_id: str
    timestamp: str
    current_question_index: int
    questions: List[QuestionResponse]
    prompt_audio_id: str
    text_file_path: Optional[str] = None
    course_request: Optional[CourseRequest] = None
    is_complete: bool = False


class CourseGenerationRequest(BaseModel):
    topic: str
    num_sections: Optional[int] = 5
    model: Optional[str] = "llama-3.3-70b-versatile"


class CourseGenerationResponse(BaseModel):
    course_id: str
    status: str
    message: str


class CourseStatusResponse(BaseModel):
    course_id: str
    status: str
    course_data: Optional[Dict[str, Any]] = None
    output_path: Optional[str] = None