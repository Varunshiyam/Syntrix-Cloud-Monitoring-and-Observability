#!/bin/bash
set -e
PROJECT_ID=project-4e3f1563-833a-4721-bf7
REGION=asia-south1
INSTANCE_NAME=syntrix-postgres
DB_NAME=cloudmart
DB_USER=cloudmart_user
DB_PASS=$(openssl rand -hex 12)

echo "Checking if SQL instance exists..."
if ! gcloud sql instances describe $INSTANCE_NAME --project=$PROJECT_ID -q >/dev/null 2>&1; then
  echo "Creating Cloud SQL instance (this takes 5-10 minutes)..."
  gcloud sql instances create $INSTANCE_NAME \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=$REGION \
    --project=$PROJECT_ID \
    -q
else
  echo "Instance already exists."
fi

echo "Creating database..."
gcloud sql databases create $DB_NAME --instance=$INSTANCE_NAME --project=$PROJECT_ID -q || true

echo "Creating user..."
gcloud sql users create $DB_USER --instance=$INSTANCE_NAME --password=$DB_PASS --project=$PROJECT_ID -q || \
gcloud sql users set-password $DB_USER --instance=$INSTANCE_NAME --password=$DB_PASS --project=$PROJECT_ID -q

CONNECTION_NAME="$PROJECT_ID:$REGION:$INSTANCE_NAME"
DB_URL="postgresql://${DB_USER}:${DB_PASS}@/cloudmart?host=/cloudsql/${CONNECTION_NAME}"

echo "Creating secret..."
if ! gcloud secrets describe database-url --project=$PROJECT_ID -q >/dev/null 2>&1; then
  gcloud secrets create database-url --project=$PROJECT_ID --replication-policy="automatic" -q
fi
printf "%s" "$DB_URL" | gcloud secrets versions add database-url --data-file=- --project=$PROJECT_ID -q

echo "Creating Cloud Run service account..."
SA_NAME="cloudrun-app-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

if ! gcloud iam service-accounts describe $SA_EMAIL --project=$PROJECT_ID -q >/dev/null 2>&1; then
  gcloud iam service-accounts create $SA_NAME --display-name="Cloud Run App SA" --project=$PROJECT_ID -q
fi

echo "Granting permissions to SA..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudsql.client" -q >/dev/null

gcloud secrets add-iam-policy-binding database-url \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor" \
  --project=$PROJECT_ID -q >/dev/null

echo "Setup Complete!"
