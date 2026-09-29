#!/bin/bash
set -e

PROJECT_ID="project-4e3f1563-833a-4721-bf7"
DATASET="syntrix_logs"

echo "============================================"
echo "  SYNTRIX — Setting Up Live Log Pipeline"
echo "============================================"
echo ""
echo "This script creates a Log Router Sink that"
echo "automatically streams Cloud Logging → BigQuery"
echo "in real-time. No polling scripts needed."
echo ""

# ─────────────────────────────────────────────────
# STEP 1: Create the Log Router Sink
# ─────────────────────────────────────────────────
echo "Step 1: Creating Log Router Sink..."

# This sink captures ALL logs from Cloud Run, GKE, and GCE
# and routes them directly to our BigQuery dataset.
# Tables are auto-created per log source (e.g., run_googleapis_com_stdout)
gcloud logging sinks create syntrix-live-sink \
  "bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/${DATASET}" \
  --log-filter='resource.type=("cloud_run_revision" OR "gce_instance" OR "k8s_container")' \
  --use-partitioned-tables \
  --project=${PROJECT_ID} \
  2>/dev/null || echo "Sink already exists, updating..."

# If sink already exists, update it
gcloud logging sinks update syntrix-live-sink \
  "bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/${DATASET}" \
  --log-filter='resource.type=("cloud_run_revision" OR "gce_instance" OR "k8s_container")' \
  --use-partitioned-tables \
  --project=${PROJECT_ID} \
  2>/dev/null || true

echo "✅ Sink created/updated."

# ─────────────────────────────────────────────────
# STEP 2: Grant the sink's service account write access to BigQuery
# ─────────────────────────────────────────────────
echo ""
echo "Step 2: Granting BigQuery write permissions to sink..."

WRITER_IDENTITY=$(gcloud logging sinks describe syntrix-live-sink \
  --project=${PROJECT_ID} \
  --format='value(writerIdentity)')

echo "Sink writer identity: $WRITER_IDENTITY"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="${WRITER_IDENTITY}" \
  --role="roles/bigquery.dataEditor" \
  --quiet > /dev/null 2>&1

echo "✅ Permissions granted."

# ─────────────────────────────────────────────────
# STEP 3: Generate some traffic so the sink creates tables
# ─────────────────────────────────────────────────
echo ""
echo "Step 3: Generating traffic to trigger table creation..."

GATEWAY_URL="https://syntrix-gateway-541833001986.asia-south1.run.app"
for i in {1..5}; do
  curl -s "$GATEWAY_URL/api/products" > /dev/null 2>&1 || true
  curl -s "$GATEWAY_URL/api/cart/1" > /dev/null 2>&1 || true
  curl -s "$GATEWAY_URL/health" > /dev/null 2>&1 || true
done

echo "✅ Traffic sent. Waiting 30 seconds for logs to flow through..."
sleep 30

# ─────────────────────────────────────────────────
# STEP 4: Check which tables the sink created
# ─────────────────────────────────────────────────
echo ""
echo "Step 4: Checking created tables..."

