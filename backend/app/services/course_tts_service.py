# app/services/course_tts_service.py
import os
from typing import Dict, List, Any, Optional
from app.services.tst_service import TextToSpeechService

class CourseTTSService:
    def __init__(self, tts_service: TextToSpeechService):
        """Initialize the service with the text-to-speech service."""
        self.tts_service = tts_service
    
    async def convert_course_to_speech(self, course_data: Dict[str, Any], voice: str = "Celeste-PlayAI") -> Dict[str, Any]:
        """
        Convert course content to speech
        
        Args:
            course_data: The full course data structure
            voice: The voice to use for speech synthesis
            
        Returns:
            Dict[str, Any]: Course data with audio IDs for each text element
        """
        # Create a copy of the course data to add audio information
        audio_course = course_data.copy()
        
        # Add audio for course title and description (combined)
        print(f"Converting course overview to speech...")
        
        # Combine title and description into one audio file
        combined_title_desc = f"{audio_course['course_title']}. {audio_course['course_description']}"
        combined_result = await self.tts_service.text_to_speech(
            text=combined_title_desc,
            voice=voice,
            transcribe=False,
            filename=f"course_overview_{self._sanitize_filename(audio_course['course_title'])}"
        )
        audio_course["overview_audio_id"] = combined_result.audio_id
        
        # Process each section
        for i, section in enumerate(audio_course["sections"]):
            print(f"Converting section {i+1}/{len(audio_course['sections'])}: {section['title']}...")
            
            # Combine section title and description if description exists
            section_text = section["title"]
            if "description" in section and section["description"]:
                section_text = f"{section_text}. {section['description']}"
            
            section_audio_result = await self.tts_service.text_to_speech(
                text=section_text,
                voice=voice,
                transcribe=False,
                filename=f"section_{i+1}_{self._sanitize_filename(section['title'])}"
            )
            section["section_audio_id"] = section_audio_result.audio_id
            
            # Process content (subsections) if they exist
            if "content" in section:
                for j, subsection in enumerate(section["content"]):
                    print(f"  Converting subsection {j+1}/{len(section['content'])}: {subsection['subsection_title']}...")
                    
                    # Combine subsection title and explanations if they exist
                    subsection_text = subsection["subsection_title"]
                    if "explanations" in subsection and subsection["explanations"]:
                        subsection_text = f"{subsection_text}. {subsection['explanations']}"
                    
                    subsection_result = await self.tts_service.text_to_speech(
                        text=subsection_text,
                        voice=voice,
                        transcribe=False,
                        filename=f"section_{i+1}_subsection_{j+1}_{self._sanitize_filename(subsection['subsection_title'])}"
                    )
                    subsection["content_audio_id"] = subsection_result.audio_id
                    
                    # Combine all key concepts into one audio file
                    if "key_concepts" in subsection and subsection["key_concepts"]:
                        concepts_text = "Key Concepts. "
                        for k, concept in enumerate(subsection["key_concepts"]):
                            concepts_text += f"Concept {k+1}: {concept}. "
                        
                        concepts_result = await self.tts_service.text_to_speech(
                            text=concepts_text,
                            voice=voice,
                            transcribe=False,
                            filename=f"section_{i+1}_subsec_{j+1}_all_concepts"
                        )
                        subsection["key_concepts_audio_id"] = concepts_result.audio_id
                    
                    # Combine all examples into one audio file
                    if "examples" in subsection and subsection["examples"]:
                        examples_text = "Examples. "
                        for k, example in enumerate(subsection["examples"]):
                            examples_text += f"Example {k+1}: {example}. "
                        
                        examples_result = await self.tts_service.text_to_speech(
                            text=examples_text,
                            voice=voice,
                            transcribe=False,
                            filename=f"section_{i+1}_subsec_{j+1}_all_examples"
                        )
                        subsection["examples_audio_id"] = examples_result.audio_id
                    
                    # Combine all summary points into one audio file
                    if "summary_points" in subsection and subsection["summary_points"]:
                        summary_text = "Summary Points. "
                        for k, point in enumerate(subsection["summary_points"]):
                            summary_text += f"Point {k+1}: {point}. "
                        
                        summary_result = await self.tts_service.text_to_speech(
                            text=summary_text,
                            voice=voice,
                            transcribe=False,
                            filename=f"section_{i+1}_subsec_{j+1}_all_summary_points"
                        )
                        subsection["summary_points_audio_id"] = summary_result.audio_id
                    
                    # Combine all assessment questions and answers into one audio file
                    if "assessment_questions" in subsection and subsection["assessment_questions"]:
                        qa_text = "Self-Assessment Questions. "
                        for q_idx, question_item in enumerate(subsection["assessment_questions"]):
                            qa_text += f"Question {q_idx+1}: {question_item['question']} Answer: {question_item['answer']}. "
                        
                        qa_result = await self.tts_service.text_to_speech(
                            text=qa_text,
                            voice=voice,
                            transcribe=False,
                            filename=f"section_{i+1}_subsec_{j+1}_all_questions"
                        )
                        subsection["assessment_questions_audio_id"] = qa_result.audio_id
        
        print("Course audio conversion completed.")
        return audio_course
        
    def _sanitize_filename(self, name: str) -> str:
        """Remove invalid characters from filenames"""
        # Replace characters that are not allowed in filenames
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            name = name.replace(char, '_')
        # Ensure the name doesn't end with a space or period
        name = name.rstrip('. ')
        # Limit length to avoid overly long filenames
        if len(name) > 50:
            name = name[:47] + "..."
        return name 