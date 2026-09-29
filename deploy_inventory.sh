#!/bin/bash
set -e
PROJECT_ID=project-4e3f1563-833a-4721-bf7
REGION=asia-south1
ZONE=asia-south1-a

echo "Building and pushing inventory image..."
docker buildx build --platform linux/amd64 -t asia-south1-docker.pkg.dev/$PROJECT_ID/syntrix-cloudmart/inventory:1.0.0 --build-arg SERVICE_NAME=services/inventory --push .

echo "Checking if VM exists..."
if ! gcloud compute instances describe syntrix-inventory --zone=$ZONE --project=$PROJECT_ID -q >/dev/null 2>&1; then
  echo "Creating startup script..."
  cat << 'EOF' > startup.sh
#!/bin/bash
apt-get update
apt-get install -y docker.io

# Start container
docker run -d -p 8000:8000 \
  --name inventory-service \
  --restart always \
  -e DATABASE_URL="$(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/attributes/database-url" -H "Metadata-Flavor: Google")" \
  asia-south1-docker.pkg.dev/project-4e3f1563-833a-4721-bf7/syntrix-cloudmart/inventory:1.0.0
EOF

  INSTANCE_NAME=syntrix-postgres
  SQL_INSTANCE="${PROJECT_ID}:${ZONE%-*}:${INSTANCE_NAME}"
  DB_IP=$(gcloud sql instances describe syntrix-postgres --project=$PROJECT_ID --format="value(ipAddresses[0].ipAddress)")
  DB_URL="postgresql://cloudmart_user:syntrix_admin_123@${DB_IP}:5432/cloudmart"

  echo "Creating VM instance..."
  gcloud compute instances create syntrix-inventory \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --machine-type=e2-micro \
    --tags=http-server \
    --scopes=cloud-platform \
    --metadata-from-file=startup-script=startup.sh \
    --metadata=database-url="$DB_URL"
else
  echo "VM syntrix-inventory already exists."
fi

echo "Allowing internal traffic..."
gcloud compute firewall-rules create allow-inventory-internal \
  --project=$PROJECT_ID \
  --network=default \
  --allow=tcp:8080 \
  --source-ranges=10.0.0.0/8 \
  --target-tags=inventory-server -q || true

echo "Compute Engine Deployment Initiated."
