#!/usr/bin/env python3
"""
PaiNaiDee Community Posts API Mock Demo

This script demonstrates the API structure without requiring a database connection.
It shows the expected request/response formats for mobile app integration.
"""

import uuid
from datetime import datetime
import json


class MockPaiNaiDeeAPI:
    """Mock client for demonstrating PaiNaiDee Community Posts API"""
    
    def __init__(self):
        self.posts_db = {}
        self.likes_db = {}
        self.comments_db = {}
        self.user_id = "user_123_demo"
    
    def health_check(self):
        """Mock health check"""
        return {
            "status": "healthy",
            "version": "1.0.0",
            "database": "postgresql",
            "search_engine": "pg_trgm + custom ranking"
        }
    
    def create_post(self, caption=None, tags=None, media_files=None, location_id=None, lat=None, lng=None):
        """Mock post creation"""
        post_id = str(uuid.uuid4())
        location_matched = None
        
        # Mock auto-location matching
        if lat and lng:
            # Railay Beach coordinates for demo
            if 7.9 <= lat <= 8.1 and 98.7 <= lng <= 98.9:
                location_matched = "Railay Beach, Krabi"
                location_id = str(uuid.uuid4())
        
        # Mock media processing
        media_responses = []
        for i, media_file in enumerate(media_files or ["demo_image.jpg"]):
            media_id = str(uuid.uuid4())
            media_type = "image" if "image" in media_file else "video"
            media_url = f"https://storage.example.com/posts/{self.user_id}/{media_file}"
            thumb_url = f"https://storage.example.com/posts/{self.user_id}/thumb_{media_file}" if media_type == "video" else None
            
            media_responses.append({
                "id": media_id,
                "media_type": media_type,
                "url": media_url,
                "thumb_url": thumb_url,
                "ordering": i
            })
        
        post = {
            "id": post_id,
            "user_id": self.user_id,
            "caption": caption,
            "tags": tags or [],
            "location_id": location_id,
            "lat": lat,
            "lng": lng,
            "like_count": 0,
            "comment_count": 0,
            "media": media_responses,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.posts_db[post_id] = post
        
        return {
            "success": True,
            "post": post,
            "location_matched": location_matched,
            "message": "Post created successfully"
        }
    
    def like_post(self, post_id):
        """Mock like/unlike functionality"""
        if post_id not in self.posts_db:
            return {"success": False, "message": "Post not found"}
        
        like_key = f"{post_id}_{self.user_id}"
        
        if like_key in self.likes_db:
            # Unlike
            del self.likes_db[like_key]
            self.posts_db[post_id]["like_count"] -= 1
            message = "Post unliked successfully"
        else:
            # Like
            self.likes_db[like_key] = {
                "id": str(uuid.uuid4()),
                "post_id": post_id,
                "user_id": self.user_id,
                "created_at": datetime.utcnow().isoformat()
            }
            self.posts_db[post_id]["like_count"] += 1
            message = "Post liked successfully"
        
        return {
            "success": True,
            "message": message,
            "like_count": self.posts_db[post_id]["like_count"]
        }
    
    def comment_on_post(self, post_id, content):
        """Mock comment creation"""
        if post_id not in self.posts_db:
            raise ValueError("Post not found")
        
        comment_id = str(uuid.uuid4())
        comment = {
            "id": comment_id,
            "post_id": post_id,
            "user_id": self.user_id,
            "content": content,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.comments_db[comment_id] = comment
        self.posts_db[post_id]["comment_count"] += 1
        
        return comment
    
    def update_comment(self, comment_id, content):
        """Mock comment update"""
        if comment_id not in self.comments_db:
            raise ValueError("Comment not found")
        
        comment = self.comments_db[comment_id]
        if comment["user_id"] != self.user_id:
            raise PermissionError("You can only edit your own comments")
        
        comment["content"] = content
        comment["updated_at"] = datetime.utcnow().isoformat()
        
        return comment
    
    def delete_comment(self, comment_id):
        """Mock comment deletion"""
        if comment_id not in self.comments_db:
            return {"success": False, "message": "Comment not found"}
        
        comment = self.comments_db[comment_id]
        if comment["user_id"] != self.user_id:
            return {"success": False, "message": "You can only delete your own comments"}
        
        post_id = comment["post_id"]
        del self.comments_db[comment_id]
        self.posts_db[post_id]["comment_count"] -= 1
        
        return {
            "success": True,
            "message": "Comment deleted successfully",
            "comment_count": self.posts_db[post_id]["comment_count"]
        }
    
    def get_post_engagement(self, post_id, limit_comments=5):
        """Mock engagement data retrieval"""
        if post_id not in self.posts_db:
            return None
        
        post = self.posts_db[post_id]
        
        # Check if user liked this post
        like_key = f"{post_id}_{self.user_id}"
        user_liked = like_key in self.likes_db
        
        # Get recent comments
        post_comments = [c for c in self.comments_db.values() if c["post_id"] == post_id]
        post_comments.sort(key=lambda x: x["created_at"], reverse=True)
        recent_comments = post_comments[:limit_comments]
        
        return {
            "post_id": post_id,
            "like_count": post["like_count"],
            "comment_count": post["comment_count"],
            "user_liked": user_liked,
            "recent_comments": recent_comments
        }
    
    def search_posts(self, query, location=None):
        """Mock search functionality"""
        results = []
        for post in self.posts_db.values():
            # Simple search matching
            if query.lower() in (post.get("caption") or "").lower():
                results.append(post)
            elif any(query.lower() in tag.lower() for tag in post.get("tags", [])):
                results.append(post)
        
        return {
            "results": results,
            "query": query,
            "total": len(results)
        }


def demo_community_posts():
    """Demonstrate the community posts system"""
    print("🇹🇭 PaiNaiDee Community Posts API Mock Demo\n")
    print("This demo shows the API structure and features without requiring database setup.\n")
    
    # Initialize mock API client
    api = MockPaiNaiDeeAPI()
    
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
            media_files=["railay_sunset.jpg", "climbing_video.mp4"],
            lat=8.0089,  # Railay Beach coordinates
            lng=98.8409
        )
        
        if post_data["success"]:
            post_id = post_data["post"]["id"]
            location_matched = post_data.get("location_matched")
            print(f"   ✅ Post created successfully!")
            print(f"   📍 Post ID: {post_id[:8]}...")
            if location_matched:
                print(f"   🎯 Auto-matched location: {location_matched}")
            print(f"   📷 Media files: {len(post_data['post']['media'])} items uploaded")
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
        
        print(f"   ✅ Comment 1 added: {comment1['id'][:8]}...")
        print(f"   ✅ Comment 2 added: {comment2['id'][:8]}...")
        print()
        
        # 5. Update a comment
        print("5. ✏️ Updating a comment...")
        updated_comment = api.update_comment(
            comment1['id'], 
            "Wow! This looks absolutely stunning! 😍 I'm definitely adding this to my bucket list!"
        )
        print(f"   ✅ Comment updated successfully")
        print(f"   📝 New content: \"{updated_comment['content'][:50]}...\"")
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
        print(f"   📍 Found {search_results['total']} results")
        for result in search_results['results']:
            print(f"      - \"{result['caption'][:50]}...\"")
        print()
        
        print("🎉 Mock Demo completed successfully!")
        print("\n📋 API Features Demonstrated:")
        print("✅ Post creation with media upload simulation")
        print("✅ Auto-location matching from coordinates") 
        print("✅ Like/unlike functionality")
        print("✅ Comment creation, editing, and deletion")
        print("✅ Engagement data retrieval")
        print("✅ Content search")
        print("\n📱 Ready for mobile app integration!")
        print("\n🔧 Database Setup:")
        print("To use the real API with database:")
        print("1. Set up PostgreSQL database")
        print("2. Configure environment variables in .env file")
        print("3. Run migrations: alembic upgrade head")
        print("4. Start server: uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")


if __name__ == "__main__":
    demo_community_posts()