#!/bin/bash
set -e
PROJECT_ID=project-4e3f1563-833a-4721-bf7
REGION=asia-south1

echo "Building and pushing order image..."
docker buildx build --platform linux/amd64 -t asia-south1-docker.pkg.dev/$PROJECT_ID/syntrix-cloudmart/order:1.0.2 --build-arg SERVICE_NAME=services/order --push .

echo "Building and pushing payment image..."
docker buildx build --platform linux/amd64 -t asia-south1-docker.pkg.dev/$PROJECT_ID/syntrix-cloudmart/payment:1.0.2 --build-arg SERVICE_NAME=services/payment --push .

echo "Checking if GKE cluster exists..."
if ! gcloud container clusters describe syntrix-gke --region=$REGION --project=$PROJECT_ID -q >/dev/null 2>&1; then
  echo "Cluster syntrix-gke not found or not ready yet. Please ensure setup_gke_cluster.sh completes."
  exit 1
fi

echo "Getting credentials for GKE..."
gcloud container clusters get-credentials syntrix-gke --region=$REGION --project=$PROJECT_ID

INSTANCE_NAME=syntrix-postgres
SQL_INSTANCE="${PROJECT_ID}:${REGION}:${INSTANCE_NAME}"
DB_URL="postgresql://cloudmart_user:syntrix_admin_123@34.14.131.84:5432/cloudmart"

echo "Creating Kubernetes secret for database URL..."
kubectl create secret generic db-secret --from-literal=DATABASE_URL="$DB_URL" --dry-run=client -o yaml | kubectl apply -f -

echo "Applying Kubernetes manifests..."
cat << 'K8S' | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: order
  template:
    metadata:
      labels:
        app: order
    spec:
      containers:
      - name: order
        image: asia-south1-docker.pkg.dev/project-4e3f1563-833a-4721-bf7/syntrix-cloudmart/order:1.0.2
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: DATABASE_URL
      imagePullSecrets:
      - name: gcr-json-key
---
apiVersion: v1
kind: Service
metadata:
  name: order-service
  annotations:
    networking.gke.io/load-balancer-type: "Internal"
spec:
  type: LoadBalancer
  ports:
  - port: 8000
    targetPort: 8080
  selector:
    app: order
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: payment
  template:
    metadata:
      labels:
        app: payment
    spec:
      containers:
      - name: payment
        image: asia-south1-docker.pkg.dev/project-4e3f1563-833a-4721-bf7/syntrix-cloudmart/payment:1.0.2
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: DATABASE_URL
      imagePullSecrets:
      - name: gcr-json-key
---
apiVersion: v1
kind: Service
metadata:
  name: payment-service
  annotations:
    networking.gke.io/load-balancer-type: "Internal"
spec:
  type: LoadBalancer
  ports:
  - port: 8000
    targetPort: 8080
  selector:
    app: payment
K8S

echo "GKE Deployment Initiated."
