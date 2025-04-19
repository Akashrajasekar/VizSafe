# app/routes/course_tts.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import os
from typing import Optional, Dict, Any
import traceback
import uuid
import json
from pathlib import Path

from app.services.course_tts_service import CourseTTSService
from app.services.tst_service import TextToSpeechService

router = APIRouter()

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

# Store for tracking TTS conversion progress
tts_tasks = {}
tts_results = {}

# Function to register routes
def register_course_tts_routes(app):
    # Get GROQ API key from environment
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ API key not found in environment variables. Please set 'GROQ_API_KEY'.")
    
    # Initialize the services
    tts_service = TextToSpeechService(api_key=api_key)
    course_tts_service = CourseTTSService(tts_service)
    
    # Import here to avoid circular imports
    from app.routes.course import course_results
    
    async def convert_course_to_speech_task(request_id: str, course_id: str, voice: str):
        """Background task to convert course to speech"""
        try:
            # Update status to in progress
            tts_tasks[request_id] = "in_progress"
            
            # Get the course data from the course service's results
            if course_id not in course_results or course_results[course_id]["status"] != "completed":
                tts_tasks[request_id] = "failed"
                tts_results[request_id] = {
                    "status": "failed",
                    "error": f"Course with ID {course_id} not found or not completed"
                }
                return
            
            course_data = course_results[course_id]["course_data"]
            
            # Convert course to speech
            audio_course = await course_tts_service.convert_course_to_speech(
                course_data=course_data,
                voice=voice
            )
            
            # Store the result
            tts_results[request_id] = {
                "status": "completed",
                "audio_course": audio_course
            }
            tts_tasks[request_id] = "completed"
            
        except Exception as e:
            error_detail = f"Error converting course to speech: {str(e)}\n{traceback.format_exc()}"
            print(error_detail)
            tts_tasks[request_id] = "failed"
            tts_results[request_id] = {
                "status": "failed",
                "error": error_detail
            }
    
    async def convert_course_from_file_task(request_id: str, course_directory: str, voice: str):
        """Background task to load a course from file and convert it to speech"""
        try:
            # Update status to in progress
            tts_tasks[request_id] = "in_progress"
            
            # Try to reconstruct course data from directory
            try:
                course_data = {}
                
                # Read course overview file
                overview_path = Path(course_directory) / "00_course_overview.txt"
                if not overview_path.exists():
                    raise FileNotFoundError(f"Course overview file not found at {overview_path}")
                
                with open(overview_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                    # Extract course title (first line after '# ')
                    title_match = content.split('\n')[0].replace('# ', '')
                    course_data["course_title"] = title_match
                    
                    # Extract course description (content between title and learning objectives)
                    desc_start = content.find('\n\n') + 2
                    desc_end = content.find('## Learning Objectives')
                    if desc_end > desc_start:
                        course_data["course_description"] = content[desc_start:desc_end].strip()
                    else:
                        course_data["course_description"] = "No description available."
                    
                    # Extract learning objectives
                    obj_start = content.find('## Learning Objectives') + len('## Learning Objectives')
                    obj_end = content.find('## Course Sections')
                    if obj_end > obj_start:
                        objectives_text = content[obj_start:obj_end].strip()
                        objectives = []
                        for line in objectives_text.split('\n'):
                            if line.strip() and line.strip()[0].isdigit():
                                obj = line.strip()
                                if '. ' in obj:
                                    obj = obj.split('. ', 1)[1]
                                objectives.append(obj)
                        course_data["learning_objectives"] = objectives
                    else:
                        course_data["learning_objectives"] = ["Learn about the topic."]
                
                # Read section directories
                course_data["sections"] = []
                for section_dir in sorted([d for d in Path(course_directory).iterdir() if d.is_dir()]):
                    # Skip directories that don't start with a number (section directories typically start with a number)
                    if not section_dir.name[0].isdigit():
                        continue
                    
                    section_info = {}
                    
                    # Read section overview
                    section_overview_path = section_dir / "00_section_overview.txt"
                    if section_overview_path.exists():
                        with open(section_overview_path, "r", encoding="utf-8") as f:
                            section_content = f.read()
                            
                            # Extract section title
                            section_title_line = section_content.split('\n')[0]
                            section_info["title"] = section_title_line.replace('# Section', '').strip()
                            if ':' in section_info["title"]:
                                section_info["title"] = section_info["title"].split(':', 1)[1].strip()
                            
                            # Extract section description
                            section_info["description"] = section_content.split('\n\n', 1)[1].strip() if '\n\n' in section_content else ""
                    else:
                        section_info["title"] = section_dir.name.replace('_', ' ')
                        section_info["description"] = "No description available."
                    
                    # Get subsection content files
                    section_info["content"] = []
                    for subsection_file in sorted([f for f in section_dir.iterdir() if f.is_file() and f.name != "00_section_overview.txt"]):
                        subsection = {}
                        
                        with open(subsection_file, "r", encoding="utf-8") as f:
                            subsection_content = f.read()
                            
                            # Extract subsection title
                            subsection["subsection_title"] = subsection_content.split('\n')[0].replace('# ', '').strip()
                            
                            # Extract key concepts
                            key_concepts = []
                            if "## Key Concepts" in subsection_content:
                                concepts_start = subsection_content.find("## Key Concepts") + len("## Key Concepts")
                                concepts_end = subsection_content.find("##", concepts_start)
                                if concepts_end == -1:
                                    concepts_end = len(subsection_content)
                                concepts_text = subsection_content[concepts_start:concepts_end].strip()
                                for line in concepts_text.split('\n'):
                                    if line.strip() and line.strip().startswith('-'):
                                        key_concepts.append(line.strip().replace('- ', '', 1))
                            subsection["key_concepts"] = key_concepts
                            
                            # Extract explanations
                            explanations = ""
                            if "## Explanations" in subsection_content:
                                expl_start = subsection_content.find("## Explanations") + len("## Explanations")
                                expl_end = subsection_content.find("##", expl_start)
                                if expl_end == -1:
                                    expl_end = len(subsection_content)
                                explanations = subsection_content[expl_start:expl_end].strip()
                            subsection["explanations"] = explanations
                            
                            # Extract examples
                            examples = []
                            if "## Examples" in subsection_content:
                                examples_start = subsection_content.find("## Examples") + len("## Examples")
                                examples_end = subsection_content.find("##", examples_start)
                                if examples_end == -1:
                                    examples_end = len(subsection_content)
                                examples_text = subsection_content[examples_start:examples_end].strip()
                                for line in examples_text.split('\n'):
                                    if line.strip() and line.strip().startswith('-'):
                                        examples.append(line.strip().replace('- ', '', 1))
                            subsection["examples"] = examples
                            
                            # Extract summary points
                            summary_points = []
                            if "## Summary Points" in subsection_content:
                                summary_start = subsection_content.find("## Summary Points") + len("## Summary Points")
                                summary_end = subsection_content.find("##", summary_start)
                                if summary_end == -1:
                                    summary_end = len(subsection_content)
                                summary_text = subsection_content[summary_start:summary_end].strip()
                                for line in summary_text.split('\n'):
                                    if line.strip() and line.strip().startswith('-'):
                                        summary_points.append(line.strip().replace('- ', '', 1))
                            subsection["summary_points"] = summary_points
                            
                            # Extract assessment questions
                            assessment_questions = []
                            if "## Self-Assessment Questions" in subsection_content:
                                qa_start = subsection_content.find("## Self-Assessment Questions") + len("## Self-Assessment Questions")
                                qa_end = len(subsection_content)
                                qa_text = subsection_content[qa_start:qa_end].strip()
                                
                                # Extract Q/A pairs
                                qa_parts = qa_text.split('Q: ')
                                for part in qa_parts:
                                    if not part.strip():
                                        continue
                                    
                                    if 'A: ' in part:
                                        question, answer = part.split('A: ', 1)
                                        question = question.strip()
                                        answer = answer.strip()
                                        if answer.endswith('\n\n'):
                                            answer = answer[:-2]
                                        assessment_questions.append({
                                            "question": question,
                                            "answer": answer
                                        })
                            subsection["assessment_questions"] = assessment_questions
                        
                        section_info["content"].append(subsection)
                    
                    course_data["sections"].append(section_info)
                
                # Convert course to speech
                audio_course = await course_tts_service.convert_course_to_speech(
                    course_data=course_data,
                    voice=voice
                )
                
                # Store the result
                tts_results[request_id] = {
                    "status": "completed",
                    "audio_course": audio_course
                }
                tts_tasks[request_id] = "completed"
                
            except Exception as e:
                error_detail = f"Error loading course from file: {str(e)}\n{traceback.format_exc()}"
                print(error_detail)
                tts_tasks[request_id] = "failed"
                tts_results[request_id] = {
                    "status": "failed",
                    "error": error_detail
                }
            
        except Exception as e:
            error_detail = f"Error processing course from file: {str(e)}\n{traceback.format_exc()}"
            print(error_detail)
            tts_tasks[request_id] = "failed"
            tts_results[request_id] = {
                "status": "failed",
                "error": error_detail
            }
    
    @router.post("/convert", response_model=CourseTTSResponse)
    async def start_course_tts_conversion(request: CourseTTSRequest, background_tasks: BackgroundTasks):
        try:
            # Import here to avoid circular imports
            from app.routes.course import course_tasks
            
            # Check if the course exists and is completed
            if request.course_id not in course_tasks:
                raise HTTPException(status_code=404, detail=f"Course with ID {request.course_id} not found")
            
            if course_tasks[request.course_id] != "completed":
                raise HTTPException(status_code=400, detail=f"Course with ID {request.course_id} is not yet completed")
            
            # Generate a unique ID for this TTS conversion task
            request_id = str(uuid.uuid4())
            
            # Schedule the TTS conversion as a background task
            background_tasks.add_task(
                convert_course_to_speech_task,
                request_id=request_id,
                course_id=request.course_id,
                voice=request.voice
            )
            
            # Store initial status
            tts_tasks[request_id] = "scheduled"
            
            return CourseTTSResponse(
                request_id=request_id,
                status="scheduled",
                message=f"Course-to-speech conversion for course ID {request.course_id} has been scheduled. Check status with /api/course-tts/status/{request_id}"
            )
        
        except Exception as e:
            error_detail = f"Error: {str(e)}\n{traceback.format_exc()}"
            print(error_detail)
            raise HTTPException(status_code=500, detail=error_detail)
    
    @router.post("/convert-from-file", response_model=CourseTTSResponse)
    async def convert_course_from_file(request: CourseFromFileRequest, background_tasks: BackgroundTasks):
        """Load a course from a file directory and convert it to speech"""
        try:
            # Check if the course directory exists
            course_dir_path = Path(request.course_directory)
            if not course_dir_path.exists() or not course_dir_path.is_dir():
                raise HTTPException(status_code=404, detail=f"Course directory {request.course_directory} not found")
            
            # Generate a unique ID for this TTS conversion task
            request_id = str(uuid.uuid4())
            
            # Schedule the TTS conversion as a background task
            background_tasks.add_task(
                convert_course_from_file_task,
                request_id=request_id,
                course_directory=request.course_directory,
                voice=request.voice
            )
            
            # Store initial status
            tts_tasks[request_id] = "scheduled"
            
            return CourseTTSResponse(
                request_id=request_id,
                status="scheduled",
                message=f"Course-to-speech conversion from directory {request.course_directory} has been scheduled. Check status with /api/course-tts/status/{request_id}"
            )
        
        except Exception as e:
            error_detail = f"Error: {str(e)}\n{traceback.format_exc()}"
            print(error_detail)
            raise HTTPException(status_code=500, detail=error_detail)
    
    @router.get("/status/{request_id}", response_model=CourseTTSStatusResponse)
    async def check_tts_status(request_id: str):
        """Check the status of a course-to-speech conversion task"""
        if request_id not in tts_tasks:
            raise HTTPException(status_code=404, detail="TTS conversion task not found")
        
        status = tts_tasks[request_id]
        
        # If completed, return the audio course data
        if status == "completed" and request_id in tts_results:
            return CourseTTSStatusResponse(
                request_id=request_id,
                status=status,
                audio_course=tts_results[request_id]["audio_course"]
            )
        
        # If failed, return the error
        if status == "failed" and request_id in tts_results:
            raise HTTPException(
                status_code=500, 
                detail=f"TTS conversion failed: {tts_results[request_id].get('error', 'Unknown error')}"
            )
        
        # If still in progress
        return CourseTTSStatusResponse(
            request_id=request_id,
            status=status
        )
    
    @router.get("/list")
    async def list_tts_tasks():
        """List all TTS conversion tasks and their statuses"""
        return {
            "tts_tasks": [
                {
                    "request_id": request_id,
                    "status": status
                }
                for request_id, status in tts_tasks.items()
            ]
        }
    
    # Include router in the app
    app.include_router(router, prefix="/api/course-tts", tags=["course-tts"]) 