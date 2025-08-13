import pytest
from app.utils.text_normalize import (
    normalize_text, 
    has_thai_chars, 
    extract_keywords, 
    create_ngrams, 
    calculate_similarity,
    expand_query_terms
)


class TestTextNormalization:
    """Test text normalization utilities"""
    
    def test_normalize_text_basic(self):
        """Test basic text normalization"""
        # English text
        assert normalize_text("Hello World") == "hello world"
        assert normalize_text("  Multiple   Spaces  ") == "multiple spaces"
        
        # Thai text (should preserve case)
        thai_text = "เชียงใหม่"
        assert normalize_text(thai_text) == thai_text
        
        # Mixed text
        mixed = "Bangkok กรุงเทพ"
        normalized = normalize_text(mixed, preserve_thai=True)
        assert "bangkok" in normalized.lower()
        assert "กรุงเทพ" in normalized
    
    def test_has_thai_chars(self):
        """Test Thai character detection"""
        assert has_thai_chars("เชียงใหม่") == True
        assert has_thai_chars("Bangkok") == False
        assert has_thai_chars("Bangkok กรุงเทพ") == True
        assert has_thai_chars("") == False
    
    def test_extract_keywords(self):
        """Test keyword extraction"""
        # English
        keywords = extract_keywords("Beautiful mountain view with sunset")
        assert "Beautiful" in keywords
        assert "mountain" in keywords
        assert "sunset" in keywords
        assert len(keywords) >= 4
        
        # Thai
        thai_keywords = extract_keywords("ภูเขาสวยงาม ดูพระอาทิตย์ตก")
        assert len(thai_keywords) >= 2
        
        # Empty/None
        assert extract_keywords("") == []
        assert extract_keywords(None) == []
        
        # Filter short words
        short_words = extract_keywords("a bb ccc dddd")
        assert "a" not in short_words  # Too short
        assert "bb" in short_words
        assert "ccc" in short_words
    
    def test_create_ngrams(self):
        """Test n-gram creation"""
        # Basic trigrams
        ngrams = create_ngrams("hello", 3)
        expected = {"hel", "ell", "llo"}
        assert ngrams == expected
        
        # Short text
        short_ngrams = create_ngrams("hi", 3)
        assert short_ngrams == {"hi"}
        
        # Empty text
        empty_ngrams = create_ngrams("", 3)
        assert empty_ngrams == set()
        
        # Different n-gram sizes
        bigrams = create_ngrams("test", 2)
        assert bigrams == {"te", "es", "st"}
    
    def test_calculate_similarity(self):
        """Test similarity calculation"""
        # Identical texts
        assert calculate_similarity("hello", "hello") == 1.0
        
        # Similar texts
        sim1 = calculate_similarity("hello", "hallo")
        assert 0.0 < sim1 < 1.0
        
        # Different texts
        sim2 = calculate_similarity("hello", "world")
        assert 0.0 <= sim2 < 0.5
        
        # Empty texts
        assert calculate_similarity("", "hello") == 0.0
        assert calculate_similarity("hello", "") == 0.0
        assert calculate_similarity("", "") == 0.0
        
        # Thai similarity
        thai_sim = calculate_similarity("เชียงใหม่", "เชียงราย")
        assert 0.0 < thai_sim < 1.0
    
    def test_expand_query_terms(self):
        """Test query term expansion"""
        # Basic expansion
        terms = expand_query_terms("Hello World")
        assert "Hello World" in terms
        assert len(terms) >= 2  # Should include normalized version
        
        # Thai expansion
        thai_terms = expand_query_terms("เชียงใหม่")
        assert "เชียงใหม่" in thai_terms
        
        # Empty query
        empty_terms = expand_query_terms("")
        assert len(empty_terms) >= 1