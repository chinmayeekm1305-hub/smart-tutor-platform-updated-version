# ---------- 1. build the React frontend ----------
FROM node:22-alpine AS web
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# ---------- 2. Python API that also serves the built frontend ----------
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY --from=web /app/frontend/dist /app/frontend/dist
RUN useradd -m tutor && chown -R tutor /app
USER tutor
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/api/health')"
CMD ["./start.sh"]
