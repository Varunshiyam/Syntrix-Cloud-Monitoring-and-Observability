#!/bin/bash
set -e

echo "Configuring docker auth..."
gcloud auth configure-docker asia-south1-docker.pkg.dev --quiet

echo "Building cart image..."
docker buildx build --platform linux/amd64 -t asia-south1-docker.pkg.dev/project-4e3f1563-833a-4721-bf7/syntrix-cloudmart/cart:1.0.0 --build-arg SERVICE_NAME=services/cart --push .

echo "Deploying syntrix-cart..."
CART_URL=$(gcloud run deploy syntrix-cart \
  --project=project-4e3f1563-833a-4721-bf7 \
  --region=asia-south1 \
  --image=asia-south1-docker.pkg.dev/project-4e3f1563-833a-4721-bf7/syntrix-cloudmart/cart:1.0.0 \
  --allow-unauthenticated \
  --set-env-vars="SERVICE_NAME=cart-service,LOG_LEVEL=INFO,ENVIRONMENT=cloud,DATABASE_URL=postgresql://postgres:postgres@postgres:5432/cloudmart" \
  --format="value(status.url)")
echo "Cart URL: $CART_URL"

echo "Building gateway image..."
docker buildx build --platform linux/amd64 -t asia-south1-docker.pkg.dev/project-4e3f1563-833a-4721-bf7/syntrix-cloudmart/gateway:1.0.0 --build-arg SERVICE_NAME=gateway --push .

echo "Deploying syntrix-gateway..."
GATEWAY_URL=$(gcloud run deploy syntrix-gateway \
  --project=project-4e3f1563-833a-4721-bf7 \
  --region=asia-south1 \
  --image=asia-south1-docker.pkg.dev/project-4e3f1563-833a-4721-bf7/syntrix-cloudmart/gateway:1.0.0 \
  --allow-unauthenticated \
  --set-env-vars="SERVICE_NAME=gateway,LOG_LEVEL=INFO,ENVIRONMENT=cloud,CATALOG_URL=https://syntrix-catalog-541833001986.asia-south1.run.app,CART_URL=$CART_URL,ORDER_URL=http://order:8000,PAYMENT_URL=http://payment:8000,INVENTORY_URL=http://inventory:8000,DATABASE_URL=postgresql://postgres:postgres@postgres:5432/cloudmart" \
  --format="value(status.url)")
echo "Gateway URL: $GATEWAY_URL"

echo "Applying IAM permissions..."
gcloud run services add-iam-policy-binding syntrix-cart --region=asia-south1 --member=allUsers --role=roles/run.invoker --project=project-4e3f1563-833a-4721-bf7 >/dev/null 2>&1 || true
gcloud run services add-iam-policy-binding syntrix-gateway --region=asia-south1 --member=allUsers --role=roles/run.invoker --project=project-4e3f1563-833a-4721-bf7 >/dev/null 2>&1 || true

echo "Testing Cart Health..."
curl -s $CART_URL/health || true

echo -e "\nTesting Gateway Health..."
curl -s $GATEWAY_URL/health || true

