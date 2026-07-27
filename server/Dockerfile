# syntax=docker/dockerfile:1

# Build context: repository root
# Build with:
#   docker build -f server/Dockerfile -t ocean-agent-backend .

FROM python:3.12-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_NAME="Ocean KG Agent" \
    APP_ENV=production \
    CORS_ORIGINS="*" \
    LLM_PROVIDER=mock

WORKDIR /app

# Install dependencies in a separate cache-friendly layer.
COPY server/requirements.txt ./
RUN python -m pip install -r requirements.txt

# Run the API as an unprivileged user. app/data remains writable because the
# application persists graph state, caches, snapshots and notifications there.
RUN adduser --system --group --no-create-home appuser
COPY --chown=appuser:appuser server/app ./app

USER appuser

EXPOSE 8000

# All mutable backend JSON/JSONL data lives here. Compose attaches a named
# volume to the same path so data survives container replacement.
VOLUME ["/app/app/data"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"]

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
