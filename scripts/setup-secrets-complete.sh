#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

#Load environment from .env file
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
fi

# Adjust service names for K3s (postgres -> postgresql, redis -> redis-master)
DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgresql:5432/${POSTGRES_DB}"
REDIS_URL="redis://redis-master:6379/0"

kubectl create namespace videogen --dry-run=client -o yaml | kubectl apply -f -

kubectl -n videogen delete secret videogen-secrets --ignore-not-found
kubectl -n videogen create secret generic videogen-secrets \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=REDIS_URL="$REDIS_URL"

kubectl -n videogen delete secret videogen-pg-auth --ignore-not-found
kubectl -n videogen create secret generic videogen-pg-auth \
  --from-literal=postgres-password="$POSTGRES_PASSWORD" \
  --from-literal=password="$POSTGRES_PASSWORD"

echo "Secrets created successfully"