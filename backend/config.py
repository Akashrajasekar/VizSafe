# backend/config.py
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check for required environment variables
if not os.environ.get("GROQ_API_KEY"):
    logger.error("GROQ_API_KEY environment variable is not set!")
    print("ERROR: GROQ_API_KEY environment variable is not set!")

# App directories
AUDIO_DIR = "audio_files"
TEXT_DIR = "text_files"
GENERATED_COURSES_DIR = "generated_courses"

# Create necessary directories
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)
os.makedirs(GENERATED_COURSES_DIR, exist_ok=True)

# Default models and voices
DEFAULT_TTS_VOICE = "Celeste-PlayAI"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_SECTIONS = 5