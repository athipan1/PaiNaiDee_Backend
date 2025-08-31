# Use a slim Python base image to reduce size
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_ENV=huggingface
ENV PORT=7860

# Set work directory
WORKDIR /app

# Install system dependencies - only curl is needed for the health check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application source code
COPY . .

# Expose the port the app runs on
EXPOSE 7860

# Healthcheck for Hugging Face Spaces to ensure the app is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://127.0.0.1:7860/health || exit 1

# Command to run the application using Gunicorn
# This is the standard for production Flask apps.
# It looks for the 'app' object in the 'wsgi.py' file.
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "wsgi:app"]
