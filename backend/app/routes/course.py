# app/routes/course.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import os
from typing import Optional, List, Dict, Any
import traceback
import uuid
from app.services.course_service import CourseGenerationService

router = APIRouter()

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

# Store for tracking course generation progress
course_tasks = {}
course_results = {}

# Function to register routes
def register_course_routes(app):
    # Get GROQ API key from environment
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ API key not found in environment variables. Please set 'GROQ_API_KEY'.")
    
    # Initialize the service
    course_service = CourseGenerationService(api_key=api_key)
    
    # Create directory for courses if it doesn't exist
    os.makedirs("generated_courses", exist_ok=True)
    
    async def generate_course_task(course_id: str, topic: str, num_sections: int, model: str):
        """Background task to generate course"""
        try:
            # Update status to in progress
            course_tasks[course_id] = "in_progress"
            
            # Create a unique directory for this course
            output_dir = f"generated_courses/{course_id}_{topic.replace(' ', '_')}"
            
            # Generate the course
            course_data = course_service.generate_accessible_course(
                topic=topic,
                output_dir=output_dir,
                num_sections=num_sections,
                model=model
            )
            
            # Store the result
            course_results[course_id] = {
                "status": "completed",
                "course_data": course_data,
                "output_path": output_dir
            }
            course_tasks[course_id] = "completed"
            
        except Exception as e:
            error_detail = f"Error generating course: {str(e)}\n{traceback.format_exc()}"
            print(error_detail)
            course_tasks[course_id] = "failed"
            course_results[course_id] = {
                "status": "failed",
                "error": error_detail
            }
    
    @router.post("/generate", response_model=CourseGenerationResponse)
    async def start_course_generation(request: CourseGenerationRequest, background_tasks: BackgroundTasks):
        try:
            # Generate a unique ID for this course generation task
            course_id = str(uuid.uuid4())
            
            # Schedule the course generation as a background task
            background_tasks.add_task(
                generate_course_task,
                course_id=course_id,
                topic=request.topic,
                num_sections=request.num_sections,
                model=request.model
            )
            
            # Store initial status
            course_tasks[course_id] = "scheduled"
            
            return CourseGenerationResponse(
                course_id=course_id,
                status="scheduled",
                message=f"Course generation for '{request.topic}' has been scheduled. Check status with /api/course/status/{course_id}"
            )
        
        except Exception as e:
            error_detail = f"Error: {str(e)}\n{traceback.format_exc()}"
            print(error_detail)
            raise HTTPException(status_code=500, detail=error_detail)
    
    @router.get("/status/{course_id}", response_model=CourseStatusResponse)
    async def check_course_status(course_id: str):
        """Check the status of a course generation task"""
        if course_id not in course_tasks:
            raise HTTPException(status_code=404, detail="Course generation task not found")
        
        status = course_tasks[course_id]
        
        # If completed, return the course data
        if status == "completed" and course_id in course_results:
            return CourseStatusResponse(
                course_id=course_id,
                status=status,
                course_data=course_results[course_id]["course_data"],
                output_path=course_results[course_id]["output_path"]
            )
        
        # If failed, return the error
        if status == "failed" and course_id in course_results:
            raise HTTPException(
                status_code=500, 
                detail=f"Course generation failed: {course_results[course_id].get('error', 'Unknown error')}"
            )
        
        # If still in progress
        return CourseStatusResponse(
            course_id=course_id,
            status=status
        )
    
    @router.get("/list")
    async def list_courses():
        """List all course generation tasks and their statuses"""
        return {
            "courses": [
                {
                    "course_id": course_id,
                    "status": status,
                    "output_path": course_results.get(course_id, {}).get("output_path") if status == "completed" else None
                }
                for course_id, status in course_tasks.items()
            ]
        }
    
    # Include router in the app
    app.include_router(router, prefix="/api/course", tags=["course-generation"])