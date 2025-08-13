# PaiNaiDee Backend API 🇹🇭

[![Tests](https://img.shields.io/badge/tests-132%20passing-green.svg)](tests/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-3.1.1-blue.svg)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-2.0.41-blue.svg)](https://sqlalchemy.org)
[![PostgreSQL](https://img.shields.io/badge/postgresql-13%2B-blue.svg)](https://postgresql.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI](https://img.shields.io/badge/ci-github%20actions-green.svg)](https://github.com/athipan1/PaiNaiDee_Backend/actions)

## 🚀 Deploy บน Vercel 🚀

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fathipan1%2FPaiNaiDee_Backend)

### Setup Instructions / คำแนะนำการติดตั้ง:

1. **Click the Deploy button** above to deploy to Vercel / คลิกปุ่ม Deploy ด้านบนเพื่อติดตั้งบน Vercel
2. **Connect your GitHub account** and fork the repository / เชื่อมต่อบัญชี GitHub ของคุณและ fork repository
3. **Configure environment variables** in Vercel dashboard / ตั้งค่าตัวแปรสภาพแวดล้อมในแดชบอร์ด Vercel:

```env
# Required Environment Variables
OPENAI_API_KEY=your-openai-api-key-here
DATABASE_URL=your-postgresql-database-url
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production

# Optional Database Configuration
DB_HOST=your-db-host
DB_NAME=your-db-name  
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_PORT=5432
```

4. **Deploy** and your API will be live at `https://your-app.vercel.app` / ติดตั้งและ API ของคุณจะพร้อมใช้งานที่ `https://your-app.vercel.app`

---

## 🤗 Deploy บน Hugging Face Spaces 🤗

[![Deploy to Spaces](https://huggingface.co/datasets/huggingface/badges/raw/main/deploy-to-spaces-lg.svg)](https://huggingface.co/spaces/new?template=docker&repo=athipan1/PaiNaiDee_Backend)

### Setup Instructions / คำแนะนำการติดตั้ง:

1. **Click the Deploy button** above / คลิกปุ่ม Deploy ด้านบน
2. **Sign up/Login** to Hugging Face (free) / สมัครสมาชิก/เข้าสู่ระบบ Hugging Face (ฟรี)
3. **Configure your Space** / ตั้งค่า Space ของคุณ:
   - Choose a unique Space name / เลือกชื่อ Space ที่ไม่ซ้ำ
   - Set SDK to "Docker" (auto-selected) / ตั้งค่า SDK เป็น "Docker" (เลือกอัตโนมัติ)
   - Set visibility (Public recommended) / ตั้งค่าการมองเห็น (แนะนำ Public)

### Repository Structure for Hugging Face / โครงสร้าง Repository สำหรับ Hugging Face:

The repository is already configured with the required files:
Repository ได้รับการตั้งค่าไฟล์ที่จำเป็นแล้ว:

- `app.py` - Hugging Face Spaces entry point / จุดเริ่มต้นสำหรับ Spaces
- `spaces_requirements.txt` - Dependencies for Spaces / Dependencies สำหรับ Spaces  
- `Dockerfile` - Container configuration / การตั้งค่า Container

### Special Notes / หมายเหตุพิเศษ:
- **Frontend/API Demo**: The Space provides a complete API backend ready for frontend integration
- **Sample Data**: Includes pre-loaded Thai tourism data for immediate testing
- **Auto-configuration**: Uses SQLite database with sample attractions for demo purposes

---

## ⚗️ ทดลองใช้งานบน Google Colab ⚗️

### 🧪 ทดลอง API ทั้งหมดใน Google Colab

[![Run in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/athipan1/PaiNaiDee_Backend/blob/main/tests/test_all_apis.ipynb)

**ภาษาไทย:** ทดสอบ API endpoints ทั้งหมดของ PaiNaiDee Backend ผ่าน Google Colab โดยไม่ต้องติดตั้งอะไรเพิ่มเติม  
**English:** Test all PaiNaiDee Backend API endpoints through Google Colab without any additional setup

### 📋 Tested Endpoints / Endpoints ที่ทดสอบ:
- ✅ `/api/talk` - Conversational AI endpoint
- ✅ `/api/attractions` - Get all attractions
- ✅ `/api/attractions/<id>` - Get specific attraction details
- ✅ `/api/videos` - Get video content
- ✅ `/api/videos/upload` - Upload video content (requires authentication)
- ✅ `/api/search` - Search attractions by keywords
- ✅ `/api/auth/register` - User registration
- ✅ `/api/auth/login` - User authentication
- ✅ Health check and system status

### 🚀 Colab Setup Instructions / คำแนะนำการติดตั้งใน Colab:

1. **Click the "Run in Colab" button** above / คลิกปุ่ม "Run in Colab" ด้านบน
2. **Install dependencies** / ติดตั้ง dependencies:
   ```python
   !pip install -r requirements.txt
   # หรือ or: !pip install requests python-dotenv
   ```
3. **Set the API endpoint URL** / ตั้งค่า URL ของ API endpoint:
   ```python
   API_BASE_URL = "https://your-deployment-url"  # Your Vercel/HF Spaces URL
   ```
4. **Use the helper function** / ใช้ฟังก์ชันช่วย:
   ```python
   def call_api(method, url, payload=None, headers=None):
       # Helper function for making API calls
       # ฟังก์ชันช่วยสำหรับเรียก API
   ```

### 💡 Usage Notes / หมายเหตุการใช้งาน:
- **Python Environment**: All code runs in Python with bilingual output (Thai/English)
- **Real-time Testing**: Test your live API deployment instantly
- **Authentication Flow**: Includes user registration and JWT token handling
- **Error Handling**: Shows detailed error messages and success indicators
- **Thai Language Support**: Tests Thai text input and output capabilities

---

PaiNaiDee ("ไปไหนดี" - "Where to go?" in Thai) is a comprehensive backend API for a tourism application that helps users discover, explore, and book attractions in Thailand. Built with Flask and PostgreSQL, it provides a robust foundation for travel applications with features including attraction management, user reviews, booking systems, and real-time analytics.

## 🌟 Features

### Core Features
- **🏛️ Attraction Management**: Complete CRUD operations for tourist attractions with detailed information including location, categories, images, and contact details
- **👥 User Authentication**: Secure JWT-based authentication and authorization system
- **⭐ Review & Rating System**: Users can rate attractions (1-5 stars) and leave detailed reviews
- **🏨 Booking System**: Book accommodations (rooms) and transportation (car rentals) at attractions
- **🎥 Video Content**: Upload and manage video content related to attractions
- **🔍 Advanced Search**: Multi-language search with trigram similarity, autocomplete, and ranking
- **📍 Location Services**: Nearby attractions with geospatial queries and distance calculations
- **📊 Analytics Dashboard**: Real-time API usage analytics and monitoring
- **🗺️ 3D Map Integration**: Ready for 3D map visualization (via separate map service)

### Search Features (New!)
- **🔤 Text Normalization**: Thai and English text processing with stop word filtering
- **🎯 Smart Search**: Similarity-based search using PostgreSQL trigram matching
- **⚡ Autocomplete**: Fast prefix-based suggestions for location and attraction names
- **📏 Proximity Search**: Find attractions within specified radius using PostGIS
- **🏆 Result Ranking**: Configurable scoring based on popularity, freshness, and relevance
- **🔧 Feature Flags**: Toggle search features on/off via environment configuration

### Technical Features
- **RESTful API Design**: Clean, consistent API endpoints following REST principles
- **Database Relationships**: Properly normalized PostgreSQL database with foreign key constraints
- **Input Validation**: Marshmallow schemas for request/response validation
- **Error Handling**: Comprehensive error handling with standardized response format
- **CORS Support**: Cross-origin resource sharing for frontend integration
- **Docker Support**: Complete containerization with Docker Compose
- **Comprehensive Testing**: 132+ test cases covering all major functionality
- **Analytics Middleware**: Automatic request tracking and performance monitoring
- **Code Quality**: Automated linting, formatting, and pre-commit hooks
- **Database Migrations**: Alembic-based schema versioning and deployment

## 🏗️ Architecture

PaiNaiDee ("ไปไหนดี" - "Where to go?" in Thai) is a comprehensive backend API for a tourism application that helps users discover, explore, and book attractions in Thailand. Built with Flask, SQLAlchemy, and PostgreSQL, it provides a robust foundation for travel applications.

### Tech Stack
- **Backend Framework**: Flask 3.1.1 with SQLAlchemy 2.0.41
- **Database**: PostgreSQL 13+ with pg_trgm extension for advanced search
- **Authentication**: JWT-based with Flask-JWT-Extended
- **Search**: Full-text search with trigram similarity and GIN indexes
- **Testing**: pytest with 132+ test cases
- **Code Quality**: ruff, black, pre-commit hooks
- **Migration**: Alembic for database versioning
- **Deployment**: Docker, Vercel, Hugging Face Spaces

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   3D Map        │    │   Dashboard     │
│   (React/Vue)   │◄──►│   Service       │◄──►│   Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     Flask API Server      │
                    │   (PaiNaiDee Backend)     │
                    │                           │
                    │  ┌─────────────────────┐  │
                    │  │   Search Engine     │  │
                    │  │  (pg_trgm + GIN)    │  │
                    │  └─────────────────────┘  │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    PostgreSQL Database    │
                    │  (Attractions, Users,     │
                    │   Reviews, Bookings,      │
                    │   Search Indexes)         │
                    └───────────────────────────┘
```

### Project Structure

```
app/                          # Main application package
├── __init__.py              # Flask app factory (create_app)
├── config.py                # Configuration management with validation
├── extensions.py            # Flask extensions (db, migrate, cache)
├── blueprints/              # API route blueprints
│   ├── api/
│   │   ├── __init__.py
│   │   ├── search.py        # Search and autocomplete endpoints
│   │   ├── posts.py         # Content management
│   │   └── locations.py     # Location-based queries
├── models/                  # SQLAlchemy models
│   ├── __init__.py
│   ├── attraction.py
│   ├── user.py
│   ├── review.py
│   └── ...
├── services/                # Business logic layer
│   ├── search_service.py    # Search algorithms and ranking
│   ├── post_service.py      # Content management
│   └── location_service.py  # Geospatial operations
└── utils/                   # Utility functions
    ├── text_normalization.py # Thai/English text processing
    ├── scoring.py           # Search result scoring
    └── distance.py          # Geographic calculations

migrations/                   # Alembic database migrations
├── versions/                # Migration scripts
└── alembic.ini             # Alembic configuration

seed/                        # Database seeding scripts
tests/                       # Test suite (132+ tests)
requirements.txt            # Python dependencies
pyproject.toml              # Tool configuration (ruff, black)
.pre-commit-config.yaml     # Code quality hooks
```

---

## 🛠️ Local Development

### Prerequisites and Setup

1. **Prerequisites:**
   - Python 3.9 or higher
   - PostgreSQL 13+ installed and running
   - Git

2. **Installation:**
   ```bash
   # Clone the repository
   git clone https://github.com/athipan1/PaiNaiDee_Backend.git
   cd PaiNaiDee_Backend

   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Database Setup:**
   ```bash
   # Create PostgreSQL database
   createdb painaidee_db

   # Initialize database tables
   python init_db.py

   # Run migrations (if needed)
   python migrate_analytics.py
   python migrate_image_urls.py
   ```

4. **Configuration:**
   Create a `.env` file in the root directory (see `.env.example` for full reference):
   ```env
   # Application Configuration
   APP_ENV=development
   LOG_LEVEL=INFO
   SECRET_KEY=your-super-secret-key-here
   FLASK_ENV=development

   # Database Configuration
   DATABASE_URL=postgresql://postgres:password@localhost:5432/painaidee_db
   # Or individual components:
   DB_HOST=localhost
   DB_NAME=painaidee_db
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_PORT=5432

   # Search Configuration
   SEARCH_RANK_WEIGHTS={"popularity": 0.4, "freshness": 0.3, "similarity": 0.3}
   MAX_NEARBY_RADIUS_KM=50
   TRIGRAM_SIM_THRESHOLD=0.3
   FEATURE_AUTOCOMPLETE=true
   FEATURE_NEARBY=true

   # Optional: Redis for caching
   REDIS_URL=redis://localhost:6379/0

   # Optional: OpenAI for AI features
   OPENAI_API_KEY=your-openai-api-key
   ```

5. **Running the Application:**
   ```bash
   # Start the Flask development server
   python run.py

   # Or use Flask CLI
   flask run

   # With specific configuration
   FLASK_ENV=development python run.py

   # API will be available at http://localhost:5000
   ```

### Search Development Roadmap

#### Phase 1: Basic Search (Current Implementation)
- ✅ Text normalization for Thai and English
- ✅ Trigram-based similarity search
- ✅ Basic ranking with popularity and freshness
- ✅ Autocomplete with prefix matching
- ✅ Nearby location search with distance filtering

#### Phase 2: Advanced Search (Future)
- 🔄 Elasticsearch integration for full-text search
- 🔄 Machine learning-based recommendation engine
- 🔄 Semantic search with vector embeddings
- 🔄 Multi-modal search (text + images)
- 🔄 Real-time search analytics and A/B testing

### Docker Deployment

1. **Prerequisites:**
   - Docker and Docker Compose installed

2. **Quick Start:**
   ```bash
   # Build and start all services
   docker-compose up --build

   # Run in background
   docker-compose up -d --build

   # View logs
   docker-compose logs -f backend
   ```

3. **Services Available:**
   - **Backend API**: http://localhost:5000
   - **Frontend**: http://localhost:80 (if included)
   - **3D Map Service**: http://localhost:8080 (if included)

## 📖 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### Core Endpoints

#### Authentication
```http
POST /api/auth/register    # Register new user
POST /api/auth/login       # Login user
```

#### Attractions
```http
GET    /api/attractions              # Get all attractions (with pagination)
GET    /api/attractions/{id}         # Get attraction details
POST   /api/attractions              # Add new attraction (auth required)
PUT    /api/attractions/{id}         # Update attraction (auth required)
DELETE /api/attractions/{id}         # Delete attraction (auth required)
```

#### Reviews
```http
GET    /api/attractions/{id}/reviews # Get attraction reviews
POST   /api/reviews                  # Add review (auth required)
PUT    /api/reviews/{id}             # Update own review (auth required)
DELETE /api/reviews/{id}             # Delete own review (auth required)
```

#### Bookings
```http
POST   /api/book-room                # Book room (auth required)
POST   /api/rent-car                 # Rent car (auth required)
```

#### Search & Discovery
```http
GET    /api/search?q={query}           # Advanced search with ranking
GET    /api/autocomplete?q={prefix}    # Autocomplete suggestions  
GET    /api/locations/nearby           # Nearby attractions by location
```

#### Videos
```http
GET    /api/videos                   # Get videos
POST   /api/videos                   # Upload video (auth required)
```

#### Analytics Dashboard
```http
GET    /api/dashboard/overview       # System overview (auth required)
GET    /api/dashboard/endpoints      # Endpoint statistics (auth required)
GET    /api/dashboard/status-codes   # Status code distribution (auth required)
```

### Example Requests

#### Get Attractions with Filters
```bash
curl "http://localhost:5000/api/attractions?page=1&limit=10&province=Bangkok&category=temple"
```

#### Add a Review
```bash
curl -X POST "http://localhost:5000/api/reviews" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "place_id": 1,
    "rating": 5,
    "comment": "Amazing temple with beautiful architecture!"
  }'
```

#### Advanced Search with Ranking
```bash
curl "http://localhost:5000/api/search?q=temple&limit=10&min_rating=4.0"
```

#### Autocomplete for Location Names
```bash
curl "http://localhost:5000/api/autocomplete?q=bang&limit=5"
```

#### Find Nearby Attractions
```bash
curl "http://localhost:5000/api/locations/nearby?lat=13.7563&lng=100.5018&radius=10"
```

For complete API documentation, see the [API Reference](docs/api-reference.md) (when available).

## 🧪 Testing

The project includes comprehensive testing with 132+ test cases covering all major functionality.

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_search.py -v

# Run tests with coverage
python -m pytest --cov=app tests/

# Run specific test category
python -m pytest tests/test_app.py::test_get_all_attractions -v

# Run search-related tests
python -m pytest tests/ -k "search" -v
```

### Test Categories
- **Unit Tests**: Service layer logic and utilities (text processing, scoring, etc.)
- **Integration Tests**: API endpoint functionality and database operations
- **Authentication Tests**: JWT and user authorization flows
- **Database Tests**: Model relationships and constraints
- **Analytics Tests**: Dashboard and monitoring features
- **Search Tests**: Search algorithms, ranking, and text processing

## 💾 Database Schema

### Core Tables
- **attractions**: Main attraction data with location and details
- **users**: User authentication and profile information
- **reviews**: User reviews and ratings for attractions
- **rooms**: Available accommodations at attractions
- **cars**: Available vehicle rentals at attractions
- **room_bookings**: Room reservation records
- **car_rentals**: Car rental records
- **video_posts**: Video content related to attractions
- **api_analytics**: Request tracking and performance metrics

For detailed schema information, see [Database Documentation](docs/database.md) (when available).

## 🛠️ Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Keep functions small and focused

### Project Structure
```
app/                         # Main application package
├── __init__.py             # Flask app factory
├── config.py               # Configuration with validation
├── extensions.py           # Flask extensions initialization
├── blueprints/             # API blueprints
│   └── api/                # API version 1
│       ├── search.py       # Search endpoints
│       ├── posts.py        # Content management
│       └── locations.py    # Location services
├── models/                 # SQLAlchemy models
├── services/               # Business logic layer
│   ├── search_service.py   # Search algorithms
│   ├── post_service.py     # Content operations
│   └── location_service.py # Geospatial services
├── utils/                  # Utility functions
│   ├── text_normalization.py
│   ├── scoring.py
│   └── distance.py
└── schemas/                # Validation schemas

migrations/                 # Alembic migrations
seed/                      # Database seed scripts
tests/                     # Test suite
requirements.txt           # Dependencies
pyproject.toml            # Tool configuration
.pre-commit-config.yaml   # Code quality hooks
```

### Adding New Features

1. **Create Model** (if needed):
   ```python
   # src/models/new_model.py
   from . import db
   
   class NewModel(db.Model):
       __tablename__ = 'new_models'
       # Define your model here
   ```

2. **Create Service Layer**:
   ```python
   # src/services/new_service.py
   class NewService:
       @staticmethod
       def get_all():
           # Business logic here
           pass
   ```

3. **Create Routes**:
   ```python
   # src/routes/new_routes.py
   from flask import Blueprint
   new_bp = Blueprint('new', __name__)
   
   @new_bp.route('/new', methods=['GET'])
   def get_new():
       # Route logic here
       pass
   ```

4. **Add Tests**:
   ```python
   # tests/test_new_feature.py
   def test_new_feature():
       # Test your feature
       pass
   ```

5. **Update Documentation**: Add your new endpoints to this README

### Database Migrations
```bash
# Create new migration
python migrate_new_feature.py

# Apply migrations
python init_db.py
```

## 🚀 Deployment

### Production Setup

1. **Environment Variables**:
   ```env
   FLASK_ENV=production
   SECRET_KEY=your-production-secret-key
   DB_HOST=your-production-db-host
   DB_NAME=painaidee_production
   DB_USER=painaidee_user
   DB_PASSWORD=secure-password
   ```

2. **Database Setup**:
   - Use managed PostgreSQL service (AWS RDS, Google Cloud SQL, etc.)
   - Set up regular backups
   - Configure connection pooling

3. **Security Considerations**:
   - Use HTTPS in production
   - Implement rate limiting
   - Set up proper CORS policies
   - Use strong JWT secret keys
   - Enable database SSL connections

### Docker Production
```bash
# Build production image
docker build -t painaidee-backend:latest .

# Run with production environment
docker run -d \
  --name painaidee-backend \
  --env-file .env.production \
  -p 5000:5000 \
  painaidee-backend:latest
```

## 🔮 Future Development Roadmap

### Short-term Goals (Next 3 months)
- [ ] **Enhanced Search**: Implement full-text search with Elasticsearch integration
- [ ] **Image Upload**: Add image upload functionality for attractions and reviews
- [ ] **Notification System**: Email/SMS notifications for booking confirmations
- [ ] **Payment Integration**: Stripe/PayPal integration for booking payments
- [ ] **API Rate Limiting**: Implement rate limiting to prevent abuse
- [ ] **Caching Layer**: Add Redis caching for frequently accessed data

### Medium-term Goals (3-6 months)
- [ ] **Mobile API Optimization**: Optimize APIs for mobile applications
- [ ] **Social Features**: User profiles, friend systems, and social sharing
- [ ] **Advanced Analytics**: Enhanced dashboard with business intelligence
- [ ] **Multi-language Support**: Internationalization for Thai and English
- [ ] **Recommendation Engine**: AI-powered attraction recommendations
- [ ] **Real-time Features**: WebSocket support for real-time notifications

### Long-term Goals (6-12 months)
- [ ] **Microservices Architecture**: Break down into smaller, specialized services
- [ ] **GraphQL API**: Implement GraphQL alongside REST for flexible queries
- [ ] **Machine Learning**: Personalized recommendations using ML algorithms
- [ ] **Mobile Apps**: Native iOS and Android applications
- [ ] **Advanced Booking**: Complex booking workflows with availability calendars
- [ ] **Merchant Portal**: Separate portal for attraction owners to manage listings

### Technical Improvements
- [ ] **Performance Optimization**: Database query optimization and indexing
- [ ] **Security Enhancements**: OAuth2 integration, 2FA support
- [ ] **Monitoring**: APM integration (New Relic, DataDog)
- [ ] **CI/CD Pipeline**: Automated testing and deployment
- [ ] **Load Testing**: Performance testing and scaling strategies
- [ ] **Documentation**: OpenAPI/Swagger documentation generation

## 🤝 Contributing

We welcome contributions to the PaiNaiDee Backend project! Here's how you can help:

### Getting Started
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following our development guidelines
4. Add tests for new functionality
5. Ensure all tests pass: `python -m pytest`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Contribution Guidelines
- **Code Quality**: Follow PEP 8 and add appropriate tests
- **Documentation**: Update README and add docstrings
- **Commit Messages**: Use clear, descriptive commit messages
- **Pull Requests**: Provide detailed description of changes
- **Issues**: Use issue templates for bug reports and feature requests

### Areas for Contribution
- 🐛 **Bug Fixes**: Help us identify and fix issues
- ✨ **New Features**: Implement features from our roadmap
- 📚 **Documentation**: Improve documentation and examples
- 🧪 **Testing**: Increase test coverage and add edge cases
- 🎨 **Code Quality**: Refactoring and performance improvements
- 🌐 **Localization**: Add support for additional languages

## 📞 Support

### Getting Help
- **Documentation**: Check this README and other documentation files
- **Issues**: Create an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas

### Contact Information
- **GitHub**: [@athipan1](https://github.com/athipan1)
- **Project Repository**: [PaiNaiDee_Backend](https://github.com/athipan1/PaiNaiDee_Backend)

### Related Projects
- **Frontend**: [PaiNaiDee Frontend](https://github.com/athipan1/pai-naidee-ui-spark)
- **3D Map**: [PaiNaiDee 3D Map](https://github.com/athipan1/PaiNaiDee_map_3D)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask and SQLAlchemy communities for excellent documentation
- PostgreSQL for reliable database foundation
- All contributors who have helped improve this project
- Tourism Authority of Thailand for inspiration

---

**Made with ❤️ for Thai tourism** 🇹🇭