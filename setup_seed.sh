#!/bin/bash
set -e
PROJECT_ID=project-4e3f1563-833a-4721-bf7
REGION=asia-south1
INSTANCE_NAME=syntrix-postgres
SQL_INSTANCE="${PROJECT_ID}:${REGION}:${INSTANCE_NAME}"
DB_URL="postgresql://cloudmart_user:syntrix_admin_123@/cloudmart?host=/cloudsql/${SQL_INSTANCE}"

echo "Building and pushing seed image..."
docker buildx build --platform linux/amd64 -t asia-south1-docker.pkg.dev/$PROJECT_ID/syntrix-cloudmart/seed:1.0.0 -f Dockerfile.seed --push .

echo "Creating Cloud Run Job..."
gcloud run jobs create syntrix-seed \
  --project=$PROJECT_ID \
  --region=$REGION \
  --image=asia-south1-docker.pkg.dev/$PROJECT_ID/syntrix-cloudmart/seed:1.0.0 \
  --set-env-vars="DATABASE_URL=$DB_URL" \
  --vpc-egress=all-traffic \
  --network=default || gcloud run jobs update syntrix-seed \
  --project=$PROJECT_ID \
  --region=$REGION \
  --image=asia-south1-docker.pkg.dev/$PROJECT_ID/syntrix-cloudmart/seed:1.0.0 \
  --set-env-vars="DATABASE_URL=$DB_URL" \
  --vpc-egress=all-traffic \
  --network=default

echo "Executing Cloud Run Job..."
gcloud run jobs execute syntrix-seed --project=$PROJECT_ID --region=$REGION --wait
