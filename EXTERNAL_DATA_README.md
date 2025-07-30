# External Data Integration System

## Overview

The PaiNaiDee Backend now includes a comprehensive **External Data Integration System** that automatically fetches, processes, and updates tourism attraction data from multiple external sources. This system ensures the application has up-to-date, comprehensive information about tourist attractions across Thailand.

## 🌟 Features

### ✅ Multi-Source Data Integration
- **Google Places API** support for rich attraction data
- **Tourism Authority of Thailand (TAT)** API integration
- **TripAdvisor Content API** support for reviews and ratings
- Extensible architecture for adding new data sources

### ✅ Automated Data Management
- **Real-time updates** - Manual triggers for immediate data refresh
- **Scheduled updates** - Automated daily/weekly/monthly data synchronization
- **Smart duplicate detection** - Prevents duplicate entries using fuzzy matching
- **Change detection** - Only updates data when changes are detected

### ✅ Comprehensive Data Coverage
- Supports all **77 Thai provinces**
- Tracks **multiple data types**: name, description, location, images, contact info
- **Image management** - Automatically updates attraction images
- **Province coverage monitoring** - Ensures nationwide tourism data coverage

### ✅ Monitoring & Management
- **Web API** for managing data sources and updates
- **Command-line interface** for admin operations
- **Update history tracking** with detailed logs
- **Real-time status monitoring** of data integration tasks

## 🚀 Quick Start

### 1. Setup External Data Sources

Configure your external API keys:

```bash
# Configure Google Places API
python external_data_cli.py configure google_places --api-key YOUR_API_KEY --enable

# Configure TripAdvisor API
python external_data_cli.py configure tripadvisor --api-key YOUR_API_KEY --enable

# TAT API is enabled by default (uses mock data for demonstration)
```

### 2. Run Initial Data Update

```bash
# Update from all enabled sources
python external_data_cli.py update-all

# Update from specific source with filters
python external_data_cli.py update tat_api --province "กรุงเทพมหานคร"
```

### 3. Set Up Automated Updates

```bash
# Schedule daily updates for TAT data
python external_data_cli.py schedule-add tat_api --frequency daily --enable

# Schedule weekly updates for Google Places
python external_data_cli.py schedule-add google_places --frequency weekly --enable
```

### 4. Monitor System Status

```bash
# Check overall system status
python external_data_cli.py status

# Check province coverage
python external_data_cli.py coverage

# View data sources
python external_data_cli.py sources
```

## 🔧 API Endpoints

### Data Source Management

```http
GET    /api/external-data/sources              # List all data sources
POST   /api/external-data/sources/{name}/configure  # Configure a source
```

### Manual Data Updates

```http
POST   /api/external-data/update/manual        # Trigger manual update
POST   /api/external-data/update/all          # Update from all sources
```

### Scheduled Updates

```http
GET    /api/external-data/schedules            # List scheduled updates
POST   /api/external-data/schedules            # Create scheduled update
PUT    /api/external-data/schedules/{id}       # Update schedule
DELETE /api/external-data/schedules/{id}       # Delete schedule
```

### Monitoring & Analytics

```http
GET    /api/external-data/tasks                # List update tasks
GET    /api/external-data/tasks/{id}           # Get task status
GET    /api/external-data/history              # Update history
GET    /api/external-data/coverage/provinces   # Province coverage stats
GET    /api/external-data/stats                # System statistics
```

### Scheduler Control

```http
GET    /api/external-data/scheduler/status     # Scheduler status
POST   /api/external-data/scheduler/start      # Start scheduler
POST   /api/external-data/scheduler/stop       # Stop scheduler
```

## 📊 Data Sources

### 1. Google Places API
- **Coverage**: Global tourist attractions
- **Data Quality**: High (rich metadata, photos, reviews)
- **Rate Limits**: Conservative (0.1 req/sec)
- **Requirements**: API key required

### 2. Tourism Authority of Thailand (TAT)
- **Coverage**: Official Thai tourism data
- **Data Quality**: Authoritative, comprehensive
- **Rate Limits**: Moderate (0.5 req/sec)
- **Requirements**: Currently uses mock data (demo)

### 3. TripAdvisor Content API
- **Coverage**: Popular attractions with reviews
- **Data Quality**: Community-driven, rich reviews
- **Rate Limits**: Conservative (0.2 req/sec)
- **Requirements**: API key required

## 🗺️ Province Coverage

The system tracks coverage across all 77 Thai provinces:

### Central Thailand
- กรุงเทพมหานคร (Bangkok)
- นนทบุรี (Nonthaburi)
- ปทุมธานี (Pathum Thani)
- สมุทรปราการ (Samut Prakan)
- ... and more

### Northern Thailand
- เชียงใหม่ (Chiang Mai)
- เชียงราย (Chiang Rai)
- ลำปาง (Lampang)
- ... and more

### Southern Thailand
- ภูเก็ต (Phuket)
- กระบี่ (Krabi)
- สงขลา (Songkhla)
- ... and more

*Check current coverage with:*
```bash
python external_data_cli.py coverage
```

