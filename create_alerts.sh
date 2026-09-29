#!/bin/bash
PROJECT_ID="project-4e3f1563-833a-4721-bf7"

echo "Creating Notification Channels..."
BABU_CHANNEL=$(gcloud beta monitoring channels create --display-name="Babu Senthil (Cloud Run)" --type=email --channel-labels=email_address="bbabusenthil@gmail.com" --project=$PROJECT_ID --format="value(name)")
VARUN_CHANNEL=$(gcloud beta monitoring channels create --display-name="Varunshiyam (Looker Pipeline)" --type=email --channel-labels=email_address="varunshiyam.analyst@gmail.com" --project=$PROJECT_ID --format="value(name)")
AKASH_CHANNEL=$(gcloud beta monitoring channels create --display-name="Akash (GKE)" --type=email --channel-labels=email_address="akaashrk02@gmail.com" --project=$PROJECT_ID --format="value(name)")
ROSHNI_CHANNEL=$(gcloud beta monitoring channels create --display-name="Roshni (GCE)" --type=email --channel-labels=email_address="roshnigloriya@gmail.com" --project=$PROJECT_ID --format="value(name)")
SWATHI_CHANNEL=$(gcloud beta monitoring channels create --display-name="Swathi (GCE)" --type=email --channel-labels=email_address="swathi062005@gmail.com" --project=$PROJECT_ID --format="value(name)")
ECCLESIASTES_CHANNEL=$(gcloud beta monitoring channels create --display-name="Ecclesiastes (BigQuery)" --type=email --channel-labels=email_address="ecclesiastescherubin1@gmail.com" --project=$PROJECT_ID --format="value(name)")
EMAYAN_CHANNEL=$(gcloud beta monitoring channels create --display-name="Emayan (BigQuery)" --type=email --channel-labels=email_address="emayanvijayakumar17@gmail.com" --project=$PROJECT_ID --format="value(name)")

mkdir -p alerts

cat << JSON > alerts/cloud_run_policy.json
{
  "displayName": "Cloud Run 5xx Errors (Babu)",
  "combiner": "OR",
  "conditions": [
    {
      "displayName": "Cloud Run Revision - Request count",
      "conditionThreshold": {
        "filter": "resource.type = \"cloud_run_revision\" AND metric.type = \"run.googleapis.com/request_count\" AND metric.labels.response_code_class = \"5xx\"",
        "comparison": "COMPARISON_GT",
        "duration": "60s",
        "thresholdValue": 10
      }
    }
  ],
  "notificationChannels": [
    "$BABU_CHANNEL"
  ]
}
JSON

cat << JSON > alerts/gke_policy.json
{
  "displayName": "GKE High CPU (Akash)",
  "combiner": "OR",
  "conditions": [
    {
      "displayName": "Kubernetes Container - CPU limit utilization",
      "conditionThreshold": {
        "filter": "resource.type = \"k8s_container\" AND metric.type = \"kubernetes.io/container/cpu/limit_utilization\"",
        "comparison": "COMPARISON_GT",
        "duration": "180s",
        "thresholdValue": 0.8
      }
    }
  ],
  "notificationChannels": [
    "$AKASH_CHANNEL"
  ]
}
JSON

cat << JSON > alerts/gce_policy.json
{
  "displayName": "GCE High CPU (Roshni & Swathi)",
  "combiner": "OR",
  "conditions": [
    {
      "displayName": "VM Instance - CPU utilization",
      "conditionThreshold": {
        "filter": "resource.type = \"gce_instance\" AND metric.type = \"compute.googleapis.com/instance/cpu/utilization\"",
        "comparison": "COMPARISON_GT",
        "duration": "180s",
        "thresholdValue": 0.85
      }
    }
  ],
  "notificationChannels": [
    "$ROSHNI_CHANNEL",
    "$SWATHI_CHANNEL"
  ]
}
JSON

cat << JSON > alerts/bigquery_policy.json
{
  "displayName": "BigQuery High Execution Time (Ecclesiastes & Emayan)",
  "combiner": "OR",
  "conditions": [
    {
      "displayName": "BigQuery Project - Query execution time",
      "conditionThreshold": {
        "filter": "resource.type = \"bigquery_project\" AND metric.type = \"bigquery.googleapis.com/query/execution_times\"",
        "comparison": "COMPARISON_GT",
        "duration": "60s",
        "thresholdValue": 10000
      }
    }
  ],
  "notificationChannels": [
    "$ECCLESIASTES_CHANNEL",
    "$EMAYAN_CHANNEL"
  ]
}
JSON

cat << JSON > alerts/looker_pipeline_policy.json
{
  "displayName": "Log Streamer Pipeline Errors (Varunshiyam)",
  "combiner": "OR",
  "conditions": [
    {
      "displayName": "Global - Log entry count",
      "conditionThreshold": {
        "filter": "resource.type = \"global\" AND metric.type = \"logging.googleapis.com/log_entry_count\" AND metric.labels.severity = \"ERROR\"",
        "comparison": "COMPARISON_GT",
        "duration": "60s",
        "thresholdValue": 5
      }
    }
  ],
  "notificationChannels": [
    "$VARUN_CHANNEL"
  ]
}
JSON

echo "Creating Alert Policies..."
gcloud alpha monitoring policies create --policy-from-file=alerts/cloud_run_policy.json --project=$PROJECT_ID
gcloud alpha monitoring policies create --policy-from-file=alerts/gke_policy.json --project=$PROJECT_ID
gcloud alpha monitoring policies create --policy-from-file=alerts/gce_policy.json --project=$PROJECT_ID
gcloud alpha monitoring policies create --policy-from-file=alerts/bigquery_policy.json --project=$PROJECT_ID
gcloud alpha monitoring policies create --policy-from-file=alerts/looker_pipeline_policy.json --project=$PROJECT_ID

echo "DONE!"
