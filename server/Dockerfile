# Use a Python lightweight runtime
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      curl \
      gcc \
      libffi-dev \
      libssl-dev \
      python3-dev \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install requirements
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app file
COPY . .

# Declare the port the app runs on
EXPOSE 5000

# Dockerfile‑level healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:5000/api/chat-check || exit 1 && \
    curl -f http://localhost:5000/api/analytics-check || exit 1 && \
    curl -f http://localhost:5000/api/db-check || exit 1

# Use Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--workers", "4", "--timeout", "120"]