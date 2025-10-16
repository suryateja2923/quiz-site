# ==============================
# 2nd Year Quiz App - Dockerfile
# ==============================

FROM python:3.11-slim

# Disable Python .pyc and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy project files into the container
COPY . .

# Create folder for generated Excel files
RUN mkdir -p /app/quiz_data

# Environment variables for image paths
# NOTE: Images are inside /app/images in your repo
ENV HEADER_IMG_PATH=/app/images/header.jpg \
    LOGO_IMG_PATH=/app/images/logo.jpg

# Optional admin credentials (change in Render dashboard if needed)
ENV QUIZ_ADMIN_USER=surya \
    QUIZ_ADMIN_PASS=nriit123

# Optional Flask secret
ENV QUIZ_SECRET=render-secret

# Expose port (Render auto-assigns $PORT)
EXPOSE 5000

# Start with gunicorn (Render default pattern)
CMD exec gunicorn -k gthread -w 2 -t 120 -b 0.0.0.0:${PORT:-5000} main:app
