#!/usr/bin/env bash
set -euo pipefail

echo "Starting port-forward"
kubectl port-forward -n videogen svc/videogen-api 8080:8000 &
PF_PID=$!
sleep 5

echo "Submitting video job"
JOB_ID=$(curl -s -X POST http://localhost:8080/api/v1/generate -H 'Content-Type: application/json' -d '{"prompt":"A cat dancing","fps":8}' | jq -r .job_id)

echo "Job ID: $JOB_ID"
echo "Monitoring"

for i in {1..5}; do

  STATUS=$(curl -s "http://localhost:8080/api/v1/job/$JOB_ID" | jq -r .status)
  echo "[$i/5] $STATUS"

  [[ "$STATUS" == "completed" || "$STATUS" == "failed" ]] && break
  sleep 5

done

echo "Final: $STATUS"
kill $PF_PID 2>/dev/null || true


