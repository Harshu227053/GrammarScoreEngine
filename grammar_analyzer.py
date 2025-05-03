import language_tool_python
import streamlit as st

# Initialize the language tool (lazy loading to improve startup time)
@st.cache_resource
def get_language_tool():
    """
    Initialize and return a LanguageTool instance with caching to avoid repeated initialization.
    
    Returns:
    --------
    LanguageTool
        Initialized LanguageTool instance for English grammar checking
    """
    return language_tool_python.LanguageTool('en-US')

def analyze_grammar(text):
    """
    Analyze the grammar of the provided text using LanguageTool.
    
    Parameters:
    -----------
    text : str
        The text to analyze for grammar errors
        
    Returns:
    --------
    dict
        A dictionary containing grammar analysis results:
        - 'matches': List of grammar issues found
        - 'total_errors': Total number of grammar issues
    """
    if not text:
        return {'matches': [], 'total_errors': 0}
    
    # Get the language tool instance
    tool = get_language_tool()
    
    # Check the text for grammar errors
    matches = tool.check(text)
    
    # Return the analysis results
    return {
        'matches': matches,
        'total_errors': len(matches)
    }

def get_grammar_score(text, matches):
    """
    Calculate a grammar score based on the number of errors relative to text length.
    
    Parameters:
    -----------
    text : str
        The original text that was analyzed
    matches : list
        List of grammar issues found by LanguageTool
        
    Returns:
    --------
    int
        A score from 0-100 representing grammar correctness
    """
    if not text or len(text.split()) < 3:
        return 0
    
    if not matches:
        return 100
    
    # Calculate words in text
    word_count = len(text.split())
    
    # Calculate error rate (errors per 100 words)
    error_rate = (len(matches) / word_count) * 100
    
    # Calculate score (100 - error rate, with minimum 0)
    # Cap error rate at 50 to ensure very bad text still gets some score
    capped_error_rate = min(error_rate, 50)
    score = 100 - capped_error_rate * 2
    
    # Ensure score is between 0 and 100
    return max(0, min(100, round(score)))
