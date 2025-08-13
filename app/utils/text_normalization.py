"""
Text normalization utilities for Thai and English search functionality.

This module provides functions for normalizing, tokenizing, and processing text
for search operations, with special handling for Thai language.
"""

import re
import unicodedata
from typing import List, Set


# Thai and English stop words
THAI_STOP_WORDS = {
    "และ", "หรือ", "แต่", "กับ", "เพื่อ", "จาก", "ใน", "ที่", "เป็น", "คือ", 
    "มี", "ไม่", "ได้", "จะ", "แล้ว", "ก็", "ด้วย", "เมื่อ", "ถ้า", "ให้",
    "ของ", "โดย", "ซึ่ง", "นั้น", "นี้", "อัน", "การ", "ความ", "เวลา", "วัน",
    "คน", "คือ", "เป็น", "อยู่", "มา", "ไป", "ขึ้น", "ลง", "เข้า", "ออก"
}

ENGLISH_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", 
    "he", "in", "is", "it", "its", "of", "on", "that", "the", "to", "was", 
    "will", "with", "the", "this", "but", "they", "have", "had", "what", 
    "said", "each", "which", "their", "time", "if", "up", "out", "many",
    "then", "them", "these", "so", "some", "her", "would", "make", "like",
    "into", "him", "has", "two", "more", "very", "after", "words", "long",
    "than", "first", "been", "call", "who", "its", "now", "find", "may",
    "down", "side", "been", "now", "find", "any", "new", "work", "part",
    "take", "get", "place", "made", "live", "where", "after", "back", "little",
    "only", "round", "man", "year", "came", "show", "every", "good", "me",
    "give", "our", "under", "name", "very", "through", "just", "form",
    "sentence", "great", "think", "say", "help", "low", "line", "differ",
    "turn", "cause", "much", "mean", "before", "move", "right", "boy",
    "old", "too", "same", "tell", "does", "set", "three", "want", "air",
    "well", "also", "play", "small", "end", "put", "home", "read", "hand",
    "port", "large", "spell", "add", "even", "land", "here", "must", "big",
    "high", "such", "follow", "act", "why", "ask", "men", "change", "went",
    "light", "kind", "off", "need", "house", "picture", "try", "us", "again",
    "animal", "point", "mother", "world", "near", "build", "self", "earth",
    "father"
}


