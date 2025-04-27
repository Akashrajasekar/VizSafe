# backend/services/qva_service.py
import os
import uuid
import io
import json
from typing import Dict, Optional, List, Tuple, BinaryIO
from groq import Groq
from datetime import datetime
from backend.models.course import QuestionResponse, CourseRequest, CourseGeneratorResult
import backend.config as config
import logging

logger = logging.getLogger(__name__)

class CourseGeneratorService:
    def __init__(self, api_key: str):
        """Initialize the service with the required API key."""
        self.client = Groq(api_key=api_key)
        self.interactions: Dict[str, Dict] = {}
        
        # Create directories for audio and text files if they don't exist
        self.audio_dir = config.AUDIO_DIR
        self.text_dir = config.TEXT_DIR
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.text_dir, exist_ok=True)
        
        # Define the fixed questions
        self.questions = [
            "Which course would you like to generate?",
            "How many sections should the course have?",
            "What is the difficulty level of the course?"
        ]
    
    async def start_course_generation(self, voice: str = "Celeste-PlayAI") -> CourseGeneratorResult:
        """
        Start a new course generation interaction with the first question
        
        Args:
            voice: The voice to use for synthesis
            
        Returns:
            CourseGeneratorResult with the first question
        """
        # Generate unique IDs
        interaction_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create questions list with empty responses
        questions = [QuestionResponse(question=q) for q in self.questions]
        
        # Get the first question
        current_question_index = 0
        current_question = questions[current_question_index].question
        
        # Create file path for the prompt audio
        prompt_audio_id = str(uuid.uuid4())
        prompt_audio_path = os.path.join(self.audio_dir, f"{prompt_audio_id}_{timestamp}_q1.wav")
        
        # Convert question to speech
        logger.info(f"Converting question to speech: {current_question}")
        speech_response = self.client.audio.speech.create(
            model="playai-tts",
            voice=voice,
            input=current_question,
            response_format="wav"
        )
        
        # Save the audio file
        speech_response.write_to_file(prompt_audio_path)
        logger.info(f"Question audio saved to: {prompt_audio_path}")
        
        # Create a text file to track the interaction
        text_file_path = os.path.join(self.text_dir, f"{interaction_id}_{timestamp}_course_gen.txt")
        
        # Store the interaction data
        interaction_data = {
            "interaction_id": interaction_id,
            "timestamp": timestamp,
            "current_question_index": current_question_index,
            "questions": questions,
            "prompt_audio_id": prompt_audio_id,
            "prompt_audio_path": prompt_audio_path,
            "text_file_path": text_file_path,
            "course_request": None,
            "is_complete": False,
            "voice": voice
        }
        self.interactions[interaction_id] = interaction_data
        
        # Initialize the text file
        with open(text_file_path, "w", encoding="utf-8") as file:
            file.write("=== COURSE GENERATION INTERACTION ===\n\n")
            file.write(f"Timestamp: {timestamp}\n")
            file.write(f"Interaction ID: {interaction_id}\n\n")
            file.write("--- QUESTIONS AND RESPONSES ---\n\n")
            file.write(f"Q1: {current_question}\n")
            file.write("A1: [Waiting for response...]\n\n")
        
        # Return the result
        return CourseGeneratorResult(
            interaction_id=interaction_id,
            timestamp=timestamp,
            current_question_index=current_question_index,
            questions=questions,
            prompt_audio_id=prompt_audio_id,
            text_file_path=text_file_path,
            is_complete=False
        )
    
    async def process_audio_response(self, 
                                    interaction_id: str,
                                    audio_file: BinaryIO,
                                    voice: str = "Celeste-PlayAI") -> CourseGeneratorResult:
        """
        Process an audio response to the current question and move to the next question if available
        
        Args:
            interaction_id: The ID of the interaction
            audio_file: The audio response file
            voice: The voice to use for synthesis
            
        Returns:
            CourseGeneratorResult with updated state
        """
        if interaction_id not in self.interactions:
            raise ValueError(f"Interaction ID {interaction_id} not found")
        
        # Get interaction data
        interaction = self.interactions[interaction_id]
        
        # Check if the interaction is already complete
        if interaction["is_complete"]:
            return self._create_result_from_interaction(interaction)
        
        # Get current question index and questions list
        current_index = interaction["current_question_index"]
        questions = interaction["questions"]
        timestamp = interaction["timestamp"]
        
        # Create file path for the user's audio response
        user_audio_path = os.path.join(
            self.audio_dir, 
            f"{interaction_id}_{timestamp}_a{current_index+1}.wav"
        )
        
        # Read the file into memory
        audio_data = audio_file.read()
        
        # Save the user's audio file
        with open(user_audio_path, "wb") as f:
            f.write(audio_data)
        
        # Transcribe the user's audio response using a file path instead of file object
        try:
            logger.info("Transcribing user audio response...")
            # Open the saved file for transcription
            with open(user_audio_path, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=file,
                    model="whisper-large-v3-turbo",
                    response_format="text",
                    language="en",
                    temperature=0.0
                )
            user_response_text = transcription
            logger.info(f"User response transcribed: {user_response_text[:50]}...")
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            user_response_text = "Failed to transcribe audio response"
        
        # Update the question's response
        questions[current_index].response_text = user_response_text
        
        # Update the text file
        text_file_path = interaction["text_file_path"]
        with open(text_file_path, "r", encoding="utf-8") as file:
            content = file.readlines()
        
        # Find the line with the current answer placeholder and replace it
        answer_line = f"A{current_index+1}: [Waiting for response...]\n"
        answer_replace = f"A{current_index+1}: {user_response_text}\n"
        
        for i, line in enumerate(content):
            if line == answer_line:
                content[i] = answer_replace
                break
        
        # Check if we have more questions to ask
        is_complete = current_index >= len(self.questions) - 1
        next_index = current_index + 1 if not is_complete else current_index
        
        prompt_audio_id = interaction["prompt_audio_id"]
        prompt_audio_path = interaction["prompt_audio_path"]
        
        # If we have more questions, prepare the next one
        if not is_complete:
            # Get the next question
            next_question = questions[next_index].question
            
            # Create new audio for the next question
            prompt_audio_id = str(uuid.uuid4())
            prompt_audio_path = os.path.join(
                self.audio_dir, 
                f"{prompt_audio_id}_{timestamp}_q{next_index+1}.wav"
            )
            
            # Convert question to speech
            logger.info(f"Converting next question to speech: {next_question}")
            speech_response = self.client.audio.speech.create(
                model="playai-tts",
                voice=voice,
                input=next_question,
                response_format="wav"
            )
            
            # Save the audio file
            speech_response.write_to_file(prompt_audio_path)
            logger.info(f"Question audio saved to: {prompt_audio_path}")
            
            # Append the next question to the text file
            content.append(f"\nQ{next_index+1}: {next_question}\n")
            content.append(f"A{next_index+1}: [Waiting for response...]\n\n")
        else:
            # If complete, finalize the course request
            course_request = CourseRequest(
                course_name=questions[0].response_text,
                sections_count=self._parse_number(questions[1].response_text),
                difficulty_level=questions[2].response_text
            )
            
            interaction["course_request"] = course_request
            
            # Add a summary to the text file
            content.append("\n--- COURSE GENERATION SUMMARY ---\n\n")
            content.append(f"Course Name: {course_request.course_name}\n")
            content.append(f"Number of Sections: {course_request.sections_count}\n")
            content.append(f"Difficulty Level: {course_request.difficulty_level}\n\n")
            content.append("Course generation interaction complete.\n")
        
        # Write the updated content back to the file
        with open(text_file_path, "w", encoding="utf-8") as file:
            file.writelines(content)
        
        # Update the interaction data
        interaction["current_question_index"] = next_index
        interaction["questions"] = questions
        interaction["is_complete"] = is_complete
        interaction["prompt_audio_id"] = prompt_audio_id
        interaction["prompt_audio_path"] = prompt_audio_path
        
        if is_complete:
            interaction["course_request"] = CourseRequest(
                course_name=questions[0].response_text,
                sections_count=self._parse_number(questions[1].response_text),
                difficulty_level=questions[2].response_text
            )
        
        # Return the updated result
        return self._create_result_from_interaction(interaction)
    
    def get_audio_file(self, audio_id: str) -> Tuple[bytes, bool]:
        """Get an audio file by ID"""
        # Look through all interactions to find the audio ID
        for interaction_id, data in self.interactions.items():
            # Check if this is a prompt audio ID
            if data.get("prompt_audio_id") == audio_id:
                audio_path = data.get("prompt_audio_path")
                if audio_path and os.path.exists(audio_path):
                    try:
                        with open(audio_path, "rb") as file:
                            content = file.read()
                        return content, True
                    except Exception as e:
                        logger.error(f"Error reading audio file: {str(e)}")
                        return None, False
        
        return None, False
    
    def get_interaction(self, interaction_id: str) -> Optional[Dict]:
        """Get interaction details by ID"""
        return self.interactions.get(interaction_id)
    
    def _create_result_from_interaction(self, interaction: Dict) -> CourseGeneratorResult:
        """Convert interaction dict to CourseGeneratorResult"""
        result = CourseGeneratorResult(
            interaction_id=interaction["interaction_id"],
            timestamp=interaction["timestamp"],
            current_question_index=interaction["current_question_index"],
            questions=interaction["questions"],
            prompt_audio_id=interaction["prompt_audio_id"],
            text_file_path=interaction["text_file_path"],
            is_complete=interaction["is_complete"]
        )
        
        if interaction["is_complete"] and interaction.get("course_request"):
            result.course_request = CourseRequest(
                course_name=interaction["course_request"].course_name,
                sections_count=interaction["course_request"].sections_count,
                difficulty_level=interaction["course_request"].difficulty_level
            )
        
        return result
    
    def _parse_number(self, text: str) -> Optional[int]:
        """Try to extract a number from text"""
        if not text:
            return None
            
        # Try to find a number in the text
        import re
        numbers = re.findall(r'\d+', text)
        if numbers:
            try:
                return int(numbers[0])
            except ValueError:
                pass
        
        return None
    
    def list_interactions(self):
        """List all interactions"""
        result = []
        for interaction_id, interaction in self.interactions.items():
            item = {
                "interaction_id": interaction_id,
                "timestamp": interaction["timestamp"],
                "is_complete": interaction["is_complete"],
                "current_question": self.questions[interaction["current_question_index"]]
            }
            
            if interaction["is_complete"] and interaction.get("course_request"):
                item["course_request"] = {
                    "course_name": interaction["course_request"].course_name,
                    "sections_count": interaction["course_request"].sections_count,
                    "difficulty_level": interaction["course_request"].difficulty_level
                }
            
            result.append(item)
        
        return result