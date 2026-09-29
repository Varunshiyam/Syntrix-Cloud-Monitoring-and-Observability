-- 1. Create a Base Cleaned View
CREATE OR REPLACE VIEW `project-4e3f1563-833a-4721-bf7.syntrix_logs.looker_cleaned_logs` AS
SELECT
  timestamp,
  IFNULL(severity, 'WARNING') AS severity,
  
  -- Extract Compute Environment and Service Name from the resource JSON string
  JSON_EXTRACT_SCALAR(resource, '$.type') AS compute_environment,
  
  -- Service Name determination based on resource type
  CASE 
    WHEN JSON_EXTRACT_SCALAR(resource, '$.type') = 'cloud_run_revision' THEN JSON_EXTRACT_SCALAR(resource, '$.labels.service_name')
    WHEN JSON_EXTRACT_SCALAR(resource, '$.type') = 'k8s_container' THEN JSON_EXTRACT_SCALAR(resource, '$.labels.container_name')
    WHEN JSON_EXTRACT_SCALAR(resource, '$.type') = 'gce_instance' THEN 'inventory-service' -- Hardcoded based on our architecture
    ELSE 'unknown'
  END AS service_name,

  -- Application Metrics extracted from jsonPayload
  JSON_EXTRACT_SCALAR(jsonPayload, '$.endpoint') AS endpoint,
  JSON_EXTRACT_SCALAR(jsonPayload, '$.method') AS method,
  CAST(JSON_EXTRACT_SCALAR(jsonPayload, '$.status_code') AS INT64) AS status_code,
  CAST(JSON_EXTRACT_SCALAR(jsonPayload, '$.latency_ms') AS INT64) AS latency_ms,
  JSON_EXTRACT_SCALAR(jsonPayload, '$.event') AS event_type,
  JSON_EXTRACT_SCALAR(jsonPayload, '$.error') AS error_message
  
FROM `project-4e3f1563-833a-4721-bf7.syntrix_logs.raw_logs`
-- Only analyze logs that have a valid service name and represent app requests/errors
WHERE JSON_EXTRACT_SCALAR(jsonPayload, '$.event') IS NOT NULL 
   OR JSON_EXTRACT_SCALAR(jsonPayload, '$.latency_ms') IS NOT NULL;

-- 2. Create Latency Analysis View
CREATE OR REPLACE VIEW `project-4e3f1563-833a-4721-bf7.syntrix_logs.looker_latency_analysis` AS
SELECT
  TIMESTAMP_TRUNC(timestamp, HOUR) AS time_window,
  service_name,
  compute_environment,
  endpoint,
  COUNT(1) as total_requests,
  AVG(latency_ms) as avg_latency_ms,
  MAX(latency_ms) as max_latency_ms
FROM `project-4e3f1563-833a-4721-bf7.syntrix_logs.looker_cleaned_logs`
WHERE latency_ms IS NOT NULL
GROUP BY 1, 2, 3, 4;

-- 3. Create Error Analysis View
CREATE OR REPLACE VIEW `project-4e3f1563-833a-4721-bf7.syntrix_logs.looker_error_analysis` AS
SELECT
  TIMESTAMP_TRUNC(timestamp, HOUR) AS time_window,
  service_name,
  compute_environment,
  COUNT(1) as total_requests,
  COUNTIF(status_code >= 400 AND status_code < 500) as client_errors_4xx,
  COUNTIF(status_code >= 500) as server_errors_5xx,
  -- Error Rate
  SAFE_DIVIDE(COUNTIF(status_code >= 400), COUNT(1)) * 100 AS error_rate_percentage
FROM `project-4e3f1563-833a-4721-bf7.syntrix_logs.looker_cleaned_logs`
WHERE status_code IS NOT NULL
GROUP BY 1, 2, 3;

-- 4. Create Usage Monitoring View
CREATE OR REPLACE VIEW `project-4e3f1563-833a-4721-bf7.syntrix_logs.looker_usage_monitoring` AS
SELECT
  TIMESTAMP_TRUNC(timestamp, DAY) AS reporting_date,
  compute_environment,
  endpoint,
  COUNT(1) as daily_requests
FROM `project-4e3f1563-833a-4721-bf7.syntrix_logs.looker_cleaned_logs`
GROUP BY 1, 2, 3;

-- 5. Create Performance KPIs View (Advanced Latency Percentiles)
CREATE OR REPLACE VIEW `project-4e3f1563-833a-4721-bf7.syntrix_logs.looker_performance_kpis` AS
SELECT
  service_name,
  compute_environment,
  COUNT(1) AS total_requests,
  APPROX_QUANTILES(latency_ms, 100)[OFFSET(50)] AS p50_latency,
  APPROX_QUANTILES(latency_ms, 100)[OFFSET(90)] AS p90_latency,
  APPROX_QUANTILES(latency_ms, 100)[OFFSET(99)] AS p99_latency,
  SAFE_DIVIDE(COUNTIF(status_code < 400), COUNT(1)) * 100 AS success_rate_percentage
FROM `project-4e3f1563-833a-4721-bf7.syntrix_logs.looker_cleaned_logs`
WHERE latency_ms IS NOT NULL AND status_code IS NOT NULL
GROUP BY 1, 2;

-- 6. Cost Optimization Recommendations View
-- Uses the most recent 24-hour window relative to the LATEST data timestamp
-- (not CURRENT_TIMESTAMP), so the view works even with historical/older data.
CREATE OR REPLACE VIEW `project-4e3f1563-833a-4721-bf7.syntrix_logs.looker_cost_optimization_recommendations` AS
WITH latest AS (
  SELECT MAX(timestamp) AS max_ts
  FROM `project-4e3f1563-833a-4721-bf7.syntrix_logs.looker_cleaned_logs`
)
SELECT
  compute_environment,
  service_name,
  COUNT(1) AS total_requests_last_24h,
  CASE
    WHEN COUNT(1) < 100 AND compute_environment = 'k8s_container' THEN 'Low Traffic: Scale down GKE nodes or migrate to Cloud Run (Scale to Zero)'
    WHEN COUNT(1) < 100 AND compute_environment = 'gce_instance' THEN 'Low Traffic: Downgrade VM instance type or migrate to Cloud Run'
    WHEN COUNT(1) > 10000 AND compute_environment = 'cloud_run_revision' THEN 'High Traffic: Consider migrating to GKE for sustained discount usage'
    ELSE 'Traffic Optimized for Environment'
  END AS cost_recommendation
FROM `project-4e3f1563-833a-4721-bf7.syntrix_logs.looker_cleaned_logs`
CROSS JOIN latest
WHERE timestamp >= TIMESTAMP_SUB(latest.max_ts, INTERVAL 24 HOUR)
GROUP BY 1, 2;
