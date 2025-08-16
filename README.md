# PaiNaiDee Backend

[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/athipan1/PaiNaiDee_Backend)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/athipan1/PaiNaiDee_Backend)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/athipan1/PaiNaiDee_Backend/blob/main/PaiNaiDee_Colab_Deploy.ipynb)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/athipan1/PaiNaiDee_Backend)

**🇹🇭 Thai Tourism API - Where to go in Thailand**

A comprehensive Flask backend API providing Thai tourism data, attractions search, user reviews, and booking management. Supports both Flask (production-ready) and FastAPI (Phase 1) implementations.

## 🚀 Quick Deploy

Click any deploy button above for one-click deployment:

- **Vercel**: Dockerfile-based deployment with automatic scaling
- **Railway**: Managed deployment with PostgreSQL database
- **Google Colab**: Interactive notebook environment for testing
- **GitHub Codespaces**: Full development environment in the cloud

## 🛠️ Local Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL (for production) or SQLite (for development)

### Using Python Virtual Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/athipan1/PaiNaiDee_Backend.git
   cd PaiNaiDee_Backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run the Flask application**
   ```bash
   # Development server
   python run.py
   
   # Or with Flask CLI
   flask run
   
   # Production with gunicorn
   gunicorn wsgi:app --bind 0.0.0.0:5000
   ```

### Using Docker

1. **Build the Docker image**
   ```bash
   docker build -t painaidee-backend .
   ```

2. **Run with Docker**
   ```bash
   # For local development (port 5000)
   docker run -p 5000:7860 -e PORT=7860 painaidee-backend
   
   # For production deployment (port 7860, matches Dockerfile)
   docker run -p 7860:7860 painaidee-backend
   ```

3. **Using Docker Compose** (includes PostgreSQL)
   ```bash
   docker-compose up -d
   ```

## ☁️ GitHub Codespaces Quick Start

1. Click the Codespaces badge above or visit the repository and click "Code" → "Codespaces" → "Create codespace on main"

2. Once the environment loads, install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```

4. Run the development server:
   ```bash
   python run.py
   ```

The app will be available on port 5000 with automatic port forwarding.

## 🔧 Environment Variables

Copy `.env.example` to `.env` and configure the following variables:

### Required Variables
| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `SECRET_KEY` | Flask secret key for sessions | `a-very-secret-key` | `your-secret-key-here` |
| `FLASK_ENV` | Flask environment | `development` | `production` |

### Database Configuration
| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DATABASE_URL` | Full database URL (Railway/Heroku) | - | `postgresql://user:pass@host:5432/db` |
| `DB_USER` | Database username | `postgres` | `your_username` |
| `DB_PASSWORD` | Database password | - | `your_password` |
| `DB_HOST` | Database host | `localhost` | `your-db-host.com` |
| `DB_PORT` | Database port | `5432` | `5432` |
| `DB_NAME` | Database name | `painaidee_db` | `your_database` |

### Optional Variables (AI Features)
| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for talk feature | - |
| `TALK_MODEL` | AI model for conversations | `gpt-3.5-turbo` |
| `TALK_MAX_TOKENS` | Max tokens for AI responses | `500` |
| `TALK_TEMPERATURE` | AI response creativity | `0.7` |

## 📚 Notebooks & Testing

### 🧪 Google Colab Notebook
**[PaiNaiDee_Colab_Deploy.ipynb](https://colab.research.google.com/github/athipan1/PaiNaiDee_Backend/blob/main/PaiNaiDee_Colab_Deploy.ipynb)** - Interactive deployment and testing environment

- One-click setup and deployment
- Automatic dependency installation
- ngrok tunnel for public access
- API testing and demonstration

### 🔬 API Testing Notebook
**[tests/test_all_apis.ipynb](https://github.com/athipan1/PaiNaiDee_Backend/blob/main/tests/test_all_apis.ipynb)** - Comprehensive API testing

- Test all endpoints
- Authentication flow testing
- Data validation tests

## 🌐 API Reference (Examples)

Base URL: `http://localhost:5000` (development) or your deployed URL

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API home and health check |
| `GET` | `/health` | Health check endpoint |

### Attractions
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/attractions` | Get all attractions (paginated) |
| `GET` | `/api/attractions/<id>` | Get specific attraction |
| `POST` | `/api/attractions` | Create new attraction |
| `PUT` | `/api/attractions/<id>` | Update attraction |
| `DELETE` | `/api/attractions/<id>` | Delete attraction |
| `GET` | `/api/attractions/category/<name>` | Get attractions by category |

### Search & Discovery
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/search` | Search attractions with fuzzy matching |
| `POST` | `/api/search` | Advanced search with filters |

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | User registration |
| `POST` | `/api/auth/login` | User login |

### User Content
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/reviews` | Submit attraction review |
| `GET` | `/api/attractions/<id>/reviews` | Get attraction reviews |
| `POST` | `/api/booking` | Create booking |
| `POST` | `/api/videos/upload` | Upload video content |
| `GET` | `/api/videos` | Get videos |

### AI Features
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/talk` | AI-powered tourism assistant |

## 🚢 Platform Deployment Notes

### Vercel Deployment
- Uses the provided `Dockerfile` for containerized deployment
- Set environment variables in Vercel dashboard
- App automatically listens on `$PORT` provided by Vercel
- Supports automatic scaling and edge functions

### Railway Deployment  
- Uses `Procfile` for deployment: `web: gunicorn wsgi:app --workers 2 --bind 0.0.0.0:$PORT`
- Configure PostgreSQL database in Railway dashboard
- Set `DATABASE_URL` environment variable automatically provided
- App listens on Railway's provided `$PORT` environment variable

### Environment Variables Configuration
- **Vercel**: Configure in Project Settings → Environment Variables
- **Railway**: Configure in Project Settings → Variables tab
- **Docker**: Pass via `-e` flags or docker-compose.yml
- **Local**: Use `.env` file (copy from `.env.example`)

### Database Notes
- **Production**: Use PostgreSQL for full feature support
- **Development/Demo**: SQLite supported for quick testing
- **Railway**: PostgreSQL addon available in dashboard
- **Vercel**: Connect external PostgreSQL or use Vercel Postgres

## 🏗️ Project Structure

```
PaiNaiDee_Backend/
├── src/                    # Main Flask application
│   ├── app.py             # Flask app factory
│   ├── routes/            # API route definitions
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   └── config.py          # Configuration management
├── app/                   # FastAPI implementation (Phase 1)
├── app.py                 # Hugging Face Spaces entry point
├── wsgi.py               # WSGI production entry point
├── run.py                # Development server entry point
├── Dockerfile            # Container configuration
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Multi-service setup
└── PaiNaiDee_Colab_Deploy.ipynb  # Colab deployment notebook
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🎉 Happy coding with PaiNaiDee Backend! 🇹🇭**

*Built with ❤️ for Thai tourism and travelers worldwide*