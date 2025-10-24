FROM python:3.11-slim

WORKDIR /app

# Install sqlite3 system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-dev \
    gcc \
    make \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

EXPOSE 8000

# Set environment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Debug version - shows more detailed errors
CMD ["gunicorn", "--preload", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker","--timeout", "24000","--bind", "0.0.0.0:${PORT:-8000}", "--log-level", "debug", "main:app"]




