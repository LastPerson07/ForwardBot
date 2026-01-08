# Using Python 3.10 slim for better performance and smaller size
FROM python:3.10-slim-buster

# Install system dependencies required for tgcrypto and other C-based extensions
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
# Note: Ensure 'gunicorn' and 'gevent' are in your requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code (including plugins/ and database.py)
COPY . .

# Set execution permissions for the runner
RUN chmod +x run.sh

# Heroku doesn't use EXPOSE, it uses the $PORT env var automatically
CMD ["./run.sh"]
