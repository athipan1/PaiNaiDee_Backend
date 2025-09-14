# Backend Phase 1 Notes (สำคัญ)

## หลีกเลี่ยงการปะปนสคีมา Flask (Integer) กับ FastAPI (UUID)

Phase 1 ใช้สคีมาแบบ UUID ทั้งหมดในตาราง `locations`, `posts`, `post_media` ฯลฯ
ห้ามใช้สคริปต์ seeding/initialization เดิมของฝั่ง Flask (เช่น `src/...`, `db.create_all()`) เพราะจะสร้างตาราง `posts` แบบ `INTEGER` แล้วทำให้ FK ใน `post_media.post_id` (ที่เป็น `UUID`) ผูกกับ `posts.id` ไม่ได้

## ขั้นตอนที่ถูกต้อง (PostgreSQL)

1) อัปเกรดสคีมาด้วย Alembic:
```bash
alembic upgrade head
```

2) Seed ข้อมูลตัวอย่างสำหรับ Phase 1 (UUID):
```bash
python seed_db.py
```

3) รันแอป FastAPI:
```bash
python run_fastapi.py
```

> หมายเหตุ:
> - หากคุณเคยรันสคริปต์ seeding เดิม (ฝั่ง Flask) มาก่อน อาจต้องล้างตารางที่เกี่ยวข้องก่อนใช้งาน Phase 1
> - สคริปต์ `seed_db.py` ที่ปรับปรุงแล้วใน Phase 1 จะทำงานกับโมเดล `app/db/models.py` เท่านั้น
> - หลีกเลี่ยงการเรียก `Base.metadata.create_all()` แบบปะปนจากหลายที่พร้อมกัน ให้ใช้ Alembic จัดการสคีมาเป็นหลัก

---

# PaiNaiDee Backend API - Phase 1

## Contextual Travel Content Search API Overview

This document describes the Phase 1 implementation of the PaiNaiDee Backend API, focusing on contextual search for travel posts with fuzzy matching, keyword expansion, basic ranking, and nearby places functionality.

## Architecture

### Framework Decision
- **Primary**: FastAPI (async-friendly, automatic OpenAPI generation, better typing)
- **Legacy**: Flask (existing codebase maintained for compatibility)
- **Database**: PostgreSQL with pg_trgm extension for fuzzy search

### Directory Structure
```
app/
├── main.py                     # FastAPI application entry point
├── api/                        # API route handlers
│   ├── routes_search.py        # Search endpoints
│   ├── routes_locations.py     # Location endpoints
│   └── routes_posts.py         # Post creation endpoints
├── core/                       # Core application components
│   ├── config.py              # Settings and configuration
│   └── logging.py             # Structured logging
├── services/                   # Business logic services
│   ├── search_service.py      # Search implementation
│   ├── location_service.py    # Location operations
│   └── post_service.py        # Post operations
├── db/                        # Database components
│   ├── session.py             # Database session management
│   ├── models.py              # SQLAlchemy models
│   └── migrations/            # Alembic migration files
├── schemas/                   # Pydantic request/response models
│   ├── search.py              # Search schemas
│   ├── locations.py           # Location schemas
│   └── posts.py               # Post schemas
└── utils/                     # Utility functions
    ├── text_normalize.py      # Text normalization
    ├── ranking.py             # Ranking algorithms
    └── expansion_loader.py    # Keyword expansion
```

## Phase 1 Features

### 1. Search API (`GET /api/search`)

**Core Functionality:**
- Fuzzy matching on location names using PostgreSQL trigram similarity
- Keyword expansion via static mapping (province → landmarks)
- Multi-field search across captions, tags, and locations
- Ranking blend combining popularity + recency with configurable weights

**Request Parameters:**
- `q`: Search query (required, 1-500 characters)
- `limit`: Number of results (default: 20, max: 100)
- `offset`: Pagination offset (default: 0)

**Response Structure:**
```json
{
  "query": "เชียงใหม่",
  "expansion": ["ดอยสุเทพ", "นิมมาน", "ถนนคนเดิน"],
  "posts": [
    {
      "id": "uuid",
      "caption": "สวยงามมากที่ดอยสุเทพ",
      "media": [{"type": "image", "url": "..."}],
      "location": {"id": "uuid", "name": "ดอยสุเทพ"},
      "like_count": 42,
      "comment_count": 5,
      "created_at": "2024-01-01T12:00:00Z",
      "score": 0.87
    }
  ],
  "suggestions": [
    {"type": "place", "text": "ดอยสุเทพ"},
    {"type": "tag", "text": "ภูเขา"}
  ],
  "latency_ms": 123
}
```

### 2. Location APIs

**Location Detail (`GET /api/locations/{id}`):**
- Complete location information with post counts
- Geographic coordinates if available
- Aliases and popularity metrics

**Nearby Places (`GET /api/locations/{id}/nearby`):**
- Geographic distance calculation (if coordinates available)
- Fallback to curated similarity-based suggestions
- Configurable radius (0.1-100 km)

**Autocomplete (`GET /api/locations/autocomplete`):**
- Fast prefix matching with fuzzy fallback
- Trigram similarity for typo tolerance
- Popularity-based ranking

