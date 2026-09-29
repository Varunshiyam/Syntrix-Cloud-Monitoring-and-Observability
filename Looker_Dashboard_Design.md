# SYNTRIX — Looker Studio Dashboard Design & Implementation Guide

**Project:** CloudMart Enterprise Log Monitoring & Visualization  
**Version:** 1.0  
**Prepared By:** SYNTRIX Analytics Team  
**Date:** August 2026

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture & Data Pipeline Overview](#2-architecture--data-pipeline-overview)
3. [Key Performance Indicators (KPIs)](#3-key-performance-indicators-kpis)
4. [BigQuery Data Sources & Views](#4-bigquery-data-sources--views)
5. [Looker Studio Dashboard Architecture — Multi-Layer Design](#5-looker-studio-dashboard-architecture--multi-layer-design)
6. [Step-by-Step Implementation Guide](#6-step-by-step-implementation-guide)
7. [Sheet 1 — Executive Overview](#7-sheet-1--executive-overview)
8. [Sheet 2 — System Performance & Latency](#8-sheet-2--system-performance--latency)
9. [Sheet 3 — Error Analysis & Reliability](#9-sheet-3--error-analysis--reliability)
10. [Sheet 4 — Infrastructure & Resource Usage](#10-sheet-4--infrastructure--resource-usage)
11. [Sheet 5 — Cost Optimization & Recommendations](#11-sheet-5--cost-optimization--recommendations)
12. [Sheet 6 — Developer Deep Dive & Log Explorer](#12-sheet-6--developer-deep-dive--log-explorer)
13. [Left-Side Navigation Panel Design](#13-left-side-navigation-panel-design)
14. [Responsive Design & Theme Guidelines](#14-responsive-design--theme-guidelines)
15. [Alert Integration & Threshold Configuration](#15-alert-integration--threshold-configuration)
16. [Appendix — LookML Reference (If Using Looker Enterprise)](#16-appendix--lookml-reference-if-using-looker-enterprise)

---

## 1. Executive Summary

### 1.1 Project Objective
Build a **cloud-based log monitoring and visualization solution** that gathers and analyzes application logs from the CloudMart microservices platform to help development teams:
- Track system performance (latency, throughput, uptime)
- Identify error patterns (4xx client errors, 5xx server errors)
- Monitor overall cloud infrastructure health across Cloud Run, GKE, and Compute Engine
- Suggest cost-saving actions based on traffic analysis

### 1.2 What This Document Delivers
A **complete, beginner-friendly, step-by-step guide** to building a professional, multi-layer Looker Studio dashboard with:
- 6 dedicated dashboard sheets (tabs) for different stakeholder perspectives
- A left-side navigation panel for seamless sheet-to-sheet navigation
- Responsive design optimized for 1920×1080 and laptop screens
- Real GCP BigQuery data connections

### 1.3 Target Audience
| Stakeholder          | Dashboard Sheet                        |
|----------------------|----------------------------------------|
| CTO / VP Engineering | Sheet 1 — Executive Overview           |
| SRE / DevOps         | Sheet 2 — Performance, Sheet 3 — Errors|
| FinOps / Cloud Mgmt  | Sheet 4 — Infrastructure, Sheet 5 — Cost|
| Developers / QA      | Sheet 6 — Log Explorer                 |

---

## 2. Architecture & Data Pipeline Overview

### 2.1 Application Architecture
```
                    CUSTOMER
                        │
                        ▼
                CloudMart Web Portal
                        │
                        ▼
                  API Gateway (Cloud Run)
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
   Catalog Service   Cart Service   Order Service
   (Cloud Run)       (Cloud Run)    (GKE)
        │               │                │
        │               │                ▼
        │               │         Payment Service
        │               │            (GKE)
        │               │                │
        ▼               ▼                ▼
                 Inventory Service
                (Compute Engine / GCE)
                        │
                        ▼
                 Cloud SQL (PostgreSQL)
```

### 2.2 Compute Environment Mapping
| Service            | GCP Compute Platform | Resource Type in Logs     |
|--------------------|----------------------|---------------------------|
| API Gateway        | Cloud Run            | `cloud_run_revision`      |
| Catalog Service    | Cloud Run            | `cloud_run_revision`      |
| Cart Service       | Cloud Run            | `cloud_run_revision`      |
| Order Service      | GKE                  | `k8s_container`           |
| Payment Service    | GKE                  | `k8s_container`           |
| Inventory Service  | Compute Engine       | `gce_instance`            |

### 2.3 Data Pipeline
```
Cloud Run / GKE / GCE Services
        │  (Structured JSON stdout logs)
        ▼
Google Cloud Logging
        │  (Log Router Sink OR realtime_log_streamer.py)
        ▼
Google Cloud Storage (gs://project-xxx-logs-bucket)
        │  (NDJSON format)
        ▼
BigQuery (syntrix_logs.raw_logs)
        │  (SQL Views for aggregation)
        ▼
BigQuery Analytical Views (6 views)
        │
        ▼
Looker Studio (Dashboard)
```

### 2.4 Log Schema (JSON Payload Fields)
Each log entry from services contains these key fields:

| Field          | Type    | Description                                    |
|----------------|---------|------------------------------------------------|
| `timestamp`    | STRING  | ISO 8601 timestamp of the log entry            |
| `severity`     | STRING  | Log level: `INFO`, `WARNING`, `ERROR`          |
| `event`        | STRING  | Event type: `request_completed`, `order_created`, `payment_processed`, etc. |
| `endpoint`     | STRING  | API endpoint path (e.g., `/api/products`)      |
| `method`       | STRING  | HTTP method: `GET`, `POST`, `PUT`, `DELETE`    |
| `status_code`  | INT     | HTTP response status code                      |
| `latency_ms`   | INT     | Request processing time in milliseconds        |
| `error`        | STRING  | Error message (if applicable)                  |
| `request_id`   | STRING  | Distributed tracing: unique per request        |
| `trace_id`     | STRING  | Distributed tracing: spans entire transaction  |
| `service`      | STRING  | Originating service name                       |
| `order_id`     | INT     | Order identifier (for order/payment events)    |
| `total_amount` | FLOAT   | Transaction amount (for order events)          |

---

## 3. Key Performance Indicators (KPIs)

### 3.1 Primary KPIs (Executive Level)
| KPI                          | Formula / Source                                      | Target          |
|------------------------------|-------------------------------------------------------|-----------------|
| **Global Success Rate**      | `(Requests with status < 400) / Total Requests × 100` | ≥ 99.5%         |
| **Global Error Rate**        | `(Requests with status ≥ 400) / Total Requests × 100` | ≤ 0.5%          |
| **Total Request Volume (24h)**| `COUNT(*)` from cleaned logs, last 24 hours           | Trend ↑         |
| **System Availability**      | `Uptime % based on error-free intervals`              | ≥ 99.9%         |

### 3.2 Performance KPIs (DevOps Level)
| KPI                          | Formula / Source                                      | Threshold       |
|------------------------------|-------------------------------------------------------|-----------------|
| **Average Latency**          | `AVG(latency_ms)` per service                         | ≤ 200ms         |
| **P50 Latency (Median)**     | `APPROX_QUANTILES(latency_ms, 100)[OFFSET(50)]`      | ≤ 100ms         |
| **P90 Latency**              | `APPROX_QUANTILES(latency_ms, 100)[OFFSET(90)]`      | ≤ 300ms         |
| **P99 Latency (Tail)**       | `APPROX_QUANTILES(latency_ms, 100)[OFFSET(99)]`      | ≤ 1000ms        |
| **Max Latency**              | `MAX(latency_ms)` per service                         | ≤ 5000ms        |

### 3.3 Error KPIs (Reliability Level)
| KPI                          | Formula / Source                                      | Threshold       |
|------------------------------|-------------------------------------------------------|-----------------|
| **Client Error Rate (4xx)**  | `COUNTIF(status_code BETWEEN 400 AND 499) / Total`   | ≤ 2%            |
| **Server Error Rate (5xx)**  | `COUNTIF(status_code >= 500) / Total`                 | ≤ 0.5%          |
| **Error Rate by Service**    | Per-service error breakdown                           | Per SLA         |
| **Error Rate by Environment**| Cloud Run vs GKE vs GCE                               | Per SLA         |

### 3.4 Infrastructure & Cost KPIs
| KPI                            | Formula / Source                                    | Action              |
|--------------------------------|-----------------------------------------------------|---------------------|
| **Requests per Environment**   | `COUNT(*)` grouped by `compute_environment`         | Monitor utilization |
| **Daily Request Trend**        | `COUNT(*)` grouped by `DATE(timestamp)`             | Capacity planning   |
| **Cost Optimization Flags**    | Rules-based analysis (low-traffic GKE → Cloud Run)  | Actionable savings  |

---

## 4. BigQuery Data Sources & Views

These 6 pre-built BigQuery views power the Looker Studio dashboards. They live in the `syntrix_logs` dataset.

### View 1: `looker_cleaned_logs` (Base View)
**Purpose:** Normalized, cleaned base table for all downstream analysis.

| Column              | Type   | Extracted From               |
|---------------------|--------|------------------------------|
| `timestamp`         | TIMESTAMP | Raw log timestamp          |
| `severity`          | STRING    | Raw log severity           |
| `compute_environment` | STRING | `resource.type`            |
| `service_name`      | STRING    | Derived from resource labels|
| `endpoint`          | STRING    | `jsonPayload.endpoint`     |
| `method`            | STRING    | `jsonPayload.method`       |
| `status_code`       | INT64     | `jsonPayload.status_code`  |
| `latency_ms`        | INT64     | `jsonPayload.latency_ms`   |
| `event_type`        | STRING    | `jsonPayload.event`        |
| `error_message`     | STRING    | `jsonPayload.error`        |

### View 2: `looker_latency_analysis`
**Purpose:** Hourly latency aggregation by service and endpoint.

| Column              | Type   | Description                    |
|---------------------|--------|--------------------------------|
| `time_window`       | TIMESTAMP | Truncated to hour           |
| `service_name`      | STRING    | Service identifier          |
| `compute_environment` | STRING | GCP platform type           |
| `endpoint`          | STRING    | API path                    |
| `total_requests`    | INT64     | Count of requests           |
| `avg_latency_ms`    | FLOAT64   | Average response time       |
| `max_latency_ms`    | INT64     | Maximum response time       |

### View 3: `looker_error_analysis`
**Purpose:** Hourly error breakdown with 4xx/5xx split.

| Column                  | Type   | Description                  |
|-------------------------|--------|------------------------------|
| `time_window`           | TIMESTAMP | Truncated to hour         |
| `service_name`          | STRING    | Service identifier        |
| `compute_environment`   | STRING    | GCP platform type         |
| `total_requests`        | INT64     | Count of requests         |
| `client_errors_4xx`     | INT64     | Client error count        |
| `server_errors_5xx`     | INT64     | Server error count        |
| `error_rate_percentage` | FLOAT64   | Overall error rate %      |

### View 4: `looker_usage_monitoring`
**Purpose:** Daily request volume per compute environment and endpoint.

| Column              | Type   | Description                    |
|---------------------|--------|--------------------------------|
| `reporting_date`    | TIMESTAMP | Truncated to day            |
| `compute_environment` | STRING | GCP platform type           |
| `endpoint`          | STRING    | API path                    |
| `daily_requests`    | INT64     | Count of daily requests     |

### View 5: `looker_performance_kpis`
**Purpose:** Advanced latency percentiles (P50/P90/P99) and success rates by service.

| Column                   | Type   | Description                 |
|--------------------------|--------|-----------------------------|
| `service_name`           | STRING    | Service identifier       |
| `compute_environment`    | STRING    | GCP platform type        |
| `total_requests`         | INT64     | Total request count      |
| `p50_latency`            | INT64     | 50th percentile latency  |
| `p90_latency`            | INT64     | 90th percentile latency  |
| `p99_latency`            | INT64     | 99th percentile latency  |
| `success_rate_percentage`| FLOAT64   | % of requests < 400      |

### View 6: `looker_cost_optimization_recommendations`
**Purpose:** Actionable cost-saving recommendations based on 24-hour traffic patterns.

| Column                   | Type   | Description                  |
|--------------------------|--------|------------------------------|
| `compute_environment`    | STRING    | GCP platform type         |
| `service_name`           | STRING    | Service identifier        |
| `total_requests_last_24h`| INT64     | Request count (24h)       |
| `cost_recommendation`    | STRING    | Actionable recommendation |

---

## 5. Looker Studio Dashboard Architecture — Multi-Layer Design

### 5.1 Dashboard Sheet Map
```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────────────────────────┐  │
│  │                  │  │                                      │  │
│  │  LEFT NAVIGATION │  │       MAIN CONTENT AREA              │  │
│  │     PANEL        │  │                                      │  │
│  │                  │  │   (Changes per selected sheet)        │  │
│  │  ● Overview      │  │                                      │  │
│  │  ● Performance   │  │                                      │  │
│  │  ● Errors        │  │                                      │  │
│  │  ● Infrastructure│  │                                      │  │
│  │  ● Cost          │  │                                      │  │
│  │  ● Log Explorer  │  │                                      │  │
│  │                  │  │                                      │  │
│  │  ─────────────── │  │                                      │  │
│  │  SYNTRIX Logo    │  │                                      │  │
│  │  Project Info    │  │                                      │  │
│  │                  │  │                                      │  │
│  └──────────────────┘  └──────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │  GLOBAL FILTER BAR: [Date Range] [Service] [Environment]    ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 5.2 Design Principles
| Principle                | Implementation                                                |
|--------------------------|---------------------------------------------------------------|
| **Multi-Layer Structure**| 6 sheets, each targeting a specific stakeholder persona       |
| **Left-Side Navigation** | Persistent sidebar with icon + label links to each sheet      |
| **Responsive Layout**   | Grid-based layout; works on 1920×1080 and 1366×768           |
| **Consistent Branding** | Same header, footer, color palette, fonts across all sheets   |
| **Filter Persistence**  | Global date range filter applies across all sheets            |
| **Drill-Down Capability**| Click a service/endpoint to filter all charts on that sheet   |

---

## 6. Step-by-Step Implementation Guide

### PHASE 1 — Setting Up the Looker Studio Report

#### Step 1: Open Looker Studio
1. Go to **https://lookerstudio.google.com**
2. Sign in with your GCP-linked Google account
3. Click **"+ Create"** → **"Report"**

#### Step 2: Connect the BigQuery Data Sources
You need to add **all 6 BigQuery views** as separate data sources.

1. In the new blank report, click **"Add data"** (bottom toolbar or Resource → Manage added data sources)
2. Select **"BigQuery"** as the connector
3. Navigate: **My Projects** → `project-4e3f1563-833a-4721-bf7` → `syntrix_logs`
4. Select the first view: **`looker_cleaned_logs`** → Click **"Add"**
5. Repeat for each remaining view:
   - `looker_latency_analysis`
   - `looker_error_analysis`
   - `looker_usage_monitoring`
   - `looker_performance_kpis`
   - `looker_cost_optimization_recommendations`

> **Beginner Tip:** You should now see 6 data sources listed in **Resource → Manage added data sources**. Name each source clearly (e.g., rename "looker_cleaned_logs" to "DS1 - Cleaned Logs").

#### Step 3: Set Up Report Pages (Sheets)
1. At the bottom of the Looker Studio canvas, you will see page tabs
2. Right-click the default page → **"Rename"** → `Executive Overview`
3. Click the **"+"** icon next to the page tab to add new pages
4. Create 5 more pages and name them:
   - `System Performance`
   - `Error Analysis`
   - `Infrastructure Usage`
   - `Cost Optimization`
   - `Developer Log Explorer`

#### Step 4: Set Report-Level Theme
1. Go to **Theme and Layout** (top menu bar → "Theme and layout")
2. Click **"Customize"**
3. Set:
   - **Canvas Size:** Custom → `1920 x 1080`
   - **Background Color:** `#0F1724` (dark navy — professional dark theme)
   - **Font Family:** `Roboto` or `Inter`
   - **Primary Text Color:** `#E8ECF1` (light gray-white)
   - **Accent Color 1:** `#4285F4` (Google Blue)
   - **Accent Color 2:** `#34A853` (Google Green)
   - **Accent Color 3:** `#EA4335` (Google Red)
   - **Grid spacing:** 10px

---

### PHASE 2 — Building the Left-Side Navigation Panel

This navigation panel must be **copied identically** onto every sheet so it appears persistent.

#### Step 5: Create the Navigation Sidebar on Sheet 1

1. **Draw a Rectangle** (Insert → Shape → Rectangle)
   - Position: `X: 0, Y: 0`
   - Size: `Width: 220, Height: 1080`
   - Background Color: `#151E2D` (slightly lighter than canvas)
   - Border: None
   - Corner Radius: 0

2. **Add the Logo / Title** at the top of the sidebar
   - Insert → Text Box
   - Text: `⚡ SYNTRIX`
   - Position: `X: 20, Y: 20`
   - Font: **Roboto Bold**, Size: 22, Color: `#4285F4`
   - Below that, add a subtitle text:
     - Text: `CloudMart Monitoring`
     - Font: Roboto Regular, Size: 11, Color: `#8899AA`

3. **Add a horizontal divider line**
   - Insert → Shape → Line
   - Position: `X: 20, Y: 75` to `X: 200, Y: 75`
   - Color: `#2A3545`, Thickness: 1px

4. **Add Navigation Buttons** (one per sheet):
   Create 6 text boxes, stacked vertically. Each acts as a clickable link to its sheet.

   | Label                   | Y Position | Icon  | Link To Page         |
   |-------------------------|------------|-------|----------------------|
   | 📊 Executive Overview    | Y: 100     | 📊    | Page 1               |
   | ⚡ Performance            | Y: 145     | ⚡    | Page 2               |
   | 🔴 Error Analysis         | Y: 190     | 🔴    | Page 3               |
   | 🏗️ Infrastructure        | Y: 235     | 🏗️   | Page 4               |
   | 💰 Cost Optimization      | Y: 280     | 💰    | Page 5               |
   | 🔍 Log Explorer           | Y: 325     | 🔍    | Page 6               |

   **How to make them clickable:**
   - Select each text box
   - In the Properties panel on the right, scroll down to **"Report Navigation"** or add a **"Link"**
   - Set link type to **"Report Page"** → select the corresponding page
   - Style: Font size 13, Color `#C0CCDA`, Padding 8px, Left-align
   - **For the ACTIVE page**: Change text color to `#4285F4` and add a small `3px wide × 30px tall` rectangle in `#4285F4` at the left edge of the active button to act as an "active indicator"

5. **Add Footer Info at the bottom of the sidebar**
   - Text: `Team SYNTRIX` / `CTS Hackathon 2026`
   - Position: near `Y: 1020`
   - Font: Size 10, Color `#556677`

6. **Select All sidebar elements** (Ctrl/Cmd + Click each element)
   → **Right-click** → **"Group"**
   → **Copy this Group** → **Paste onto every other sheet** in the exact same position

---

### PHASE 3 — Global Filter Bar

#### Step 6: Add Filters (on each sheet, below the header)

1. **Date Range Control**
   - Insert → **"Date range control"**
   - Position: `X: 240, Y: 20`, Width: 250
   - Default: "Last 7 Days"
   - Style: Background `#1A2535`, text `#E8ECF1`, border `#2A3545`

2. **Service Name Filter (Drop-down)**
   - Insert → **"Drop-down list"** control
   - Data Source: `DS1 - Cleaned Logs`
   - Dimension: `service_name`
   - Position: `X: 510, Y: 20`, Width: 200
   - Label: "Service"

3. **Compute Environment Filter (Drop-down)**
   - Insert → **"Drop-down list"** control
   - Dimension: `compute_environment`
   - Position: `X: 730, Y: 20`, Width: 200
   - Label: "Environment"

> **Beginner Tip:** These filters automatically cross-filter all charts on the page that use the same data source. If charts use different data sources, you must set up **"Data source filter binding"** under each chart's properties.

---

## 7. Sheet 1 — Executive Overview

**Data Sources Used:** `looker_performance_kpis`, `looker_error_analysis`, `looker_usage_monitoring`

**Layout:**
```
┌──────────────────────────────────────────────────────────────┐
│ [NAV]  │  HEADER: Executive Overview          [Filters]      │
│        │─────────────────────────────────────────────────────│
│        │                                                     │
│  📊    │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐   │
│  (act) │  │Success │  │ Error  │  │  Total │  │  Avg   │   │
│        │  │ Rate % │  │ Rate % │  │Requests│  │Latency │   │
│  ⚡    │  │ 99.7%  │  │  0.3%  │  │ 14,502 │  │ 127ms  │   │
│        │  └────────┘  └────────┘  └────────┘  └────────┘   │
│  🔴    │                                                     │
│        │  ┌──────────────────────────────────────────────┐   │
│  🏗️   │  │                                              │   │
│        │  │    DAILY TRAFFIC TREND (TIME SERIES LINE)     │   │
│  💰    │  │                                              │   │
│        │  └──────────────────────────────────────────────┘   │
│  🔍    │                                                     │
│        │  ┌────────────────────┐  ┌──────────────────────┐   │
│        │  │ ERROR RATE BY      │  │ REQUEST DISTRIBUTION │   │
│        │  │ SERVICE (BAR)      │  │ BY ENVIRONMENT (PIE) │   │
│        │  └────────────────────┘  └──────────────────────┘   │
│        │                                                     │
└──────────────────────────────────────────────────────────────┘
```

### Step-by-Step Build:

#### 7.1 KPI Scorecards (Row of 4 cards)

**Card 1: Global Success Rate**
1. Insert → **Scorecard**
2. Data Source: `looker_performance_kpis`
3. Metric: `success_rate_percentage` → Aggregation: **AVG**
4. Position: `X: 250, Y: 90`, Size: `280 × 120`
5. Style:
   - Background: `#1A2535`
   - Value Font: Roboto Bold, Size 40, Color `#34A853` (green)
   - Label: "Success Rate" — Font size 12, Color `#8899AA`
   - Border Radius: 12px
   - Add a shadow for depth
6. Compact Number: OFF
7. Number Format: Percent, 1 decimal place

**Card 2: Global Error Rate**
1. Insert → Scorecard
2. Data Source: `looker_error_analysis`
3. Metric: `error_rate_percentage` → Aggregation: **AVG**
4. Value Color: `#EA4335` (red)
5. Label: "Error Rate"

**Card 3: Total Requests (24h)**
1. Insert → Scorecard
2. Data Source: `looker_usage_monitoring`
3. Metric: `daily_requests` → Aggregation: **SUM**
4. Value Color: `#4285F4` (blue)
5. Label: "Total Requests"

**Card 4: Average Latency**
1. Insert → Scorecard
2. Data Source: `looker_latency_analysis`
3. Metric: `avg_latency_ms` → Aggregation: **AVG**
4. Value Color: `#FBBC04` (yellow/amber)
5. Suffix: "ms"
6. Label: "Avg Latency"

#### 7.2 Daily Traffic Trend Line Chart
1. Insert → **Time Series Chart**
2. Data Source: `looker_usage_monitoring`
3. Date Dimension: `reporting_date`
4. Metric: `daily_requests` → Aggregation: **SUM**
5. Position: Below scorecards, spanning full width (`X: 250, Y: 230, Width: 1640, Height: 320`)
6. Style:
   - Line Color: `#4285F4`
   - Background: `#1A2535`
   - Grid Lines Color: `#2A3545`
   - Data Point size: 4
   - Enable Trend Line: Yes (linear)
   - X-Axis Label Color: `#8899AA`

#### 7.3 Error Rate by Service (Bar Chart)
1. Insert → **Bar Chart**
2. Data Source: `looker_error_analysis`
3. Dimension: `service_name`
4. Metric: `error_rate_percentage` → Aggregation: **AVG**
5. Position: `X: 250, Y: 570, Width: 800, Height: 350`
6. Sort: Descending by metric
7. Style: Horizontal bars, Color series `#EA4335`, Background `#1A2535`

#### 7.4 Request Distribution by Environment (Donut Chart)
1. Insert → **Pie Chart** → Style as **Donut**
2. Data Source: `looker_usage_monitoring`
3. Dimension: `compute_environment`
4. Metric: `daily_requests` → SUM
5. Position: `X: 1080, Y: 570, Width: 810, Height: 350`
6. Style:
   - Donut Hole Size: 60%
   - Colors: Cloud Run = `#4285F4`, GKE = `#34A853`, GCE = `#FBBC04`
   - Background: `#1A2535`
   - Show Legend: Right side

---

## 8. Sheet 2 — System Performance & Latency

**Data Sources Used:** `looker_latency_analysis`, `looker_performance_kpis`

### Layout:
```
┌──────────────────────────────────────────────────────────────┐
│ [NAV]  │  HEADER: System Performance & Latency   [Filters]   │
│        │─────────────────────────────────────────────────────│
│        │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐   │
│        │  │  P50   │  │  P90   │  │  P99   │  │  Max   │   │
│        │  │  87ms  │  │ 245ms  │  │ 890ms  │  │ 3200ms │   │
│        │  └────────┘  └────────┘  └────────┘  └────────┘   │
│        │                                                     │
│        │  ┌──────────────────────────────────────────────┐   │
│        │  │  LATENCY OVER TIME (TIME SERIES, BY SERVICE) │   │
│        │  └──────────────────────────────────────────────┘   │
│        │                                                     │
│        │  ┌──────────────────────┐ ┌─────────────────────┐   │
│        │  │ PERCENTILE LATENCY   │ │ AVG LATENCY BY      │   │
│        │  │ BY SERVICE (GROUPED  │ │ ENDPOINT (TABLE)     │   │
│        │  │ BAR CHART)           │ │                      │   │
│        │  └──────────────────────┘ └─────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### Step-by-Step Build:

#### 8.1 Latency KPI Scorecards
Create 4 Scorecards using data source `looker_performance_kpis`:

| Card   | Metric          | Aggregation | Color     |
|--------|-----------------|-------------|-----------|
| P50    | `p50_latency`   | AVG         | `#34A853` |
| P90    | `p90_latency`   | AVG         | `#FBBC04` |
| P99    | `p99_latency`   | AVG         | `#EA4335` |
| Max    | `max_latency_ms`| MAX (from latency_analysis) | `#EA4335` |

#### 8.2 Latency Over Time (Multi-line Time Series)
1. Insert → **Time Series Chart**
2. Data Source: `looker_latency_analysis`
3. Date Dimension: `time_window`
4. Breakdown Dimension: `service_name`
5. Metric: `avg_latency_ms` → AVG
6. This creates one colored line per service
7. Style: Background `#1A2535`, Legend at bottom

#### 8.3 Percentile Latency by Service (Grouped Bar Chart)
1. Insert → **Bar Chart** (Grouped/Clustered)
2. Data Source: `looker_performance_kpis`
3. Dimension: `service_name`
4. Metrics: `p50_latency`, `p90_latency`, `p99_latency`
5. Bar Colors: P50 = `#34A853`, P90 = `#FBBC04`, P99 = `#EA4335`
6. This gives 3 bars per service, showing the percentile breakdown

#### 8.4 Latency by Endpoint (Data Table)
1. Insert → **Table with Heatmap**
2. Data Source: `looker_latency_analysis`
3. Dimensions: `service_name`, `endpoint`
4. Metrics: `total_requests`, `avg_latency_ms`, `max_latency_ms`
5. Sort: `avg_latency_ms` DESC
6. Style: Heatmap on `avg_latency_ms` column (green → red gradient)
7. Row limit: 25

---

## 9. Sheet 3 — Error Analysis & Reliability

**Data Sources Used:** `looker_error_analysis`, `looker_cleaned_logs`

### Layout:
```
┌──────────────────────────────────────────────────────────────┐
│ [NAV]  │  HEADER: Error Analysis & Reliability   [Filters]   │
│        │─────────────────────────────────────────────────────│
│        │  ┌────────┐  ┌────────┐  ┌────────┐               │
│        │  │  4xx   │  │  5xx   │  │ Error  │               │
│        │  │ Count  │  │ Count  │  │ Rate % │               │
│        │  └────────┘  └────────┘  └────────┘               │
│        │                                                     │
│        │  ┌──────────────────────────────────────────────┐   │
│        │  │   ERROR RATE OVER TIME (BY SERVICE)           │   │
│        │  └──────────────────────────────────────────────┘   │
│        │                                                     │
│        │  ┌──────────────────────┐ ┌─────────────────────┐   │
│        │  │ 4xx vs 5xx STACKED   │ │ ERROR MESSAGES      │   │
│        │  │ BAR CHART (BY SVC)   │ │ TABLE (top errors)  │   │
│        │  └──────────────────────┘ └─────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### Step-by-Step Build:

#### 9.1 Error KPI Scorecards
| Card         | Data Source           | Metric                | Aggregation | Color     |
|--------------|-----------------------|-----------------------|-------------|-----------|
| 4xx Count    | `looker_error_analysis` | `client_errors_4xx`  | SUM         | `#FBBC04` |
| 5xx Count    | `looker_error_analysis` | `server_errors_5xx`  | SUM         | `#EA4335` |
| Error Rate % | `looker_error_analysis` | `error_rate_percentage` | AVG      | `#EA4335` |

#### 9.2 Error Rate Over Time (Time Series)
1. Insert → **Time Series Chart**
2. Data Source: `looker_error_analysis`
3. Date Dimension: `time_window`
4. Breakdown: `service_name`
5. Metric: `error_rate_percentage` → AVG
6. Add a **Reference Line** at `5%` (threshold, dashed red) via chart properties

#### 9.3 4xx vs 5xx Stacked Bar (Per Service)
1. Insert → **Stacked Bar Chart**
2. Data Source: `looker_error_analysis`
3. Dimension: `service_name`
4. Metrics: `client_errors_4xx` (SUM), `server_errors_5xx` (SUM)
5. Colors: 4xx = `#FBBC04`, 5xx = `#EA4335`

#### 9.4 Top Error Messages Table
1. Insert → **Table**
2. Data Source: `looker_cleaned_logs`
3. Filter: `severity` = `ERROR` (add chart-level filter)
4. Dimensions: `service_name`, `error_message`
5. Metric: `Record Count`
6. Sort: Record Count DESC
7. Row limit: 15

---

## 10. Sheet 4 — Infrastructure & Resource Usage

**Data Sources Used:** `looker_usage_monitoring`, `looker_latency_analysis`

### Layout:
```
┌──────────────────────────────────────────────────────────────┐
│ [NAV]  │  HEADER: Infrastructure & Resource Usage [Filters]  │
│        │─────────────────────────────────────────────────────│
│        │  ┌────────┐  ┌────────┐  ┌────────┐               │
│        │  │Cloud   │  │  GKE   │  │  GCE   │               │
│        │  │Run Req │  │ Reqs   │  │ Reqs   │               │
│        │  └────────┘  └────────┘  └────────┘               │
│        │                                                     │
│        │  ┌──────────────────────────────────────────────┐   │
│        │  │  DAILY REQUEST VOLUME BY ENVIRONMENT (AREA)   │   │
│        │  └──────────────────────────────────────────────┘   │
│        │                                                     │
│        │  ┌──────────────────────┐ ┌─────────────────────┐   │
│        │  │ REQUESTS BY ENDPOINT │ │ ENVIRONMENT PERF    │   │
│        │  │ (TREEMAP)            │ │ COMPARISON TABLE    │   │
│        │  └──────────────────────┘ └─────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### Step-by-Step Build:

#### 10.1 Environment KPI Scorecards
Create 3 scorecards from `looker_usage_monitoring`. Each card uses a **chart-level filter** on `compute_environment`:

| Card       | Filter                              | Metric          | Color     |
|------------|-------------------------------------|-----------------|-----------|
| Cloud Run  | `compute_environment` = `cloud_run_revision` | `daily_requests` SUM | `#4285F4` |
| GKE        | `compute_environment` = `k8s_container`      | `daily_requests` SUM | `#34A853` |
| GCE        | `compute_environment` = `gce_instance`        | `daily_requests` SUM | `#FBBC04` |

#### 10.2 Daily Request Volume by Environment (Stacked Area Chart)
1. Insert → **Area Chart**
2. Data Source: `looker_usage_monitoring`
3. Date Dimension: `reporting_date`
4. Breakdown: `compute_environment`
5. Metric: `daily_requests` → SUM
6. Style: Stacked, use environment colors, opacity 70%

#### 10.3 Requests by Endpoint (Treemap)
1. Insert → **Treemap Chart**
2. Data Source: `looker_usage_monitoring`
3. Dimension: `endpoint`
4. Metric: `daily_requests` → SUM
5. Color scale: Blue gradient

#### 10.4 Environment Performance Comparison Table
1. Insert → **Pivot Table** or **Table with Heatmap**
2. Data Source: `looker_latency_analysis`
3. Row Dimension: `compute_environment`
4. Metrics: `total_requests` SUM, `avg_latency_ms` AVG, `max_latency_ms` MAX
5. Heatmap on `avg_latency_ms`

---

## 11. Sheet 5 — Cost Optimization & Recommendations

**Data Sources Used:** `looker_cost_optimization_recommendations`, `looker_usage_monitoring`

### Layout:
```
┌──────────────────────────────────────────────────────────────┐
│ [NAV]  │  HEADER: Cost Optimization & Recommendations        │
│        │─────────────────────────────────────────────────────│
│        │                                                     │
│        │  ┌──────────────────────────────────────────────┐   │
│        │  │  COST RECOMMENDATION TABLE (FULL WIDTH)      │   │
│        │  │  ┌──────┬──────────┬────────┬──────────────┐ │   │
│        │  │  │ Svc  │ Env      │ Reqs   │Recommendation│ │   │
│        │  │  ├──────┼──────────┼────────┼──────────────┤ │   │
│        │  │  │ inv  │ gce_inst │ 42     │ ⚠ Downgrade  │ │   │
│        │  │  │ order│ k8s_cont │ 87     │ ⚠ Scale Down │ │   │
│        │  │  │ catal│ cloud_run│ 12,400 │ ✅ Optimized  │ │   │
│        │  │  └──────┴──────────┴────────┴──────────────┘ │   │
│        │  └──────────────────────────────────────────────┘   │
│        │                                                     │
│        │  ┌──────────────────────┐ ┌─────────────────────┐   │
│        │  │ TRAFFIC VOLUME BAR   │ │ COST EFFICIENCY      │   │
│        │  │ (PER SERVICE+ENV)    │ │ MATRIX (BUBBLE)      │   │
│        │  └──────────────────────┘ └─────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### Step-by-Step Build:

#### 11.1 Cost Recommendation Table (Primary Component)
1. Insert → **Table**
2. Data Source: `looker_cost_optimization_recommendations`
3. Dimensions: `service_name`, `compute_environment`, `cost_recommendation`
4. Metric: `total_requests_last_24h` → SUM
5. Style:
   - Full width: `X: 250, Y: 90, Width: 1640, Height: 360`
   - Background: `#1A2535`
   - **Conditional Formatting on `cost_recommendation`:**
     - Contains "Scale down" or "Downgrade" → Background `#FFF3CD` (amber), Text `#856404`
     - Contains "migrate to Cloud Run" → Background `#D4EDDA` (light green), Text `#155724`
     - Contains "Optimized" → Background `#1A2535`, Text `#34A853`
6. Sort: `total_requests_last_24h` ASC (show lowest traffic / most actionable first)

#### 11.2 Traffic Volume per Service (Bar Chart)
1. Insert → **Bar Chart**
2. Data Source: `looker_cost_optimization_recommendations`
3. Dimension: `service_name`
4. Breakdown: `compute_environment`
5. Metric: `total_requests_last_24h` → SUM
6. Stacked bars, color-coded by environment

#### 11.3 Cost Efficiency Bubble Chart
1. Insert → **Scatter / Bubble Chart**
2. Data Source: `looker_latency_analysis`
3. Dimension: `service_name`
4. X-Axis: `total_requests` (SUM) — represents traffic volume
5. Y-Axis: `avg_latency_ms` (AVG) — represents performance
6. Bubble Size: `total_requests` (SUM)
7. This reveals services with high latency + low traffic (candidates for cost reduction)

---

## 12. Sheet 6 — Developer Deep Dive & Log Explorer

**Data Sources Used:** `looker_cleaned_logs`

### Layout:
```
┌──────────────────────────────────────────────────────────────┐
│ [NAV]  │  HEADER: Developer Log Explorer          [Filters]  │
│        │─────────────────────────────────────────────────────│
│        │  EXTRA FILTERS: [Severity ▼] [Status Code ▼]       │
│        │                 [Event Type ▼] [Search Error Msg]   │
│        │                                                     │
│        │  ┌──────────────────────────────────────────────┐   │
│        │  │  FULL LOG TABLE (SCROLLABLE)                  │   │
│        │  │  ┌────────┬────┬──────┬────┬─────┬────┬────┐ │   │
│        │  │  │Timestmp│Sev │ Svc  │Endp│Code │Lat │Err │ │   │
│        │  │  ├────────┼────┼──────┼────┼─────┼────┼────┤ │   │
│        │  │  │ ...    │INFO│catalog│/api│ 200 │ 45 │    │ │   │
│        │  │  │ ...    │ERR │order │/chk│ 500 │2100│Tmot│ │   │
│        │  │  │ ...    │WARN│pay   │/pay│ 408 │ 890│Tmot│ │   │
│        │  │  └────────┴────┴──────┴────┴─────┴────┴────┘ │   │
│        │  └──────────────────────────────────────────────┘   │
│        │                                                     │
│        │  ┌──────────────────────┐ ┌─────────────────────┐   │
│        │  │ LOG VOLUME BY        │ │ SEVERITY             │   │
│        │  │ SEVERITY (BAR)       │ │ DISTRIBUTION (PIE)   │   │
│        │  └──────────────────────┘ └─────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### Step-by-Step Build:

#### 12.1 Additional Filter Controls
Add these filter controls at the top of this sheet only:

| Filter          | Dimension       | Control Type     |
|-----------------|-----------------|------------------|
| Severity        | `severity`      | Drop-down        |
| Status Code     | `status_code`   | Drop-down or Slider |
| Event Type      | `event_type`    | Drop-down        |
| Error Message   | `error_message` | Text Input (search) |

#### 12.2 Full Log Table
1. Insert → **Table**
2. Data Source: `looker_cleaned_logs`
3. Dimensions:
   - `timestamp` (format: `YYYY-MM-DD HH:mm:ss`)
   - `severity`
   - `service_name`
   - `compute_environment`
   - `endpoint`
   - `method`
   - `status_code`
   - `latency_ms`
   - `event_type`
   - `error_message`
4. Sort: `timestamp` DESC (newest first)
5. Rows per page: 50
6. Enable pagination
7. Style:
   - Full width: `X: 250, Y: 170, Width: 1640, Height: 550`
   - Background: `#1A2535`
   - Header row: `#151E2D`, Bold
   - **Conditional Formatting:**
     - `severity` = "ERROR" → Row background: `rgba(234,67,53,0.15)` (faint red)
     - `severity` = "WARNING" → Row background: `rgba(251,188,4,0.15)` (faint amber)
     - `status_code` >= 500 → Cell `#EA4335` bold

#### 12.3 Log Volume by Severity (Bar Chart)
1. Insert → **Bar Chart**
2. Dimension: `severity`
3. Metric: Record Count
4. Colors: INFO = `#4285F4`, WARNING = `#FBBC04`, ERROR = `#EA4335`

#### 12.4 Severity Distribution (Donut Chart)
1. Insert → **Pie Chart** (Donut style)
2. Dimension: `severity`
3. Metric: Record Count
4. Same color scheme as above

---

## 13. Left-Side Navigation Panel Design

### 13.1 Visual Specification

```
┌─────────────────────┐
│                     │
│   ⚡ SYNTRIX         │  ← Logo, color #4285F4
│   CloudMart Monitor │  ← Subtitle, color #8899AA
│                     │
│  ─────────────────  │  ← Divider, color #2A3545
│                     │
│  ▌📊 Overview       │  ← Active: blue indicator bar + #4285F4 text
│   ⚡ Performance     │  ← Inactive: #C0CCDA text
│   🔴 Errors          │
│   🏗️ Infrastructure │
│   💰 Cost            │
│   🔍 Log Explorer    │
│                     │
│                     │
│                     │
│                     │
│                     │
│  ─────────────────  │
│   Team SYNTRIX      │  ← Footer, color #556677
│   CTS Hackathon '26 │
│                     │
└─────────────────────┘
     Width: 220px
```

### 13.2 Interactivity
- Each label is a **Text Box** with a **Report Page link** configured
- On hover: Text color changes (configure via Looker Studio text style)
- The "active indicator" (small blue bar) is manually placed on each sheet to highlight the current active page

### 13.3 Replication Across Sheets
1. Build the sidebar on Sheet 1
2. Group all elements (Ctrl/Cmd+A within the sidebar area → Right-click → Group)
3. Copy → Navigate to Sheet 2 → Paste in Place (Ctrl/Cmd+Shift+V)
4. On each sheet, update the active indicator position to match the current page
5. Repeat for all 6 sheets

---

## 14. Responsive Design & Theme Guidelines

### 14.1 Color Palette

| Token                | Hex       | Usage                              |
|----------------------|-----------|------------------------------------|
| **Canvas Background**| `#0F1724` | Report background                  |
| **Card Background**  | `#1A2535` | All chart/card backgrounds         |
| **Sidebar Background**| `#151E2D`| Navigation panel                   |
| **Divider / Border** | `#2A3545` | Subtle separators                  |
| **Primary Text**     | `#E8ECF1` | Headings, values                   |
| **Secondary Text**   | `#8899AA` | Labels, subtitles                  |
| **Muted Text**       | `#556677` | Footer, disabled state             |
| **Accent Blue**      | `#4285F4` | Primary actions, active states     |
| **Success Green**    | `#34A853` | Positive KPIs, success states      |
| **Warning Amber**    | `#FBBC04` | Warnings, moderate values          |
| **Error Red**        | `#EA4335` | Errors, critical alerts            |

### 14.2 Typography
| Element       | Font           | Size  | Weight | Color     |
|---------------|----------------|-------|--------|-----------|
| Page Title    | Roboto         | 24px  | Bold   | `#E8ECF1` |
| Section Title | Roboto         | 16px  | Medium | `#E8ECF1` |
| Card Value    | Roboto         | 36-40px | Bold | Accent    |
| Card Label    | Roboto         | 12px  | Regular| `#8899AA` |
| Table Header  | Roboto         | 12px  | Bold   | `#C0CCDA` |
| Table Body    | Roboto         | 11px  | Regular| `#E8ECF1` |
| Nav Label     | Roboto         | 13px  | Medium | `#C0CCDA` |

### 14.3 Layout Grid
| Property            | Value        |
|---------------------|--------------|
| Canvas Width        | 1920px       |
| Canvas Height       | 1080px       |
| Sidebar Width       | 220px        |
| Content Area Start  | X: 250px     |
| Content Area Width  | 1640px       |
| Grid Spacing        | 10px         |
| Card Border Radius  | 12px         |
| Chart Padding       | 16px         |
| Gap between cards   | 20px         |

### 14.4 Responsive Considerations
- Looker Studio auto-scales on smaller screens via its responsive setting
- Go to **File → Report Settings** → **Layout:** set to **"Fit to width"**
- Test at 1920×1080 and 1366×768 by resizing the browser window
- Avoid placing critical elements beyond X: 1800 to prevent overflow

---

## 15. Alert Integration & Threshold Configuration

### 15.1 GCP Cloud Monitoring Alerts (Already Configured)
These alerts are already deployed via `create_alerts.sh`:

| Alert Name                               | Condition                         | Recipient                  |
|------------------------------------------|-----------------------------------|----------------------------|
| Cloud Run 5xx Errors                     | 5xx count > 10 in 60s            | Babu (Cloud Run Owner)     |
| GKE High CPU                            | CPU utilization > 80% for 3min   | Akash (GKE Owner)          |
| GCE High CPU                            | CPU utilization > 85% for 3min   | Roshni & Swathi (GCE)      |
| BigQuery High Execution Time             | Query time > 10s in 60s          | Ecclesiastes & Emayan (BQ) |
| Log Streamer Pipeline Errors             | ERROR logs > 5 in 60s            | Varunshiyam (Pipeline)     |

### 15.2 Looker Studio Scheduled Email Delivery
1. Go to **Share** → **Schedule email delivery**
2. Set frequency: **Daily at 9:00 AM IST**
3. Recipients: Team distribution list
4. Subject: `[SYNTRIX] Daily CloudMart Dashboard Report`
5. Select which pages to include (recommend: Executive Overview + Cost Optimization)

### 15.3 Embedding Alerts Context in Dashboard
- On Sheet 1 (Executive Overview), add a **Text Box** at the bottom titled **"Active Alert Policies"**
- List the alert thresholds from section 15.1 as reference info for stakeholders
- This provides context when a scorecard shows a degraded metric

---

## 16. Appendix — LookML Reference (If Using Looker Enterprise)

> **Note:** This section is relevant only if you are using **Looker Enterprise** (not Looker Studio). Looker Studio uses direct BigQuery connections. Looker Enterprise requires LookML model definitions.

### 16.1 Model File (`syntrix.model.lkml`)
```lkml
connection: "syntrix_bigquery"

include: "/views/*.view.lkml"

explore: cleaned_logs {
  label: "CloudMart Log Explorer"
  description: "Base cleaned log data for all services"
}

explore: latency_analysis {
  label: "Latency Analysis"
  description: "Hourly latency aggregations by service and endpoint"
}

explore: error_analysis {
  label: "Error Analysis"
  description: "Hourly error breakdown with 4xx/5xx split"
}

explore: performance_kpis {
  label: "Performance KPIs"
  description: "Percentile latency and success rates"
}

explore: cost_optimization {
  label: "Cost Optimization"
  description: "Cost-saving recommendations based on traffic"
}
```

### 16.2 Example View File (`cleaned_logs.view.lkml`)
```lkml
view: cleaned_logs {
  sql_table_name: `project-4e3f1563-833a-4721-bf7.syntrix_logs.looker_cleaned_logs` ;;

  dimension_group: timestamp {
    type: time
    timeframes: [raw, time, hour, date, week, month]
    sql: ${TABLE}.timestamp ;;
  }

  dimension: severity {
    type: string
    sql: ${TABLE}.severity ;;
  }

  dimension: service_name {
    type: string
    sql: ${TABLE}.service_name ;;
  }

  dimension: compute_environment {
    type: string
    sql: ${TABLE}.compute_environment ;;
  }

  dimension: endpoint {
    type: string
    sql: ${TABLE}.endpoint ;;
  }

  dimension: method {
    type: string
    sql: ${TABLE}.method ;;
  }

  dimension: status_code {
    type: number
    sql: ${TABLE}.status_code ;;
  }

  dimension: latency_ms {
    type: number
    sql: ${TABLE}.latency_ms ;;
  }

  dimension: event_type {
    type: string
    sql: ${TABLE}.event_type ;;
  }

  dimension: error_message {
    type: string
    sql: ${TABLE}.error_message ;;
  }

  measure: total_requests {
    type: count
    drill_fields: [timestamp_time, service_name, endpoint, status_code, latency_ms]
  }

  measure: avg_latency {
    type: average
    sql: ${latency_ms} ;;
    value_format: "0.0 \"ms\""
  }

  measure: error_rate {
    type: number
    sql: 1.0 * ${error_count} / NULLIF(${total_requests}, 0) * 100 ;;
    value_format: "0.00\"%\""
  }

  measure: error_count {
    type: count
    filters: [status_code: ">=400"]
  }

  measure: success_rate {
    type: number
    sql: 100.0 - ${error_rate} ;;
    value_format: "0.00\"%\""
  }
}
```

---

## Quick Reference Checklist

Use this checklist to track your progress:

- [ ] **Phase 1:** Looker Studio report created
- [ ] **Phase 1:** All 6 BigQuery data sources connected
- [ ] **Phase 1:** 6 pages/sheets created and named
- [ ] **Phase 1:** Dark theme applied
- [ ] **Phase 2:** Left-side navigation sidebar built on Sheet 1
- [ ] **Phase 2:** Navigation links configured to each page
- [ ] **Phase 2:** Sidebar copied to all 6 sheets
- [ ] **Phase 3:** Global filter bar added (Date, Service, Environment)
- [ ] **Sheet 1:** Executive Overview — 4 KPI cards + 2 charts
- [ ] **Sheet 2:** System Performance — Latency scorecards + time series + bar + table
- [ ] **Sheet 3:** Error Analysis — Error scorecards + time series + stacked bar + error table
- [ ] **Sheet 4:** Infrastructure Usage — Environment cards + area chart + treemap + table
- [ ] **Sheet 5:** Cost Optimization — Recommendation table + bar chart + bubble chart
- [ ] **Sheet 6:** Log Explorer — Extra filters + full log table + severity charts
- [ ] **Final:** Responsive layout tested at 1920×1080 and 1366×768
- [ ] **Final:** Scheduled email delivery configured
- [ ] **Final:** Report shared with team

---

**End of Document**  
*Prepared by SYNTRIX Analytics Team — CloudMart Enterprise Observability Platform*
