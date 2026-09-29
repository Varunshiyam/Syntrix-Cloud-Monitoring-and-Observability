import subprocess
import json

PROJECT_ID = "project-4e3f1563-833a-4721-bf7"

def get_channel(email):
    cmd = f"gcloud beta monitoring channels list --project={PROJECT_ID} --format=json"
    out = subprocess.check_output(cmd, shell=True, text=True)
    channels = json.loads(out)
    for c in channels:
        if c.get("labels", {}).get("email_address") == email:
            return c["name"]
    return None

babu = get_channel("bbabusenthil@gmail.com")
ecclesiastes = get_channel("ecclesiastescherubin1@gmail.com")
emayan = get_channel("emayanvijayakumar17@gmail.com")

cloud_run_policy = {
  "displayName": "Cloud Run 5xx Errors (Babu)",
  "combiner": "OR",
  "conditions": [
    {
      "displayName": "Cloud Run Revision - Request count",
      "conditionThreshold": {
        "filter": 'resource.type = "cloud_run_revision" AND metric.type = "run.googleapis.com/request_count" AND metric.labels.response_code_class = "5xx"',
        "comparison": "COMPARISON_GT",
        "duration": "60s",
        "thresholdValue": 10,
        "aggregations": [
          {
            "alignmentPeriod": "60s",
            "perSeriesAligner": "ALIGN_RATE"
          }
        ]
      }
    }
  ],
  "notificationChannels": [babu] if babu else []
}

bq_policy = {
  "displayName": "BigQuery High Execution Time (Ecclesiastes & Emayan)",
  "combiner": "OR",
  "conditions": [
    {
      "displayName": "BigQuery Project - Query execution time",
      "conditionThreshold": {
        "filter": 'resource.type = "bigquery_project" AND metric.type = "bigquery.googleapis.com/query/execution_times"',
        "comparison": "COMPARISON_GT",
        "duration": "60s",
        "thresholdValue": 10000,
        "aggregations": [
          {
            "alignmentPeriod": "60s",
            "perSeriesAligner": "ALIGN_PERCENTILE_99"
          }
        ]
      }
    }
  ],
  "notificationChannels": filter(None, [ecclesiastes, emayan])
}
bq_policy["notificationChannels"] = list(bq_policy["notificationChannels"])

with open("alerts/cloud_run_policy.json", "w") as f:
    json.dump(cloud_run_policy, f)
with open("alerts/bigquery_policy.json", "w") as f:
    json.dump(bq_policy, f)

