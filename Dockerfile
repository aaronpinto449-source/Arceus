# Multi-stage build for ARES Mars Mission Control
# Stage 1: Svelte Frontend Builder
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend-svelte
RUN npm install -g pnpm
COPY frontend-svelte/package.json frontend-svelte/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend-svelte ./
RUN pnpm build

# Stage 2: Production Python Runtime
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8001 \
    HOST=0.0.0.0

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY data ./data
COPY --from=frontend-builder /app/frontend-svelte/dist ./frontend-svelte/dist

EXPOSE 8001

CMD ["sh", "-c", "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8001}"]
