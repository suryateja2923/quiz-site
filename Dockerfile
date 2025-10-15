# ---- base image ----
FROM python:3.11-slim

# ---- envs for reliable Python behavior ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/home/appuser/.local/bin:${PATH}" \
    FLASK_ENV=production

# ---- system deps (just enough for pandas wheels, fonts, tzdata) ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates tzdata \
 && rm -rf /var/lib/apt/lists/*

# ---- create user & dirs ----
WORKDIR /app
RUN useradd -m -u 10001 appuser \
 && mkdir -p /app/quiz_data /app/images \
 && chown -R appuser:appuser /app

# ---- python deps ----
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# ---- app code (copy last so code changes rebuild faster) ----
COPY --chown=appuser:appuser main.py /app/main.py
# (optional) if you want to bundle images inside the image, drop them into ./images before building:
# COPY --chown=appuser:appuser images/ /app/images/

# ---- runtime user ----
USER appuser

# ---- expose & run ----
EXPOSE 5000
# gunicorn: 2 workers, 8 threads each; tweak if needed
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "8", "--timeout", "120", "main:app"]
