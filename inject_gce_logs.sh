#!/bin/bash
for i in {1..5}; do
  gcloud logging write inventory-access-log "{\"service_name\": \"inventory\", \"endpoint\": \"/api/inventory/reserve\", \"latency_ms\": $((10 + RANDOM % 30)), \"status_code\": 200, \"trace_id\": \"mock-$RANDOM\"}" \
    --payload-type=json \
    --monitored-resource-type=gce_instance \
    --monitored-resource-labels=instance_id=12345,zone=asia-south1-a \
    --project=project-4e3f1563-833a-4721-bf7
done
