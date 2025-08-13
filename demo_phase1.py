#!/usr/bin/env python3
"""
Phase 1 API Demo Script

This script demonstrates the FastAPI Phase 1 implementation
by creating an in-memory mock of the API responses.
"""

import json
import time
from datetime import datetime, timedelta
from app.utils.text_normalize import normalize_text
from app.utils.expansion_loader import expansion_loader
from app.utils.ranking import calculate_combined_score
from app.schemas.search import SearchResponse, PostResponse, MediaResponse, LocationResponse, SuggestionResponse


def demo_search_functionality():
    """Demonstrate the search functionality with mock data"""
    
    print("🔍 PaiNaiDee Backend API - Phase 1 Demo")
    print("=" * 50)
    
    # Mock data
    mock_locations = [
        {"id": "loc1", "name": "ดอยสุเทพ", "province": "เชียงใหม่", "lat": 18.8042, "lng": 98.9217},
        {"id": "loc2", "name": "วัดพระแก้ว", "province": "กรุงเทพมหานคร", "lat": 13.7515, "lng": 100.4917},
        {"id": "loc3", "name": "หาดป่าตอง", "province": "ภูเก็ต", "lat": 7.8955, "lng": 98.2958},
    ]
    
    mock_posts = [
        {
            "id": "post1",
            "caption": "สวยงามมากที่ดอยสุเทพ วิวเมืองเชียงใหม่จากด้านบน",
            "location_id": "loc1",
            "like_count": 156,
            "comment_count": 23,
            "created_at": datetime.now() - timedelta(hours=6),
            "media": [{"type": "image", "url": "https://example.com/doi_suthep_1.jpg"}]
        },
        {
            "id": "post2", 
            "caption": "วัดพระแก้วมรกต สถานที่ศักดิ์สิทธิ์ใจกลางกรุงเทพ",
            "location_id": "loc2",
            "like_count": 89,
            "comment_count": 12,
            "created_at": datetime.now() - timedelta(days=2),
            "media": [{"type": "image", "url": "https://example.com/wat_phra_kaew.jpg"}]
        },
        {
            "id": "post3",
            "caption": "ทะเลใสใสที่หาดป่าตอง สีฟ้าสวยงาม",
            "location_id": "loc3", 
            "like_count": 234,
            "comment_count": 45,
            "created_at": datetime.now() - timedelta(hours=12),
            "media": [{"type": "image", "url": "https://example.com/patong_beach.jpg"}]
        }
    ]
    
    # Test queries
    test_queries = ["เชียงใหม่", "ทะเล", "วัด", "ภูเขา"]
    
    for query in test_queries:
        print(f"\n🔍 Search Query: '{query}'")
        print("-" * 30)
        
        start_time = time.time()
        
        # 1. Normalize query
        normalized = normalize_text(query)
        print(f"Normalized: '{normalized}'")
        
        # 2. Expand query terms
        expanded = expansion_loader.expand_query(query)
        expansion_list = list(expanded - {query})
        print(f"Expanded terms: {expansion_list[:5]}")  # Show first 5
        
        # 3. Find matching posts (simple simulation)
        matching_posts = []
        for post in mock_posts:
            # Simple matching logic for demo
            score = 0.0
            if any(term.lower() in post["caption"].lower() for term in expanded):
                # Calculate ranking score
                combined_score, components = calculate_combined_score(
                    post["like_count"],
                    post["comment_count"], 
                    post["created_at"]
                )
                score = combined_score
                matching_posts.append((post, score))
        
        # Sort by score
        matching_posts.sort(key=lambda x: x[1], reverse=True)
        
        # 4. Generate response
        post_responses = []
        for post, score in matching_posts:
            location = next((loc for loc in mock_locations if loc["id"] == post["location_id"]), None)
            
            post_responses.append({
                "id": post["id"],
                "caption": post["caption"],
                "location": location["name"] if location else None,
                "like_count": post["like_count"],
                "comment_count": post["comment_count"],
                "score": round(score, 3),
                "created_at": post["created_at"].isoformat()
            })
        
        latency_ms = (time.time() - start_time) * 1000
        
        # 5. Display results
        print(f"Results found: {len(post_responses)}")
        print(f"Latency: {latency_ms:.1f}ms")
        
        for i, post in enumerate(post_responses[:2], 1):  # Show top 2 results
            print(f"  {i}. {post['caption'][:50]}...")
            print(f"     Location: {post['location']}")
            print(f"     Score: {post['score']} | Likes: {post['like_count']} | Comments: {post['comment_count']}")


def demo_ranking_algorithm():
    """Demonstrate the ranking algorithm"""
    
    print("\n\n📊 Ranking Algorithm Demo")
    print("=" * 50)
    
    test_posts = [
        {"name": "Very Recent + Popular", "likes": 100, "comments": 20, "hours_ago": 1},
        {"name": "Old but Very Popular", "likes": 500, "comments": 80, "hours_ago": 72},
        {"name": "Recent but Less Popular", "likes": 20, "comments": 5, "hours_ago": 2},
        {"name": "Old and Less Popular", "likes": 30, "comments": 10, "hours_ago": 168},
    ]
    
    print(f"{'Post':<25} {'Likes':<6} {'Comments':<8} {'Age':<8} {'Pop Score':<9} {'Recency':<8} {'Combined':<8}")
    print("-" * 85)
    
    for post in test_posts:
        created_at = datetime.now() - timedelta(hours=post["hours_ago"])
        score, components = calculate_combined_score(
            post["likes"],
            post["comments"],
            created_at
        )
        
        print(f"{post['name']:<25} {post['likes']:<6} {post['comments']:<8} {post['hours_ago']}h{'':<4} "
              f"{components['popularity']:.3f}{'':<5} {components['recency']:.3f}{'':<4} {score:.3f}")


def demo_geographic_features():
    """Demonstrate geographic features"""
    
    print("\n\n📍 Geographic Features Demo")
    print("=" * 50)
    
    from app.utils.ranking import haversine_distance
    
    # Bangkok coordinates
    bangkok = (13.7563, 100.5018)
    
    locations = [
        ("Chiang Mai", 18.7883, 98.9853),
        ("Phuket", 7.8804, 98.3923),
        ("Ayutthaya", 14.3532, 100.5648),
        ("Hua Hin", 12.5684, 99.9576),
    ]
    
    print(f"Distances from Bangkok:")
    print(f"{'Location':<15} {'Distance (km)':<12} {'Travel Category'}")
    print("-" * 45)
    
    for name, lat, lng in locations:
        distance = haversine_distance(bangkok[0], bangkok[1], lat, lng)
        category = "Nearby" if distance < 200 else "Regional" if distance < 500 else "Far"
        print(f"{name:<15} {distance:.0f}{'':<9} {category}")


if __name__ == "__main__":
    try:
        demo_search_functionality()
        demo_ranking_algorithm()
        demo_geographic_features()
        
        print("\n\n✅ Phase 1 Demo Complete!")
        print("🚀 Next Phase: Semantic search with embeddings")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()