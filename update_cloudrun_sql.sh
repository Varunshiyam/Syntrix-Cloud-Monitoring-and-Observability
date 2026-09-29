#!/bin/bash
set -e
PROJECT_ID=project-4e3f1563-833a-4721-bf7
REGION=asia-south1
INSTANCE_NAME=syntrix-postgres
SQL_INSTANCE="${PROJECT_ID}:${REGION}:${INSTANCE_NAME}"
DB_URL="postgresql://cloudmart_user:syntrix_admin_123@/cloudmart?host=/cloudsql/${SQL_INSTANCE}"

echo "Updating catalog..."
gcloud run services update syntrix-catalog \
  --region=$REGION --project=$PROJECT_ID \
  --add-cloudsql-instances=$SQL_INSTANCE \
  --update-env-vars="DATABASE_URL=$DB_URL"

echo "Updating cart..."
gcloud run services update syntrix-cart \
  --region=$REGION --project=$PROJECT_ID \
  --add-cloudsql-instances=$SQL_INSTANCE \
  --update-env-vars="DATABASE_URL=$DB_URL"

echo "Updating gateway..."
gcloud run services update syntrix-gateway \
  --region=$REGION --project=$PROJECT_ID \
  --add-cloudsql-instances=$SQL_INSTANCE \
  --update-env-vars="DATABASE_URL=$DB_URL,INVENTORY_URL=http://10.160.0.6:8000,ORDER_URL=http://10.160.0.5:8000,PAYMENT_URL=http://10.160.0.7:8000,CATALOG_URL=https://syntrix-catalog-541833001986.asia-south1.run.app,CART_URL=https://syntrix-cart-541833001986.asia-south1.run.app" \
  --vpc-egress=all-traffic \
  --network=default
