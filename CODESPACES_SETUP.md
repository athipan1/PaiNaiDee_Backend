# GitHub Codespaces Setup for PaiNaiDee Backend

This document explains the GitHub Codespaces configuration for the PaiNaiDee Backend project with FastAPI app located at `app/main.py`.

## Configuration Overview

### .devcontainer/devcontainer.json
- **workspaceFolder**: `/workspaces/PaiNaiDee_Backend` (repository root)
- **service**: `backend` (from docker-compose.yml)
- **postCreateCommand**: `pip install -r requirements.txt` (installs dependencies)
- **postStartCommand**: `python run_fastapi.py` (starts FastAPI app automatically)

### Port Forwarding
- **8000**: FastAPI app (primary)
- **5000**: Flask app (legacy)
- **5432**: PostgreSQL database
- **7860**: Hugging Face Spaces port

### Database Configuration
The app automatically detects the environment:
- **Codespaces/Docker**: Uses PostgreSQL with async driver (`postgresql+asyncpg://`)
- **Standalone**: Falls back to SQLite with async driver (`sqlite+aiosqlite://`)

## Files Modified

### 1. `.devcontainer/devcontainer.json`
```json
{
  "workspaceFolder": "/workspaces/PaiNaiDee_Backend",  // Fixed from "/app"
  "postStartCommand": "python run_fastapi.py",        // Changed from Flask to FastAPI
  "forwardPorts": [5000, 8000, 5432, 7860],          // Added port 8000
  "mounts": [
    "source=${localWorkspaceFolder}/.env,target=/workspaces/PaiNaiDee_Backend/.env,type=bind,consistency=cached"
  ]
}
```

### 2. `docker-compose.yml`
```yaml
services:
  backend:
    build:
      context: .                    # Fixed from "./PaiNaiDee_Backend"
    ports:
      - "5000:5000"
      - "8000:8000"                # Added FastAPI port
    command: >
      sh -c "
        pip install psycopg2-binary &&
        python init_db.py &&
        python migrate_image_urls.py &&
        python run_fastapi.py        # Changed from run.py
      "
```

### 3. `Dockerfile`
```dockerfile
WORKDIR /workspaces/PaiNaiDee_Backend  # Changed from /app
COPY . .                               # Copy entire repository
EXPOSE 8000 7860 5000                  # Added development ports
CMD ["python", "run_fastapi.py"]       # Default to FastAPI
```

### 4. `app/db/session.py`
- Added support for async SQLite driver (`sqlite+aiosqlite://`)
- Made database initialization PostgreSQL-aware (skips pg_trgm for SQLite)

### 5. `run_fastapi.py`
- Auto-detects PostgreSQL vs SQLite environment
- Uses PostgreSQL when `DB_HOST` or `DATABASE_URL` environment variables are set
- Falls back to SQLite for standalone demo mode

## Usage

### Starting Codespaces
1. Click "Open in GitHub Codespaces" 
2. Wait for container to build
3. FastAPI app starts automatically on port 8000
4. Access documentation at `http://localhost:8000/docs`

### Manual Startup
```bash
# Install dependencies (if not done automatically)
pip install -r requirements.txt

# Start FastAPI app
python run_fastapi.py
```

### Accessing the API
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Search Example**: http://localhost:8000/api/search?q=เชียงใหม่

## Dependencies Added
- `aiosqlite`: For async SQLite support in standalone mode

## Environment Variables
The app uses these environment variables (automatically set in Codespaces):
- `DB_HOST`: PostgreSQL host (default: "db")
- `DB_USER`: PostgreSQL user (default: "postgres") 
- `DB_PASSWORD`: PostgreSQL password
- `DB_NAME`: Database name (default: "painaidee_db")
- `DATABASE_URL`: Complete database URL (overrides individual settings)

## Troubleshooting

### Port Issues
If port 8000 is not accessible, check that it's forwarded in the Ports tab of VS Code.

### Database Connection Issues
- PostgreSQL: Ensure the `db` service is running in docker-compose
- SQLite: App will automatically create `demo.db` file

### Permission Issues
If you encounter permission issues:
```bash
sudo chown -R $(whoami) /workspaces/PaiNaiDee_Backend
```

## Development Workflow
1. Make changes to code
2. FastAPI automatically reloads (thanks to `reload=True` in uvicorn)
3. Test via http://localhost:8000/docs
4. Use PostgreSQL for full testing, SQLite for quick demos