import streamlit as st
import pandas as pd
from grammar_analyzer import get_grammar_score
import re
from collections import Counter

def highlight_errors(text, matches):
    """
    Create an HTML-highlighted version of the text with grammar errors marked.
    
    Parameters:
    -----------
    text : str
        The original text
    matches : list
        List of grammar issues found by LanguageTool
        
    Returns:
    --------
    str
        HTML-formatted string with errors highlighted
    """
    if not matches:
        return text
    
    # Sort matches by position (from end to beginning to avoid offset issues)
    sorted_matches = sorted(matches, key=lambda x: x['offset'], reverse=True)
    
    # Insert HTML tags for highlighting
    highlighted_text = text
    for match in sorted_matches:
        offset = match['offset']
        length = match['errorLength']
        error_text = highlighted_text[offset:offset + length]
        
        # Create tooltip with error message
        tooltip_text = match['message']
        
        # Replace the error with highlighted version
        highlighted_text = (
            highlighted_text[:offset] + 
            f'<span style="background-color: #ffdddd; border-bottom: 2px solid red;" title="{tooltip_text}">{error_text}</span>' + 
            highlighted_text[offset + length:]
        )
    
    return highlighted_text

def categorize_error(match):
    """
    Categorize a grammar error into a simplified category.
    
    Parameters:
    -----------
    match : dict
        A match object from LanguageTool
        
    Returns:
    --------
    str
        Simplified error category
    """
    # Get the rule ID and category
    rule_id = match.get('ruleId', '')
    category = match.get('rule', {}).get('category', {}).get('name', '')
    
    # Map to simplified categories
    if 'PUNCTUATION' in rule_id or 'COMMA' in rule_id or 'PERIOD' in rule_id:
        return 'Punctuation'
    elif 'AGREEMENT' in rule_id or 'VERB_FORM' in rule_id:
        return 'Agreement'
    elif 'SPELL' in rule_id or category == 'TYPOS':
        return 'Spelling'
    elif 'GRAMMAR' in rule_id or category == 'GRAMMAR':
        return 'Grammar'
    elif 'STYLE' in rule_id or category == 'STYLE':
        return 'Style'
    else:
        return 'Other'

def generate_statistics(grammar_analysis):
    """
    Generate statistics based on grammar analysis.
    
    Parameters:
    -----------
    grammar_analysis : dict
        Results from analyze_grammar function
        
    Returns:
    --------
    dict
        Dictionary containing various statistics about the grammar analysis
    """
    matches = grammar_analysis['matches']
    total_errors = grammar_analysis['total_errors']
    
    # Calculate error categories
    error_categories = [categorize_error(match) for match in matches]
    error_counts = dict(Counter(error_categories))
    
    # Calculate score (if there are matches)
    if 'context' in (matches[0] if matches else {}):
        sample_text = matches[0]['context']
        score = get_grammar_score(sample_text, matches)
    else:
        score = 100 if total_errors == 0 else max(0, 100 - total_errors * 5)
    
    return {
        'total_errors': total_errors,
        'error_counts': error_counts,
        'score': int(score)
    }
