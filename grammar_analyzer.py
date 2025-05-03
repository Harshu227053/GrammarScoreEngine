import streamlit as st
from simple_grammar_checker import check_grammar, calculate_grammar_score

def analyze_grammar(text):
    """
    Analyze the grammar of the provided text using our custom grammar checker.
    
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
    
    # Check the text for grammar errors using our custom checker
    return check_grammar(text)

def get_grammar_score(text, matches):
    """
    Calculate a grammar score based on the number of errors relative to text length.
    
    Parameters:
    -----------
    text : str
        The original text that was analyzed
    matches : list
        List of grammar issues found
        
    Returns:
    --------
    int
        A score from 0-100 representing grammar correctness
    """
    return calculate_grammar_score(text, matches)
