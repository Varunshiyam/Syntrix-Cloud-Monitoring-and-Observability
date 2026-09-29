#!/bin/bash
set -e

PROJECT_ID="project-4e3f1563-833a-4721-bf7"
BUCKET="gs://$PROJECT_ID-logs-bucket"
DATASET="syntrix_logs"
TABLE="raw_logs"

echo "Extracting logs..."
# Using --limit=1000 for demonstration purposes in the hackathon
gcloud logging read 'resource.type=("cloud_run_revision" OR "gce_instance" OR "k8s_container")' --project=$PROJECT_ID --format=json --limit=1000 > raw_logs.json

echo "Converting to NDJSON and stringifying complex objects..."
python3 prepare_bq_json.py raw_logs.json raw_logs.ndjson

echo "Uploading to GCS..."
gsutil cp raw_logs.ndjson $BUCKET/raw_logs.ndjson

echo "Loading into BigQuery..."
bq load --autodetect --source_format=NEWLINE_DELIMITED_JSON --replace $PROJECT_ID:$DATASET.$TABLE $BUCKET/raw_logs.ndjson

echo "Log extraction and BigQuery load complete."
