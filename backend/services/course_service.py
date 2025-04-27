# backend/services/course_service.py
import requests
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import traceback
import uuid
import backend.config as config
import logging
from backend.models.course import CourseOutline
import copy

logger = logging.getLogger(__name__)

class CourseGenerationService:
    def __init__(self, api_key: str):
        """Initialize the service with the required API key."""
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Storage for course generation tasks
        self.course_tasks = {}
        self.course_results = {}
    
    def call_groq_api(self, prompt: str, model: str) -> str:
        """Call the Groq API directly and return the response content"""
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert educational content creator specializing in accessible learning materials."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code != 200:
            logger.error(f"Error: {response.status_code}")
            logger.error(response.text)
            return f"Error generating content: {response.text}"
        
        return response.json()["choices"][0]["message"]["content"]
    
    def extract_json(self, text: str) -> Dict:
        """Extract JSON from text that might contain non-JSON elements"""
        try:
            # First try to parse the entire text as JSON
            return json.loads(text)
        except json.JSONDecodeError:
            # If that fails, try to find JSON within the text
            start = text.find('{')
            end = text.rfind('}')
            
            if start != -1 and end != -1:
                json_str = text[start:end+1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    # If still failing, try a more aggressive approach to fix common issues
                    # Remove any markdown code block markers
                    cleaned = json_str.replace("```json", "").replace("```", "").strip()
                    try:
                        return json.loads(cleaned)
                    except json.JSONDecodeError:
                        # Create a fallback structure
                        logger.warning("Could not parse JSON response. Creating fallback structure.")
                        return {
                            "content": [
                                {
                                    "subsection_title": "Generated Content", 
                                    "explanations": "The model returned content in an unexpected format. Please try regenerating this section."
                                }
                            ]
                        }
            else:
                # Create a fallback structure
                logger.warning("Could not extract JSON. Creating fallback structure.")
                return {
                    "content": [
                        {
                            "subsection_title": "Generated Content", 
                            "explanations": "The model returned content in an unexpected format. Please try regenerating this section."
                        }
                    ]
                }
    
    def generate_course(self, topic: str, num_sections: int = 5, model: str = "llama-3.3-70b-versatile") -> Dict:
        """
        Generate a complete course with multiple sections on a given topic.
        
        Args:
            topic (str): The main topic of the course
            num_sections (int): Number of sections to generate
            model (str): The Groq model to use for generation
        
        Returns:
            dict: The complete course structure with content
        """
        logger.info(f"Step 1/3: Generating course outline...")
        # First, generate the course outline
        outline_prompt = f"""
        Create a detailed outline for a comprehensive course on "{topic}". This course is designed for a learning 
        platform for individuals who are deaf, blind, or non-verbal, so the content should be:
        
        1. Clear and descriptive without relying on visual or auditory cues
        2. Well-structured with logical progression
        3. Broken down into {num_sections} main sections
        4. Each section should have 3-5 subsections
        
        For each section and subsection, provide a brief description of what will be covered.
        Format your response as a JSON object with the following structure:
        {{
            "course_title": "Title of the Course",
            "course_description": "Overall description of the course",
            "learning_objectives": ["objective1", "objective2", ...],
            "sections": [
                {{
                    "title": "Section 1 Title",
                    "description": "Description of this section",
                    "subsections": [
                        {{
                            "title": "Subsection 1.1 Title",
                            "description": "Description of this subsection"
                        }},
                        ...
                    ]
                }},
                ...
            ]
        }}
        
        IMPORTANT: Ensure your response is ONLY the JSON object, with no additional text before or after it.
        """
        
        outline_response = self.call_groq_api(outline_prompt, model)
        
        # Extract the JSON from the response
        try:
            # Try to find JSON in the response if it's not already pure JSON
            course_outline = self.extract_json(outline_response)
            logger.info("✓ Course outline generated successfully")
        except Exception as e:
            logger.warning(f"Warning: Failed to parse course outline. Error: {str(e)}")
            logger.info("✓ Creating simplified course structure...")
            # Create a basic outline if parsing fails
            course_outline = {
                "course_title": f"Introduction to {topic}",
                "course_description": f"A comprehensive course on {topic} designed for accessibility.",
                "learning_objectives": [
                    f"Understand the basic concepts of {topic}",
                    f"Learn practical applications of {topic}",
                    f"Develop skills to work with {topic} independently"
                ],
                "sections": []
            }
            
            # Create basic sections
            for i in range(num_sections):
                if i == 0:
                    title = f"Introduction to {topic}"
                    description = f"An overview of {topic} and its importance."
                elif i == num_sections - 1:
                    title = f"Advanced Topics and Next Steps"
                    description = f"Further exploration of {topic} and ways to continue learning."
                else:
                    title = f"Core Concepts {i}"
                    description = f"Essential knowledge about {topic} - part {i}."
                    
                course_outline["sections"].append({
                    "title": title,
                    "description": description,
                    "subsections": [
                        {"title": f"Topic {i}.1", "description": "First subtopic"},
                        {"title": f"Topic {i}.2", "description": "Second subtopic"},
                        {"title": f"Topic {i}.3", "description": "Third subtopic"}
                    ]
                })
        
        # For each section in the outline, generate detailed content
        full_course = copy.deepcopy(course_outline)
        
        logger.info(f"Step 2/3: Generating content for {len(full_course['sections'])} sections...")
        for i, section in enumerate(full_course["sections"]):
            logger.info(f"  Generating content for section {i+1}/{len(full_course['sections'])}: {section['title']}...")
            
            # First determine subsections if they exist in the outline
            subsections = []
            if "subsections" in section:
                for sub in section["subsections"]:
                    subsections.append({
                        "title": sub["title"],
                        "description": sub.get("description", "")
                    })
            
            # Create a prompt with subsection information if available
            subsection_text = ""
            if subsections:
                subsection_text = "This section includes the following subsections:\n"
                for j, sub in enumerate(subsections):
                    subsection_text += f"  {j+1}. {sub['title']} - {sub['description']}\n"
            
            section_prompt = f"""
            Generate detailed content for Section {i+1}: "{section['title']}" of the course on {topic}.
            
            This is the section description: {section.get('description', 'No description provided')}
            
            {subsection_text}
            
            This content is for a learning platform designed for individuals who are deaf, blind, or non-verbal, so:
            1. Provide clear, descriptive text without relying on visual or auditory references
            2. Break complex concepts into simple, clear explanations
            3. Include practical examples that don't require vision or hearing
            4. For each subsection, include:
               - Key concepts (3-5 main points)
               - Detailed explanations (2-3 paragraphs)
               - Examples (2-3 practical examples)
               - Summary points for reinforcement (3-5 bullet points)
               - Self-assessment questions (2-3 questions with answers)
            
            Format your response as a JSON object with the following structure:
            {{
                "content": [
                    {{
                        "subsection_title": "Title",
                        "key_concepts": ["concept1", "concept2", ...],
                        "explanations": "Detailed text explaining the concepts...",
                        "examples": ["example1", "example2", ...],
                        "summary_points": ["point1", "point2", ...],
                        "assessment_questions": [
                            {{
                                "question": "Question text?",
                                "answer": "Answer text"
                            }},
                            ...
                        ]
                    }},
                    ...
                ]
            }}
            
            IMPORTANT: Ensure your response is ONLY the JSON object, with no additional text before or after it.
            """
            
            section_content = self.call_groq_api(section_prompt, model)
            
            try:
                section_data = self.extract_json(section_content)
                section["content"] = section_data.get("content", [])
                logger.info(f"  ✓ Content generated for section {i+1} with {len(section['content'])} subsections")
            except Exception as e:
                logger.warning(f"  Warning: Failed to parse content for section {i+1}. Error: {str(e)}")
                logger.info(f"  ✓ Creating placeholder content for section {i+1}")
                
                # Create placeholder content based on subsections if available
                if subsections:
                    section["content"] = []
                    for sub in subsections:
                        section["content"].append({
                            "subsection_title": sub["title"],
                            "key_concepts": [f"Key concept for {sub['title']}"],
                            "explanations": f"This section explains important concepts related to {sub['title']}.",
                            "examples": [f"Example related to {sub['title']}"],
                            "summary_points": [f"Summary point for {sub['title']}"],
                            "assessment_questions": [
                                {"question": f"Question about {sub['title']}?", "answer": "Answer to the question."}
                            ]
                        })
                else:
                    section["content"] = [{"subsection_title": "Generated Content", 
                                        "explanations": f"Content for {section['title']} will be provided here."}]
        
        logger.info("Step 3/3: Finalizing course structure...")
        return full_course
    
    def sanitize_filename(self, name: str) -> str:
        """Remove invalid characters from filenames and directory names"""
        # Replace characters that are not allowed in Windows filenames
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            name = name.replace(char, '_')
        # Ensure the name doesn't end with a space or period
        name = name.rstrip('. ')
        return name
    
    def save_course_to_files(self, course: Dict, output_dir: str = "generated_course") -> str:
        """
        Save the generated course to text files with a clear structure
        
        Args:
            course: The course data structure
            output_dir: Directory to save the files to
            
        Returns:
            str: Path to the generated course directory
        """
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        # Write course overview
        with open(output_path / "00_course_overview.txt", "w", encoding="utf-8") as f:
            f.write(f"# {course['course_title']}\n\n")
            f.write(f"{course['course_description']}\n\n")
            f.write("## Learning Objectives\n\n")
            for i, obj in enumerate(course['learning_objectives']):
                f.write(f"{i+1}. {obj}\n")
            f.write("\n## Course Sections\n\n")
            for i, section in enumerate(course['sections']):
                f.write(f"{i+1}. {section['title']} - {section['description']}\n")
        
        # Write each section to its own file
        for i, section in enumerate(course['sections']):
            # Sanitize section title for directory naming
            safe_section_name = self.sanitize_filename(section['title'])
            section_path = output_path / f"{i+1:02d}_{safe_section_name.replace(' ', '_')}"
            section_path.mkdir(exist_ok=True)
            
            # Write section overview
            with open(section_path / "00_section_overview.txt", "w", encoding="utf-8") as f:
                f.write(f"# Section {i+1}: {section['title']}\n\n")
                f.write(f"{section['description']}\n\n")
            
            # Write each subsection content
            if "content" in section:
                for j, subsection in enumerate(section["content"]):
                    # Sanitize subsection title for file naming
                    safe_subsection_name = self.sanitize_filename(subsection['subsection_title'])
                    file_path = section_path / f"{j+1:02d}_{safe_subsection_name.replace(' ', '_')}.txt"
                    
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(f"# {subsection['subsection_title']}\n\n")
                        
                        if "key_concepts" in subsection:
                            f.write("## Key Concepts\n\n")
                            for concept in subsection["key_concepts"]:
                                f.write(f"- {concept}\n")
                            f.write("\n")
                        
                        if "explanations" in subsection:
                            f.write("## Explanations\n\n")
                            f.write(f"{subsection['explanations']}\n\n")
                        
                        if "examples" in subsection:
                            f.write("## Examples\n\n")
                            for example in subsection["examples"]:
                                f.write(f"- {example}\n")
                            f.write("\n")
                        
                        if "summary_points" in subsection:
                            f.write("## Summary Points\n\n")
                            for point in subsection["summary_points"]:
                                f.write(f"- {point}\n")
                            f.write("\n")
                        
                        if "assessment_questions" in subsection:
                            f.write("## Self-Assessment Questions\n\n")
                            for q in subsection["assessment_questions"]:
                                f.write(f"Q: {q['question']}\n")
                                f.write(f"A: {q['answer']}\n\n")
        
        return str(output_path)
    
    def generate_accessible_course(self, 
                                  topic: str, 
                                  output_dir: str = "generated_course", 
                                  num_sections: int = 5, 
                                  model: str = "llama-3.3-70b-versatile") -> Dict:
        """
        Generate and save a complete accessible course
        
        Args:
            topic: The course topic
            output_dir: Directory to save the course to
            num_sections: Number of sections to generate
            model: The Groq model to use
            
        Returns:
            Dict: The generated course data
        """
        logger.info(f"Generating course on '{topic}' with {num_sections} sections...")
        course = self.generate_course(topic, num_sections, model)
        
        logger.info("Saving course to files...")
        output_path = self.save_course_to_files(course, output_dir)
        
        logger.info(f"Course generated successfully and saved to {output_path}/")
        
        # Add the output path to the course data
        course["output_path"] = output_path
        return course
        
    def start_course_generation(self, topic: str, num_sections: int = 5, model: str = "llama-3.3-70b-versatile"):
        """
        Start asynchronous course generation
        
        Args:
            topic: The course topic
            num_sections: Number of sections to generate
            model: Model to use
            
        Returns:
            str: Course ID for tracking
        """
        # Generate a unique ID for this course generation task
        course_id = str(uuid.uuid4())
        
        # Store initial status
        self.course_tasks[course_id] = "scheduled"
        
        # Start the generation process in the background using threading
        # In a real-world application, you might want to use a proper background task queue
        import threading
        thread = threading.Thread(
            target=self._generate_course_task,
            args=(course_id, topic, num_sections, model)
        )
        thread.daemon = True
        thread.start()
        
        return course_id
    
    def _generate_course_task(self, course_id: str, topic: str, num_sections: int, model: str):
        """Background task to generate course"""
        try:
            # Update status to in progress
            self.course_tasks[course_id] = "in_progress"
            
            # Create a unique directory for this course
            output_dir = f"{config.GENERATED_COURSES_DIR}/{course_id}_{topic.replace(' ', '_')}"
            
            # Generate the course
            course_data = self.generate_accessible_course(
                topic=topic,
                output_dir=output_dir,
                num_sections=num_sections,
                model=model
            )
            
            # Store the result
            self.course_results[course_id] = {
                "status": "completed",
                "course_data": course_data,
                "output_path": output_dir
            }
            self.course_tasks[course_id] = "completed"
            
        except Exception as e:
            error_detail = f"Error generating course: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_detail)
            self.course_tasks[course_id] = "failed"
            self.course_results[course_id] = {
                "status": "failed",
                "error": error_detail
            }
    
    def get_course_status(self, course_id: str):
        """Get the status of a course generation task"""
        if course_id not in self.course_tasks:
            return None
        
        status = self.course_tasks[course_id]
        
        # If completed, return the course data
        if status == "completed" and course_id in self.course_results:
            return {
                "course_id": course_id,
                "status": status,
                "course_data": self.course_results[course_id]["course_data"],
                "output_path": self.course_results[course_id]["output_path"]
            }
        
        # If failed, return the error
        if status == "failed" and course_id in self.course_results:
            return {
                "course_id": course_id,
                "status": status,
                "error": self.course_results[course_id].get("error", "Unknown error")
            }
        
        # If still in progress
        return {
            "course_id": course_id,
            "status": status
        }
    
    def list_courses(self):
        """List all course generation tasks and their statuses"""
        return [
            {
                "course_id": course_id,
                "status": status,
                "output_path": self.course_results.get(course_id, {}).get("output_path") if status == "completed" else None,
                "topic": self.course_results.get(course_id, {}).get("course_data", {}).get("course_title", "Unknown")
                    if status == "completed" else "Unknown"
            }
            for course_id, status in self.course_tasks.items()
        ]