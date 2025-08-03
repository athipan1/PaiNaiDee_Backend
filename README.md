# PaiNaiDee Backend API 🇹🇭

[![Tests](https://img.shields.io/badge/tests-82%20passing-green.svg)](tests/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-3.1.1-blue.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

PaiNaiDee ("ไปไหนดี" - "Where to go?" in Thai) is a comprehensive backend API for a tourism application that helps users discover, explore, and book attractions in Thailand. Built with Flask and PostgreSQL, it provides a robust foundation for travel applications with features including attraction management, user reviews, booking systems, and real-time analytics.

## 🌟 Features

### Core Features
- **🏛️ Attraction Management**: Complete CRUD operations for tourist attractions with detailed information including location, categories, images, and contact details
- **👥 User Authentication**: Secure JWT-based authentication and authorization system
- **⭐ Review & Rating System**: Users can rate attractions (1-5 stars) and leave detailed reviews
- **🏨 Booking System**: Book accommodations (rooms) and transportation (car rentals) at attractions
- **🎥 Video Content**: Upload and manage video content related to attractions
- **🔍 Advanced Search**: Search attractions by name, location, category with pagination support
- **📊 Analytics Dashboard**: Real-time API usage analytics and monitoring
- **🗺️ 3D Map Integration**: Ready for 3D map visualization (via separate map service)

### Technical Features
- **RESTful API Design**: Clean, consistent API endpoints following REST principles
- **Database Relationships**: Properly normalized PostgreSQL database with foreign key constraints
- **Input Validation**: Marshmallow schemas for request/response validation
- **Error Handling**: Comprehensive error handling with standardized response format
- **CORS Support**: Cross-origin resource sharing for frontend integration
- **Docker Support**: Complete containerization with Docker Compose
- **Comprehensive Testing**: 82 test cases covering all major functionality
- **Analytics Middleware**: Automatic request tracking and performance monitoring

## 🏗️ Architecture

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
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    PostgreSQL Database    │
                    │  (Attractions, Users,     │
                    │   Reviews, Bookings)      │
                    └───────────────────────────┘
```

## 🚀 Quick Deploy

Deploy PaiNaiDee Backend instantly with one click:

### 🌟 Permanent Deployment
[![Deploy to Hugging Face Spaces](https://huggingface.co/datasets/huggingface/badges/raw/main/deploy-to-spaces-sm.svg)](https://huggingface.co/new-space)

**Deploy permanently on Hugging Face Spaces**
- ✅ **One-click deployment** - No setup required
- ✅ **Always online** - Permanent public URL  
- ✅ **Free hosting** - No cost for basic usage
- ✅ **Auto-scaling** - Handles traffic automatically
- ✅ **Sample data included** - Ready to test immediately

**How to deploy:**
1. Click the "Deploy to Spaces" button above
2. Sign up/login to Hugging Face (free)
3. Choose "Clone a repository" and enter: `https://github.com/athipan1/PaiNaiDee_Backend`
4. Set SDK to "Docker" and choose a name for your Space
5. Click "Create Space"
6. Wait 2-3 minutes for deployment
7. Your API will be live at `https://your-space-name.hf.space`

### 🔬 Temporary Testing
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/athipan1/PaiNaiDee_Backend/blob/main/PaiNaiDee_Colab_Deploy.ipynb)

**Run temporarily on Google Colab with ngrok tunnel**
- ✅ **Instant testing** - No account required
- ✅ **Full database** - SQLite with sample data
- ✅ **Public URL** - Access from anywhere via ngrok
- ✅ **Interactive notebook** - Step-by-step guided setup
- ⚠️ **Temporary** - Stops when notebook closes

**How to run:**
1. Click the "Open in Colab" button above  
2. Run all cells (Runtime → Run all)
3. Copy the ngrok URL from the output
4. Use the URL to test the API
5. Server runs until you close the notebook

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
   Create a `.env` file in the root directory:
   ```env
   # Flask Configuration
   SECRET_KEY=your-super-secret-key-here
   FLASK_ENV=development

   # Database Configuration
   DB_HOST=localhost
   DB_NAME=painaidee_db
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_PORT=5432
   ```

5. **Running the Application:**
   ```bash
   # Start the Flask development server
   python run.py

   # Or use Flask CLI
   flask run

   # API will be available at http://localhost:5000
   ```

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

#### Search
```http
GET    /api/search                   # Search attractions
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

#### Search Attractions
```bash
curl "http://localhost:5000/api/search?q=temple&location=Bangkok"
```

For complete API documentation, see the [API Reference](docs/api-reference.md) (when available).

## 🌐 Deployment Options

### 🌟 Hugging Face Spaces (Recommended for Demo/Production)

Hugging Face Spaces provides free, permanent hosting for your PaiNaiDee Backend API.

#### ✅ Advantages:
- **Always online** - 24/7 availability with public URL
- **No server management** - Automatic scaling and maintenance
- **Free hosting** - No cost for basic usage  
- **Easy sharing** - Share your API with a simple URL
- **Version control** - Git-based deployment and updates

#### 🚀 Quick Deploy Steps:
1. **Click Deploy Button**: Use the deploy button in the Quick Deploy section above
2. **Create Account**: Sign up for free Hugging Face account if needed
3. **Configure Space**: 
   - Choose a unique name (e.g., `my-painaidee-api`)
   - Set visibility (Public recommended for demo)
   - SDK will be automatically set to "Docker"
4. **Deploy**: Click "Create Space" and wait 2-3 minutes
5. **Access**: Your API will be live at `https://your-space-name.hf.space`

#### 📝 Hugging Face Spaces Configuration:
The deployment uses these files:
- `app.py` - Hugging Face Spaces entry point
- `spaces_requirements.txt` - Optimized dependencies for Spaces
- SQLite database with sample Thai tourism data

#### 🔧 Customization:
After deployment, you can:
- Update the sample data by modifying `app.py`
- Add your own attractions and categories
- Customize the API responses and branding
- Connect to external PostgreSQL database if needed

#### 🌐 Example Deployed Space:
```
https://your-space-name.hf.space/                    # Homepage with API info
https://your-space-name.hf.space/api/attractions     # Get all attractions  
https://your-space-name.hf.space/api/search?q=วัด    # Search attractions
https://your-space-name.hf.space/health              # Health check
```

---

### 🔬 Google Colab (Best for Testing & Development)

Perfect for testing the API temporarily without any setup or accounts.

#### ✅ Advantages:
- **No setup required** - Runs in your browser
- **Instant testing** - Start in under 5 minutes
- **Full environment** - Complete Python environment provided
- **ngrok tunnel** - Public URL for external access
- **Interactive** - Step-by-step guided setup

#### 🚀 Quick Start Steps:
1. **Open Notebook**: Click the "Open in Colab" button above
2. **Run All Cells**: Go to Runtime → Run all (or Ctrl+F9)
3. **Wait for Setup**: Takes 2-3 minutes to install and configure
4. **Copy URL**: Get the ngrok URL from the output
5. **Test API**: Use the URL to access your API endpoints

#### 📋 What the Notebook Does:
1. **Installs Dependencies**: Flask, SQLAlchemy, ngrok, etc.
2. **Clones Repository**: Gets latest code from GitHub
3. **Sets up Database**: Creates SQLite with 8+ sample attractions
4. **Starts Server**: Runs Flask development server
5. **Creates Tunnel**: ngrok provides public HTTPS URL
6. **Provides Testing**: Sample API calls to verify setup

#### 🌐 Example Colab URLs:
```
https://abc123.ngrok.io/                    # Homepage (changes each run)
https://abc123.ngrok.io/api/attractions     # API endpoints
https://abc123.ngrok.io/health              # Health check
```

#### ⚠️ Important Notes:
- **Temporary**: Server stops when you close the notebook
- **URL Changes**: New ngrok URL each time you restart
- **Keep Running**: Don't close the browser tab
- **Free Tier**: Google Colab free tier has usage limits

---

### 🔧 Production Deployment Considerations

For production deployment, consider these additional options:

#### 🐳 Docker Deployment:
```bash
# Build and run with Docker
docker-compose up --build

# Access at http://localhost:5000
```

#### ☁️ Cloud Platforms:
- **Heroku**: Use the provided Dockerfile
- **Railway**: Connect GitHub repository for auto-deploy
- **AWS/GCP/Azure**: Use container services with PostgreSQL
- **DigitalOcean App Platform**: Deploy directly from GitHub

#### 🗄️ Database Options:
- **Development**: SQLite (included in both deployment options)
- **Production**: PostgreSQL (recommended)
- **Cloud**: AWS RDS, Google Cloud SQL, Azure Database

#### 🔒 Security Considerations:
- Change default SECRET_KEY in production
- Set up proper environment variables
- Enable HTTPS in production
- Configure CORS policies appropriately
- Use strong JWT secrets and expiration times

## 🧪 Testing

The project includes comprehensive testing with 82 test cases covering all major functionality.

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_reviews.py -v

# Run tests with coverage
python -m pytest --cov=src tests/

# Run specific test
python -m pytest tests/test_app.py::test_get_all_attractions -v
```

### Test Categories
- **Unit Tests**: Service layer logic and utilities
- **Integration Tests**: API endpoint functionality
- **Authentication Tests**: JWT and user authorization
- **Database Tests**: Model relationships and constraints
- **Analytics Tests**: Dashboard and monitoring features

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
src/
├── app.py                 # Flask application factory
├── config.py             # Configuration settings
├── database.py           # Database initialization
├── models/               # SQLAlchemy models
├── routes/               # API route blueprints
├── services/             # Business logic layer
├── schemas/              # Marshmallow validation schemas
├── utils/                # Utility functions and middleware
└── errors.py             # Error handlers

tests/                    # Test files
requirements.txt          # Python dependencies
docker-compose.yml        # Docker configuration
Dockerfile               # Docker build instructions
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