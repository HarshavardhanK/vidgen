#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

#Load environment from .env file
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
fi

echo "Installing K3s and GPU support"

cd "$SCRIPT_DIR"

sudo ./setup-k3s-complete.sh
sudo ./setup-gpu-complete.sh
./setup-secrets-complete.sh

echo "Building and deploying"
cd "$PROJECT_ROOT"

docker build -t videogen:latest .
docker save videogen:latest | sudo k3s ctr images import -

kubectl apply -f k3s/configmap.yaml
kubectl apply -f k3s/pvc.yaml
kubectl apply -f k3s/postgres.yaml
kubectl apply -f k3s/redis.yaml

sleep 20 #sleep to apply changes

kubectl apply -f k3s/api-deployment.yaml
kubectl apply -f k3s/worker-deployment.yaml
kubectl apply -f k3s/api-service.yaml

echo "Waiting for deployments"
kubectl -n videogen rollout status deploy/videogen-api --timeout=180s
kubectl -n videogen rollout status deploy/videogen-worker --timeout=300s

echo "Testing GPU access -"
kubectl exec -n videogen deployment/videogen-worker -- nvidia-smi --query-gpu=name --format=csv,noheader

EXTERNAL_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')

echo
echo "Deployment complete"
echo "API: kubectl port-forward -n videogen svc/videogen-api 8080:8000"
echo "External: http://${EXTERNAL_IP}:30080"
