## videogen - Video Generation Pipeline

Generate videos via FastAPI + Celery on NVIDIA H100.

### Directory structure
- `api/` FastAPI service (see `api/README.md`)
- `vid/` model pipelines (see `vid/README.md`)
- `k3s/` K3s manifests (see `k3s/README.md`)
- `scripts/` ops scripts (see `scripts/README.md`)
- `setup/` host setup scripts (see `setup/README.md`)
- `MONITORING.md` metrics and Flower

### Architecture
- FastAPI API (submit jobs, query status, list completed videos)
- Celery worker with Redis broker
- PostgreSQL for job metadata and results
- CogVideoX-2B model running on H100 GPU for text-to-video generation

### System design (K3s orchestration)
- Single image `videogen:latest` runs API and Worker (separate deployments)
- API: `replicas: 3`, RollingUpdate (maxSurge=1, maxUnavailable=0), readiness/liveness on `/health`
- Worker: `replicas: 1`, Recreate strategy, `runtimeClassName: nvidia` for GPU
- Shared PVC `videogen-output` mounted at `/app/output`
- Config via ConfigMap; secrets via `videogen-secrets` and `videogen-pg-auth`
- Services: ClusterIP for internal, NodePort 30080 for external API access

### Prerequisites
- Docker and Docker Compose
- NVIDIA GPU drivers (for actual generation)

### Setup
1) Create environment file
```bash
cp .env.example .env
# edit values (passwords, URLs)
```

2) Start services (Docker Compose)
```bash
docker compose up -d --build
```

For Kubernetes (K3s) deployment, see `k3s/README.md` for full cluster setup and rollout.

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

### Configuration Management
- Centralized config in `api/config.py` with environment-specific settings
- Configuration validation on startup
- Environment variables with sensible defaults
- No secrets hard-coded in source code

### Fresh deployments
- Clean volume is created for Postgres
- DB init job applies tables, indexes, and functions

### More docs
- API usage: `api/README.md`
- Kubernetes: `k3s/README.md`
- Video pipeline: `vid/README.md`
- Monitoring: `MONITORING.md`
