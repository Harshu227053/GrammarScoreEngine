import streamlit as st
import speech_recognition as sr
import os
import tempfile
import time
import base64

def transcribe_audio(audio_path):
    """
    Transcribe the given audio file to text using speech recognition.
    
    Parameters:
    -----------
    audio_path : str
        Path to the audio file to transcribe
        
    Returns:
    --------
    str
        Transcribed text, or empty string if transcription failed
    """
    # Initialize recognizer
    recognizer = sr.Recognizer()
    
    # Check if the file exists
    if not os.path.exists(audio_path):
        st.error(f"Audio file not found at {audio_path}")
        return ""
    
    # Load the audio file
    try:
        with sr.AudioFile(audio_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source)
            
            # Record the audio
            audio_data = recognizer.record(source)
            
            # Try to recognize the speech
            try:
                # Use Google's speech recognition service
                text = recognizer.recognize_google(audio_data)
                return text
            except sr.UnknownValueError:
                st.warning("Speech Recognition could not understand the audio")
                return ""
            except sr.RequestError as e:
                st.error(f"Could not request results from Speech Recognition service; {e}")
                return ""
    except Exception as e:
        # Handle unsupported audio formats or other errors
        if "audio file could not be read" in str(e).lower():
            st.error("The audio file format is not supported. Please use WAV, MP3, M4A, or OGG format.")
        else:
            st.error(f"Error processing the audio file: {e}")
        return ""

def get_sample_audio_data():
    """
    Create a simulated audio data object for environments where microphone
    access is not available (like Replit).
    
    Returns:
    --------
    AudioData
        A sample audio data object containing sample speech
    """
    # Sample text to use for demonstration
    sample_texts = [
        "Hello world this is a grammar test",
        "I have been working on my english skills for many years",
        "This sentence contains two grammatical error",
        "She don't like ice cream but I do",
        "The weather are nice today and we should go outside",
        "I would of gone to the party if I had been invited",
        "Between you and I this project is very exciting",
        "Their going to announce the winners tomorrow morning",
        "I have went to the store already",
        "The book was laying on the table all day"
    ]
    
    import random
    selected_text = random.choice(sample_texts)
    
    # Create a temporary WAV file with silent audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        sample_path = tmp_file.name
    
    # Create recognizer and AudioData object with text
    recognizer = sr.Recognizer()
    
    # In a real scenario, we would have actual audio data here
    # For this simulation, we'll create a minimal AudioData object
    # and attach our sample text to be returned by recognize_google
    
    # Use a very small WAV file as a placeholder
    with open(sample_path, 'wb') as f:
        # Write a minimal WAV header for a tiny silent audio clip
        f.write(base64.b64decode(
            'UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA='))
    
    # Create audio data from the sample file
    with sr.AudioFile(sample_path) as source:
        audio_data = recognizer.record(source)
    
    # Clean up
    os.remove(sample_path)
    
    # Add the selected text as an attribute to be used in simulation
    audio_data.sample_text = selected_text
    
    return audio_data

def record_audio(duration=5):
    """
    Record audio from the microphone for a specified duration.
    In environments without microphone access (like Replit), 
    this will simulate recording using sample text.
    
    Parameters:
    -----------
    duration : int
        The duration (in seconds) to record
        
    Returns:
    --------
    AudioData
        The recorded or simulated audio data
    """
    try:
        # First try to use an actual microphone
        recognizer = sr.Recognizer()
        
        # Try to initialize the microphone
        try:
            # This will fail in Replit environment
            sr.Microphone()
            microphone_available = True
        except (OSError, ImportError, AttributeError) as e:
            microphone_available = False
            st.warning("Microphone access is not available in this environment. Using simulated speech instead.")
        
        if microphone_available:
            # Real microphone recording
            with sr.Microphone() as source:
                # Adjust for ambient noise
                st.write("Adjusting for ambient noise... Please wait.")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Record the audio
                st.write(f"Recording for {duration} seconds...")
                audio_data = recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
                st.write("Recording complete!")
                
                return audio_data
        else:
            # Simulated recording for environments without microphone
            st.write(f"Simulating recording for {duration} seconds...")
            
            # Add a slight delay to simulate recording time
            progress_bar = st.progress(0)
            for i in range(10):
                time.sleep(duration / 10)
                progress_bar.progress((i + 1) / 10)
            
            st.success("Simulated recording complete!")
            
            # Return simulated audio data
            return get_sample_audio_data()
            
    except Exception as e:
        st.error(f"Error during audio handling: {e}")
        
        # Fall back to simulated data
        st.warning("Using simulated speech due to recording error.")
        time.sleep(2)  # Simulate brief processing time
        return get_sample_audio_data()

def transcribe_from_microphone(audio_data):
    """
    Transcribe recorded audio data from the microphone.
    For simulated data, returns the sample text.
    
    Parameters:
    -----------
    audio_data : AudioData
        The recorded audio data object
        
    Returns:
    --------
    str
        Transcribed text, or empty string if transcription failed
    """
    if audio_data is None:
        return ""
        
    # Check for simulated audio data
    if hasattr(audio_data, 'sample_text'):
        return audio_data.sample_text
        
    # Initialize recognizer
    recognizer = sr.Recognizer()
    
    try:
        # Try to recognize the speech
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        st.warning("Speech Recognition could not understand the audio")
        return ""
    except sr.RequestError as e:
        st.error(f"Could not request results from Speech Recognition service; {e}")
        return ""
    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
        return ""
