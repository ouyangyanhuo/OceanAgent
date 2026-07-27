# syntax=docker/dockerfile:1

# Build context: repository root
#   docker build -f client/Dockerfile -t ocean-agent-frontend .

# ---------- Build ----------
FROM oven/bun:1.3.14-alpine AS build

WORKDIR /app

COPY client/package.json client/bun.lock ./
RUN bun install --frozen-lockfile

COPY client/index.html client/vite.config.js ./
COPY client/src ./src

RUN bun run build

# ---------- Runtime ----------
FROM oven/bun:1.3.14-alpine AS production

WORKDIR /app

COPY --from=build --chown=bun:bun /app/dist ./dist
COPY --chown=bun:bun client/package.json client/server.js ./

ENV HOST=0.0.0.0 \
    PORT=5173 \
    API_TARGET=http://backend:8000

USER bun

EXPOSE 5173

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["bun", "-e", "fetch('http://127.0.0.1:5173/').then(r => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"]

CMD ["bun", "run", "start"]
