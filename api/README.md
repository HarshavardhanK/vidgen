## API

FastAPI service for submitting video generation jobs and querying results.

### Base URL
- Local: `http://localhost:8000`
- K3s NodePort: `http://EXTERNAL_IP:30080`

### Health
```
GET /health
200 -> { status, services, workers, gpu }
```

### Metrics (basic JSON)
```
GET /metrics
```

### Submit generation job
```
POST /api/v1/generate
Content-Type: application/json
Body: {
  "user_id": "alice",
  "prompt": "A cat dancing",
  "fps": 24
}
201 -> { success, job_id, message }
```

Required fields: `user_id`, `prompt`. Optional: `fps` (1..60) and advanced fields per `schemas.py`.

### Check job status
```
GET /api/v1/job/{job_id}
200 -> { job_id, status, message, result }
```

`status` is one of `pending | running | completed | failed`. When completed, `result` is the output path.

### List completed videos
```
GET /api/v1/videos
200 -> { videos: [ { job_id, user_id, filename, file_size, created_at, status } ] }
```

Optional query: `user_id` to filter.

### Errors
- 400: bad input (empty `user_id`/`prompt`, invalid `job_id`)
- 404: job not found
- 422: validation errors (standardized JSON in `main.py`)

### Environment
See `api/config.py`. Required: `DATABASE_URL`. Common: `REDIS_URL`, `ENVIRONMENT`, `LOG_LEVEL`.

### Local run
```
uvicorn api.main:app --reload --port 8000
```


