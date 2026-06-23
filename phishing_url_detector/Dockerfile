# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PRODUCTION=true

# Install system dependencies (NO Chrome — disabled in production)
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies first (layer cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose the API port (Render overrides with $PORT env var)
EXPOSE 5000

# Run gunicorn — use $PORT so Render can inject the correct port
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 300 --preload app:app
