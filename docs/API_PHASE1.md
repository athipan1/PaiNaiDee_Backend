# PaiNaiDee Backend API - Phase 1 Documentation

## Overview

The PaiNaiDee Backend API is a contextual travel content search system built with FastAPI and PostgreSQL. This Phase 1 implementation provides comprehensive search functionality with fuzzy matching, keyword expansion, geographic filtering, and ranking algorithms.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://dae2ecbe68a0.ngrok-free.app/api`

## Authentication

The API supports two authentication methods:

### 1. JWT Token Authentication
```http
Authorization: Bearer <jwt-token>
```

### 2. API Key Authentication
```http
X-API-Key: demo-api-key
X-Actor-Id: user_123
```

**Valid API Keys for Testing:**
- `demo-api-key`
- `test-key-123` 
- `painaidee-dev-key`

## Core Endpoints

### Health Check

#### `GET /health`
Enhanced health check with database status and version information.

**Response Example:**
```json
{
  "status": "ok",
  "app_version": "1.0.0",
  "timestamp": 1757953187.644,
  "checks": {
    "database": "ok",
    "response_time_ms": 12.5
  },
  "message": "PaiNaiDee Backend API is running"
}
```

### Search API

#### `GET /api/search`
Search for travel posts with comprehensive filtering and ranking.

**Parameters:**
- `q` (required): Search query (1-500 characters)
- `lat` (optional): Latitude for distance-based filtering/sorting
- `lon` (optional): Longitude for distance-based filtering/sorting  
- `radius_km` (optional): Search radius in kilometers (default: 50)
- `limit` (optional): Number of results (1-100, default: 20)
- `offset` (optional): Pagination offset (default: 0)
- `sort` (optional): Sort order - `relevance`, `distance`, `popularity`, `newest` (default: relevance)

**Example Request:**
```http
GET /api/search?q=เชียงใหม่&lat=18.7883&lon=98.9853&sort=distance&limit=10
```

**Features:**
- **Fuzzy Matching**: Uses PostgreSQL pg_trgm for similarity scoring
- **Keyword Expansion**: Automatically expands queries (e.g., "เชียงใหม่" → ["ดอยสุเทพ", "นิมมาน"])
- **Geographic Filtering**: Distance-based filtering using Haversine formula
- **Multiple Ranking**: Relevance, popularity, recency, and distance-based sorting

#### `POST /api/search`
Alternative search endpoint accepting JSON request body.

**Request Body:**
```json
{
  "q": "ทะเล",
  "lat": 7.8804,
  "lon": 98.3923,
  "radius_km": 50,
  "sort": "distance",
  "limit": 20,
  "offset": 0
}
```

**Response Format:**
```json
{
  "query": "เชียงใหม่",
  "expansion": ["ดอยสุเทพ", "นิมมาน", "ถนนคนเดิน"],
  "posts": [
    {
      "id": "uuid",
      "caption": "Beautiful sunset at Doi Suthep",
      "media": [
        {
          "type": "image",
          "url": "https://storage.example.com/image.jpg",
          "thumb_url": null
        }
      ],
      "location": {
        "id": "uuid",
        "name": "ดอยสุเทพ",
        "province": "เชียงใหม่",
        "lat": 18.8047,
        "lng": 98.9217
      },
      "like_count": 25,
      "comment_count": 3,
      "created_at": "2024-01-15T10:30:00Z",
      "score": 0.85,
      "distance_km": 5.2
    }
  ],
  "suggestions": [],
  "latency_ms": 45.2,
  "total_count": 150
}
```

### Locations API

#### `GET /api/locations`
Get paginated list of locations with optional filtering.

**Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (1-100, default: 20)
- `province` (optional): Filter by province name
- `lat` (optional): Latitude for distance filtering
- `lon` (optional): Longitude for distance filtering
- `radius_km` (optional): Search radius in kilometers

**Example:**
```http
GET /api/locations?province=เชียงใหม่&page=1&page_size=20
```

#### `GET /api/locations/{location_id}`
Get detailed information about a specific location.

**Response Example:**
```json
{
  "id": "uuid",
  "name": "ดอยสุเทพ",
  "province": "เชียงใหม่",
  "aliases": ["Doi Suthep", "วัดพระธาตุดอยสุเทพ"],
  "lat": 18.8047,
  "lng": 98.9217,
  "popularity_score": 95,
  "created_at": "2024-01-01T00:00:00Z",
  "posts_count": 1250,
  "nearby_locations": []
}
```

#### `GET /api/locations/{location_id}/nearby`
Get nearby locations within specified radius.

**Parameters:**
- `radius_km` (optional): Search radius (0.1-100 km, default: 10)

#### `GET /api/locations/autocomplete`
Get location autocomplete suggestions.

**Parameters:**
- `q` (required): Search query
- `limit` (optional): Maximum suggestions (1-50, default: 10)

### Posts API

#### `GET /api/posts`
Get paginated list of posts, ordered by creation date (newest first).

**Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (1-50, default: 10)

#### `POST /api/posts`
Create a new post with media uploads. **Requires Authentication**.

**Content-Type**: `multipart/form-data`

**Form Fields:**
- `caption` (optional): Post caption (max 2000 chars)
- `tags` (optional): JSON array of tags, e.g., `["beach", "sunset"]`
- `location_id` (optional): Location UUID
- `lat` (optional): Latitude for auto-location matching
- `lng` (optional): Longitude for auto-location matching  
- `media_files` (required): One or more image/video files

**Features:**
- **Auto-location Matching**: Finds nearest location within 5km radius
- **Multi-file Upload**: Supports multiple images and videos
- **Tag Processing**: Automatic indexing for search

