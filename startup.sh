#!/bin/bash
apt-get update
apt-get install -y docker.io

# Start container
docker run -d -p 8000:8000 \
  --name inventory-service \
  --restart always \
  -e DATABASE_URL="$(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/attributes/database-url" -H "Metadata-Flavor: Google")" \
  asia-south1-docker.pkg.dev/project-4e3f1563-833a-4721-bf7/syntrix-cloudmart/inventory:1.0.0