### 3. Post Creation (`POST /api/posts`)

**Multipart Upload Support:**
- Image and video file uploads
- Caption and tag processing
- Auto-location matching based on coordinates (5km radius)
- Structured logging for analytics

**Features:**
- Optional location association via coordinates or location_id
- Tag indexing for search
- Media organization with ordering
- Auto-location matching within 5km radius

## Data Models

### Locations Table
```sql
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    province TEXT,
    aliases TEXT[] DEFAULT '{}',
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    popularity_score INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

### Posts Table
```sql
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    caption TEXT,
    tags TEXT[] DEFAULT '{}',
    location_id UUID REFERENCES locations(id),
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

### Post Media Table
```sql
CREATE TABLE post_media (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    media_type TEXT CHECK (media_type IN ('image','video')),
    url TEXT NOT NULL,
    thumb_url TEXT,
    ordering INTEGER DEFAULT 0
);
```

## Ranking Algorithm

### Combined Score Formula
```
score = w_pop × popularityNorm + w_recency × recencyDecay
```

**Popularity Normalization:**
```
popularityNorm = rawScore / (rawScore + maxExpected)
rawScore = likeCount + αComment × commentCount
```

**Recency Decay:**
```
recencyDecay = exp(-ageMinutes / τMinutes)
```

**Default Configuration:**
- `w_pop`: 0.7 (popularity weight)
- `w_recency`: 0.3 (recency weight)
- `αComment`: 2.0 (comment multiplier)
- `τMinutes`: 4320 (3 days decay constant)

## Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=painaidee_db
DB_USER=postgres
DB_PASSWORD=password

# Search Configuration
SEARCH_RANK_WEIGHTS='{"w_pop": 0.7, "w_recency": 0.3}'
MAX_NEARBY_RADIUS_KM=50.0
TRIGRAM_SIM_THRESHOLD=0.35
ALPHA_COMMENT=2.0
TAU_MINUTES=4320.0

# Application
DEBUG=false
```

### Keyword Expansion Data
Located in `seed/keyword_expansion.json`:
- Province → Landmark mappings
- Category → Related terms
- Synonym expansions

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Install PostgreSQL and create database
createdb painaidee_db

# Run migrations
alembic upgrade head
```

### 3. Run FastAPI Server
```bash
# Development
python run_fastapi.py

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Run Demo
```bash
python demo_phase1.py
```

## Testing

### Unit Tests
```bash
# Run specific test modules
pytest tests/test_text_normalize.py -v
pytest tests/test_ranking.py -v
pytest tests/test_expansion_loader.py -v

# Run all new tests
pytest tests/test_*.py -v
```

### Integration Testing
```bash
# Test search functionality (requires database)
pytest tests/test_search_integration.py -v
```

## Performance Optimizations

### Database Indexes
- **Trigram index**: `locations.name` using gin_trgm_ops
- **GIN indexes**: `locations.aliases`, `posts.tags`
- **Standard indexes**: Foreign keys, timestamps, popularity scores
- **Geographic indexes**: PostGIS or lat/lng composite indexes

### Search Optimizations
- Query normalization and caching
- Fuzzy match threshold tuning (default: 0.35)
- Limit expansion terms to prevent query explosion
- SQL-based ranking computation for performance

## Analytics & Logging

### Structured Events
- `search.performed`: Query, result count, latency
- `post.upload`: Post ID, geo status, location matching
- `location.nearby.request`: Location, radius, result count

### Log Format
```json
{
  "event_type": "search.performed",
  "timestamp": 1641024000.0,
  "query": "เชียงใหม่",
  "normalized": "เชียงใหม่",
  "resultCount": 15,
  "latencyMs": 123.45
}
```

## API Documentation

### OpenAPI Schema
- **Interactive docs**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`
- **Exported schema**: `openapi/contextual-search.yaml`

## Future Enhancements (Phase 2)

### Planned Features
1. **Semantic Search**: Vector embeddings with FAISS/Pinecone
2. **Related Posts**: Semantic similarity endpoint
3. **Advanced Moderation**: Content filtering and review system
4. **Enhanced Analytics**: Real-time dashboards and metrics
5. **Multi-language Support**: Expanded Thai/English processing

### Technical Improvements
- **Caching Layer**: Redis for search results and expansions
- **Search Suggestions**: ML-based query completion
- **Geographic Enhancement**: PostGIS integration for complex queries
- **Performance**: Query optimization and result caching

## Open Questions & TODOs

1. **PostGIS Availability**: Confirm PostGIS setup for production
2. **Authentication Integration**: JWT token extraction and user management
3. **Flask Compatibility**: Dual-framework maintenance strategy
4. **File Storage**: Cloud storage integration for media uploads
5. **Rate Limiting**: API protection and quota management

---

## Quick Start Example

```python
# Search for Chiang Mai content
import requests

response = requests.get('http://localhost:8000/api/search?q=เชียงใหม่&limit=5')
results = response.json()

print(f"Found {len(results['posts'])} posts")
print(f"Expanded terms: {results['expansion']}")
print(f"Search took {results['latency_ms']}ms")
```

This Phase 1 implementation provides a solid foundation for contextual travel content search, with room for semantic enhancements in Phase 2.