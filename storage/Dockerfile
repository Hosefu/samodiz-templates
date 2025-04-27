FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including libmagic
RUN apt-get update && \
    apt-get install -y \
    curl \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONUNBUFFERED=1

# media/static будут на volume'ах
