#!/bin/bash

set -e

if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found"
    exit 1
fi

BASE_URL="http://$EXTERNAL_IP:30080"
USER_ID="demo_user"

echo "videogen API Demo"
echo "=================="
echo "API: $BASE_URL"
echo "User: $USER_ID"
echo ""

echo "1. Checking API health..."
health=$(curl -s "$BASE_URL/health" | jq -r '.status')
if [ "$health" = "healthy" ]; then
    echo "API is healthy"
else
    echo "API health check failed"
    exit 1
fi
echo ""

echo "2. Submitting video generation job..."
job_response=$(curl -s -X POST "$BASE_URL/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"prompt\": \"A golden retriever playing in a sunny meadow\",
    \"fps\": 24
  }")

job_id=$(echo "$job_response" | jq -r '.job_id')
success=$(echo "$job_response" | jq -r '.success')

if [ "$success" = "true" ]; then
    echo "Job submitted successfully"
    echo "Job ID: $job_id"
else
    echo "Job submission failed"
    exit 1
fi
echo ""

echo "3. Monitoring job progress..."
while true; do
    status_response=$(curl -s "$BASE_URL/api/v1/job/$job_id")
    status=$(echo "$status_response" | jq -r '.status')
    
    case $status in
        "pending")
            echo "Status: Pending..."
            ;;
        "running")
            echo "Status: Generating video..."
            ;;
        "completed")
            echo "Video generation completed"
            output_file=$(echo "$status_response" | jq -r '.result')
            echo "Output: $output_file"
            break
            ;;
        "failed")
            echo "Video generation failed"
            exit 1
            ;;
    esac
    
    sleep 5
done
echo ""

echo "4. Downloading generated video..."
download_file="demo_video_$(date +%s).mp4"
curl -s -o "$download_file" "$BASE_URL/api/v1/download/$job_id?user_id=$USER_ID"

if [ -f "$download_file" ] && [ -s "$download_file" ]; then
    file_size=$(stat -c%s "$download_file")
    file_size_mb=$(echo "scale=2; $file_size / 1024 / 1024" | bc)
    echo "Video downloaded successfully"
    echo "File: $download_file"
    echo "Size: ${file_size_mb} MB"
else
    echo "Video download failed"
    exit 1
fi
echo ""

echo "5. Listing user's completed videos..."
videos_response=$(curl -s "$BASE_URL/api/v1/videos?user_id=$USER_ID")
video_count=$(echo "$videos_response" | jq '.videos | length')
echo "User has $video_count completed videos"
echo ""

echo "Demo completed successfully"
echo "Generated video: $download_file"
