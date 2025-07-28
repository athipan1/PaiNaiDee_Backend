# Backend Dashboard API

This document describes the backend dashboard API that provides comprehensive analytics and monitoring capabilities for the PaiNaiDee Backend.

## Overview

The dashboard provides real-time analytics on API usage, including:
- **Endpoint Usage**: Track which endpoints are being called and how often
- **Performance Metrics**: Monitor response times and identify bottlenecks  
- **Error Analysis**: Analyze HTTP status codes and error rates
- **Traffic Sources**: Track source IPs and client applications
- **Time-based Analytics**: View usage patterns over time

## Features Implemented

### ✅ Automatic Request Tracking
- **Middleware Integration**: Automatically captures all API requests
- **Real-time Data**: Analytics data is captured in real-time as requests are made
- **Minimal Overhead**: Lightweight middleware with negligible performance impact

### ✅ Comprehensive Metrics
1. **รายชื่อ endpoint ทั้งหมด** - Complete list of all API endpoints with usage statistics
2. **ประเภทข้อมูลที่ถูกเรียกใช้** - Data types and JSON schemas accessed (via endpoint tracking)
3. **จำนวนครั้งที่ถูกเรียก** - Request counts with daily/weekly/monthly breakdowns
4. **ระยะเวลาในการตอบกลับ** - Response time analytics (avg, min, max, median, p95)
5. **สถานะของ response** - HTTP status code distribution (200, 404, 500, etc.)
6. **Source IP หรือ client app** - Source IP tracking with request counts
7. **Timestamp ของคำขอล่าสุด** - Latest request timestamps for each endpoint

## API Endpoints

All dashboard endpoints require JWT authentication and are prefixed with `/api/dashboard/`.

### 1. System Overview
```http
GET /api/dashboard/overview
```

**Description**: Get overall system analytics overview including total requests, unique endpoints, error rates, and latest activity.

**Response Example**:
```json
{
  "success": true,
  "data": {
    "total_requests": 1250,
    "unique_endpoints": 15,
    "unique_source_ips": 45,
    "error_rate": 2.5,
    "latest_request": "2025-01-15T10:30:45Z",
    "date_range": {
      "start_date": "2025-01-15T00:00:00Z",
      "end_date": "2025-01-15T23:59:59Z"
    }
  }
}
```

### 2. Endpoints Summary
```http
GET /api/dashboard/endpoints
```

**Description**: Get detailed statistics for all API endpoints including request counts and response times.

**Response Example**:
```json
{
  "success": true,
  "data": [
    {
      "endpoint": "/api/attractions",
      "method": "GET",
      "request_count": 450,
      "avg_response_time": 125.5,
      "min_response_time": 45.2,
      "max_response_time": 892.1,
      "last_request": "2025-01-15T10:30:45Z"
    }
  ]
}
```

### 3. Request Count by Period
```http
GET /api/dashboard/requests-by-period?period=day
```

**Parameters**:
- `period`: `day`, `week`, or `month`

**Description**: Get request count grouped by time period for trend analysis.

### 4. Status Code Distribution
```http
GET /api/dashboard/status-codes
```

**Description**: Get HTTP status code distribution with counts and percentages.

**Response Example**:
```json
{
  "success": true,
  "data": [
    {
      "status_code": 200,
      "count": 1180,
      "percentage": 94.4
    },
    {
      "status_code": 404,
      "count": 45,
      "percentage": 3.6
    }
  ]
}
```

### 5. Source IP Analytics
```http
GET /api/dashboard/source-ips?limit=10
```

**Parameters**:
- `limit`: Number of top IPs to return (1-100)

**Description**: Get top source IPs by request count.

### 6. Response Time Analytics
```http
GET /api/dashboard/response-times
```

**Description**: Get comprehensive response time statistics.

**Response Example**:
```json
{
  "success": true,
  "data": {
    "avg_response_time": 125.5,
    "min_response_time": 15.2,
    "max_response_time": 2500.8,
    "median_response_time": 98.4,
    "p95_response_time": 450.2
  }
}
```

