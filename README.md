# PaiNaiDee_Backend

![Deployment Status](https://img.shields.io/badge/Deployment-Ready-brightgreen?style=flat-square)
![Platforms](https://img.shields.io/badge/Platforms-7-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

## 🚀 One-Click Deployment

Deploy PaiNaiDee Backend to your favorite platform with a single click:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/G2tGbV?referralCode=alphaDev)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/athipan1/PaiNaiDee_Backend)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/athipan1/PaiNaiDee_Backend)
[![Deploy on HF Spaces](https://huggingface.co/spaces/button)](https://huggingface.co/spaces/new?repo=athipan1/PaiNaiDee_Backend)
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/athipan1/PaiNaiDee_Backend)

### 🔧 Development Environments

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/athipan1/PaiNaiDee_Backend)
[![Run on Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/athipan1/PaiNaiDee_Backend/blob/main/PaiNaiDee_Colab_Deploy.ipynb)

### 🛠️ Quick Deploy Script

For a guided deployment experience, run:
```bash
chmod +x deploy.sh
./deploy.sh
```

This interactive script will help you choose and deploy to your preferred platform.

---

## 📖 Deployment Guide

### Platform Comparison

| Platform | Type | Database | Free Tier | Best For |
|----------|------|----------|-----------|----------|
| **Railway** | PaaS | PostgreSQL | 500 hrs/month | Production apps |
| **Render** | PaaS | PostgreSQL | 750 hrs/month | Web services |
| **Vercel** | Serverless | External DB | Generous limits | API endpoints |
| **HF Spaces** | Container | SQLite | Unlimited | Demos & prototypes |
| **Codespaces** | Dev Environment | PostgreSQL | 60 hrs/month | Development |
| **Google Colab** | Notebook | SQLite | Free with limits | Quick testing |

### 🚂 Railway Deployment

1. Click the Railway deploy button above
2. Connect your GitHub account
3. Configure environment variables (optional - Railway will auto-provision PostgreSQL)
4. Deploy automatically with PostgreSQL database

**Features:**
- ✅ Automatic PostgreSQL database
- ✅ Custom domain support
- ✅ Environment variables management
- ✅ Automatic deployments on git push

### 🎨 Render Deployment

1. Click the Render deploy button above
2. Connect your GitHub repository
3. Render will automatically create both web service and PostgreSQL database
4. Set up custom domain (optional)

**Features:**
- ✅ Free PostgreSQL database
- ✅ Automatic SSL certificates
- ✅ Git-based deployments
- ✅ Health checks and monitoring

### ⚡ Vercel Deployment

**Note:** Vercel is optimized for serverless functions. This deployment uses SQLite.

1. Click the Vercel deploy button above
2. Import the repository to your Vercel account
3. Add environment variables in Vercel dashboard:
   - `SECRET_KEY`: Your Flask secret key
   - `DATABASE_URL`: External database URL (optional)
4. Deploy

**Features:**
- ✅ Serverless architecture
- ✅ Global CDN
- ✅ Automatic HTTPS
- ⚠️ External database required for persistence

### 🤗 Hugging Face Spaces

Perfect for demos and sharing your API publicly.

1. Click the HF Spaces deploy button above
2. Create new Space with Docker SDK
3. Space automatically deploys with SQLite database
4. Share your public API URL

**Features:**
- ✅ Always free
- ✅ Public sharing
- ✅ Docker container
- ⚠️ SQLite database (not persistent across restarts)

### 💻 Development with GitHub Codespaces

1. Click "Open in GitHub Codespaces" button above
2. Wait for container to build (uses docker-compose.yml)
3. Codespace includes PostgreSQL database
4. Start developing immediately

**Features:**
- ✅ Full development environment
- ✅ PostgreSQL database included
- ✅ VS Code in browser
- ✅ 60 hours free per month

### 📓 Google Colab (Quick Testing)

For immediate testing without any setup:

1. Click "Run on Google Colab" button above
2. Run all cells in sequence
3. Get a public ngrok URL for testing
4. Perfect for API exploration

**Features:**
- ✅ No account setup needed
- ✅ Instant public URL via ngrok
- ✅ Sample data included
- ⚠️ Temporary (session-based)

---

## 🔧 Environment Variables

Copy `.env.example` to `.env` and configure the following variables:

### Required Variables
```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here          # Generate a secure random key
FLASK_ENV=production                     # or 'development' for local dev

# Database Configuration (for Railway/Render/local development)
DATABASE_URL=postgresql://user:pass@host:port/db  # Auto-provided by most platforms
# OR individual database settings:
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=painaidee_db
```

### Optional Variables
```bash
# LLM/Chat Features (Optional)
OPENAI_API_KEY=sk-your-key-here         # For AI chat features
TALK_MODEL=gpt-3.5-turbo               # OpenAI model to use
TALK_MAX_TOKENS=500                    # Response length limit
```

### Platform-Specific Notes

- **Railway/Render/Heroku**: `DATABASE_URL` is automatically provided
- **Vercel**: Requires external database (Supabase, PlanetScale, etc.)
- **HF Spaces**: Uses SQLite, no database config needed
- **Codespaces**: Uses Docker Compose with PostgreSQL
- **Google Colab**: Uses temporary SQLite database

---

## Overview (Short)

- This repository contains the backend for PaiNaiDee.
- HF Spaces SDK: Docker
- App port: 7860

---

## Verified files

- Dockerfile: present at repository root and exposes port 7860. The Dockerfile uses gunicorn and includes a health check at `/health`.
- requirements.txt: present at repository root and lists runtime dependencies.

(These files were checked and are present in the repository root.)

---

## Quick Start (English)

1. Clone the repository:

```bash
git clone https://github.com/athipan1/PaiNaiDee_Backend.git
cd PaiNaiDee_Backend
```

2. Build Docker image (optional, for local testing):

```bash
docker build -t painaidee-backend:latest .
```

3. Run Docker locally:

```bash
docker run -p 7860:7860 painaidee-backend:latest
```

- Health endpoint: http://localhost:7860/health
- The app listens on port 7860.

---

## การติดตั้งด่วน (ภาษาไทย)

1. โคลนรีโป:

```bash
git clone https://github.com/athipan1/PaiNaiDee_Backend.git
cd PaiNaiDee_Backend
```

2. สร้าง Docker image (ทดสอบเครื่องท้องถิ่น):

```bash
docker build -t painaidee-backend:latest .
```

3. รัน Docker:

```bash
docker run -p 7860:7860 painaidee-backend:latest
```

- ตรวจสุขภาพ: http://localhost:7860/health
- แอปฟังพอร์ต 7860

---

## Notes for Hugging Face Spaces

- This repository is configured to be used as a Docker-based Hugging Face Space (Docker SDK).
- To create a Space from this repo: click the button at the top or visit:

```
https://huggingface.co/spaces/new?repo=athipan1/PaiNaiDee_Backend
```

- The Space will run the Dockerfile in the repository root. Ensure the repo is public or you have access to create the Space.

---

## Mobile-friendly tips

- Sections use short headings and bullet lists for easy reading on small screens.
- Code blocks are short and focused.

---

## 🔧 Troubleshooting Deployments

### Common Issues

#### Railway Deployment
- **Build fails**: Check that `requirements.txt` is in the root directory
- **Database connection**: Railway auto-provides `DATABASE_URL` environment variable
- **Port issues**: Railway automatically detects the port from your application

#### Render Deployment  
- **Build timeout**: Large dependency installations may timeout on free tier
- **Database creation**: Make sure PostgreSQL service starts before web service
- **Health check fails**: Verify `/health` endpoint is accessible

#### Vercel Deployment
- **Serverless limitations**: Each function has 50MB limit and 10s timeout on hobby plan
- **Database persistence**: Use external database service (Supabase, PlanetScale)
- **Cold starts**: First request may be slow due to serverless nature

#### Hugging Face Spaces
- **Space fails to start**: Check Dockerfile syntax and port 7860 exposure
- **No database**: Uses SQLite with sample data, data resets on restart
- **Memory limits**: Space may restart under high memory usage

#### GitHub Codespaces
- **Port forwarding**: Make sure ports 5000 and 5432 are forwarded
- **Database not accessible**: Wait for PostgreSQL container to fully start
- **Permission issues**: Run `sudo chown -R $(whoami) /app` if needed

### Getting Help

1. **Check logs**: Each platform provides deployment logs
2. **Environment variables**: Verify all required variables are set
3. **Database connectivity**: Test database connection with provided credentials
4. **Health endpoint**: Verify `/health` returns 200 OK response

For more help, [open an issue](https://github.com/athipan1/PaiNaiDee_Backend/issues) with:
- Platform used
- Error message or logs
- Environment variables used (without sensitive values)

---

## 📊 Deployment Status

All deployment configurations have been tested and validated:

- ✅ `app.json` - Valid JSON for Railway/Heroku deployment
- ✅ `railway.json` - Valid Railway-specific configuration  
- ✅ `render.yaml` - Valid Render service configuration
- ✅ `vercel.json` - Valid Vercel serverless configuration
- ✅ `devcontainer.json` - Valid GitHub Codespaces configuration
- ✅ `Dockerfile` - Tested container build for Hugging Face Spaces
- ✅ `PaiNaiDee_Colab_Deploy.ipynb` - Working Google Colab notebook

---