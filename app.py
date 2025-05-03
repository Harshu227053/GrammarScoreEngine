import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import tempfile
import os
from audio_handler import transcribe_audio
from grammar_analyzer import analyze_grammar
from utils import highlight_errors, generate_statistics

st.set_page_config(
    page_title="Grammar Scoring Engine",
    page_icon="🎤",
    layout="wide"
)

def main():
    st.title("Grammar Scoring Engine for Voice Samples")
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