## Query Parameters

All endpoints support the following optional query parameters for filtering:

- **`start_date`**: ISO 8601 datetime string (e.g., `2025-01-15T00:00:00Z`)
- **`end_date`**: ISO 8601 datetime string
- **`period`**: Time grouping for period-based queries (`day`, `week`, `month`)
- **`limit`**: Number of results to return (1-100)

### Example with Date Filtering
```http
GET /api/dashboard/overview?start_date=2025-01-01T00:00:00Z&end_date=2025-01-15T23:59:59Z
```

## Authentication

All dashboard endpoints require JWT authentication. Include the JWT token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

To obtain a JWT token, use the existing authentication endpoint:
```http
POST /api/auth/login
```

## Database Schema

The dashboard uses a dedicated `api_analytics` table with the following structure:

```sql
CREATE TABLE api_analytics (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_ip VARCHAR(45),
    user_agent TEXT,
    request_size INTEGER,
    response_size INTEGER,
    user_id INTEGER REFERENCES users(id)
);
```

**Indexes**: The table is indexed on `endpoint`, `status_code`, and `timestamp` for optimal query performance.

## Setup Instructions

### 1. Database Migration
Run the migration script to create the analytics table:
```bash
python migrate_analytics.py
```

### 2. Middleware Integration
The analytics middleware is automatically enabled when the app starts. No additional configuration is required.

### 3. Testing
Run the test suite to verify functionality:
```bash
pytest tests/test_analytics_service.py tests/test_dashboard.py -v
```

## Performance Considerations

- **Middleware Overhead**: ~1-2ms per request
- **Database Storage**: ~200 bytes per request record
- **Query Performance**: All dashboard queries include appropriate indexes
- **Data Retention**: Consider implementing data retention policies for large-scale deployments

## Frontend Integration

The dashboard API is designed to be consumed by frontend applications. Example JavaScript usage:

```javascript
// Get system overview
async function getDashboardOverview() {
  const response = await fetch('/api/dashboard/overview', {
    headers: {
      'Authorization': `Bearer ${jwt_token}`,
      'Content-Type': 'application/json'
    }
  });
  return await response.json();
}

// Get endpoints with date filtering
async function getEndpointsStats(startDate, endDate) {
  const params = new URLSearchParams({
    start_date: startDate,
    end_date: endDate
  });
  
  const response = await fetch(`/api/dashboard/endpoints?${params}`, {
    headers: {
      'Authorization': `Bearer ${jwt_token}`,
      'Content-Type': 'application/json'
    }
  });
  return await response.json();
}
```

## Security

- **Authentication Required**: All endpoints require valid JWT tokens
- **Rate Limiting**: Consider implementing rate limiting for dashboard endpoints in production
- **Data Privacy**: Source IP addresses are stored but can be anonymized if required
- **Access Control**: Dashboard access is currently tied to any authenticated user; consider role-based access for production

## Troubleshooting

### Common Issues

1. **No analytics data showing**
   - Verify the middleware is enabled in the app configuration
   - Check that the `api_analytics` table was created successfully
   - Ensure API requests are being made to endpoints starting with `/api/`

2. **Dashboard endpoints returning 500 errors**
   - Check database connectivity
   - Verify the `api_analytics` table exists and has the correct schema
   - Check application logs for specific error messages

3. **Slow dashboard queries**
   - Ensure database indexes are created properly
   - Consider adding data retention policies for large datasets
   - Use date range filtering to limit query scope

### Debug Mode
To debug analytics data capture, you can check the `api_analytics` table directly:

```sql
SELECT 
  endpoint, 
  method, 
  COUNT(*) as request_count,
  AVG(response_time) as avg_time
FROM api_analytics 
WHERE timestamp >= NOW() - INTERVAL '1 day'
GROUP BY endpoint, method 
ORDER BY request_count DESC;
```