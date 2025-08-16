# Use a lightweight Python image
FROM python:3.11-slim

# Ensure output is not buffered
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /workspaces/PaiNaiDee_Backend

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN apt-get update \
    && apt-get install -y curl \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the application source code for both development and Spaces
COPY . .

# Expose ports for development (FastAPI) and Spaces
EXPOSE 8000 7860 5000

# Optional healthcheck for Spaces container
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || curl -f http://127.0.0.1:7860/health || exit 1

# Default command for development (can be overridden by docker-compose)
CMD ["python", "run_fastapi.py"]
