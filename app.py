import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import tempfile
import os
from audio_handler import transcribe_audio, record_audio, transcribe_from_microphone
from grammar_analyzer import analyze_grammar
from utils import highlight_errors, generate_statistics

st.set_page_config(
    page_title="Grammar Scoring Engine",
    page_icon="🎤",
    layout="wide"
)

def main():
    st.title("Grammar Scoring Engine for Voice Samples")
    
    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["Upload Audio", "Live Recording"])
    
    with tab1:
        st.subheader("Upload your voice sample to analyze grammar")
        
        # File uploader for audio files
        uploaded_file = st.file_uploader(
            "Choose an audio file", 
            type=["wav", "mp3", "m4a", "ogg"],
            help="Upload a voice recording to analyze grammar"
        )

        if uploaded_file is not None:
            # Create a progress container
            progress_container = st.container()
            
            with progress_container:
                progress_text = st.empty()
                progress_bar = st.progress(0)
                
                # Processing steps
                progress_text.text("Processing audio file...")
                progress_bar.progress(25)
                
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_filename = tmp_file.name
                
                try:
                    # Transcribe audio
                    progress_text.text("Transcribing speech to text...")
                    progress_bar.progress(50)
                    
                    transcription = transcribe_audio(temp_filename)
                    
                    if not transcription:
                        st.error("Could not transcribe the audio. Please ensure the audio contains clear speech.")
                        return
                    
                    # Analyze grammar
                    progress_text.text("Analyzing grammar...")
                    progress_bar.progress(75)
                    
                    grammar_analysis = analyze_grammar(transcription)
                    
                    # Generate statistics
                    progress_text.text("Generating results...")
                    progress_bar.progress(100)
                    
                    stats = generate_statistics(grammar_analysis)
                    
                    # Clear progress elements
                    progress_text.empty()
                    progress_bar.empty()
                    
                    # Display results
                    display_results(transcription, grammar_analysis, stats)
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                finally:
                    # Remove temporary file
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
        else:
            st.info("Please upload an audio file to get started.")
            
            # Display sample information
            with st.expander("How it works"):
                st.write("""
                1. Upload an audio file containing spoken English
                2. Our system will transcribe the speech to text
                3. We'll analyze the grammar and provide a detailed score
                4. You'll receive feedback on any grammatical errors found
                5. Statistics will show your overall grammatical accuracy
                """)
                
                st.write("""
                **Supported audio formats:**
                - WAV
                - MP3
                - M4A
                - OGG
                """)
    
    with tab2:
        st.subheader("Record live speech for grammar analysis")
        
        # Session state to track if we've recorded audio
        if "audio_recorded" not in st.session_state:
            st.session_state.audio_recorded = False
            st.session_state.audio_data = None
            st.session_state.transcription = None
            st.session_state.analyzed = False
        
        # Recording duration selector
        duration = st.slider("Recording duration (seconds)", 
                            min_value=3, 
                            max_value=30, 
                            value=10, 
                            step=1)
        
        # Record button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Start Recording"):
                with st.spinner("Recording in progress..."):
                    # Record audio
                    st.session_state.audio_data = record_audio(duration)
                    st.session_state.audio_recorded = True
                    st.session_state.analyzed = False
        
        # Analyze button (only show if audio is recorded)
        if st.session_state.audio_recorded and not st.session_state.analyzed:
            with col2:
                if st.button("Analyze Recording"):
                    with st.spinner("Analyzing speech..."):
                        # Create a progress container
                        progress_text = st.empty()
                        progress_bar = st.progress(0)
                        
                        # Transcribe audio
                        progress_text.text("Transcribing speech to text...")
                        progress_bar.progress(33)
                        
                        transcription = transcribe_from_microphone(st.session_state.audio_data)
                        st.session_state.transcription = transcription
                        
                        if not transcription:
                            st.error("Could not transcribe the audio. Please try speaking more clearly.")
                            progress_text.empty()
                            progress_bar.empty()
                            return
                        
                        # Analyze grammar
                        progress_text.text("Analyzing grammar...")
                        progress_bar.progress(66)
                        
                        grammar_analysis = analyze_grammar(transcription)
                        
                        # Generate statistics
                        progress_text.text("Generating results...")
                        progress_bar.progress(100)
                        
                        stats = generate_statistics(grammar_analysis)
                        
                        # Clear progress elements
                        progress_text.empty()
                        progress_bar.empty()
                        
                        # Display results
                        display_results(transcription, grammar_analysis, stats)
                        
                        # Set analyzed to true
                        st.session_state.analyzed = True
        
        # Reset button (only show after analysis)
        if st.session_state.analyzed:
            if st.button("Record New Speech"):
                st.session_state.audio_recorded = False
                st.session_state.audio_data = None
                st.session_state.transcription = None
                st.session_state.analyzed = False
                st.rerun()
        
        # Instructions
        if not st.session_state.audio_recorded:
            st.info("Click 'Start Recording' and speak clearly into your microphone.")
            
            with st.expander("Tips for best results"):
                st.write("""
                - Speak clearly and at a normal pace
                - Minimize background noise
                - Use a good quality microphone if possible
                - Try to speak in complete sentences
                - Longer samples (10+ seconds) provide better analysis
                """)

def display_results(transcription, grammar_analysis, stats):
    st.subheader("Analysis Results")
    
    # Create columns for score and stats
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Display the overall score
        st.metric("Grammar Score", f"{stats['score']}%")
        
        # Display error counts
        st.write("Error Summary:")
        error_df = pd.DataFrame({
            'Error Type': list(stats['error_counts'].keys()),
            'Count': list(stats['error_counts'].values())
        })
        
        # Bar chart of error types
        if not error_df.empty and error_df['Count'].sum() > 0:
            fig = px.bar(
                error_df, 
                x='Error Type', 
                y='Count',
                title='Grammar Error Types',
                color='Count',
                color_continuous_scale=px.colors.sequential.Viridis
            )
            fig.update_layout(xaxis_title="Error Category", yaxis_title="Number of Errors")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("No grammar errors detected! Your speech is grammatically correct.")
    
    with col2:
        # Display the original transcription
        st.subheader("Transcription")
        st.write(transcription)
        
        # Display the highlighted errors
        st.subheader("Grammar Issues")
        if grammar_analysis['matches']:
            highlighted_text = highlight_errors(transcription, grammar_analysis['matches'])
            st.markdown(highlighted_text, unsafe_allow_html=True)
            
            # Display detailed error information
            st.subheader("Detailed Feedback")
            for i, match in enumerate(grammar_analysis['matches']):
                with st.expander(f"Issue #{i+1}: {match['message'][:50]}..."):
                    st.markdown(f"**Error Type:** {match['rule'].get('category', 'Grammar')} error")
                    st.markdown(f"**Issue:** {match['message']}")
                    if match.get('replacements'):
                        st.markdown(f"**Suggested correction:** {', '.join(match['replacements'][:3])}")
                    st.markdown(f"**Context:** ...{match['context']}...")
        else:
            st.success("No grammar issues found in the transcription.")

if __name__ == "__main__":
    main()
