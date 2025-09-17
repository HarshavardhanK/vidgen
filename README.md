## videogen - Video Generation Pipeline

Generate videos via FastAPI + Celery on NVIDIA H100.

### Architecture
- FastAPI API (submit jobs, query status, list completed videos)
- Celery worker with Redis broker
- PostgreSQL for job metadata and results

### Prerequisites
- Docker and Docker Compose
- NVIDIA GPU drivers (for actual generation)

### Setup
1) Create environment file
```bash
cp .env.example .env
# edit values (passwords, URLs)
```

2) Start services
```bash
docker compose up -d --build
```

### Usage
- Health: `GET http://localhost:8000/health`
- Submit: `POST http://localhost:8000/api/v1/generate` (JSON: prompt, fps)
- Status: `GET http://localhost:8000/api/v1/job/{job_id}`
- Completed videos: `GET http://localhost:8000/api/v1/videos`
- Flower UI (optional): `http://localhost:5555`

### Logging
- View logs: `docker compose logs -f videogen` (API) or `docker compose logs -f celery-worker` (tasks)
- Portainer UI: `http://localhost:9000` → Containers → Logs
- Log files: `logs/app.log` (structured logging with rotation)

### Environment
Configure in `.env` (see `.env.example`). Typical variables:
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `DATABASE_URL`, `REDIS_URL`, `FLOWER_BASIC_AUTH`
- `ENVIRONMENT`, `LOG_LEVEL`

### Fresh deployments
- Clean volume is created for Postgres
- DB init job applies tables, indexes, and functions
