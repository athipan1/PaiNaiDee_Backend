# Use a lightweight Python image
FROM python:3.11-slim

# Ensure output is not buffered
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN apt-get update \
    && apt-get install -y curl \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the application source code and Spaces entrypoint
COPY src/ ./src/
COPY app.py .
COPY run.py .
COPY migrate_image_urls.py .
COPY init_db.py .

# Expose the port Hugging Face Spaces expects (7860)
EXPOSE 7860

# Optional healthcheck for Spaces container
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:7860/health || exit 1

# Use gunicorn to run the app module created for Spaces (app:app)
CMD ["gunicorn", "app:app", "--workers", "1", "--bind", "0.0.0.0:7860"]
