# Use Python 3.11 slim image for lightweight container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# - ca-certificates: required for TLS/SSL (e.g., Gmail SMTP)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create necessary directories for uploads and receipts
RUN mkdir -p /app/Kloudpython/static/uploads \
    && mkdir -p /app/Kloudpython/static/receipts

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=Kloudpython/app.py

# Expose port 5000 (Gunicorn will listen here)
EXPOSE 5000

# Run Gunicorn with Flask app factory
# Using 3 workers as specified, binding to 0.0.0.0:5000
# --timeout 120: allow longer requests for PDF generation
# --access-logfile -: log to stdout
# --error-logfile -: log errors to stderr
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "Kloudpython.app:app"]

