## Monitoring

Simple JSON metrics and Celery Flower.

### API Metrics
```
GET /metrics
```
Returns JSON with keys like:
- `system.api_requests_total`
- `video_generation.total`, `video_generation.failed`
- `workers.active`, `queue_length`
- `gpu.gpu_available`

Use curl or a lightweight scraper. No Prometheus format.

### Celery Flower
- Docker Compose: exposed at `http://localhost:5555` (service `celery-flower`).
- Auth via `FLOWER_BASIC_AUTH` in `.env`.
- Inspect workers, tasks, queues.
- Not deployed in K3s manifests by default.

### Logs
- File: `/app/logs/app.log`
- Stdout: `docker compose logs -f videogen` or `celery-worker`
- K3s: `kubectl -n videogen logs deploy/videogen-api -f`


