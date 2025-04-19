# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import config
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check for required environment variables
if not os.environ.get("GROQ_API_KEY"):
    logger.error("GROQ_API_KEY environment variable is not set!")
    print("ERROR: GROQ_API_KEY environment variable is not set!")

app = FastAPI(title="Text-Speech-Text Pipeline with GROQ Chatbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register Text-Speech-Text routes
try:
    from app.routes.audio import register_tst_routes
    register_tst_routes(app)
    logger.info("Successfully registered Text-Speech-Text routes")
except Exception as e:
    logger.error(f"Failed to register Text-Speech-Text routes: {str(e)}")
    print(f"ERROR registering TST routes: {str(e)}")

# Import and register Chatbot routes
try:
    from app.routes.chatbot import register_chatbot_routes
    register_chatbot_routes(app)
    logger.info("Successfully registered Chatbot routes")
except Exception as e:
    logger.error(f"Failed to register Chatbot routes: {str(e)}")
    print(f"ERROR registering Chatbot routes: {str(e)}")

# Import and register Course Generation routes
try:
    from app.routes.course import register_course_routes
    register_course_routes(app)
    logger.info("Successfully registered Course Generation routes")
except Exception as e:
    logger.error(f"Failed to register Course Generation routes: {str(e)}")
    print(f"ERROR registering Course Generation routes: {str(e)}")

# Import and register Course-to-Speech routes
try:
    from app.routes.course_tts import register_course_tts_routes
    register_course_tts_routes(app)
    logger.info("Successfully registered Course-to-Speech routes")
except Exception as e:
    logger.error(f"Failed to register Course-to-Speech routes: {str(e)}")
    print(f"ERROR registering Course-to-Speech routes: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "api_key_set": bool(os.environ.get("GROQ_API_KEY"))}