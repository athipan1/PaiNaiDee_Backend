# PaiNaiDee Community Posts System 🇹🇭

A comprehensive backend system for community posts with likes, comments, and media uploads, specifically designed for mobile-first tourism applications.

## 🚀 Features Implemented

### ✅ **Complete Post System**
- **Post Schema**: Complete with `caption`, `hashtags` (tags), `media_url`, `created_at`, `user_id`
- **Media Support**: Images and videos with automatic thumbnail generation
- **Location Integration**: Auto-location matching based on GPS coordinates
- **Mobile-Optimized**: Designed for mobile app integration with multipart form uploads

### ✅ **Engagement System**
- **Like/Unlike**: Toggle-based liking system with real-time counts
- **Comments**: Create, read, update, delete comments with ownership validation
- **Engagement Analytics**: Real-time like/comment counts and user interaction tracking

### ✅ **Authentication & Security**
- **JWT Integration**: Ready for user authentication system
- **Permission Control**: Users can only edit/delete their own content
- **Input Validation**: Comprehensive validation for all inputs

### ✅ **Cloud Storage Ready**
- **Multi-Backend Support**: Supabase, Firebase, or demo storage
- **File Type Validation**: Images and videos with size limits
- **Organized Storage**: Files organized by user and post for easy management

## 📋 API Endpoints

### Posts
```http
POST   /api/posts                     # Create new post with media
GET    /api/posts/{id}               # Get post details
```

### Engagement
```http
POST   /api/posts/{id}/like          # Like/unlike a post
GET    /api/posts/{id}/engagement    # Get engagement data
POST   /api/posts/{id}/comments      # Add comment
PUT    /api/comments/{id}            # Update comment
DELETE /api/comments/{id}            # Delete comment
```

### Search & Discovery
```http
GET    /api/search                   # Search posts and locations
GET    /api/locations                # Browse locations
```

## 🔧 Configuration

### Environment Variables
```env
# Storage Configuration
STORAGE_TYPE=demo|supabase|firebase

# Supabase Storage (optional)
SUPABASE_URL=your_supabase_url
SUPABASE_API_KEY=your_supabase_anon_key

# Firebase Storage (optional)
FIREBASE_CREDENTIALS_PATH=path/to/credentials.json
FIREBASE_BUCKET_NAME=your_bucket_name
```

### Database Schema
The system includes these new tables:
- `posts` - Community posts with media and location data
- `post_media` - Media files associated with posts
- `post_likes` - User likes for posts
- `post_comments` - User comments on posts
- `locations` - Location data for auto-matching

## 📱 Mobile App Integration

### Creating a Post
```javascript
// Example: React Native/Flutter integration
const createPost = async (caption, tags, mediaFiles, location) => {
  const formData = new FormData();
  
  formData.append('caption', caption);
  formData.append('tags', JSON.stringify(tags));
  
  if (location) {
    formData.append('lat', location.latitude);
    formData.append('lng', location.longitude);
  }
  
  mediaFiles.forEach(file => {
    formData.append('media_files', file);
  });
  
  const response = await fetch('/api/posts', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${authToken}`,
    },
    body: formData,
  });
  
  return response.json();
};
```

### Liking a Post
```javascript
const likePost = async (postId) => {
  const response = await fetch(`/api/posts/${postId}/like`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${authToken}`,
      'Content-Type': 'application/json',
    },
  });
  
  return response.json();
};
```

### Adding a Comment
```javascript
const addComment = async (postId, content) => {
  const response = await fetch(`/api/posts/${postId}/comments`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${authToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      post_id: postId,
      content: content,
    }),
  });
  
  return response.json();
};
```

## 🧪 Testing

### Run the Demo
```bash
# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run the community posts demo
python demo_community_posts.py
```

### API Testing
The API includes comprehensive OpenAPI documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Unit Tests
```bash
# Run engagement system tests
python -m pytest tests/test_engagement.py -v

# Run all tests
python -m pytest tests/ -v
```

## 🏗️ Architecture

### Mobile-First Design
- **Multipart Form Support**: Native mobile file upload support
- **Efficient APIs**: Optimized for mobile network conditions
- **Real-time Updates**: Live engagement counts and notifications ready

### Scalable Backend
- **Async Architecture**: FastAPI with async/await for high performance
- **Database Indexing**: Optimized queries for engagement and search
- **Cloud Storage**: Ready for CDN integration and global scaling

### Future-Ready
- **Microservices Ready**: Clean separation of concerns
- **Analytics Integration**: Structured logging for business intelligence
- **Extensible Schema**: Easy to add new features like stories, polls, etc.

## 🎯 Use Cases

### Tourism Community
- **Travel Posts**: Share photos/videos from tourist attractions
- **Location Discovery**: Auto-match posts to known destinations
- **Social Engagement**: Like and comment on travel experiences
- **Content Search**: Find posts by location, hashtags, or content

### Mobile Features
- **Offline Support**: Ready for offline-first mobile implementation
- **Push Notifications**: Backend ready for like/comment notifications
- **Progressive Upload**: Support for background media uploads
- **Responsive Media**: Automatic thumbnail generation for videos

## 📊 Analytics & Insights

The system includes comprehensive logging for:
- Post creation and engagement metrics
- User interaction patterns
- Popular locations and content
- Search queries and discovery patterns

## 🔮 Future Enhancements

### Phase 2 Features
- **Stories**: Temporary post support
- **Video Streaming**: Live streaming capabilities
- **AI Recommendations**: Content recommendation engine
- **Social Graph**: Follow/follower system
- **Monetization**: Business posting and promotion features

### Technical Roadmap
- **Real-time Features**: WebSocket support for live updates
- **Advanced Search**: Semantic search with embeddings
- **Content Moderation**: AI-powered content filtering
- **Performance**: Redis caching and CDN integration

---

**Built with ❤️ for the Thai tourism community** 🇹🇭

Ready for mobile app integration and production deployment!