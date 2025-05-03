import re
import streamlit as st
import string
from collections import Counter

# Common grammar errors
common_errors = [
    # Subject-verb agreement errors
    {"pattern": r"\b(he|she|it) (are|were|have)\b", 
     "message": "Subject-verb agreement error. Use 'is/was/has' with he/she/it.", 
     "category": "Agreement"},
    {"pattern": r"\b(they|we|you) (is|was|has)\b", 
     "message": "Subject-verb agreement error. Use 'are/were/have' with they/we/you.", 
     "category": "Agreement"},
    {"pattern": r"\b(this|that) (are|were)\b", 
     "message": "Subject-verb agreement error. Use 'is/was' with this/that.", 
     "category": "Agreement"},
    {"pattern": r"\b(these|those) (is|was)\b", 
     "message": "Subject-verb agreement error. Use 'are/were' with these/those.", 
     "category": "Agreement"},
    
    # Incorrect verb forms
    {"pattern": r"\bhave went\b", 
     "message": "Incorrect verb form. Use 'have gone' instead of 'have went'.", 
     "category": "Grammar"},
    {"pattern": r"\bhave came\b", 
     "message": "Incorrect verb form. Use 'have come' instead of 'have came'.", 
     "category": "Grammar"},
    {"pattern": r"\bhave saw\b", 
     "message": "Incorrect verb form. Use 'have seen' instead of 'have saw'.", 
     "category": "Grammar"},
    
    # Double negatives
    {"pattern": r"\b(don't|doesn't|didn't|can't|won't|haven't|hasn't|hadn't).*\b(no|nobody|nothing|nowhere|never)\b", 
     "message": "Double negative detected. Use only one negative word.", 
     "category": "Grammar"},
    
    # Common confusions
    {"pattern": r"\byour (going|trying|looking|planning|coming|working)\b", 
     "message": "Incorrect use of 'your'. Did you mean 'you're'?", 
     "category": "Spelling"},
    {"pattern": r"\btheir (going|trying|looking|planning|coming|working)\b", 
     "message": "Incorrect use of 'their'. Did you mean 'they're'?", 
     "category": "Spelling"},
    {"pattern": r"\bits (going|trying|looking|planning|coming|working)\b", 
     "message": "Incorrect use of 'its'. Did you mean 'it's'?", 
     "category": "Spelling"},
    {"pattern": r"\bthere (cat|dog|book|car|house|man|woman|friend|mother|father)\b", 
     "message": "Incorrect use of 'there'. Did you mean 'their'?", 
     "category": "Spelling"},
    
    # Incorrect article usage
    {"pattern": r"\ban [^aeiou]", 
     "message": "Incorrect article. Use 'a' before consonant sounds, not 'an'.", 
     "category": "Grammar"},
    {"pattern": r"\ba [aeiou]", 
     "message": "Incorrect article. Use 'an' before vowel sounds, not 'a'.", 
     "category": "Grammar"},
    
    # Common preposition errors
    {"pattern": r"\bdifferent (to|than)\b", 
     "message": "Incorrect preposition. Use 'different from'.", 
     "category": "Grammar"},
    {"pattern": r"\bin regards to\b", 
     "message": "Incorrect phrase. Use 'with regard to' or 'regarding'.", 
     "category": "Grammar"},
    
    # Common misused terms
    {"pattern": r"\bshouldn't of\b", 
     "message": "Incorrect phrase. Use 'shouldn't have' instead.", 
     "category": "Grammar"},
    {"pattern": r"\bcould of\b", 
     "message": "Incorrect phrase. Use 'could have' instead.", 
     "category": "Grammar"},
    {"pattern": r"\bwould of\b", 
     "message": "Incorrect phrase. Use 'would have' instead.", 
     "category": "Grammar"},
    {"pattern": r"\bmust of\b", 
     "message": "Incorrect phrase. Use 'must have' instead.", 
     "category": "Grammar"},
    
    # Common redundancies
    {"pattern": r"\b(very) unique\b", 
     "message": "Redundant phrase. 'Unique' doesn't need modifiers like 'very'.", 
     "category": "Style"},
    {"pattern": r"\batm machine\b", 
     "message": "Redundant phrase. ATM already stands for Automated Teller Machine.", 
     "category": "Style"},
    
    # Punctuation errors
    {"pattern": r"[a-z][.?!] [a-z]", 
     "message": "Capitalization error. Capitalize the first letter of a new sentence.", 
     "category": "Punctuation"},
    {"pattern": r"\b[A-Z][a-z]+ i\b", 
     "message": "Capitalization error. The pronoun 'I' should always be capitalized.", 
     "category": "Punctuation"},
    
    # Plural/singular confusion
    {"pattern": r"\bthis (are|were)\b", 
     "message": "Agreement error. Use 'is/was' with 'this'.", 
     "category": "Agreement"},
    {"pattern": r"\bthese (is|was)\b", 
     "message": "Agreement error. Use 'are/were' with 'these'.", 
     "category": "Agreement"},
    
    # More common ones
    {"pattern": r"\bthey is\b", 
     "message": "Subject-verb agreement error. Use 'they are' instead.", 
     "category": "Agreement"},
    {"pattern": r"\bshe don't\b", 
     "message": "Subject-verb agreement error. Use 'she doesn't' instead.", 
     "category": "Agreement"},
    {"pattern": r"\bhe don't\b", 
     "message": "Subject-verb agreement error. Use 'he doesn't' instead.", 
     "category": "Agreement"},
    {"pattern": r"\bit don't\b", 
     "message": "Subject-verb agreement error. Use 'it doesn't' instead.", 
     "category": "Agreement"}
]

