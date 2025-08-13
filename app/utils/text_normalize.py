import re
import unicodedata
from typing import List, Set


def normalize_text(text: str, preserve_thai: bool = True) -> str:
    """
    Normalize text for search purposes
    
    Args:
        text: Input text to normalize
        preserve_thai: Whether to preserve Thai characters (don't lowercase)
    
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    # Trim whitespace
    text = text.strip()
    
    # Unicode NFC normalization
    text = unicodedata.normalize('NFC', text)
    
    # For Thai text, be careful with case conversion
    if preserve_thai and has_thai_chars(text):
        # Only normalize whitespace and remove extra spaces
        text = re.sub(r'\s+', ' ', text)
    else:
        # Safe to lowercase for Latin text
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
    
    return text


def has_thai_chars(text: str) -> bool:
    """Check if text contains Thai characters"""
    thai_range = range(0x0E00, 0x0E7F + 1)  # Thai Unicode block
    return any(ord(char) in thai_range for char in text)


def extract_keywords(text: str) -> List[str]:
    """
    Extract keywords from text for search indexing
    
    Args:
        text: Input text
        
    Returns:
        List of extracted keywords
    """
    if not text:
        return []
    
    # Simple tokenization - split on whitespace and punctuation
    # For Thai, this is basic but sufficient for Phase 1
    keywords = re.findall(r'\b\w+\b', text, re.UNICODE)
    
    # Remove very short keywords (< 2 chars)
    keywords = [k for k in keywords if len(k) >= 2]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword.lower() not in seen:
            seen.add(keyword.lower())
            unique_keywords.append(keyword)
    
    return unique_keywords


def create_ngrams(text: str, n: int = 3) -> Set[str]:
    """
    Create n-grams for fuzzy matching
    
    Args:
        text: Input text
        n: Size of n-grams
        
    Returns:
        Set of n-grams
    """
    if not text or len(text) < n:
        return {text} if text else set()
    
    text = normalize_text(text)
    ngrams = set()
    
    for i in range(len(text) - n + 1):
        ngrams.add(text[i:i + n])
    
    return ngrams


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts using n-gram overlap
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
    
    ngrams1 = create_ngrams(text1)
    ngrams2 = create_ngrams(text2)
    
    if not ngrams1 or not ngrams2:
        return 0.0
    
    intersection = len(ngrams1.intersection(ngrams2))
    union = len(ngrams1.union(ngrams2))
    
    return intersection / union if union > 0 else 0.0


def expand_query_terms(query: str) -> List[str]:
    """
    Expand query terms with common variations
    
    Args:
        query: Search query
        
    Returns:
        List of expanded terms including original
    """
    terms = [query]
    normalized_query = normalize_text(query)
    
    # Add normalized version if different
    if normalized_query != query:
        terms.append(normalized_query)
    
    # Add keywords
    keywords = extract_keywords(query)
    terms.extend(keywords)
    
    # Remove duplicates
    return list(dict.fromkeys(terms))