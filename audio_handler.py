import streamlit as st
import speech_recognition as sr
import os
import tempfile
import time

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

def record_audio(duration=5):
    """
    Record audio from the microphone for a specified duration.
    
    Parameters:
    -----------
    duration : int
        The duration (in seconds) to record
        
    Returns:
    --------
    tuple
        (audio_data, sample_rate) where audio_data is the recorded audio
        and sample_rate is the sample rate of the recording
    """
    # Initialize recognizer
    recognizer = sr.Recognizer()
    
    # Set up microphone
    try:
        with sr.Microphone() as source:
            # Adjust for ambient noise
            st.write("Adjusting for ambient noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Record the audio
            st.write(f"Recording for {duration} seconds...")
            audio_data = recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
            st.write("Recording complete!")
            
            return audio_data
    except Exception as e:
        st.error(f"Error recording audio: {e}")
        return None

def transcribe_from_microphone(audio_data):
    """
    Transcribe recorded audio data from the microphone.
    
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
