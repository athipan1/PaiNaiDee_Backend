# Frontend Connectivity Verification Guide

This document explains how to verify that the PaiNaiDee Backend API can properly connect to frontend applications.

## Quick Verification

### 1. Run Automated Tests
```bash
# Run all frontend connectivity tests
python -m pytest tests/test_frontend_connectivity.py -v

# Run all tests to ensure nothing is broken
python -m pytest tests/ -v
```

### 2. Manual API Testing
```bash
# Run the manual testing script (uses SQLite for easy testing)
python test_frontend_connectivity.py
```

### 3. Health Check Endpoint
The API now includes a health check endpoint specifically for frontend monitoring:

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "cors_enabled": true,
    "endpoints": {
      "auth": "/api/auth/login, /api/auth/register",
      "attractions": "/api/attractions",
      "booking": "/api/book-room, /api/rent-car",
      "reviews": "/api/reviews",
      "search": "/api/search/suggestions"
    }
  },
  "message": "API is running and ready for frontend connections",
  "success": true
}
```

## API Endpoints for Frontend

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns JWT token)

### Attractions
- `GET /api/attractions` - Get all attractions with pagination
- `GET /api/attractions/{id}` - Get attraction details
- `POST /api/attractions` - Add new attraction (authenticated)
- `PUT /api/attractions/{id}` - Update attraction (authenticated)
- `DELETE /api/attractions/{id}` - Delete attraction (authenticated)

### Search
- `GET /api/search/suggestions?query={text}` - Get search suggestions for autocomplete

### Booking
- `POST /api/book-room` - Book a room (authenticated)
- `POST /api/rent-car` - Rent a car (authenticated)

### Reviews
- `POST /api/reviews` - Add a review (authenticated)

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:3000` (local development)
- `https://painaidee.com` (production)
- `https://frontend-painaidee.web.app` (Firebase hosting)

## Response Format

All API responses follow this standardized format:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data here
  }
}
```

For errors:
```json
{
  "success": false,
  "message": "Error description",
  "data": null
}
```

## Authentication Flow

1. Frontend sends login request to `/api/auth/login`
2. API returns JWT token in `data.access_token`
3. Frontend includes token in subsequent requests: `Authorization: Bearer {token}`
4. API validates token for protected endpoints

## Verification Checklist

- [ ] Health check endpoint responds correctly
- [ ] CORS headers are present for allowed origins
- [ ] OPTIONS preflight requests work
- [ ] Authentication flow returns valid JWT tokens
- [ ] Protected endpoints accept Bearer tokens
- [ ] All responses follow standardized format
- [ ] Search suggestions work for autocomplete
- [ ] Error handling returns consistent format
- [ ] JSON content type is properly handled

## Troubleshooting

### Database Connection Issues
If using PostgreSQL and getting connection errors, you can:
1. Use the testing script which uses SQLite: `python test_frontend_connectivity.py`
2. Set up PostgreSQL with credentials from `.env.example`
3. Run with testing config: `FLASK_ENV=testing python run.py`

### CORS Issues
If frontend can't connect:
1. Verify the frontend origin is in the CORS configuration in `src/app.py`
2. Check that OPTIONS requests return 200/204 status
3. Ensure the frontend sends proper Origin headers

### Authentication Issues
If JWT tokens don't work:
1. Verify the token is included as `Authorization: Bearer {token}`
2. Check that the user exists in the database
3. Ensure the JWT secret key is consistent