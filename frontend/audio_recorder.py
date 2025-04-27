# frontend/audio_recorder.py

import streamlit as st
from io import BytesIO
import base64
import json

def audio_recorder(key=None, start_prompt="Click to start recording", stop_prompt="Click to stop recording"):
    """
    Create an audio recorder component for Streamlit
    
    Args:
        key: A unique key for the component
        start_prompt: Text to display on the start button
        stop_prompt: Text to display on the stop button
        
    Returns:
        Binary audio data if recording was made and submitted, None otherwise
    """
    # Generate a unique key if not provided
    if key is None:
        key = "audio_recorder"
    
    # Custom JavaScript for recording audio
    st.markdown(
        f"""
        <style>
        .stButton > button {{
            width: 100%;
        }}
        </style>
        <script>
        const audioRecorder = {{
            audioBlobs: [],
            mediaRecorder: null,
            streamBeingCaptured: null,
            
            start: function() {{
                // Request audio recording permission and start recording
                navigator.mediaDevices.getUserMedia({{ audio: true }})
                .then(stream => {{
                    this.streamBeingCaptured = stream;
                    this.mediaRecorder = new MediaRecorder(stream);
                    this.audioBlobs = [];
                    
                    this.mediaRecorder.addEventListener("dataavailable", event => {{
                        this.audioBlobs.push(event.data);
                    }});
                    
                    this.mediaRecorder.start();
                }});
            }},
            
            stop: function() {{
                if (this.mediaRecorder) {{
                    this.mediaRecorder.stop();
                    
                    // Stop all audio tracks
                    this.streamBeingCaptured.getTracks().forEach(track => track.stop());
                    
                    return new Promise(resolve => {{
                        this.mediaRecorder.addEventListener("stop", () => {{
                            // Create a blob from all audio chunks
                            const audioBlob = new Blob(this.audioBlobs, {{ type: 'audio/wav' }});
                            
                            // Convert to base64
                            const reader = new FileReader();
                            reader.readAsDataURL(audioBlob);
                            reader.onloadend = () => {{
                                const base64Audio = reader.result.split(',')[1];
                                resolve(base64Audio);
                            }};
                        }});
                    }});
                }}
                return Promise.resolve(null);
            }}
        }};
        
        // Communication with Streamlit
        const sendMessageToStreamlit = data => {{
            const stringifiedData = JSON.stringify(data);
            window.parent.postMessage({{
                type: "streamlit:setComponentValue",
                value: stringifiedData,
                dataType: "json"
            }}, "*");
        }};
        
        // Initialize recording state
        window.recorder_state = {{
            isRecording: false,
            audioData: null
        }};
        
        // Handle button click events
        const buttonClicked = async (buttonKey) => {{
            if (buttonKey === "start_recording_{key}") {{
                window.recorder_state.isRecording = true;
                audioRecorder.start();
                sendMessageToStreamlit({{ state: "recording", data: null }});
            }} 
            else if (buttonKey === "stop_recording_{key}") {{
                if (window.recorder_state.isRecording) {{
                    window.recorder_state.isRecording = false;
                    const base64Audio = await audioRecorder.stop();
                    sendMessageToStreamlit({{ state: "stopped", data: base64Audio }});
                }}
            }}
        }};
        
        // Register event listeners for the buttons
        document.addEventListener('DOMContentLoaded', (event) => {{
            // Find buttons and add click handlers
            document.body.addEventListener('click', function(e) {{
                if (e.target.closest('button[data-testid="baseButton-secondary"]')) {{
                    if (e.target.textContent.includes("{start_prompt}")) {{
                        buttonClicked("start_recording_{key}");
                    }}
                    else if (e.target.textContent.includes("{stop_prompt}")) {{
                        buttonClicked("stop_recording_{key}");
                    }}
                }}
            }});
        }});
        </script>
        """,
        unsafe_allow_html=True
    )
    
    # Create UI for the audio recorder
    col1, col2 = st.columns(2)
    
    with col1:
        start_button = st.button(f"{start_prompt}", key=f"start_{key}")
    
    with col2:
        stop_button = st.button(f"{stop_prompt}", key=f"stop_{key}")
    
    # Handle component state
    component_state = st.session_state.get(f"recorder_state_{key}", {"state": "idle", "data": None})
    
    # Get the component value from session state
    if "audio_recorder_value" in st.session_state:
        try:
            value = json.loads(st.session_state.audio_recorder_value)
            component_state = value
            st.session_state[f"recorder_state_{key}"] = component_state
        except (json.JSONDecodeError, TypeError):
            pass
    
    # Show recording status
    if component_state["state"] == "recording":
        st.warning("Recording in progress...")
    elif component_state["state"] == "stopped" and component_state["data"]:
        st.success("Recording complete!")
        
        # Display the audio player if we have data
        if component_state["data"]:
            audio_bytes = base64.b64decode(component_state["data"])
            st.audio(audio_bytes, format="audio/wav")
            
            # Return the audio data
            return audio_bytes
    
    return None
# Add these debugging functions to help troubleshoot audio recording
# Place this code at the bottom of audio_recorder.py or in a separate utilities.py file

