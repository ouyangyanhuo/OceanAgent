# ---- Frontend Dockerfile ----
# Ocean Agent Intelligence Platform — Vue 3 frontend
#
# Multi-stage build:
#   1. Build stage  — Bun installs deps + Vite builds static assets
#   2. Serve stage  — Nginx serves the built assets + reverse-proxies /api to backend

# ---------- Stage 1: Build ----------
FROM oven/bun:1.1-alpine AS build

WORKDIR /app

# Install dependencies first (cache-friendly layer)
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

# Copy source and build
COPY . .
RUN bun run build

# ---------- Stage 2: Serve ----------
FROM nginx:1.27-alpine AS production

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Nginx config: serve static files + reverse-proxy /api and /health to backend
COPY --from=build /app/dist /usr/share/nginx/html

RUN cat > /etc/nginx/conf.d/default.conf <<'NGINX'
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # API_TARGET is resolved at container start via envsubst
    # Default to host.docker.internal for Docker Desktop / Linux
    set $api_target "${API_TARGET}";

    location /api/ {
        proxy_pass $api_target;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass $api_target;
        proxy_set_header Host $host;
    }

    # SPA fallback — serve index.html for unknown routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets aggressively
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
NGINX

# envsubst template at startup so API_TARGET is configurable at runtime
ENV API_TARGET="http://host.docker.internal:8000"

EXPOSE 80

# Use envsubst to bake API_TARGET into the nginx config at container start
CMD ["/bin/sh", "-c", "envsubst '${API_TARGET}' < /etc/nginx/conf.d/default.conf > /tmp/default.conf && mv /tmp/default.conf /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
