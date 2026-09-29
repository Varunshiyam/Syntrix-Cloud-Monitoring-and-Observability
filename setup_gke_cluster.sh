#!/bin/bash
set -e
PROJECT_ID=project-4e3f1563-833a-4721-bf7
REGION=asia-south1

echo "Building and pushing order image..."
docker buildx build --platform linux/amd64 -t asia-south1-docker.pkg.dev/$PROJECT_ID/syntrix-cloudmart/order:1.0.1 --build-arg SERVICE_NAME=services/order --push .

echo "Building and pushing payment image..."
docker buildx build --platform linux/amd64 -t asia-south1-docker.pkg.dev/$PROJECT_ID/syntrix-cloudmart/payment:1.0.1 --build-arg SERVICE_NAME=services/payment --push .

echo "Checking if GKE cluster exists..."
if ! gcloud container clusters describe syntrix-gke --region=$REGION --project=$PROJECT_ID -q >/dev/null 2>&1; then
  echo "Creating GKE Autopilot cluster (this takes 5-10 minutes)..."
  gcloud container clusters create-auto syntrix-gke \
    --region=$REGION \
    --project=$PROJECT_ID \
    -q
else
  echo "GKE cluster syntrix-gke already exists."
fi

echo "GKE Cluster Provisioning Initiated/Completed."
