FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY src/ ./src
COPY scripts/ ./scripts

# Create data and reports folders inside container
RUN mkdir -p /app/data /app/reports

# Default command
CMD ["python", "-u", "src/collector.py"]