import json
import os
from typing import Dict, List, Set
from pathlib import Path


class ExpansionLoader:
    """Loads and manages keyword expansion data"""
    
    def __init__(self, expansion_file: str = None):
        if expansion_file is None:
            # Default to seed/keyword_expansion.json relative to project root
            project_root = Path(__file__).parent.parent.parent
            expansion_file = project_root / "seed" / "keyword_expansion.json"
        
        self.expansion_file = expansion_file
        self._data = None
        self._load_expansion_data()
    
    def _load_expansion_data(self) -> None:
        """Load expansion data from JSON file"""
        try:
            with open(self.expansion_file, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Expansion file {self.expansion_file} not found. Using empty data.")
            self._data = {"provinces": {}, "categories": {}, "synonyms": {}}
        except json.JSONDecodeError as e:
            print(f"Warning: Error parsing expansion file: {e}. Using empty data.")
            self._data = {"provinces": {}, "categories": {}, "synonyms": {}}
    
    def get_province_landmarks(self, province: str) -> List[str]:
        """
        Get landmark expansions for a province
        
        Args:
            province: Province name
            
        Returns:
            List of landmark names
        """
        return self._data.get("provinces", {}).get(province, [])
    
    def get_category_terms(self, category: str) -> List[str]:
        """
        Get related terms for a category
        
        Args:
            category: Category name
            
        Returns:
            List of related terms
        """
        return self._data.get("categories", {}).get(category, [])
    
    def get_synonyms(self, term: str) -> List[str]:
        """
        Get synonyms for a term
        
        Args:
            term: Term to find synonyms for
            
        Returns:
            List of synonyms
        """
        return self._data.get("synonyms", {}).get(term, [])
    
    def expand_query(self, query: str) -> Set[str]:
        """
        Expand query with related terms
        
        Args:
            query: Original search query
            
        Returns:
            Set of expanded terms including original
        """
        expanded_terms = {query}
        query_lower = query.lower()
        
        # Add province landmarks
        for province, landmarks in self._data.get("provinces", {}).items():
            if query_lower in province.lower() or province.lower() in query_lower:
                expanded_terms.update(landmarks)
        
        # Add category terms
        for category, terms in self._data.get("categories", {}).items():
            if query_lower in category.lower() or category.lower() in query_lower:
                expanded_terms.update(terms)
        
        # Add synonyms
        for term, synonyms in self._data.get("synonyms", {}).items():
            if query_lower in term.lower() or term.lower() in query_lower:
                expanded_terms.update(synonyms)
                expanded_terms.add(term)
        
        return expanded_terms
    
    def find_matching_provinces(self, query: str) -> List[str]:
        """
        Find provinces that match the query
        
        Args:
            query: Search query
            
        Returns:
            List of matching provinces
        """
        matching_provinces = []
        query_lower = query.lower()
        
        for province in self._data.get("provinces", {}).keys():
            if query_lower in province.lower() or province.lower() in query_lower:
                matching_provinces.append(province)
        
        return matching_provinces


# Global instance
expansion_loader = ExpansionLoader()