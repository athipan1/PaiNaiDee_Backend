# Fuzzy Search Implementation

## Overview
This implementation provides advanced fuzzy search capabilities for the PaiNaiDee Backend system using PostgreSQL's `pg_trgm` extension and Python-based fallback algorithms.

## Features

### 1. Fuzzy Search Engine
- **PostgreSQL pg_trgm Integration**: Uses PostgreSQL's trigram matching for high-performance fuzzy search
- **Python Fallback**: Implements custom fuzzy matching when pg_trgm is not available
- **Multi-language Support**: Handles both Thai and English search queries
- **Synonym Expansion**: Automatically expands search terms with related synonyms

### 2. Multiple Query Parameters Support
The search endpoint supports various parameters for flexible searching:

#### Search Parameters
- `query` (string): Main search term
- `language` (string): Language preference ("th" or "en")
- `province` (string): Filter by province name
- `category` (string): Filter by attraction category
- `min_rating` (float): Minimum rating filter
- `max_rating` (float): Maximum rating filter
- `sort_by` (string): Sort order ("relevance", "rating", "name")
- `limit` (int): Number of results per page (default: 20)
- `offset` (int): Starting position for pagination

## API Endpoints

### 1. Main Search Endpoint
```
GET/POST /api/search
```

**Parameters (GET):**
```
?query=วัด&language=th&province=กรุงเทพฯ&category=วัฒนธรรม&sort_by=relevance&limit=10
```

**Parameters (POST):**
```json
{
  "query": "temple",
  "language": "en",
  "province": "Bangkok",
  "category": "Culture",
  "min_rating": 4.0,
  "sort_by": "rating",
  "limit": 10,
  "offset": 0
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": 1,
        "name": "วัดพระแก้ว",
        "description": "วัดที่ศักดิ์สิทธิ์...",
        "province": "กรุงเทพฯ",
        "category": "วัฒนธรรม",
        "similarity_score": 0.95,
        "matched_fields": ["name:exact", "category:contains"],
        "confidence": 0.95,
        "average_rating": 4.8,
        "total_reviews": 156
      }
    ],
    "total_count": 25,
    "query": "วัด",
    "filters": {
      "language": "th",
      "province": null,
      "category": null,
      "sort_by": "relevance"
    },
    "pagination": {
      "limit": 10,
      "offset": 0,
      "has_more": true
    },
    "processing_time_ms": 45.2
  }
}
```

### 2. Search Suggestions
```
GET /api/search/suggestions?query=วัด&language=th&limit=10
```

**Response:**
```json
{
  "success": true,
  "data": {
    "suggestions": [
      {
        "id": "attraction-1",
        "type": "attraction",
        "text": "วัดพระแก้ว",
        "description": "กรุงเทพฯ",
        "confidence": 1.0,
        "province": "กรุงเทพฯ",
        "category": "วัฒนธรรม"
      }
    ]
  }
}
```

### 3. Trending Searches
```
GET /api/search/trending?language=th
```

**Response:**
```json
{
  "success": true,
  "data": {
    "trending": ["ทะเล", "วัด", "ภูเขา", "น้ำตก", "ตลาด"]
  }
}
```

## Technical Implementation

### Search Service Components

#### 1. SearchQuery Dataclass
```python
@dataclass
class SearchQuery:
    query: str = ""
    language: str = "th"
    province: Optional[str] = None
    category: Optional[str] = None
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    sort_by: str = "relevance"
    limit: int = 20
    offset: int = 0
```

#### 2. Fuzzy Matching Algorithm
- **Exact Match**: 100% similarity for identical terms
- **Contains Match**: 80% similarity for substring matches
- **Word Boundary Match**: 60% similarity for word-level matches
- **Fuzzy Match**: Variable similarity using sequence matching

#### 3. PostgreSQL Integration
When PostgreSQL with pg_trgm is available:
- Uses `similarity()` function for trigram matching
- Creates GIN indexes for performance
- Supports threshold-based filtering
- Handles multiple search terms efficiently

### Synonym System

#### Thai Synonyms
```python
thai_synonyms = {
    "ทะเล": ["ชายหาด", "หาด", "เกาะ", "น้ำ"],
    "วัด": ["พระ", "โบสถ์", "ศาสนา", "พุทธ"],
    "ภูเขา": ["ดอย", "เขา", "ยอด", "ปีน"],
    # ...
}
```

#### English Synonyms
```python
english_synonyms = {
    "beach": ["sea", "ocean", "coast", "island", "water"],
    "temple": ["wat", "buddhist", "religious", "sacred", "buddha"],
    "mountain": ["hill", "peak", "summit", "doi", "climb"],
    # ...
}
```

## Database Setup

### PostgreSQL Extensions
```sql
-- Enable pg_trgm extension
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable unaccent extension (optional)
CREATE EXTENSION IF NOT EXISTS unaccent;
```

### Performance Indexes
```sql
-- GIN indexes for fuzzy search
CREATE INDEX CONCURRENTLY idx_attractions_name_gin 
ON attractions USING gin (name gin_trgm_ops);

CREATE INDEX CONCURRENTLY idx_attractions_description_gin 
ON attractions USING gin (description gin_trgm_ops);

CREATE INDEX CONCURRENTLY idx_attractions_province_gin 
ON attractions USING gin (province gin_trgm_ops);
```

### Custom Functions
```sql
-- Custom fuzzy search function
CREATE OR REPLACE FUNCTION fuzzy_search_attractions(
    search_query TEXT,
    similarity_threshold REAL DEFAULT 0.3
)
RETURNS TABLE (
    id INTEGER,
    name VARCHAR(255),
    similarity_score REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.id,
        a.name,
        similarity(a.name, search_query) as similarity_score
    FROM attractions a
    WHERE similarity(a.name, search_query) > similarity_threshold
    ORDER BY similarity_score DESC;
END;
$$ LANGUAGE plpgsql;
```

## Testing

### Test Coverage
- ✅ Basic search functionality
- ✅ Multiple parameter support
- ✅ Fuzzy matching capabilities
- ✅ Sorting options
- ✅ Pagination
- ✅ Filter combinations
- ✅ Error handling
- ✅ Response structure validation

### Running Tests
```bash
# Run all search tests
python -m pytest tests/test_search.py -v

# Run specific test
python -m pytest tests/test_search.py::TestSearchRoutes::test_search_attractions_basic -v
```

## Usage Examples

### Simple Search
```bash
curl "http://localhost:5000/api/search?query=วัด&language=th"
```

### Advanced Search with Filters
```bash
curl -X POST "http://localhost:5000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "beach",
    "language": "en",
    "province": "Krabi",
    "min_rating": 4.0,
    "sort_by": "rating",
    "limit": 5
  }'
```

### Autocomplete Suggestions
```bash
curl "http://localhost:5000/api/search/suggestions?query=วัด&language=th"
```

## Performance Considerations

1. **Database Indexes**: GIN indexes significantly improve fuzzy search performance
2. **Query Optimization**: Limits synonym expansion to prevent overly complex queries
3. **Caching**: Consider implementing Redis caching for frequent searches
4. **Pagination**: Always use pagination for large result sets
5. **Connection Pooling**: Use connection pooling for database access

## Future Enhancements

1. **Machine Learning**: Implement ML-based ranking algorithms
2. **Search Analytics**: Track search patterns and optimize accordingly
3. **Personalization**: User-based search result customization
4. **Geographic Search**: Distance-based filtering and sorting
5. **Search History**: Personal search history and suggestions