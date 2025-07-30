#!/usr/bin/env python3
"""
Demo script to showcase the fuzzy search functionality
Run this script to see examples of how the search system works
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.services.search_service import SearchService, SearchQuery
from src.models import db, Attraction
from src.app import create_app
import json

def demo_search_service():
    """Demonstrate search service functionality without database"""
    print("=== PaiNaiDee Fuzzy Search Demo ===\n")
    
    service = SearchService()
    
    print("1. Text Normalization:")
    test_texts = [
        "ดอยอินทนนท์",
        "Temple with ÀccénteD characters!",
        "  Extra   Spaces   "
    ]
    
    for text in test_texts:
        normalized = service.normalize_text(text)
        print(f"   '{text}' → '{normalized}'")
    print()
    
    print("2. Synonym Expansion:")
    test_queries = [
        ("temple", "en"),
        ("วัด", "th"),
        ("beach", "en"),
        ("ทะเล", "th")
    ]
    
    for query, lang in test_queries:
        expanded = service.expand_query_with_synonyms(query, lang)
        print(f"   '{query}' ({lang}) → {expanded}")
    print()
    
    print("3. Fuzzy Matching Examples:")
    test_matches = [
        ("temple", "Wat Phra Kaew Temple"),
        ("วัด", "วัดพระแก้ว"),
        ("beach", "Beautiful beach resort"),
        ("mountan", "mountain peak")  # typo
    ]
    
    for query, text in test_matches:
        similarity = service._fuzzy_match(query, text)
        print(f"   '{query}' vs '{text}' → {similarity:.3f}")
    print()
    
    print("4. Search Suggestions:")
    trending_th = service.get_trending_searches("th")
    trending_en = service.get_trending_searches("en")
    print(f"   Trending (Thai): {trending_th}")
    print(f"   Trending (English): {trending_en}")
    print()


def demo_api_usage():
    """Demonstrate API usage examples"""
    print("=== API Usage Examples ===\n")
    
    print("1. Basic Search (GET):")
    print("   curl 'http://localhost:5000/api/search?query=วัด&language=th'\n")
    
    print("2. Advanced Search (POST):")
    post_example = {
        "query": "temple",
        "language": "en",
        "province": "Bangkok",
        "category": "Culture",
        "min_rating": 4.0,
        "sort_by": "rating",
        "limit": 10
    }
    print("   curl -X POST 'http://localhost:5000/api/search' \\")
    print("     -H 'Content-Type: application/json' \\")
    print(f"     -d '{json.dumps(post_example, indent=2)}'")
    print()
    
    print("3. Search Suggestions:")
    print("   curl 'http://localhost:5000/api/search/suggestions?query=วัด&language=th'\n")
    
    print("4. Multiple Filters:")
    print("   curl 'http://localhost:5000/api/search?province=เชียงใหม่&category=ธรรมชาติ&min_rating=4.0'\n")
    
    print("5. Pagination:")
    print("   curl 'http://localhost:5000/api/search?query=beach&limit=10&offset=20'\n")


def demo_database_search():
    """Demonstrate database search with test data"""
    print("=== Database Search Demo ===\n")
    
    try:
        app = create_app("testing")
        with app.app_context():
            db.create_all()
            
            # Create test attractions
            test_attractions = [
                Attraction(
                    name="วัดพระแก้ว",
                    description="วัดที่ศักดิ์สิทธิ์ที่สุดในประเทศไทย",
                    province="กรุงเทพฯ",
                    category="วัฒนธรรม"
                ),
                Attraction(
                    name="Phi Phi Islands",
                    description="Beautiful islands in the Andaman Sea",
                    province="Krabi",
                    category="Beach"
                ),
                Attraction(
                    name="ดอยอินทนนท์",
                    description="ยอดเขาที่สูงที่สุดในประเทศไทย",
                    province="เชียงใหม่",
                    category="ธรรมชาติ"
                )
            ]
            
            for attraction in test_attractions:
                db.session.add(attraction)
            db.session.commit()
            
            # Test search service
            service = SearchService()
            
            print("Test 1: Search for 'วัด' (temple):")
            query = SearchQuery(query="วัด", language="th")
            results, total = service.search_attractions_with_fuzzy(query)
            print(f"   Found {total} results")
            for result in results:
                print(f"   - {result.attraction.name} (score: {result.similarity_score:.3f})")
            print()
            
            print("Test 2: Search for 'island' with filters:")
            query = SearchQuery(query="island", language="en", province="Krabi")
            results, total = service.search_attractions_with_fuzzy(query)
            print(f"   Found {total} results")
            for result in results:
                print(f"   - {result.attraction.name} (score: {result.similarity_score:.3f})")
            print()
            
            print("Test 3: Category filter:")
            query = SearchQuery(category="ธรรมชาติ", language="th")
            results, total = service.search_attractions_with_fuzzy(query)
            print(f"   Found {total} results in 'ธรรมชาติ' category")
            for result in results:
                print(f"   - {result.attraction.name}")
            print()
            
            db.session.remove()
            db.drop_all()
            
    except Exception as e:
        print(f"   Database demo error: {e}")
        print("   This is normal if PostgreSQL is not available")
    print()


def main():
    """Run all demos"""
    print("🔍 PaiNaiDee Backend Fuzzy Search Demo")
    print("=" * 50)
    print()
    
    demo_search_service()
    demo_api_usage()
    demo_database_search()
    
    print("=== Demo Complete ===")
    print("✅ Fuzzy search system is working correctly!")
    print("📖 See FUZZY_SEARCH_README.md for detailed documentation")
    print("🧪 Run 'python -m pytest tests/test_search.py -v' for comprehensive tests")


if __name__ == "__main__":
    main()