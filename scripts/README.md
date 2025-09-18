# K3s Deployment Scripts

Simple deployment for videogen on K3s with GPU support.

## Quick Deploy

```bash
./deploy-all.sh
```

Installs K3s, configures GPU support, builds the app, and deploys everything.

**Note**: Uses configuration from `.env` file.

## Test the System

```bash
./demo-k3s.sh
```

Submits a video generation job and monitors progress.

## API Access Methods

### External Access (NodePort)
```bash
#Get the external IP

EXTERNAL_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')

#Access API directly from anywhere

curl http://$EXTERNAL_IP:30080/health
curl -X POST http://$EXTERNAL_IP:30080/api/v1/generate -H 'Content-Type: application/json' -d '{"prompt":"A cat dancing"}'

#From your local browser/machine
# Visit: http://EXTERNAL_IP:30080/health
```

### Local Development (Port-Forward)
```bash
#Forward to local port
kubectl port-forward -n videogen svc/videogen-api 8080:8000 &

#Access via localhost
curl http://localhost:8080/health
curl -X POST http://localhost:8080/api/v1/generate -H 'Content-Type: application/json' -d '{"prompt":"A cat dancing"}'
```

### Other Tests
```bash
#Test GPU in worker
kubectl exec -n videogen deployment/videogen-worker -- nvidia-smi

#Check metrics
curl http://$EXTERNAL_IP:30080/metrics
```

## Architecture

- **K3s** with containerd runtime (lightweight)
- **NVIDIA Container Toolkit** for GPU access
- **Worker Pod** with `runtimeClassName: nvidia`
- **API Pod** for HTTP endpoints
- **PostgreSQL** and **Redis** for data/queue for Celery

## GPU Setup

Uses K3s NVIDIA runtime:
```yaml
spec:
  runtimeClassName: nvidia
  env:
  - name: NVIDIA_VISIBLE_DEVICES
    value: "all"
```

## Troubleshooting

```bash
#Check pods
kubectl get pods -n videogen

#Check logs  
kubectl logs -n videogen -l app=videogen-worker

#Access API
kubectl port-forward -n videogen svc/videogen-api 8080:8000
```
