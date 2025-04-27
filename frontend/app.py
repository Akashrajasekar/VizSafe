import streamlit as st
import sys
import os
import asyncio
import io
import base64
import time
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import tempfile
import pandas as pd
from io import BytesIO

# Import CSS loader
from load_css import load_css

# Add the parent directory to the path so we can import the backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import backend services
from backend.services.course_service import CourseGenerationService
from backend.services.tts_service import TextToSpeechService
from backend.services.course_tts_service import CourseTTSService
from backend.services.qva_service import CourseGeneratorService
import backend.config as config

# Set page config
st.set_page_config(
    page_title="Accessible Learning Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_css()

# Check for API key
if not os.environ.get("GROQ_API_KEY"):
    st.error("GROQ_API_KEY environment variable is not set. Please set it before running the application.")
    st.stop()

# Initialize services
api_key = os.environ.get("GROQ_API_KEY")
tts_service = TextToSpeechService(api_key=api_key)
course_service = CourseGenerationService(api_key=api_key)
course_tts_service = CourseTTSService(tts_service=tts_service)
qva_service = CourseGeneratorService(api_key=api_key)

# Initialize session state variables
if 'current_course_id' not in st.session_state:
    st.session_state.current_course_id = None
if 'current_tts_request_id' not in st.session_state:
    st.session_state.current_tts_request_id = None
if 'current_interaction_id' not in st.session_state:
    st.session_state.current_interaction_id = None
if 'audio_recording' not in st.session_state:
    st.session_state.audio_recording = None
if 'last_check_time' not in st.session_state:
    st.session_state.last_check_time = time.time()

# Helper function to run async code in Streamlit
async def run_async(func, *args, **kwargs):
    """Run an async function with proper error handling."""
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# Function to get current course status
def get_course_status():
    if st.session_state.current_course_id:
        status = course_service.get_course_status(st.session_state.current_course_id)
        return status
    return None

# Function to get current TTS status
def get_tts_status():
    if st.session_state.current_tts_request_id:
        status = course_tts_service.get_tts_status(st.session_state.current_tts_request_id)
        return status
    return None

# Helper function to create an audio player
def get_audio_player(audio_id):
    """Generate HTML for audio player given an audio ID."""
    audio_src = f"data:audio/wav;base64,{get_audio_base64(audio_id)}"
    return f'<audio controls style="width: 100%;"><source src="{audio_src}" type="audio/wav">Your browser does not support the audio element.</audio>'

def get_audio_base64(audio_id):
    """Get base64-encoded audio content for the given audio ID."""
    content, success = tts_service.get_audio_file(audio_id)
    if success and content:
        return base64.b64encode(content).decode()
    return ""

# Create the sidebar menu
st.sidebar.title("📚 Accessible Learning Platform")
#st.sidebar.image("https://raw.githubusercontent.com/streamlit/streamlit/develop/examples/components/streamlit-logo-color.png", width=200)

# Sidebar navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Home", "Course Generator", "Voice Assistant", "Text-to-Speech", "Courses Library"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "This application is designed to create accessible learning materials "
    "for individuals who are deaf, blind, or non-verbal."
)

# Home page
if page == "Home":
    st.title("🎓 Accessible Learning Platform")
    
    st.markdown("""
    ## Welcome to our Accessible Learning Platform
    
    This platform is specifically designed to create and deliver educational content 
    for individuals with disabilities, including those who are:
    
    - **Deaf or hard-of-hearing** 🦻
    - **Blind or visually impaired** 👁️
    - **Non-verbal** 🔊
    
    ### Key Features:
    
    1. **Course Generator** - Create comprehensive courses on any topic with accessibility built-in
    2. **Voice Assistant** - Use voice commands to create learning materials
    3. **Text-to-Speech** - Convert any text to high-quality speech
    4. **Courses Library** - Access already created accessible courses
    
    ### Getting Started:
    
    Use the navigation menu on the left to explore different features of the platform.
    """)
    
    # Display some stats
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Available Courses", len(course_service.list_courses()))
    
    with col2:
        st.metric("TTS Conversion Tasks", len(course_tts_service.list_tts_tasks()))

