import streamlit as st
import speech_recognition as sr
import os

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