def normalize_text(text: str) -> str:
    """
    Normalize text for search operations.
    
    Args:
        text (str): Input text to normalize
        
    Returns:
        str: Normalized text
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Unicode normalization (NFD - decomposed form)
    text = unicodedata.normalize('NFD', text)
    
    # Remove diacritics but preserve Thai characters
    # Thai unicode range: \u0e00-\u0e7f
    normalized_chars = []
    for char in text:
        if unicodedata.category(char) != 'Mn' or '\u0e00' <= char <= '\u0e7f':
            normalized_chars.append(char)
    text = ''.join(normalized_chars)
    
    # Remove extra whitespace and normalize spaces
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but preserve Thai and alphanumeric
    text = re.sub(r'[^\w\s\u0e00-\u0e7f]', ' ', text)
    
    # Remove extra spaces again after character removal
    text = re.sub(r'\s+', ' ', text.strip())
    
    return text


def tokenize(text: str) -> List[str]:
    """
    Tokenize text into words, handling both Thai and English.
    
    For Thai text, this is a simple whitespace tokenization.
    For more sophisticated Thai tokenization, consider using libraries like:
    - PyThaiNLP
    - python-thai-tokenizer
    
    Args:
        text (str): Text to tokenize
        
    Returns:
        List[str]: List of tokens
    """
    if not text:
        return []
    
    # Basic tokenization by whitespace
    tokens = text.split()
    
    # Filter out very short tokens (likely not meaningful)
    tokens = [token for token in tokens if len(token) >= 2]
    
    return tokens


def strip_stop_words(tokens: List[str], language: str = "auto") -> List[str]:
    """
    Remove stop words from a list of tokens.
    
    Args:
        tokens (List[str]): List of tokens
        language (str): Language hint ("thai", "english", or "auto")
        
    Returns:
        List[str]: Tokens with stop words removed
    """
    if not tokens:
        return []
    
    if language == "auto":
        # Auto-detect language based on character ranges
        stop_words = THAI_STOP_WORDS | ENGLISH_STOP_WORDS
    elif language == "thai":
        stop_words = THAI_STOP_WORDS
    elif language == "english":
        stop_words = ENGLISH_STOP_WORDS
    else:
        # Default to both
        stop_words = THAI_STOP_WORDS | ENGLISH_STOP_WORDS
    
    return [token for token in tokens if token.lower() not in stop_words]


def generate_search_terms(text: str) -> List[str]:
    """
    Generate search terms from input text.
    
    This function combines normalization, tokenization, and stop word removal
    to produce a list of search terms.
    
    Args:
        text (str): Input text
        
    Returns:
        List[str]: List of search terms
    """
    if not text:
        return []
    
    # Normalize the text
    normalized = normalize_text(text)
    
    # Tokenize
    tokens = tokenize(normalized)
    
    # Remove stop words
    search_terms = strip_stop_words(tokens)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_terms = []
    for term in search_terms:
        if term not in seen:
            seen.add(term)
            unique_terms.append(term)
    
    return unique_terms


def generate_search_variants(text: str) -> Set[str]:
    """
    Generate search variants including partial matches for autocomplete.
    
    Args:
        text (str): Input text
        
    Returns:
        Set[str]: Set of search variants
    """
    if not text:
        return set()
    
    variants = set()
    normalized = normalize_text(text)
    variants.add(normalized)
    
    # Add the original text (lowercased)
    variants.add(text.lower().strip())
    
    # Generate prefixes for autocomplete (minimum 2 characters)
    words = normalized.split()
    for word in words:
        if len(word) >= 2:
            variants.add(word)
            # Add prefixes of length 2 to len(word)-1
            for i in range(2, len(word)):
                variants.add(word[:i])
    
    # Generate n-grams for partial matching
    for word in words:
        if len(word) >= 3:
            # Trigrams
            for i in range(len(word) - 2):
                variants.add(word[i:i+3])
    
    return variants


def calculate_text_similarity_score(query: str, text: str) -> float:
    """
    Calculate a simple text similarity score between query and text.
    
    This is a basic implementation. For production use, consider more
    sophisticated algorithms like Jaccard similarity, cosine similarity,
    or edit distance.
    
    Args:
        query (str): Search query
        text (str): Text to compare against
        
    Returns:
        float: Similarity score between 0.0 and 1.0
    """
    if not query or not text:
        return 0.0
    
    query_terms = set(generate_search_terms(query))
    text_terms = set(generate_search_terms(text))
    
    if not query_terms or not text_terms:
        return 0.0
    
    # Jaccard similarity: intersection / union
    intersection = len(query_terms & text_terms)
    union = len(query_terms | text_terms)
    
    return intersection / union if union > 0 else 0.0


def is_thai_text(text: str) -> bool:
    """
    Check if text contains Thai characters.
    
    Args:
        text (str): Text to check
        
    Returns:
        bool: True if text contains Thai characters
    """
    if not text:
        return False
    
    for char in text:
        if '\u0e00' <= char <= '\u0e7f':
            return True
    return False


def clean_search_query(query: str, max_length: int = 100) -> str:
    """
    Clean and validate a search query.
    
    Args:
        query (str): Raw search query
        max_length (int): Maximum allowed query length
        
    Returns:
        str: Cleaned query
    """
    if not query:
        return ""
    
    # Truncate if too long
    if len(query) > max_length:
        query = query[:max_length]
    
    # Normalize and clean
    cleaned = normalize_text(query)
    
    # Remove excessive repetition (more than 2 consecutive identical characters)
    cleaned = re.sub(r'(.)\1{2,}', r'\1\1', cleaned)
    
    return cleaned.strip()


# Example usage and testing
if __name__ == "__main__":
    # Test with Thai text
    thai_text = "วัดพระแก้วเป็นวัดที่สวยงามมากในกรุงเทพฯ"
    print("Thai text:", thai_text)
    print("Normalized:", normalize_text(thai_text))
    print("Tokens:", tokenize(normalize_text(thai_text)))
    print("Search terms:", generate_search_terms(thai_text))
    print()
    
    # Test with English text
    english_text = "The Grand Palace is a beautiful temple in Bangkok"
    print("English text:", english_text)
    print("Normalized:", normalize_text(english_text))
    print("Tokens:", tokenize(normalize_text(english_text)))
    print("Search terms:", generate_search_terms(english_text))
    print()
    
    # Test with mixed text
    mixed_text = "วัดพระแก้ว (Temple of the Emerald Buddha)"
    print("Mixed text:", mixed_text)
    print("Normalized:", normalize_text(mixed_text))
    print("Search terms:", generate_search_terms(mixed_text))
    print("Variants:", generate_search_variants(mixed_text))
    print()
    
    # Test similarity
    query = "วัดพระแก้ว"
    text = "วัดพระแก้วเป็นวัดสำคัญ"
    print(f"Similarity between '{query}' and '{text}':", 
          calculate_text_similarity_score(query, text))