def debug_audio_recorder(audio_data=None, verbose=True):
    """
    Debug audio recording issues
    
    Args:
        audio_data: The audio data to debug
        verbose: Whether to print verbose information
    """
    st.markdown("### Audio Recorder Debugging")
    
    # Check browser capabilities
    st.markdown("""
    <script>
    function checkAudioCapabilities() {
        const capabilities = {
            mediaDevices: !!navigator.mediaDevices,
            getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
            mediaRecorder: !!window.MediaRecorder,
            audioContext: !!window.AudioContext || !!window.webkitAudioContext,
            permissions: 'unknown'
        };
        
        // Check permissions if possible
        if (navigator.permissions && navigator.permissions.query) {
            navigator.permissions.query({name:'microphone'})
            .then(function(permissionStatus) {
                capabilities.permissions = permissionStatus.state;
                sendResults(capabilities);
            })
            .catch(function() {
                capabilities.permissions = 'error_checking';
                sendResults(capabilities);
            });
        } else {
            sendResults(capabilities);
        }
        
        function sendResults(capabilities) {
            const stringifiedData = JSON.stringify(capabilities);
            window.parent.postMessage({
                type: "streamlit:setComponentValue",
                value: stringifiedData,
                dataType: "json"
            }, "*");
        }
    }
    
    // Run the check
    checkAudioCapabilities();
    </script>
    """, unsafe_allow_html=True)
    
    # Check if we received any audio data
    if audio_data is not None:
        st.success("✅ Audio data received")
        # Display audio data size
        data_size = len(audio_data)
        st.write(f"Audio data size: {data_size} bytes")
        
        # Check if the audio data is valid
        if data_size < 100:
            st.error("❌ Audio data too small - likely invalid")
        elif data_size < 1000:
            st.warning("⚠️ Audio data is very small - might be corrupt")
        else:
            st.success("✅ Audio data size looks reasonable")
        
        # Display the first few bytes for debugging
        if verbose:
            st.write("First 20 bytes (hex):")
            import binascii
            hex_data = binascii.hexlify(audio_data[:20]).decode('utf-8')
            st.code(hex_data, language="text")
            
            # Check WAV header
            if data_size >= 44:  # Minimum WAV header size
                if audio_data[:4] == b'RIFF' and audio_data[8:12] == b'WAVE':
                    st.success("✅ Valid WAV header detected")
                else:
                    st.error("❌ Invalid WAV header - not a proper WAV file")
            
        # Allow downloading the audio for external analysis
        st.download_button(
            "Download audio for analysis",
            data=audio_data,
            file_name="debug_audio.wav",
            mime="audio/wav"
        )
    else:
        st.error("❌ No audio data received")
    
    # Display browser capabilities if we get them
    if "audio_capabilities" in st.session_state:
        try:
            capabilities = json.loads(st.session_state.audio_capabilities)
            st.write("### Browser Audio Capabilities:")
            
            cap_status = []
            for key, value in capabilities.items():
                icon = "✅" if value == True or value == "granted" else "❌" 
                if value == "prompt":
                    icon = "⚠️"
                    
                cap_status.append(f"{icon} **{key}**: {value}")
            
            for status in cap_status:
                st.markdown(status)
                
            if not capabilities.get("mediaDevices", False) or not capabilities.get("getUserMedia", False):
                st.error("Your browser doesn't support audio recording. Try Chrome or Firefox.")
            
            if capabilities.get("permissions") == "denied":
                st.error("Microphone permission denied. Please allow microphone access in your browser settings.")
                
        except Exception as e:
            st.error(f"Error parsing browser capabilities: {str(e)}")
    
    return None

def test_audio_format(audio_data):
    """Generate a test file with your audio format and help debug it"""
    import wave
    import numpy as np
    from io import BytesIO
    
    st.markdown("### Testing Audio Format Compatibility")
    
    # Try to create a test WAV file with specific parameters
    sample_rate = 16000  # 16 kHz, good for speech
    duration = 1  # seconds
    
    # Generate a 440 Hz sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    test_audio = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    
    # Convert to 16-bit PCM
    test_audio_int = (test_audio * 32767).astype(np.int16)
    
    # Create a BytesIO object
    buffer = BytesIO()
    
    # Write as WAV file
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(test_audio_int.tobytes())
    
    # Get the WAV data
    test_wav_data = buffer.getvalue()
    
    # Display information
    st.write(f"Test audio file created: {len(test_wav_data)} bytes")
    st.audio(test_wav_data, format="audio/wav")
    
    # Allow downloading for testing with Groq API
    st.download_button(
        "Download test audio file",
        data=test_wav_data,
        file_name="test_audio.wav",
        mime="audio/wav"
    )
    
    # Compare with received audio (if any)
    if audio_data is not None:
        st.write("### Comparing with your recorded audio:")
        st.write(f"Your audio file size: {len(audio_data)} bytes")
        
        # Check format differences
        try:
            with wave.open(BytesIO(audio_data), 'rb') as wf_user:
                user_channels = wf_user.getnchannels()
                user_sample_width = wf_user.getsampwidth()
                user_framerate = wf_user.getframerate()
                user_frames = wf_user.getnframes()
                
                st.write(f"Your audio: {user_channels} channels, {user_sample_width*8} bits, {user_framerate} Hz")
                st.write(f"Test audio: 1 channel, 16 bits, {sample_rate} Hz")
                
                # Provide recommendations
                if user_channels > 1:
                    st.warning("Your audio has multiple channels. Groq Whisper works best with mono audio.")
                
                if user_framerate < 16000:
                    st.warning("Your sample rate is low. Groq Whisper works best with 16kHz or higher.")
        except Exception as e:
            st.error(f"Error analyzing your audio: {str(e)}")
    
    return test_wav_data