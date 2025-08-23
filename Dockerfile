FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=7860
EXPOSE 7860

# Healthcheck for Hugging Face Spaces
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:7860/health || exit 1

CMD ["python", "run_fastapi.py"]