TABLES=$(bq ls --format=json ${PROJECT_ID}:${DATASET} 2>/dev/null | python3 -c "
import json, sys
data = json.load(sys.stdin)
for t in data:
    tid = t.get('tableReference', {}).get('tableId', '')
    if tid != 'raw_logs' and not tid.startswith('looker_'):
        print(tid)
" 2>/dev/null || echo "")

echo "Sink tables found:"
echo "$TABLES"

# ─────────────────────────────────────────────────
# STEP 5: Update the base view to read from BOTH
#         old raw_logs AND new sink tables
# ─────────────────────────────────────────────────
echo ""
echo "Step 5: Updating BigQuery views for live data..."

# Build UNION query for all sink tables
# We read from the OLD raw_logs (historical data) AND new sink tables (live data)
bq query --use_legacy_sql=false --project_id=${PROJECT_ID} "
CREATE OR REPLACE VIEW \`${PROJECT_ID}.${DATASET}.looker_cleaned_logs\` AS

-- === LIVE DATA from Log Router Sink (Cloud Run) ===
SELECT
  timestamp,
  IFNULL(severity, 'WARNING') AS severity,
  resource.type AS compute_environment,
  CASE
    WHEN resource.type = 'cloud_run_revision' THEN resource.labels.service_name
    ELSE 'unknown'
  END AS service_name,
  JSON_VALUE(TO_JSON_STRING(jsonPayload), '$.endpoint') AS endpoint,
  JSON_VALUE(TO_JSON_STRING(jsonPayload), '$.method') AS method,
  SAFE_CAST(JSON_VALUE(TO_JSON_STRING(jsonPayload), '$.status_code') AS INT64) AS status_code,
  SAFE_CAST(JSON_VALUE(TO_JSON_STRING(jsonPayload), '$.latency_ms') AS INT64) AS latency_ms,
  JSON_VALUE(TO_JSON_STRING(jsonPayload), '$.event') AS event_type,
  JSON_VALUE(TO_JSON_STRING(jsonPayload), '$.error') AS error_message
FROM \`${PROJECT_ID}.${DATASET}.run_googleapis_com_stderr\`
WHERE JSON_VALUE(TO_JSON_STRING(jsonPayload), '$.event') IS NOT NULL
   OR JSON_VALUE(TO_JSON_STRING(jsonPayload), '$.latency_ms') IS NOT NULL

UNION ALL

-- === LIVE DATA from Log Router Sink (GKE) ===
SELECT
  timestamp,
  IFNULL(severity, 'WARNING') AS severity,
  resource.type AS compute_environment,
  CASE
    WHEN resource.type = 'k8s_container' THEN resource.labels.container_name
    ELSE 'unknown'
  END AS service_name,
  JSON_VALUE(TO_JSON_STRING(jsonPayload), '$.endpoint') AS endpoint,
  JSON_VALUE(TO_JSON_STRING(jsonPayload), '$.method') AS method,
  SAFE_CAST(JSON_VALUE(TO_JSON_STRING(jsonPayload), '$.status_code') AS INT64) AS status_code,
  SAFE_CAST(JSON_VALUE(TO_JSON_STRING(jsonPayload), '$.latency_ms') AS INT64) AS latency_ms,
  JSON_VALUE(TO_JSON_STRING(jsonPayload), '$.event') AS event_type,
  JSON_VALUE(TO_JSON_STRING(jsonPayload), '$.error') AS error_message
FROM \`${PROJECT_ID}.${DATASET}.stderr\`
WHERE JSON_VALUE(TO_JSON_STRING(jsonPayload), '$.event') IS NOT NULL
   OR JSON_VALUE(TO_JSON_STRING(jsonPayload), '$.latency_ms') IS NOT NULL

UNION ALL

-- === HISTORICAL DATA from manual export (keeps old data) ===
SELECT
  timestamp,
  IFNULL(severity, 'WARNING') AS severity,
  JSON_EXTRACT_SCALAR(resource, '$.type') AS compute_environment,
  CASE
    WHEN JSON_EXTRACT_SCALAR(resource, '$.type') = 'cloud_run_revision' THEN JSON_EXTRACT_SCALAR(resource, '$.labels.service_name')
    WHEN JSON_EXTRACT_SCALAR(resource, '$.type') = 'k8s_container' THEN JSON_EXTRACT_SCALAR(resource, '$.labels.container_name')
    WHEN JSON_EXTRACT_SCALAR(resource, '$.type') = 'gce_instance' THEN 'inventory-service'
    ELSE 'unknown'
  END AS service_name,
  JSON_EXTRACT_SCALAR(jsonPayload, '$.endpoint') AS endpoint,
  JSON_EXTRACT_SCALAR(jsonPayload, '$.method') AS method,
  CAST(JSON_EXTRACT_SCALAR(jsonPayload, '$.status_code') AS INT64) AS status_code,
  CAST(JSON_EXTRACT_SCALAR(jsonPayload, '$.latency_ms') AS INT64) AS latency_ms,
  JSON_EXTRACT_SCALAR(jsonPayload, '$.event') AS event_type,
  JSON_EXTRACT_SCALAR(jsonPayload, '$.error') AS error_message
FROM \`${PROJECT_ID}.${DATASET}.raw_logs\`
WHERE JSON_EXTRACT_SCALAR(jsonPayload, '$.event') IS NOT NULL
   OR JSON_EXTRACT_SCALAR(jsonPayload, '$.latency_ms') IS NOT NULL
;
"

echo "✅ Base view updated (reads LIVE sink tables + historical raw_logs)."

# The 5 downstream views DON'T need any changes — they all reference
# looker_cleaned_logs, which now includes live data automatically.

echo ""
echo "============================================"
echo "  ✅ LIVE PIPELINE SETUP COMPLETE"
echo "============================================"
echo ""
echo "What just happened:"
echo "  1. Created a Log Router Sink in Cloud Logging"
echo "  2. Logs now flow: Cloud Run/GKE/GCE → Cloud Logging → BigQuery (automatic)"
echo "  3. Updated the base BigQuery view to read from live sink tables"
echo "  4. All 5 downstream views auto-inherit live data"
echo ""
echo "IMPORTANT — Final step in Looker Studio:"
echo "  1. Open your Looker Studio dashboard"
echo "  2. Click 'Resource' → 'Manage added data sources'"
echo "  3. For EACH data source, click 'Edit' → 'Edit connection'"
echo "  4. Set 'Data freshness' to '1 minute'"
echo "  5. Click 'Reconnect' to pick up the new view schema"
echo ""
echo "Your dashboard will now update within ~1-2 minutes of any"
echo "action on the CloudMart website."
echo ""