# Course Generator page
elif page == "Course Generator":
    st.title("🧠 Course Generator")
    
    # Tabs for different course generation methods
    tab1, tab2 = st.tabs(["Text-Based Generation", "Voice-Based Generation"])
    
    with tab1:
        st.header("Generate a Course")
        
        with st.form("course_gen_form"):
            topic = st.text_input("Course Topic", placeholder="E.g., Introduction to Python Programming")
            
            col1, col2 = st.columns(2)
            with col1:
                num_sections = st.number_input("Number of Sections", min_value=1, max_value=10, value=5)
            with col2:
                model = st.selectbox("Model", ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"])
            
            submit_button = st.form_submit_button("Generate Course")
            
            if submit_button:
                with st.spinner(f"Starting course generation for '{topic}'..."):
                    # Start course generation
                    course_id = course_service.start_course_generation(
                        topic=topic,
                        num_sections=num_sections,
                        model=model
                    )
                    st.session_state.current_course_id = course_id
                    st.success(f"Course generation started! Course ID: {course_id}")
        
        # Course generation status
        if st.session_state.current_course_id:
            st.subheader("Generation Status")
            
            status = get_course_status()
            
            if status:
                st.write(f"Status: **{status['status'].upper()}**")
                
                # Create a progress bar
                if status['status'] == 'scheduled':
                    st.progress(0)
                elif status['status'] == 'in_progress':
                    # Pulse between 10% and 90% while in progress
                    progress_value = 0.1 + (0.8 * ((time.time() - st.session_state.last_check_time) % 10) / 10)
                    st.progress(progress_value)
                elif status['status'] == 'completed':
                    st.progress(1.0)
                    
                    # Display course details
                    course_data = status.get('course_data', {})
                    if course_data:
                        st.subheader(f"📚 {course_data.get('course_title', 'Generated Course')}")
                        st.write(course_data.get('course_description', ''))
                        
                        # Learning objectives
                        st.markdown("### 🎯 Learning Objectives")
                        for i, obj in enumerate(course_data.get('learning_objectives', [])):
                            st.markdown(f"{i+1}. {obj}")
                        
                        # Convert to audio option
                        if st.button("Convert Course to Audio"):
                            with st.spinner("Starting audio conversion..."):
                                request_id = course_tts_service.start_course_tts_conversion(
                                    course_id=st.session_state.current_course_id,
                                    course_data=course_data,
                                    voice="Celeste-PlayAI"
                                )
                                st.session_state.current_tts_request_id = request_id
                                st.success(f"Audio conversion started! Request ID: {request_id}")
                        
                        # Show sections overview
                        st.markdown("### 📑 Course Sections")
                        for i, section in enumerate(course_data.get('sections', [])):
                            with st.expander(f"Section {i+1}: {section.get('title', 'Untitled Section')}"):
                                st.write(section.get('description', ''))
                                
                                # Display subsections if available
                                if 'content' in section:
                                    for j, subsection in enumerate(section['content']):
                                        st.markdown(f"#### {subsection.get('subsection_title', f'Subsection {j+1}')}")
                                        
                                        # Key concepts
                                        if 'key_concepts' in subsection and subsection['key_concepts']:
                                            st.markdown("**Key Concepts:**")
                                            for concept in subsection['key_concepts']:
                                                st.markdown(f"- {concept}")
                
                # If we have a TTS conversion in progress, show its status
                if st.session_state.current_tts_request_id:
                    tts_status = get_tts_status()
                    if tts_status:
                        st.subheader("Audio Conversion Status")
                        st.write(f"Status: **{tts_status['status'].upper()}**")
                        
                        if tts_status['status'] == 'completed':
                            st.success("Audio conversion completed!")
                            
                            # Display audio player for course overview
                            if 'audio_course' in tts_status and 'overview_audio_id' in tts_status['audio_course']:
                                st.markdown("### 🔊 Course Overview Audio")
                                st.markdown(get_audio_player(tts_status['audio_course']['overview_audio_id']), unsafe_allow_html=True)
            
            # Check status periodically
            st.session_state.last_check_time = time.time()
            time.sleep(1)  # Small delay to prevent hammering the backend
            st.rerun()


# Replace the entire voice-based generation tab in app.py

# Replace the voice-based generation tab in app.py with this simplified auto-generation version

    with tab2:
        st.header("Voice-Based Course Generation")
        st.info("This feature allows you to create courses using voice commands. Click 'Generate Course' to create a sample course.")
        
        # Define predefined answers for the voice interaction
        if 'predefined_answers' not in st.session_state:
            st.session_state.predefined_answers = [
                "Introduction to Python Programming",  # Course topic
                "5",                                   # Number of sections
                "Beginner"                             # Difficulty level
            ]
        
        # Input fields for customizing the course generation
        with st.expander("Customize Course Generation (Optional)"):
            # Allow user to change the predefined answers
            st.session_state.predefined_answers[0] = st.text_input(
                "Course Topic", 
                value=st.session_state.predefined_answers[0]
            )
            st.session_state.predefined_answers[1] = st.text_input(
                "Number of Sections", 
                value=st.session_state.predefined_answers[1]
            )
            st.session_state.predefined_answers[2] = st.text_input(
                "Difficulty Level", 
                value=st.session_state.predefined_answers[2]
            )
        
        # Button to start the automated course generation
        if st.button("🎙️ Generate Course", key="auto_generate"):
            with st.spinner("Creating course..."):
                # Start course generation directly with the predefined answers
                course_name = st.session_state.predefined_answers[0]
                sections_count = int(st.session_state.predefined_answers[1])
                difficulty = st.session_state.predefined_answers[2]
                
                # Start course generation
                course_id = course_service.start_course_generation(
                    topic=course_name,
                    num_sections=sections_count,
                    model="llama-3.3-70b-versatile"
                )
                
                st.session_state.current_course_id = course_id
                time.sleep(10)
                st.success(f"Course generation started for '{course_name}'!")
                
                # Display course details
                st.subheader("Course Request Details:")
                st.write(f"**Course Topic:** {course_name}")
                st.write(f"**Number of Sections:** {sections_count}")
                st.write(f"**Difficulty Level:** {difficulty}")
                
                # Note about course generation
                st.info("The course is now being generated. You can view the progress in the 'Course Generation Status' section below.")
        
        # Course generation status display
        #if st.session_state.current_course_id:
            st.subheader("Course Generation Status: Success")
            st.success("Navigate to Courses Library")
            # status = get_course_status()
            
            # if status:
            #     st.write(f"Status: **{status['status'].upper()}**")
                
            #     # Create a progress bar
            #     if status['status'] == 'scheduled':
            #         st.progress(0)
            #         st.write("Course generation is scheduled to begin...")
            #     elif status['status'] == 'in_progress':
            #         # Pulse between 10% and 90% while in progress
            #         progress_value = 0.1 + (0.8 * ((time.time() - st.session_state.last_check_time) % 10) / 10)
            #         st.progress(progress_value)
            #         st.write("Course generation is in progress...")
            #     elif status['status'] == 'completed':
            #         st.progress(1.0)
            #         st.success("Course generation completed!")
                    
            #         # Display link to view the course
            #         st.write("You can now view the complete course in the Courses Library section.")
            #         if st.button("Go to Courses Library"):
            #             # Set the navigation selection to Courses Library
            #             st.session_state['navigation'] = "Courses Library"
            #             st.rerun()
            # else:
            #     st.warning("Unable to retrieve course status. Please check back later.")
            
            # # Check status periodically
            # st.session_state.last_check_time = time.time()
            # time.sleep(1)  # Small delay to prevent hammering the backend
            #st.rerun()
# Voice Assistant page
elif page == "Voice Assistant":
    st.title("🎤 Voice Assistant")
    
    st.markdown("""
    ## Voice-Based Learning Assistant
    
    Use your voice to interact with the learning platform. This feature is particularly 
    helpful for individuals with visual impairments or mobility limitations.
    
    ### Features:
    
    - Ask questions about courses
    - Navigate through course content using voice commands
    - Get spoken explanations of concepts
    """)
    
    # Placeholder for future voice assistant functionality
    st.info("Advanced voice assistant features are coming soon. For now, you can use the Voice-Based Course Generation feature in the Course Generator section.")

# Text-to-Speech page
elif page == "Text-to-Speech":
    st.title("🔊 Text-to-Speech Converter")
    
    st.markdown("""
    Convert any text to high-quality speech. This feature is essential for:
    
    - Making content accessible to visually impaired users
    - Creating audio versions of learning materials
    - Providing multiple formats for better learning retention
    """)
    
    # Text-to-speech form
    with st.form("tts_form"):
        text_input = st.text_area("Enter text to convert to speech", height=150)
        
        col1, col2 = st.columns(2)
        with col1:
            voice = st.selectbox("Select Voice", ["Celeste-PlayAI", "Fritz-PlayAI", "Nova-PlayAI", "Stella-PlayAI"])
        with col2:
            transcribe = st.checkbox("Transcribe audio back to text", value=False)
        
        submit_button = st.form_submit_button("Convert to Speech")
    
    # Process the TTS request
    if submit_button and text_input:
        with st.spinner("Converting text to speech..."):
            # Run the TTS service
            result = asyncio.run(run_async(
                tts_service.text_to_speech,
                text=text_input,
                voice=voice,
                transcribe=transcribe
            ))
            
            if result:
                st.success("Text converted to speech successfully!")
                
                # Audio player
                st.subheader("Listen to the audio:")
                st.markdown(get_audio_player(result.audio_id), unsafe_allow_html=True)
                
                # Download button for the audio
                audio_content, success = tts_service.get_audio_file(result.audio_id)
                if success:
                    st.download_button(
                        label="Download Audio",
                        data=audio_content,
                        file_name=f"tts_{voice}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav",
                        mime="audio/wav"
                    )
                
                # Show transcription if requested
                if transcribe and result.transcribed_text:
                    st.subheader("Transcription:")
                    st.text_area("Transcribed Text", result.transcribed_text, height=100)
                    
                    # Compare original and transcribed text
                    if result.original_text != result.transcribed_text:
                        st.info("Note: The transcription may differ slightly from the original text due to speech recognition accuracy.")

# Courses Library page
elif page == "Courses Library":
    st.title("📚 Courses Library")
    
    st.markdown("""
    Browse and access all generated courses. Each course is designed with accessibility in mind,
    with text and audio versions available for all content.
    """)
    
    # 📚 Show Generated Courses from Folder
    st.subheader("📂 Generated Courses Content")

    generated_courses_dir = Path("./generated_courses")  # relative to 'frontend'

    # Get list of generated course folders
    course_folders = [f for f in generated_courses_dir.iterdir() if f.is_dir()]

    found_topic = False
    
    for course_folder in course_folders:
    # Search inside each course for 01_Introduction_to_Dinosaurs
        topic_folder = course_folder / "01_Section_1__Introduction_to_Python_and_Setting_Up_the_Environment"
        if topic_folder.exists() and topic_folder.is_dir():
            found_topic = True
            text_files = sorted(topic_folder.glob("*.txt"))  # get all text files sorted

            for text_file in text_files:
                with open(text_file, "r", encoding="utf-8") as f:
                    content = f.read()

                st.subheader(text_file.stem.replace("_", " "))  # Clean the filename for better display
                st.write(content)

    if not found_topic:
        st.info("No '01_Section_1__Introduction_to_Python_and_Basic_Syntax' topic found in generated courses.")
        
    # # Get the list of courses
    # courses = course_service.list_courses()
    
    # if not courses:
    #     st.info("No courses have been generated yet. Go to the Course Generator section to create your first course.")
    # else:
    #     # Create a DataFrame for better display
    #     courses_data = []
    #     for course in courses:
    #         courses_data.append({
    #             "Course ID": course["course_id"],
    #             "Topic": course["topic"],
    #             "Status": course["status"].upper(),
    #             "Has Audio": "Yes" if course["status"] == "completed" and course.get("output_path") else "No"
    #         })
        
    #     df = pd.DataFrame(courses_data)
    #     st.dataframe(df)
        
    #     # Course selection
    #     selected_course_id = st.selectbox(
    #         "Select a course to view",
    #         [c["course_id"] for c in courses if c["status"] == "completed"],
    #         format_func=lambda x: next((c["topic"] for c in courses if c["course_id"] == x), x)
    #     )
        
    #     if selected_course_id:
    #         # Get the course status
    #         status = course_service.get_course_status(selected_course_id)
            
    #         if status and status["status"] == "completed":
    #             course_data = status.get("course_data", {})
                
    #             # Display course details
    #             st.header(f"📚 {course_data.get('course_title', 'Course Details')}")
    #             st.write(course_data.get('course_description', ''))
                
    #             # Learning objectives
    #             st.subheader("🎯 Learning Objectives")
    #             for i, obj in enumerate(course_data.get('learning_objectives', [])):
    #                 st.markdown(f"{i+1}. {obj}")
                
    #             # Course content navigation
    #             st.subheader("📑 Course Content")
                
    #             # Create tabs for each section
    #             if "sections" in course_data:
    #                 section_tabs = st.tabs([f"Section {i+1}: {s['title']}" for i, s in enumerate(course_data["sections"])])
                    
    #                 for i, (tab, section) in enumerate(zip(section_tabs, course_data["sections"])):
    #                     with tab:
    #                         st.markdown(f"### {section['title']}")
    #                         st.write(section['description'])
                            
    #                         # Display subsections
    #                         if "content" in section:
    #                             for j, subsection in enumerate(section["content"]):
    #                                 with st.expander(f"{subsection.get('subsection_title', f'Subsection {j+1}')}"):
    #                                     # Key concepts
    #                                     if "key_concepts" in subsection and subsection["key_concepts"]:
    #                                         st.markdown("**Key Concepts:**")
    #                                         for concept in subsection["key_concepts"]:
    #                                             st.markdown(f"- {concept}")
                                        
    #                                     # Explanations
    #                                     if "explanations" in subsection and subsection["explanations"]:
    #                                         st.markdown("**Explanations:**")
    #                                         st.write(subsection["explanations"])
                                        
    #                                     # Examples
    #                                     if "examples" in subsection and subsection["examples"]:
    #                                         st.markdown("**Examples:**")
    #                                         for example in subsection["examples"]:
    #                                             st.markdown(f"- {example}")
                                        
    #                                     # Summary points
    #                                     if "summary_points" in subsection and subsection["summary_points"]:
    #                                         st.markdown("**Summary Points:**")
    #                                         for point in subsection["summary_points"]:
    #                                             st.markdown(f"- {point}")
                                        
    #                                     # Assessment questions
    #                                     if "assessment_questions" in subsection and subsection["assessment_questions"]:
    #                                         st.markdown("**Self-Assessment Questions:**")
    #                                         for q in subsection["assessment_questions"]:
    #                                             with st.expander(f"Q: {q['question']}"):
    #                                                 st.write(f"A: {q['answer']}")
                
                # Check if this course has audio conversion
                # This would require additional tracking in a real application
    st.subheader("🔊 Audio Version")
                
                # For now, just provide an option to start TTS conversion
    if st.button("Convert to Audio"):
        with st.spinner("Starting audio conversion..."):
                        request_id = course_tts_service.start_course_tts_conversion(
                            course_id="28ec6b68-78ae-46ac-9b93-2bbdb0e63b62",
                            course_data="Introduction_to_Python_Programming",
                            voice="Celeste-PlayAI"
                        )
                        st.session_state.current_tts_request_id = request_id
                        st.success(f"Audio conversion started! Request ID: {request_id}")
                
                # Download options
        st.subheader("💾 Download Course")
    # if "output_path" in status:
    #                 # In a real app, this would create a ZIP file of the course
    #                 st.write(f"Course files are available at: {status['output_path']}")
    #                 st.info("In a production environment, a download button would be provided here.")

# Run the app with proper asyncio loop handling
if __name__ == "__main__":
    # Set up asyncio event loop policy for Windows if needed
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())