#!/usr/bin/env python3
"""
PaiNaiDee Community Posts API Example Usage

This script demonstrates how to use the community post system APIs
including posting, liking, commenting, and media upload functionality.

Requirements:
- FastAPI server running on localhost:8000 (or update BASE_URL)
- Python requests library: pip install requests
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# API Configuration
BASE_URL = "http://localhost:8000/api"
HEADERS = {"Content-Type": "application/json"}

class PaiNaiDeeAPI:
    """Client for PaiNaiDee Community Posts API"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        response = self.session.get(f"{self.base_url.rstrip('/api')}/health")
        response.raise_for_status()
        return response.json()
    
    def create_post(
        self,
        caption: Optional[str] = None,
        tags: list = None,
        media_files: list = None,
        location_id: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create a new community post
        
        Args:
            caption: Post caption (max 2000 chars)
            tags: List of hashtags
            media_files: List of file paths to upload
            location_id: Optional location UUID
            lat: Latitude for auto-location matching
            lng: Longitude for auto-location matching
            
        Returns:
            Post creation response
        """
        url = f"{self.base_url}/posts"
        
        # Prepare form data
        data = {}
        if caption:
            data["caption"] = caption
        if tags:
            data["tags"] = json.dumps(tags)
        if location_id:
            data["location_id"] = location_id
        if lat is not None:
            data["lat"] = lat
        if lng is not None:
            data["lng"] = lng
        
        # Prepare files (for demo, we'll create dummy files)
        files = []
        if media_files:
            for i, file_path in enumerate(media_files):
                # In real usage, open actual files
                # files.append(('media_files', open(file_path, 'rb')))
                # For demo, create dummy file content
                files.append(('media_files', (f'demo_image_{i}.jpg', b'dummy_image_content', 'image/jpeg')))
        else:
            # Default demo file
            files.append(('media_files', ('demo_image.jpg', b'dummy_image_content', 'image/jpeg')))
        
        response = self.session.post(url, data=data, files=files)
        response.raise_for_status()
        return response.json()
    
    def like_post(self, post_id: str) -> Dict[str, Any]:
        """Like or unlike a post (toggle behavior)"""
        url = f"{self.base_url}/posts/{post_id}/like"
        response = self.session.post(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    
    def comment_on_post(self, post_id: str, content: str) -> Dict[str, Any]:
        """Add a comment to a post"""
        url = f"{self.base_url}/posts/{post_id}/comments"
        data = {"post_id": post_id, "content": content}
        response = self.session.post(url, json=data, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    
    def update_comment(self, comment_id: str, content: str) -> Dict[str, Any]:
        """Update a comment"""
        url = f"{self.base_url}/comments/{comment_id}"
        data = {"content": content}
        response = self.session.put(url, json=data, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    
    def delete_comment(self, comment_id: str) -> Dict[str, Any]:
        """Delete a comment"""
        url = f"{self.base_url}/comments/{comment_id}"
        response = self.session.delete(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    
    def get_post_engagement(self, post_id: str, limit_comments: int = 5) -> Dict[str, Any]:
        """Get engagement data for a post"""
        url = f"{self.base_url}/posts/{post_id}/engagement"
        params = {"limit_comments": limit_comments}
        response = self.session.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    
    def search_posts(self, query: str, location: Optional[str] = None) -> Dict[str, Any]:
        """Search for posts"""
        url = f"{self.base_url}/search"
        params = {"q": query}
        if location:
            params["location"] = location
        response = self.session.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        return response.json()


def demo_community_posts():
    """Demonstrate the community posts system"""
    print("🇹🇭 PaiNaiDee Community Posts API Demo\n")
    
    # Initialize API client
    api = PaiNaiDeeAPI()
    
    try:
        # 1. Health check
        print("1. ✅ API Health Check")
        health = api.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Version: {health['version']}")
        print()
        
        # 2. Create a post
        print("2. 📝 Creating a new post...")
        post_data = api.create_post(
            caption="Amazing sunset at Railay Beach! 🌅 Perfect evening for rock climbing and relaxation.",
            tags=["sunset", "railay", "krabi", "beach", "rockclimbing"],
            lat=8.0089,  # Railay Beach coordinates
            lng=98.8409
        )
        
        if post_data["success"]:
            post_id = post_data["post"]["id"]
            location_matched = post_data.get("location_matched")
            print(f"   ✅ Post created successfully!")
            print(f"   📍 Post ID: {post_id}")
            if location_matched:
                print(f"   🎯 Auto-matched location: {location_matched}")
            print()
        else:
            print("   ❌ Failed to create post")
            return
        
        # 3. Like the post
        print("3. ❤️ Liking the post...")
        like_result = api.like_post(post_id)
        print(f"   ✅ {like_result['message']}")
        print(f"   👍 Like count: {like_result['like_count']}")
        print()
        
        # 4. Add comments
        print("4. 💬 Adding comments...")
        comment1 = api.comment_on_post(post_id, "Wow! This looks absolutely stunning! 😍")
        comment2 = api.comment_on_post(post_id, "I need to visit Krabi soon. Thanks for sharing!")
        
        print(f"   ✅ Comment 1 added: {comment1['id']}")
        print(f"   ✅ Comment 2 added: {comment2['id']}")
        print()
        
        # 5. Update a comment
        print("5. ✏️ Updating a comment...")
        updated_comment = api.update_comment(
            comment1['id'], 
            "Wow! This looks absolutely stunning! 😍 I'm definitely adding this to my bucket list!"
        )
        print(f"   ✅ Comment updated successfully")
        print()
        
        # 6. Get engagement data
        print("6. 📊 Getting post engagement data...")
        engagement = api.get_post_engagement(post_id)
        print(f"   👍 Likes: {engagement['like_count']}")
        print(f"   💬 Comments: {engagement['comment_count']}")
        print(f"   ❤️ User liked: {engagement['user_liked']}")
        print(f"   📝 Recent comments: {len(engagement['recent_comments'])}")
        
        for comment in engagement['recent_comments']:
            print(f"      - \"{comment['content'][:50]}...\" by {comment['user_id']}")
        print()
        
        # 7. Unlike the post
        print("7. 💔 Unliking the post...")
        unlike_result = api.like_post(post_id)
        print(f"   ✅ {unlike_result['message']}")
        print(f"   👍 Like count: {unlike_result['like_count']}")
        print()
        
        # 8. Delete a comment
        print("8. 🗑️ Deleting a comment...")
        delete_result = api.delete_comment(comment2['id'])
        print(f"   ✅ {delete_result['message']}")
        print(f"   💬 Comment count: {delete_result['comment_count']}")
        print()
        
        # 9. Search for posts
        print("9. 🔍 Searching for beach posts...")
        search_results = api.search_posts("beach sunset")
        print(f"   📍 Found {len(search_results.get('results', []))} results")
        print()
        
        print("🎉 Demo completed successfully!")
        print("\nAPI Features Demonstrated:")
        print("✅ Post creation with media upload")
        print("✅ Auto-location matching from coordinates") 
        print("✅ Like/unlike functionality")
        print("✅ Comment creation, editing, and deletion")
        print("✅ Engagement data retrieval")
        print("✅ Content search")
        print("\n📱 Ready for mobile app integration!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server.")
        print("   Make sure the FastAPI server is running on http://localhost:8000")
        print("   Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e}")
        print(f"   Response: {e.response.text if e.response else 'No response'}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    demo_community_posts()