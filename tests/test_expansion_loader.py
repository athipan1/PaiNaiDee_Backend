import pytest
from unittest.mock import patch, mock_open
import json
from app.utils.expansion_loader import ExpansionLoader


class TestExpansionLoader:
    """Test keyword expansion loader"""
    
    def test_expansion_loader_basic(self):
        """Test basic expansion functionality"""
        # Mock expansion data
        mock_data = {
            "provinces": {
                "กรุงเทพมหานคร": ["วัดพระแก้ว", "วัดโพธิ์"],
                "เชียงใหม่": ["ดอยสุเทพ", "นิมมาน"]
            },
            "categories": {
                "ทะเล": ["ชายหาด", "หาด", "เกาะ"],
                "ภูเขา": ["ดอย", "เขา", "ยอด"]
            },
            "synonyms": {
                "เที่ยว": ["ท่องเที่ยว", "เดินทาง"],
                "สวย": ["งาม", "สวยงาม"]
            }
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            loader = ExpansionLoader("fake_file.json")
            
            # Test province landmarks
            landmarks = loader.get_province_landmarks("กรุงเทพมหานคร")
            assert "วัดพระแก้ว" in landmarks
            assert "วัดโพธิ์" in landmarks
            
            # Test category terms
            sea_terms = loader.get_category_terms("ทะเล")
            assert "ชายหาด" in sea_terms
            assert "หาด" in sea_terms
            
            # Test synonyms
            travel_synonyms = loader.get_synonyms("เที่ยว")
            assert "ท่องเที่ยว" in travel_synonyms
            assert "เดินทาง" in travel_synonyms
    
    def test_expand_query(self):
        """Test query expansion"""
        mock_data = {
            "provinces": {
                "เชียงใหม่": ["ดอยสุเทพ", "นิมมาน"]
            },
            "categories": {
                "ทะเล": ["ชายหาด", "หาด"]
            },
            "synonyms": {
                "เที่ยว": ["ท่องเที่ยว"]
            }
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            loader = ExpansionLoader("fake_file.json")
            
            # Test province expansion
            expanded = loader.expand_query("เชียงใหม่")
            assert "เชียงใหม่" in expanded
            assert "ดอยสุเทพ" in expanded
            assert "นิมมาน" in expanded
            
            # Test category expansion
            sea_expanded = loader.expand_query("ทะเล")
            assert "ทะเล" in sea_expanded
            assert "ชายหาด" in sea_expanded
            assert "หาด" in sea_expanded
            
            # Test synonym expansion
            travel_expanded = loader.expand_query("เที่ยว")
            assert "เที่ยว" in travel_expanded
            assert "ท่องเที่ยว" in travel_expanded
    
    def test_find_matching_provinces(self):
        """Test province matching"""
        mock_data = {
            "provinces": {
                "กรุงเทพมหานคร": ["วัดพระแก้ว"],
                "เชียงใหม่": ["ดอยสุเทพ"],
                "ภูเก็ต": ["ป่าตอง"]
            },
            "categories": {},
            "synonyms": {}
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            loader = ExpansionLoader("fake_file.json")
            
            # Test exact match
            matches = loader.find_matching_provinces("เชียงใหม่")
            assert "เชียงใหม่" in matches
            
            # Test partial match
            partial_matches = loader.find_matching_provinces("กรุงเทพ")
            assert "กรุงเทพมหานคร" in partial_matches
            
            # Test no match
            no_matches = loader.find_matching_provinces("ไม่มีจังหวัดนี้")
            assert len(no_matches) == 0
    
    def test_file_not_found(self):
        """Test handling of missing expansion file"""
        with patch("builtins.open", side_effect=FileNotFoundError):
            loader = ExpansionLoader("nonexistent_file.json")
            
            # Should not crash and return empty results
            assert loader.get_province_landmarks("test") == []
            assert loader.get_category_terms("test") == []
            assert loader.get_synonyms("test") == []
            
            # Expand query should still work with original term
            expanded = loader.expand_query("test")
            assert "test" in expanded
    
    def test_invalid_json(self):
        """Test handling of invalid JSON file"""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            loader = ExpansionLoader("invalid_file.json")
            
            # Should not crash and return empty results
            assert loader.get_province_landmarks("test") == []
            assert loader.get_category_terms("test") == []
            assert loader.get_synonyms("test") == []