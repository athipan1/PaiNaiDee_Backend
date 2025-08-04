# PaiNaiDee Admin Video Management System

## Overview

This system provides a complete admin video management backend for the "ไปไหนดี" (PaiNaiDee) application. It includes email/password authentication for admins, secure video storage, and Row-Level Security (RLS) to ensure data isolation between admin users.

## Features

### 1. ✅ Email/Password Authentication for Admins with JWT
- Admin registration and login endpoints
- Email-based authentication (instead of username)
- JWT token-based authorization
- Separate admin and regular user authentication flows

### 2. ✅ Enhanced Database Schema
- Updated `User` model with email field and admin role
- Enhanced `VideoPost` model with title, description, thumbnail support
- Automatic timestamps (created_at, updated_at)
- File size and duration tracking

### 3. ✅ Cloud Storage Integration
- `StorageService` for handling video and thumbnail uploads
- Unique filename generation to prevent conflicts
- Support for multiple file formats
- Local storage implementation (ready for S3/GCS extension)

### 4. ✅ Row-Level Security (RLS)
- Application-level RLS enforcement
- Admins can only see/modify their own videos
- Secure API endpoints that prevent cross-admin access

### 5. ✅ Complete Admin Video API
- Upload videos with thumbnails
- List admin's own videos
- Get video details
- Update video metadata
- Delete videos
- Get video statistics

## API Endpoints

### Authentication

#### Register Admin
```http
POST /api/auth/admin/register
Content-Type: application/json

{
  "username": "admin",
  "email": "admin@painaidee.com", 
  "password": "securepassword123"
}
```

#### Admin Login
```http
POST /api/auth/admin/login
Content-Type: application/json

{
  "email": "admin@painaidee.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "message": "Admin login successful."
}
```

### Video Management

All video endpoints require admin authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer {access_token}
```

#### Upload Video
```http
POST /api/admin/videos/upload
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

Form Data:
- title: "Video Title" (required)
- description: "Video description" (optional)
- caption: "Video caption" (optional)
- video: video_file.mp4 (required)
- thumbnail: thumbnail.jpg (optional)
```

#### Get Admin Videos (RLS Applied)
```http
GET /api/admin/videos
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "Test Video",
      "description": "This is a test video",
      "caption": "Testing upload",
      "video_url": "/uploads/videos/video_123.mp4",
      "thumbnail_url": "/uploads/thumbnails/thumb_123.jpg",
      "file_size": 1048576,
      "duration": 120,
      "user_id": 1,
      "username": "admin",
      "email": "admin@painaidee.com",
      "created_at": "2025-08-04T01:00:00",
      "updated_at": "2025-08-04T01:00:00"
    }
  ],
  "message": "Retrieved 1 videos"
}
```

#### Get Video Details
```http
GET /api/admin/videos/{video_id}
Authorization: Bearer {access_token}
```

#### Update Video
```http
PUT /api/admin/videos/{video_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated description",
  "caption": "Updated caption"
}
```

#### Delete Video
```http
DELETE /api/admin/videos/{video_id}
Authorization: Bearer {access_token}
```

#### Get Video Statistics
```http
GET /api/admin/videos/stats
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_videos": 5,
    "total_size_mb": 150.5,
    "total_duration_minutes": 45.0,
    "average_size_mb": 30.1,
    "average_duration_minutes": 9.0
  },
  "message": "Video statistics retrieved successfully"
}
```

## Security Features

### Row-Level Security (RLS)
- **Application-level enforcement**: All video queries filter by `user_id = current_admin_id`
- **Cross-admin protection**: Admin A cannot access Admin B's videos
- **Consistent enforcement**: RLS applies to all CRUD operations

### Authentication & Authorization
- **JWT-based auth**: Secure token-based authentication
- **Admin role checking**: Endpoints verify `is_admin = true`
- **Token validation**: All protected endpoints validate JWT tokens

### File Security
- **Unique filenames**: UUID-based filenames prevent conflicts
- **File type validation**: Only allowed video/image formats accepted
- **Size limits**: Configurable file size limits
- **Secure storage**: Files stored outside web root

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Video Posts Table
```sql
CREATE TABLE video_posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    caption TEXT,
    video_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    duration INTEGER,
    file_size BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### PostgreSQL RLS Policies
```sql
-- Enable RLS on video_posts table
ALTER TABLE video_posts ENABLE ROW LEVEL SECURITY;

-- Create policy for admin access
CREATE POLICY admin_video_policy ON video_posts
FOR ALL
USING (user_id = CAST(current_setting('app.current_user_id', true) AS INTEGER))
WITH CHECK (user_id = CAST(current_setting('app.current_user_id', true) AS INTEGER));
```

## Testing

The system includes comprehensive tests covering:

- ✅ Admin authentication (register/login)
- ✅ Video upload with validation
- ✅ RLS enforcement between admins
- ✅ Permission validation (admin vs regular users)
- ✅ CRUD operations on videos
- ✅ File handling and storage

### Manual Testing Examples

1. **Register and login as admin**:
```bash
# Register admin
curl -X POST http://localhost:5000/api/auth/admin/register \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "email": "admin@painaidee.com", "password": "admin123456"}'

# Login admin
curl -X POST http://localhost:5000/api/auth/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@painaidee.com", "password": "admin123456"}'
```

2. **Upload a video**:
```bash
# Upload video with thumbnail
curl -X POST http://localhost:5000/api/admin/videos/upload \
  -H "Authorization: Bearer {token}" \
  -F "title=Test Video" \
  -F "description=This is a test" \
  -F "video=@video.mp4" \
  -F "thumbnail=@thumb.jpg"
```

3. **Test RLS**:
```bash
# Admin 1 creates video, Admin 2 cannot see it
# Admin 1 token gets video list -> sees their videos
# Admin 2 token gets video list -> sees empty list
```

## Deployment Notes

### Environment Variables
```bash
# Database
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=painaidee_db

# Flask
SECRET_KEY=your-secret-key
FLASK_ENV=production
```

### Database Migration
Run the migration script to set up the enhanced schema:
```bash
python migrate_admin_video_system.py
```

### File Storage
- Development: Local file storage in `uploads/` directory
- Production: Extend `StorageService` for S3/GCS integration

### PostgreSQL RLS Setup
For production PostgreSQL deployments, run the RLS setup commands to enable database-level security policies.

## Future Enhancements

1. **Cloud Storage**: Full S3/GCS integration
2. **Video Processing**: Thumbnail generation, transcoding
3. **Analytics**: Video view tracking, admin dashboard
4. **Bulk Operations**: Batch upload/delete
5. **Content Moderation**: Automated content scanning
6. **API Rate Limiting**: Prevent abuse
7. **Advanced Search**: Full-text search on video metadata

## Conclusion

The PaiNaiDee Admin Video Management System provides a secure, scalable foundation for admin video content management with proper authentication, authorization, and data isolation through Row-Level Security.