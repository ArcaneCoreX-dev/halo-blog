FROM python:3.12-slim AS base

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (cache layer)
COPY pyproject.toml ./
RUN mkdir -p src && touch src/__init__.py && \
    pip install --no-cache-dir . && \
    rm -rf src

# Copy source
COPY src/ ./src/

# Runtime
ENV HALO_HOST=0.0.0.0
ENV HALO_PORT=8000
EXPOSE 8000

# Data volume
VOLUME ["/app/data", "/app/uploads"]

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
