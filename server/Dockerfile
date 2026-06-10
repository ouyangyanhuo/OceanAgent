# ---- Backend Dockerfile ----
# Ocean Agent Intelligence Platform — FastAPI backend

FROM python:3.12-slim AS base

WORKDIR /app

# System deps (none needed for this minimal stack, but keep the layer for future)
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first (cache-friendly layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ app/

# Ensure data directories exist at build time
# (startup event also creates them, but having them in the image avoids mount surprises)
RUN mkdir -p app/data/graph app/data/cache app/data/prompts app/data/mock app/data/snapshots

# Non-root user for production
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Default env — override at runtime via -e or .env file
ENV APP_NAME="Ocean KG Agent" \
    APP_ENV=production \
    CORS_ORIGINS="*" \
    LLM_PROVIDER=mock

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
