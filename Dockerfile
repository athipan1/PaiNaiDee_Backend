# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y curl && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code
COPY src/ ./src/
COPY run.py .
COPY migrate_image_urls.py .
COPY init_db.py .

# Expose the port the app runs on
EXPOSE 5000

# Set the command to run the application
CMD ["python", "run.py"]
