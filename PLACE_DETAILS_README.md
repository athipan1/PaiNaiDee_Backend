# Place Details Feature - Backend Implementation

This document describes the new place details feature implementation for the PaiNaiDee Backend.

## Overview

The place details feature allows users to add, update, and delete additional information for places (attractions) beyond the basic attraction data. This includes extended descriptions and additional links.

## Database Schema

A new `place_details` table has been added:

```sql
CREATE TABLE place_details (
    id SERIAL PRIMARY KEY,
    place_id INT REFERENCES attractions(id) ON DELETE CASCADE,
    description TEXT,
    link TEXT
);
```

## API Endpoints

### 1. Get Place Details
```
GET /api/places/:id
```
- **Description**: Retrieve place information including optional place details
- **Authentication**: None required
- **Response**: Place object with `place_detail` field (null if no details exist)

### 2. Add Place Details
```
POST /api/places/:id/details
```
- **Description**: Add additional details for a place
- **Authentication**: JWT token required
- **Request Body**:
  ```json
  {
    "description": "Additional place description (optional)",
    "link": "https://example.com/more-info (optional)"
  }
  ```
- **Response**: Created place detail object

### 3. Update Place Details
```
PUT /api/places/:id/details
```
- **Description**: Update existing place details
- **Authentication**: JWT token required
- **Request Body**: Same as POST (partial updates supported)
- **Response**: Updated place detail object

### 4. Delete Place Details
```
DELETE /api/places/:id/details
```
- **Description**: Delete place details
- **Authentication**: JWT token required
- **Response**: Success message

## Response Format

### Place Response (with details)
```json
{
  "success": true,
  "message": "Place retrieved successfully.",
  "data": {
    "id": 1,
    "name": "Sample Place",
    "description": "Original place description",
    "address": "123 Test Street",
    "province": "Test Province",
    "district": "Test District",
    "location": {"lat": 0.0, "lng": 0.0},
    "category": "Attraction",
    "opening_hours": "9:00-18:00",
    "entrance_fee": "Free",
    "contact_phone": "123-456-7890",
    "website": "https://place.com",
    "images": [],
    "rooms": [],
    "cars": [],
    "average_rating": 0.0,
    "total_reviews": 0,
    "place_detail": {
      "id": 1,
      "place_id": 1,
      "description": "Additional place description with more details",
      "link": "https://example.com/more-info"
    }
  }
}
```

### Place Detail Response
```json
{
  "success": true,
  "message": "Place details added successfully.",
  "data": {
    "id": 1,
    "place_id": 1,
    "description": "Additional place description",
    "link": "https://example.com/more-info"
  }
}
```

## Migration

To set up the new table, run the migration script:

```bash
python migrate_place_details.py
```

## Testing

Run the test suite to verify functionality:

```bash
# Run all tests
python -m pytest tests/ -v

# Run only place details tests
python -m pytest tests/test_places.py -v
```

## Frontend Integration

1. **Backward Compatibility**: Existing `/api/attractions/:id` endpoints continue to work and now include `place_detail` field
2. **New Endpoints**: Use `/api/places/:id` for place-specific operations
3. **Authentication**: Modification operations require JWT authentication
4. **JSON Format**: All responses follow the same standardized format used throughout the API

## Security

- All modification endpoints (POST, PUT, DELETE) require JWT authentication
- Input validation using Marshmallow schemas
- Foreign key constraints ensure data integrity
- Proper error handling with appropriate HTTP status codes

## Development

### Files Added/Modified

- `src/models/place_detail.py` - PlaceDetail model
- `src/schemas/place_detail.py` - Validation schemas
- `src/services/place_detail_service.py` - Business logic
- `src/routes/places.py` - API routes
- `tests/test_places.py` - Comprehensive tests
- `src/models/attraction.py` - Updated to include place details
- `src/app.py` - Route registration

### Testing the API

Use the demo script to see example requests and responses:

```bash
python test_place_details_api.py
```

This will show API documentation and example usage without requiring a running server.