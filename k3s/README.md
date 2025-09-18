## K3s Deployment

Lightweight Kubernetes deployment with GPU worker.

### Prereqs
- K3s on the node with external IP
- NVIDIA drivers + NVIDIA Container Toolkit
- `.env` in repo root (DB and Redis creds)

### Quick deploy
```
./scripts/deploy-all.sh
```

What it does:
- Installs K3s and GPU runtime
- Builds `videogen:latest` and imports to K3s
- Applies ConfigMap, PVC, Postgres, Redis, API, Worker, Services

### Components
- `api-deployment.yaml`: FastAPI (replicas=3), mounts `/app/output`
- `worker-deployment.yaml`: Celery worker with `runtimeClassName: nvidia`
- `postgres.yaml`: Postgres + PVC
- `redis.yaml`: Redis + Service `redis-master`
- `api-service.yaml`: ClusterIP and NodePort 30080
- `configmap.yaml`: non-secret env

### Orchestration details
- API Deployment:
  - Replicas: 3
  - Strategy: RollingUpdate (`maxSurge: 1`, `maxUnavailable: 0`)
  - Probes: readiness and liveness on `/health`
  - Graceful drain: `preStop: sleep 10`, `terminationGracePeriodSeconds: 30`
- Worker Deployment:
  - Replicas: 1
  - Strategy: Recreate (ensures single GPU consumer)
  - GPU: `runtimeClassName: nvidia`, `NVIDIA_VISIBLE_DEVICES=all`
  - Termination grace: 180s to let tasks finish

### Operate
```
kubectl -n videogen get pods
kubectl -n videogen logs deploy/videogen-api -f
kubectl -n videogen logs deploy/videogen-worker -f
kubectl -n videogen rollout restart deploy/videogen-api
kubectl -n videogen exec deploy/videogen-worker -- nvidia-smi
```

### Access API
```
#NodePort
EXTERNAL_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')
curl http://$EXTERNAL_IP:30080/health

#Port-forward (local dev)
kubectl -n videogen port-forward svc/videogen-api 8080:8000 &
curl http://localhost:8080/health
```

### Storage
- Output videos stored via PVC `videogen-output` mounted at `/app/output` in API and Worker.

### Env/Secrets
- Non-secrets: `k3s/configmap.yaml`
- Secrets: created by `scripts/setup-secrets-complete.sh` as `videogen-secrets` and `videogen-pg-auth`.

### Troubleshooting
```
kubectl -n videogen get events --sort-by=.lastTimestamp | tail -n 50
kubectl -n videogen describe pod <pod>
kubectl -n videogen logs <pod> -c api --previous
kubectl -n videogen get deploy,pods,svc,pvc
```

Common issues:
- CrashLoopBackOff API: check `DATABASE_URL` secret and DB readiness.
- Worker no GPU: verify `runtimeClassName: nvidia` and `nvidia-smi` works.
- No external access: ensure NodePort 30080 reachable on the node.