**Example with curl:**
```bash
curl -X POST "/api/posts" \
  -H "X-API-Key: demo-api-key" \
  -H "X-Actor-Id: user_123" \
  -F "caption=Beautiful sunset at the beach" \
  -F "tags=[\"beach\", \"sunset\"]" \
  -F "lat=7.8804" \
  -F "lng=98.3923" \
  -F "media_files=@image1.jpg" \
  -F "media_files=@image2.jpg"
```

#### `GET /api/posts/{post_id}`
Get detailed information about a specific post.

### Engagement API

#### `POST /api/posts/{post_id}/like`
Like or unlike a post (toggle behavior). **Requires Authentication**.

**Features:**
- **Idempotent**: Same user can't like a post multiple times
- **Toggle Behavior**: Second request unlikes the post
- **Count Updates**: Automatically updates post like count

**Response Example:**
```json
{
  "success": true,
  "message": "Post liked successfully",
  "like_count": 26
}
```

#### `GET /api/posts/{post_id}/comments`
Get paginated comments for a post.

**Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Comments per page (1-50, default: 10)

#### `POST /api/posts/{post_id}/comments`
Add a comment to a post. **Requires Authentication**.

**Request Body:**
```json
{
  "content": "Great photo! Love the lighting."
}
```

**Response Example:**
```json
{
  "id": "uuid",
  "post_id": "uuid", 
  "user_id": "user_123",
  "content": "Great photo! Love the lighting.",
  "created_at": "2024-01-15T15:30:00Z",
  "updated_at": "2024-01-15T15:30:00Z"
}
```

## HTTP Status Codes

The API returns appropriate HTTP status codes:

- **200 OK**: Successful GET requests
- **201 Created**: Successful POST requests
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **405 Method Not Allowed**: HTTP method not supported
- **422 Unprocessable Entity**: Request validation failed

## Error Response Format

```json
{
  "detail": "Error message describing what went wrong",
  "type": "validation_error" 
}
```

## Search Algorithm Details

### Fuzzy Matching
- Uses PostgreSQL `pg_trgm` extension for trigram similarity
- Configurable similarity threshold (default: 0.35)
- Optimized with GIN indexes using `gin_trgm_ops`

### Keyword Expansion
Static mappings from `data/keyword_mapping.json`:
- **Provinces**: "เชียงใหม่" → ["ดอยสุเทพ", "นิมมาน", "ถนนคนเดิน"]
- **Categories**: "ทะเล" → ["sea", "beach", "ชายทะเล", "เกาะ"]
- **Activities**: "ดำน้ำ" → ["diving", "snorkeling", "underwater"]
- **Thai/English**: "beach" ↔ ["ชายหาด", "ทะเล", "เกาะ"]

### Ranking Algorithm

**Combined Score Formula:**
```
score = w_pop × popularityNorm + w_recency × recencyDecay × relevanceScore
```

**Components:**
- **Popularity**: `log(1 + likes + 2×comments) / log(1001)`
- **Recency**: `exp(-age_minutes / 4320)` (3-day decay)
- **Relevance**: Match quality (0.5-0.9 based on field and match type)
- **Weights**: `w_pop = 0.7`, `w_recency = 0.3` (configurable)

### Distance Calculation
Haversine formula for geographic distance:
```sql
6371 * acos(cos(radians(lat1)) * cos(radians(lat2)) * 
cos(radians(lng2) - radians(lng1)) + sin(radians(lat1)) * sin(radians(lat2)))
```

## Database Schema

### Core Tables
- **locations**: Places with coordinates and metadata
- **posts**: User-generated content with location links
- **post_media**: Images/videos associated with posts
- **post_likes**: Like relationships with uniqueness constraints
- **post_comments**: User comments on posts

### Performance Indexes
- `idx_locations_name_trgm`: GIN trigram index for fuzzy search
- `idx_locations_aliases`: GIN index for alias arrays
- `idx_posts_tags`: GIN index for tag arrays
- Geographic indexes for distance calculations

## Configuration

Key environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Authentication  
API_KEYS=demo-api-key,test-key-123,painaidee-dev-key
JWT_SECRET_KEY=your-secret-key

# Search Configuration
TRIGRAM_SIM_THRESHOLD=0.35
SEARCH_RANK_WEIGHTS={"w_pop": 0.7, "w_recency": 0.3}
ALPHA_COMMENT=2.0
TAU_MINUTES=4320

# Application
DEBUG=true
APP_VERSION=1.0.0
```

## OpenAPI Documentation

Interactive API documentation is available at:
- **Swagger UI**: `/docs`
- **OpenAPI Schema**: `/openapi.json`

The documentation includes request/response examples, parameter descriptions, and authentication requirements for each endpoint.

## Example Usage Scenarios

### 1. Search for Beach Content Near Phuket
```http
GET /api/search?q=ทะเล&lat=7.8804&lon=98.3923&sort=distance&limit=10
```

### 2. Find Popular Mountain Content
```http  
GET /api/search?q=ภูเขา&sort=popularity&limit=20
```

### 3. Create Post with Auto-Location
```bash
curl -X POST "/api/posts" \
  -H "X-API-Key: demo-api-key" \
  -H "X-Actor-Id: user_123" \
  -F "caption=Amazing view from the top!" \
  -F "lat=18.8047" \
  -F "lng=98.9217" \
  -F "media_files=@mountain_view.jpg"
```

### 4. Like a Post
```bash
curl -X POST "/api/posts/uuid/like" \
  -H "X-API-Key: demo-api-key" \
  -H "X-Actor-Id: user_123"
```

This completes the Phase 1 API implementation with comprehensive search, location management, post creation, and engagement features.