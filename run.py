#!/usr/bin/env python
"""
Utility script to run the Accessible Learning Platform.
This creates necessary directories and launches the Streamlit app.
"""
import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check for Groq API key
if not os.environ.get("GROQ_API_KEY"):
    print("ERROR: GROQ_API_KEY environment variable is not set!")
    print("Please set your Groq API key in a .env file or as an environment variable.")
    print("Example: export GROQ_API_KEY='your-api-key-here'")
    sys.exit(1)

# Create necessary directories
directories = ["audio_files", "text_files", "generated_courses"]
for directory in directories:
    Path(directory).mkdir(exist_ok=True)
    print(f"✓ Ensured directory exists: {directory}")

# Run the Streamlit app
print("\n🚀 Starting the Accessible Learning Platform...")
try:
    os.chdir("frontend")
    subprocess.run(["streamlit", "run", "app.py"])
except KeyboardInterrupt:
    print("\n👋 Shutting down the Accessible Learning Platform...")
except Exception as e:
    print(f"\n❌ Error running the application: {str(e)}")
    sys.exit(1)