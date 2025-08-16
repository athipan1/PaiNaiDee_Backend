# PaiNaiDee_Backend

[![Deploy on HF Spaces](https://huggingface.co/spaces/button)](https://huggingface.co/spaces/new?repo=athipan1/PaiNaiDee_Backend)

คลิกปุ่มด้านบนเพื่อสร้าง Hugging Face Space ใหม่จากรีโปนี้โดยตรง (ใช้พารามิเตอร์ `repo=` เพื่อหลีกเลี่ยงข้อผิดพลาด 400 ที่เกิดจาก `template=`)

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

## What changed in this PR

- Updated README.md to:
  - Replace the HF Spaces deploy link to use `repo=` to avoid 400 errors from `template=`.
  - Add English and Thai quick-install instructions.
  - Add a verified note that Dockerfile and requirements.txt exist at repo root.
  - Clarify Docker SDK and port 7860.
  - Use mobile-friendly markdown structure.

This PR modifies README.md only.

---

## PR metadata
- Branch: fix/readme-hf-spaces-deploy
- Base: main
- Title: docs: update README to fix HF Spaces deploy button and add install instructions
- Files changed: README.md (full replacement with content above)