def check_grammar(text):
    """
    Check text for common grammar errors using regex patterns
    
    Parameters:
    -----------
    text : str
        The text to check for grammar errors
        
    Returns:
    --------
    dict
        Dictionary containing grammar analysis results
    """
    if not text:
        return {'matches': [], 'total_errors': 0}
    
    matches = []
    
    # Convert text to lowercase for case-insensitive matching
    lower_text = text.lower()
    
    # Check for each pattern
    for error in common_errors:
        for match in re.finditer(error["pattern"], lower_text, re.IGNORECASE):
            start, end = match.span()
            error_text = text[start:end]
            
            # Get some context around the error
            context_start = max(0, start - 20)
            context_end = min(len(text), end + 20)
            context = text[context_start:context_end]
            
            # Create a match object similar to what LanguageTool would return
            match_obj = {
                'message': error["message"],
                'offset': start,
                'errorLength': end - start,
                'context': context,
                'replacements': [],  # Could add suggestions here
                'rule': {
                    'category': {'name': error["category"]},
                    'id': f"CUSTOM_{error['category'].upper()}"
                }
            }
            
            matches.append(match_obj)
    
    # Check for basic punctuation errors (ending sentences)
    sentences = re.split(r'(?<=[.!?]) +', text)
    for i, sentence in enumerate(sentences):
        if sentence and len(sentence) > 0:
            if sentence[0].islower() and i > 0:
                # Create a match object for capitalization error
                match_obj = {
                    'message': "Sentence should start with a capital letter.",
                    'offset': text.find(sentence),
                    'errorLength': 1,
                    'context': sentence[:min(40, len(sentence))],
                    'replacements': [sentence[0].upper() + sentence[1:]],
                    'rule': {
                        'category': {'name': 'Punctuation'},
                        'id': 'CUSTOM_CAPITALIZATION'
                    }
                }
                matches.append(match_obj)
    
    # Check for missing punctuation at the end of sentences
    if text and not text[-1] in '.!?':
        match_obj = {
            'message': "Sentence should end with proper punctuation.",
            'offset': len(text) - 1,
            'errorLength': 1,
            'context': text[max(0, len(text)-40):],
            'replacements': [text + '.', text + '!', text + '?'],
            'rule': {
                'category': {'name': 'Punctuation'},
                'id': 'CUSTOM_END_PUNCTUATION'
            }
        }
        matches.append(match_obj)
    
    # Return analysis in a format similar to what we'd get from LanguageTool
    return {
        'matches': matches,
        'total_errors': len(matches)
    }

def calculate_grammar_score(text, matches):
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