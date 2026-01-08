# Use Bullseye instead of Buster to fix the 404 repository error
FROM python:3.10-slim-bullseye

# Install system dependencies
# These are needed for tgcrypto, motor, and git-based installs
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your ForwardBot code
COPY . .

# Set execution permissions
RUN chmod +x run.sh

# Start the process
CMD ["./run.sh"]
