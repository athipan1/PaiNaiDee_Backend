# ใช้ Python 3.10 แบบ slim เพื่อลดขนาด image
FROM python:3.10-slim

# ติดตั้ง curl และ git สำหรับ healthcheck และ clone repo
RUN apt-get update && apt-get install -y curl git && rm -rf /var/lib/apt/lists/*

# Clone โค้ดจาก GitHub repo โดยตรง
RUN git clone https://github.com/athipan1/PaiNaiDee_Backend.git /app

# ตั้ง working directory
WORKDIR /app

# ติดตั้ง dependencies จาก requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ตั้งค่าพอร์ตและ expose
ENV PORT=7860
EXPOSE 7860

# Healthcheck สำหรับ Hugging Face Spaces
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:7860/health || exit 1

# รันแอปด้วย Python
CMD ["python", "app.py"]