## 🔄 Data Update Process

### 1. Data Fetching
- Connects to configured external APIs
- Applies rate limiting to respect API quotas
- Handles API errors gracefully with retry logic

### 2. Data Processing
- Normalizes data formats across different sources
- Extracts Thai province names from addresses
- Categorizes attractions (วัด, ชายหาด, ภูเขา, etc.)
- Processes multiple image URLs

### 3. Duplicate Detection
- Uses fuzzy string matching for attraction names
- Compares location coordinates for proximity
- Checks province and category for consistency

### 4. Database Updates
- **Create**: Adds new attractions not in database
- **Update**: Updates existing attractions with new information
- **Merge**: Combines image URLs without duplicates
- **Track**: Records update timestamps and data sources

## 🛠️ Administration

### Command Line Interface

The `external_data_cli.py` provides comprehensive management:

```bash
# View help
python external_data_cli.py --help

# Data source management
python external_data_cli.py sources
python external_data_cli.py configure SOURCE_NAME --api-key KEY

# Manual updates
python external_data_cli.py update SOURCE_NAME
python external_data_cli.py update-all

# Scheduling
python external_data_cli.py schedules
python external_data_cli.py schedule-add SOURCE --frequency daily

# Monitoring
python external_data_cli.py status
python external_data_cli.py tasks
python external_data_cli.py coverage
```

### Web Dashboard

Access the analytics dashboard at `/api/dashboard/` to:
- Monitor API usage and performance
- View update success/failure rates
- Track data source statistics
- Analyze province coverage trends

## 🗃️ Database Schema

### New Tracking Fields

The system adds several fields to the `attractions` table:

```sql
-- External data tracking
external_id VARCHAR(255)           -- Source-specific ID
data_source VARCHAR(100)           -- Source name (google_places, tat_api, etc.)
last_external_update TIMESTAMP     -- Last update from external source
data_version VARCHAR(100)          -- Data version/hash for change detection
is_external_data BOOLEAN           -- Flag for externally sourced data
external_data_raw JSONB           -- Original external data (for debugging)

-- Standard timestamps
created_at TIMESTAMP               -- Record creation time
updated_at TIMESTAMP               -- Last modification time
```

### Update History Table

```sql
CREATE TABLE external_data_updates (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    update_type VARCHAR(50) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    total_processed INTEGER DEFAULT 0,
    new_created INTEGER DEFAULT 0,
    existing_updated INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    error_messages TEXT[],
    parameters JSONB,
    result_summary JSONB
);
```

## 🧪 Testing

The system includes comprehensive tests:

```bash
# Run all external data tests
pytest tests/test_external_data.py -v

# Run specific test categories
pytest tests/test_external_data.py::TestExternalDataService -v
pytest tests/test_external_data.py::TestDataUpdateScheduler -v
pytest tests/test_external_data.py::TestExternalDataRoutes -v
```

## 🔐 Security & Configuration

### API Key Management
- Store API keys in environment variables
- Use `.env` file for development
- Rotate keys regularly for production

### Rate Limiting
- Conservative defaults to prevent API quota exhaustion
- Configurable per-source rate limits
- Automatic backoff on API errors

### Error Handling
- Graceful degradation when APIs are unavailable
- Detailed error logging for debugging
- Automatic retry logic with exponential backoff

## 📈 Performance Considerations

### Scalability
- Async task processing for non-blocking updates
- Configurable concurrent task limits
- Database indexing for fast lookups

### Monitoring
- Request/response time tracking
- Success/failure rate monitoring
- Database performance metrics

### Optimization
- Incremental updates (only changed data)
- Efficient duplicate detection algorithms
- Batch processing for large datasets

## 🚀 Future Enhancements

### Short-term Goals
- [ ] **Real API Integration** - Connect to actual TAT and other APIs
- [ ] **Image Processing** - Automatic image optimization and CDN upload
- [ ] **Data Validation** - Enhanced quality checks and validation rules
- [ ] **Email Notifications** - Alert admins of update failures

### Medium-term Goals
- [ ] **Machine Learning** - Automatic categorization and duplicate detection
- [ ] **Multi-language Support** - Content translation and localization
- [ ] **Advanced Scheduling** - Complex scheduling rules and dependencies
- [ ] **Data Analytics** - Trend analysis and insights

### Long-term Goals
- [ ] **Real-time Streaming** - Live data updates via webhooks
- [ ] **Federated Search** - Search across multiple external sources
- [ ] **Data Marketplace** - Integration with tourism data providers
- [ ] **AI-powered Enhancement** - Automatic content enhancement and fact-checking

---

## Support

For questions and support regarding the External Data Integration System:

1. **Check the CLI help**: `python external_data_cli.py --help`
2. **Review API documentation**: Use the `/api/external-data/` endpoints
3. **Monitor system status**: Regular checks via `/api/external-data/stats`
4. **Check logs**: Review application logs for detailed error information

**The External Data Integration System ensures your PaiNaiDee application always has the most current and comprehensive tourism data for Thailand! 🇹🇭**