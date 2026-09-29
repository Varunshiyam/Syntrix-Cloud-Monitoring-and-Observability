#!/usr/bin/env python3
"""
CLOUDPULSE — Complete Project Architecture & Implementation Guide
Professional PDF & DOCX Generator

Reverse-engineered technical documentation for the SYNTRIX CloudMart
hackathon project. Covers architecture, services, deployment, logging,
BigQuery, monitoring, alerting, FinOps, IAM, networking, and more.
"""

import re
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether, ListFlowable, ListItem
)
from reportlab.lib import colors

# ── Color Palette ──
ACCENT_BLUE = HexColor("#4285F4")
SUCCESS_GREEN = HexColor("#34A853")
ERROR_RED = HexColor("#EA4335")
WARNING_AMBER = HexColor("#FBBC04")
TEXT_PRIMARY = HexColor("#1a1a2e")
TEXT_SECONDARY = HexColor("#444466")
TEXT_LIGHT = HexColor("#666688")
TABLE_HEADER_BG = HexColor("#2C3E6B")
TABLE_ALT_ROW = HexColor("#F4F6FB")
BORDER_COLOR = HexColor("#D0D5E0")
CODE_BG = HexColor("#F0F2F5")
CALLOUT_BG = HexColor("#E8F0FE")
CALLOUT_BORDER = HexColor("#4285F4")
SECTION_BG = HexColor("#F8F9FA")

WIDTH, HEIGHT = A4


def build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'CoverTitle', parent=styles['Title'],
        fontSize=28, leading=34, textColor=TEXT_PRIMARY,
        alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        'CoverSubtitle', parent=styles['Normal'],
        fontSize=14, leading=20, textColor=TEXT_SECONDARY,
        alignment=TA_CENTER, fontName='Helvetica', spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        'CoverDetail', parent=styles['Normal'],
        fontSize=10, leading=14, textColor=TEXT_LIGHT,
        alignment=TA_CENTER, fontName='Helvetica', spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        'H1', parent=styles['Heading1'],
        fontSize=20, leading=26, textColor=ACCENT_BLUE,
        spaceBefore=24, spaceAfter=12, fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        'H2', parent=styles['Heading2'],
        fontSize=15, leading=20, textColor=HexColor("#2C3E6B"),
        spaceBefore=16, spaceAfter=8, fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        'H3', parent=styles['Heading3'],
        fontSize=12, leading=16, textColor=HexColor("#3D4F7C"),
        spaceBefore=12, spaceAfter=6, fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontSize=9.5, leading=14.5, textColor=TEXT_PRIMARY,
        spaceAfter=6, fontName='Helvetica', alignment=TA_JUSTIFY,
    ))
    styles.add(ParagraphStyle(
        'BulletItem', parent=styles['Normal'],
        fontSize=9.5, leading=14, textColor=TEXT_PRIMARY,
        spaceAfter=3, fontName='Helvetica',
        leftIndent=18, bulletIndent=8,
    ))
    styles.add(ParagraphStyle(
        'SubBulletItem', parent=styles['Normal'],
        fontSize=9, leading=13, textColor=TEXT_SECONDARY,
        spaceAfter=2, fontName='Helvetica',
        leftIndent=32, bulletIndent=22,
    ))
    styles.add(ParagraphStyle(
        'CodeBlock', parent=styles['Normal'],
        fontSize=8, leading=11, textColor=HexColor("#333355"),
        fontName='Courier', backColor=CODE_BG,
        leftIndent=10, rightIndent=10, spaceBefore=4, spaceAfter=6,
        borderWidth=0.5, borderColor=BORDER_COLOR, borderPadding=6,
    ))
    styles.add(ParagraphStyle(
        'Callout', parent=styles['Normal'],
        fontSize=9, leading=13, textColor=HexColor("#1a56a6"),
        fontName='Helvetica', backColor=CALLOUT_BG,
        leftIndent=10, rightIndent=10, spaceBefore=6, spaceAfter=8,
        borderWidth=1, borderColor=CALLOUT_BORDER, borderPadding=8,
    ))
    styles.add(ParagraphStyle(
        'Confirmed', parent=styles['Normal'],
        fontSize=8.5, leading=12, textColor=SUCCESS_GREEN,
        fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        'Inferred', parent=styles['Normal'],
        fontSize=8.5, leading=12, textColor=WARNING_AMBER,
        fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        'Unknown', parent=styles['Normal'],
        fontSize=8.5, leading=12, textColor=ERROR_RED,
        fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        'TOCEntry', parent=styles['Normal'],
        fontSize=10, leading=16, textColor=TEXT_PRIMARY,
        fontName='Helvetica', leftIndent=10, spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        'TOCEntryBold', parent=styles['Normal'],
        fontSize=10, leading=16, textColor=TEXT_PRIMARY,
        fontName='Helvetica-Bold', leftIndent=0, spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        'Footer', parent=styles['Normal'],
        fontSize=7.5, textColor=HexColor("#888888"),
        fontName='Helvetica',
    ))
    return styles


def make_table(headers, rows, col_widths=None):
    """Create a professional styled table."""
    data = [headers] + rows
    if col_widths is None:
        available = 170 * mm
        col_widths = [available / len(headers)] * len(headers)
    
    # Wrap cells in Paragraphs for word wrapping
    style = getSampleStyleSheet()
    header_style = ParagraphStyle('TH', parent=style['Normal'], fontSize=8, textColor=white, fontName='Helvetica-Bold', leading=11)
    cell_style = ParagraphStyle('TC', parent=style['Normal'], fontSize=8, textColor=TEXT_PRIMARY, fontName='Helvetica', leading=11)
    
    formatted = []
    for ri, row in enumerate(data):
        frow = []
        for cell in row:
            s = header_style if ri == 0 else cell_style
            frow.append(Paragraph(str(cell), s))
        formatted.append(frow)
    
    t = Table(formatted, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_BG),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, TABLE_ALT_ROW]),
    ]))
    return t


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(HexColor("#888888"))
    canvas.setFont('Helvetica', 7.5)
    canvas.drawString(20 * mm, 10 * mm, "SYNTRIX — CLOUDPULSE Complete Project Architecture & Implementation Guide")
    canvas.drawRightString(A4[0] - 20 * mm, 10 * mm, f"Page {doc.page}")
    canvas.setStrokeColor(BORDER_COLOR)
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, A4[1] - 18 * mm, A4[0] - 20 * mm, A4[1] - 18 * mm)
    canvas.line(20 * mm, 14 * mm, A4[0] - 20 * mm, 14 * mm)
    canvas.restoreState()


def h1(s, text): return Paragraph(text, s['H1'])
def h2(s, text): return Paragraph(text, s['H2'])
def h3(s, text): return Paragraph(text, s['H3'])
def body(s, text): return Paragraph(text, s['Body'])
def bullet(s, text): return Paragraph(f"•  {text}", s['BulletItem'])
def sub_bullet(s, text): return Paragraph(f"◦  {text}", s['SubBulletItem'])
def code(s, text): return Paragraph(text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), s['CodeBlock'])
def callout(s, text): return Paragraph(f"ℹ  {text}", s['Callout'])
def confirmed(s, text): return Paragraph(f"[CONFIRMED] {text}", s['Confirmed'])
def inferred(s, text): return Paragraph(f"[INFERRED] {text}", s['Inferred'])
def unknown(s, text): return Paragraph(f"[UNKNOWN] {text}", s['Unknown'])
def sp(height_mm=4): return Spacer(1, height_mm * mm)
def hr(): return HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=3*mm, spaceBefore=3*mm)
def pb(): return PageBreak()


def build_document():
    s = build_styles()
    f = []  # flowables

    # ═══════════════════════════════════════════════════════════════
    # COVER PAGE
    # ═══════════════════════════════════════════════════════════════
    f.append(sp(40))
    f.append(Paragraph("SYNTRIX", ParagraphStyle('Logo', parent=s['CoverTitle'], fontSize=48, textColor=ACCENT_BLUE)))
    f.append(sp(6))
    f.append(Paragraph("CLOUDPULSE", s['CoverTitle']))
    f.append(sp(4))
    f.append(Paragraph("Complete Project Architecture &amp; Implementation Guide", s['CoverSubtitle']))
    f.append(sp(6))
    f.append(HRFlowable(width="50%", thickness=2, color=ACCENT_BLUE, spaceAfter=6*mm))
    f.append(Paragraph("Reverse-Engineered Technical Documentation", s['CoverSubtitle']))
    f.append(sp(16))

    cover_info = [
        ["Project", "CloudMart Enterprise Observability Platform"],
        ["Team", "SYNTRIX"],
        ["Purpose", "Hackathon Project — CTS Cloud Innovation Challenge"],
        ["Document Type", "Reverse-Engineered Architecture & Implementation Guide"],
        ["Version", "1.0"],
        ["Generated", datetime.now().strftime("%d %B %Y, %H:%M IST")],
        ["GCP Project ID", "project-4e3f1563-833a-4721-bf7"],
        ["Region", "asia-south1 (Mumbai)"],
    ]
    ct = Table(cover_info, colWidths=[55*mm, 115*mm])
    ct.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), ACCENT_BLUE),
        ('TEXTCOLOR', (1, 0), (1, -1), TEXT_PRIMARY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER_COLOR),
    ]))
    f.append(ct)
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "Table of Contents"))
    f.append(sp(4))
    toc_items = [
        "1. Executive Summary",
        "2. Project Objective",
        "3. Actual Final Architecture",
        "4. Technology & Service Inventory",
        "5. Application Architecture",
        "6. Build From Zero — Chronological Roadmap",
        "7. Containerization",
        "8. Artifact Registry",
        "9. Cloud Run",
        "10. GKE (Google Kubernetes Engine)",
        "11. Compute Engine",
        "12. Cloud SQL",
        "13. Logging Architecture",
        "14. Log Streamer Daemon",
        "15. BigQuery",
        "16. ETL & Analytics",
        "17. Cloud Monitoring",
        "18. Alerting",
        "19. Looker Studio",
        "20. Cost Optimization / FinOps",
        "21. IAM & Security",
        "22. Networking",
        "23. End-to-End Runtime Flow",
        "24. Configuration Master Table",
        "25. Command Reference",
        "26. Design Decisions & Trade-offs",
        "27. Project Limitations",
        "28. What Is Actually Implemented vs Conceptual",
        "29. Presentation Talking Points",
        "30. Judge Q&A",
        "31. Personal Learning Roadmap",
        "32. Final Cheat Sheet",
        "Appendix",
    ]
    for item in toc_items:
        f.append(Paragraph(item, s['TOCEntry']))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 1: EXECUTIVE SUMMARY
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "1. Executive Summary"))
    f.append(body(s,
        "CloudPulse (codename: CloudMart) is a cloud-native e-commerce observability platform built by Team SYNTRIX "
        "for the CTS Cloud Innovation Hackathon. The project demonstrates a complete observability pipeline: "
        "from application microservices generating structured JSON logs, through Google Cloud's native logging "
        "infrastructure, into BigQuery for analytics, and finally visualized in Looker Studio dashboards — with "
        "Cloud Monitoring alerting layered on top."
    ))
    f.append(sp(2))
    f.append(body(s,
        "The system is architected across <b>three distinct GCP compute platforms</b> (Cloud Run, GKE, Compute Engine) "
        "to demonstrate multi-environment observability. A custom <b>Log Streamer Daemon</b> bridges Google Cloud Logging "
        "to BigQuery via API polling and NDJSON batch loading. Six BigQuery analytical views power Looker Studio dashboards "
        "covering latency, errors, usage, performance KPIs, and cost optimization recommendations."
    ))
    f.append(sp(2))
    f.append(callout(s,
        "<b>Key Innovation:</b> Unlike simple log-forwarding projects, CloudPulse implements a full-cycle observability pipeline "
        "with custom ETL, cross-platform log correlation via distributed tracing, simulation-driven chaos engineering for "
        "generating organic error telemetry, and SQL-based FinOps recommendations — all orchestrated across three compute environments."
    ))
    f.append(sp(4))

    f.append(h2(s, "At a Glance"))
    at_glance = [
        ["Metric", "Value"],
        ["Microservices", "6 (Gateway + 5 backend services)"],
        ["Compute Platforms", "3 (Cloud Run, GKE, Compute Engine)"],
        ["Database", "Cloud SQL PostgreSQL 15 (db-f1-micro)"],
        ["Log Pipeline", "Cloud Logging → Custom Streamer → BigQuery"],
        ["Analytics Views", "6 (cleaned logs + 5 analytical)"],
        ["Alert Policies", "5 (Cloud Run, GKE, GCE, BigQuery, Pipeline)"],
        ["Notification Channels", "7 email channels (team members)"],
        ["Event System", "Pub/Sub (order-events, payment-events, inventory-events)"],
        ["Frontend", "SPA with glassmorphism UI + Developer Control Panel"],
        ["Region", "asia-south1 (Mumbai)"],
    ]
    f.append(make_table(at_glance[0], at_glance[1:], [55*mm, 115*mm]))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 2: PROJECT OBJECTIVE
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "2. Project Objective"))
    f.append(body(s,
        "Build a production-style cloud-native application that generates rich, organic, structured JSON telemetry "
        "and demonstrates a complete observability pipeline on Google Cloud Platform."
    ))
    f.append(sp(2))
    f.append(h3(s, "Primary Goals"))
    for g in [
        "Demonstrate multi-platform deployment (Cloud Run + GKE + Compute Engine) of microservices",
        "Implement structured JSON logging with distributed tracing across all compute environments",
        "Build a custom log pipeline from Cloud Logging to BigQuery for analytical workloads",
        "Create analytical views and Looker Studio dashboards for operational intelligence",
        "Implement Cloud Monitoring alert policies for proactive incident detection",
        "Demonstrate FinOps/cost optimization through SQL-based traffic analysis",
        "Show simulation-driven chaos engineering for generating realistic error telemetry",
    ]:
        f.append(bullet(s, g))
    f.append(sp(2))
    f.append(h3(s, "Secondary Goals"))
    for g in [
        "Event-driven architecture via Pub/Sub for order, payment, and inventory events",
        "Kubernetes secrets management for sensitive database credentials",
        "IAM least-privilege service accounts for Cloud Run workloads",
        "VPC-based internal networking between Cloud Run, GKE, and Cloud SQL",
    ]:
        f.append(bullet(s, g))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 3: ACTUAL FINAL ARCHITECTURE
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "3. Actual Final Architecture"))
    f.append(body(s,
        "The following architecture was reverse-engineered from the actual repository source code, deployment scripts, "
        "Kubernetes manifests, Cloud Run configurations, and BigQuery SQL. Every component listed below has direct "
        "evidence in the codebase."
    ))
    f.append(sp(2))
    f.append(h2(s, "3.1 Application & Data Flow Architecture"))
    
    arch_text = """USER (Browser)
   │  HTTPS
   ↓
FastAPI Gateway  ← Cloud Run (syntrix-gateway)
   │  Serves SPA frontend (index.html, app.js, admin.js)
   │  Proxies /api/* requests to backend services
   │
   ├── /api/products, /api/categories, /api/search
   │      → Catalog Service ← Cloud Run (syntrix-catalog)
   │
   ├── /api/cart, /api/cart/items
   │      → Cart Service ← Cloud Run (syntrix-cart)
   │
   ├── /api/checkout, /api/orders
   │      → Order Service ← GKE (order-deployment)
   │          ├── calls Cart Service (validate cart)
   │          ├── calls Inventory Service (reserve stock)
   │          ├── calls Payment Service (process payment)
   │          └── publishes to Pub/Sub (order-events)
   │
   ├── /api/payments
   │      → Payment Service ← GKE (payment-deployment)
   │          └── publishes to Pub/Sub (payment-events)
   │
   └── /api/inventory
          → Inventory Service ← Compute Engine (syntrix-inventory)
              └── publishes to Pub/Sub (inventory-events)

ALL SERVICES → Cloud SQL PostgreSQL (syntrix-postgres)"""
    
    for line in arch_text.split('\n'):
        f.append(code(s, line))
    f.append(sp(4))

    f.append(h2(s, "3.2 Observability Pipeline Architecture"))
    obs_text = """ALL SERVICES (Cloud Run / GKE / Compute Engine)
   │  Structured JSON logs → stdout
   ↓
Google Cloud Logging
   │  Automatic ingestion by platform
   ↓
Log Streamer Daemon (realtime_log_streamer.py)
   │  Polls via: gcloud logging read (every 10 seconds)
   │  Filters: resource.type = cloud_run_revision | gce_instance | k8s_container
   │  Sanitizes keys, stringifies nested JSON
   │  Writes batch to /tmp/stream_batch.ndjson
   ↓
BigQuery (syntrix_logs.raw_logs)
   │  Loaded via: bq load --source_format=NEWLINE_DELIMITED_JSON
   ↓
BigQuery Views (ETL)
   ├── looker_cleaned_logs        (base cleaning + field extraction)
   ├── looker_latency_analysis    (avg/max latency by service/endpoint)
   ├── looker_error_analysis      (4xx/5xx rates by service)
   ├── looker_usage_monitoring    (daily request counts by endpoint)
   ├── looker_performance_kpis    (p50/p90/p99 latency, success rate)
   └── looker_cost_optimization   (traffic-based cost recommendations)
   ↓
Looker Studio Dashboards (6 sheets)

PARALLEL: Cloud Monitoring
   ├── Alert: Cloud Run 5xx Errors → Email (Babu, Mugunthan)
   ├── Alert: GKE High CPU → Email (Akash)
   ├── Alert: GCE High CPU → Email (Roshni, Swathi)
   ├── Alert: BigQuery High Execution Time → Email (Ecclesiastes, Emayan)
   └── Alert: Log Pipeline Errors → Email (Varunshiyam)"""

    for line in obs_text.split('\n'):
        f.append(code(s, line))
    f.append(sp(2))
    f.append(confirmed(s, "Architecture verified from: gateway/main.py, deploy_*.sh, deploy_gke.sh K8s manifests, "
                          "realtime_log_streamer.py, bq_views.sql, create_alerts.sh"))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 4: TECHNOLOGY & SERVICE INVENTORY
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "4. Technology &amp; Service Inventory"))
    f.append(body(s, "Classification of every Google Cloud service based on evidence found in the repository:"))
    f.append(sp(2))

    svc_rows = [
        ["Cloud Run", "ACTUALLY IMPLEMENTED", "Gateway, Catalog, Cart deployed as Cloud Run services; Seed as Cloud Run Job"],
        ["Artifact Registry", "ACTUALLY IMPLEMENTED", "syntrix-cloudmart repository in asia-south1-docker.pkg.dev"],
        ["GKE (Autopilot)", "ACTUALLY IMPLEMENTED", "syntrix-gke cluster; Order + Payment deployments with LoadBalancer services"],
        ["Compute Engine", "ACTUALLY IMPLEMENTED", "syntrix-inventory VM (e2-micro) in asia-south1-a with Docker startup script"],
        ["Cloud Logging", "ACTUALLY IMPLEMENTED", "Automatic ingestion from all platforms; structured JSON via python-json-logger"],
        ["Cloud Monitoring", "ACTUALLY IMPLEMENTED", "5 alert policies created via create_alerts.sh and fix_alerts.py"],
        ["BigQuery", "ACTUALLY IMPLEMENTED", "syntrix_logs dataset with raw_logs table + 6 analytical views"],
        ["Looker Studio", "ACTUALLY IMPLEMENTED", "Dashboard design documented in Looker_Dashboard_Design.md (1143 lines)"],
        ["Cloud SQL", "ACTUALLY IMPLEMENTED", "syntrix-postgres (PostgreSQL 15, db-f1-micro) in asia-south1"],
        ["Pub/Sub", "ACTUALLY IMPLEMENTED", "3 topics: order-events, payment-events, inventory-events; publisher in code"],
        ["Secret Manager", "ACTUALLY IMPLEMENTED", "database-url secret created in setup_cloudsql.sh"],
        ["IAM", "ACTUALLY IMPLEMENTED", "cloudrun-app-sa service account, roles/cloudsql.client, secretmanager.secretAccessor"],
        ["VPC Networking", "ACTUALLY IMPLEMENTED", "Default VPC, firewall rules, vpc-egress=all-traffic for Cloud Run"],
        ["Cloud Storage", "PARTIALLY IMPLEMENTED", "gs://project-...-logs-bucket referenced in export_logs.sh for log staging"],
        ["Log Router / Sink", "NOT IMPLEMENTED", "Logs are polled via gcloud CLI, not exported via native log sinks"],
        ["Cloud Functions", "NOT IMPLEMENTED", "No evidence in repository"],
        ["Cloud Scheduler", "NOT IMPLEMENTED", "No evidence in repository"],
        ["API Gateway (managed)", "NOT IMPLEMENTED", "Custom FastAPI gateway used instead"],
        ["Recommender API", "NOT IMPLEMENTED", "Cost recommendations are custom SQL logic, not GCP Recommender"],
        ["Cloud Billing API", "NOT IMPLEMENTED", "No billing API integration found"],
        ["Load Balancing (explicit)", "PARTIALLY IMPLEMENTED", "GKE internal LoadBalancer services; no external HTTP(S) LB"],
    ]
    f.append(make_table(
        ["Service", "Status", "Evidence"],
        svc_rows,
        [35*mm, 35*mm, 100*mm]
    ))
    f.append(sp(2))

    f.append(h2(s, "Application Technology Stack"))
    tech_rows = [
        ["Language", "Python 3.12"],
        ["Web Framework", "FastAPI + Uvicorn"],
        ["ORM", "SQLAlchemy"],
        ["Database", "PostgreSQL 15"],
        ["HTTP Client", "httpx (async)"],
        ["Logging", "python-json-logger (pythonjsonlogger)"],
        ["Container Runtime", "Docker (python:3.12-slim)"],
        ["Frontend", "Vanilla HTML/CSS/JS (SPA)"],
        ["Pub/Sub Client", "google-cloud-pubsub"],
        ["Migrations", "Alembic (configured but migrations not generated)"],
        ["Testing", "pytest + httpx (async)"],
    ]
    f.append(make_table(["Component", "Technology"], tech_rows, [45*mm, 125*mm]))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 5: APPLICATION ARCHITECTURE
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "5. Application Architecture"))
    f.append(body(s,
        "CloudMart is a microservices-based e-commerce platform consisting of 6 services (1 gateway + 5 backend) "
        "that communicate via HTTP REST. All services share a common PostgreSQL database via SQLAlchemy ORM and "
        "emit structured JSON logs via a shared logging library."
    ))
    f.append(sp(2))

    f.append(h2(s, "5.1 Service Inventory"))
    svc_detail = [
        ["Gateway", "gateway/main.py", "FastAPI", "Cloud Run", "8080",
         "API proxy, frontend hosting, simulation config", "Catalog, Cart, Order, Payment, Inventory (via HTTP proxy)"],
        ["Catalog", "services/catalog/main.py", "FastAPI", "Cloud Run", "8080",
         "Product listing, search, categories", "PostgreSQL (read-only)"],
        ["Cart", "services/cart/main.py", "FastAPI", "Cloud Run", "8080",
         "Cart CRUD, item management", "PostgreSQL (read-write)"],
        ["Order", "services/order/main.py", "FastAPI", "GKE", "8080",
         "Checkout orchestration, order lifecycle", "Cart, Inventory, Payment (HTTP); Pub/Sub; PostgreSQL"],
        ["Payment", "services/payment/main.py", "FastAPI", "GKE", "8080",
         "Payment processing, simulation modes", "Pub/Sub; PostgreSQL"],
        ["Inventory", "services/inventory/main.py", "FastAPI", "Compute Engine", "8000",
         "Stock management, reserve/release", "Pub/Sub; PostgreSQL"],
    ]
    f.append(make_table(
        ["Service", "Entry Point", "Framework", "Platform", "Port", "Responsibilities", "Dependencies"],
        svc_detail,
        [20*mm, 32*mm, 14*mm, 20*mm, 10*mm, 40*mm, 34*mm]
    ))
    f.append(sp(4))

    f.append(h2(s, "5.2 Service Dependency Map"))
    dep_text = """Gateway (Cloud Run)
 ├── Catalog Service (Cloud Run)        — product browsing
 ├── Cart Service (Cloud Run)           — cart management
 ├── Order Service (GKE)                — checkout orchestration
 │      ├── Cart Service                — validates cart contents
 │      ├── Inventory Service (GCE)     — reserves stock
 │      ├── Payment Service (GKE)       — processes payment
 │      └── Pub/Sub (order-events)      — publishes order.created
 ├── Payment Service (GKE)              — direct payment queries
 │      └── Pub/Sub (payment-events)    — publishes payment.completed/failed
 └── Inventory Service (Compute Engine) — stock queries
        └── Pub/Sub (inventory-events)  — publishes inventory.reserved/insufficient"""
    for line in dep_text.split('\n'):
        f.append(code(s, line))
    f.append(sp(2))
    f.append(confirmed(s, "Verified from: gateway/main.py SERVICES map, order/main.py HTTP calls, "
                          "payment/main.py and inventory/main.py Pub/Sub publishers"))
    f.append(sp(4))

    f.append(h2(s, "5.3 API Endpoint Reference"))
    api_rows = [
        ["GET", "/api/products", "Gateway → Catalog", "List all products"],
        ["GET", "/api/products/{id}", "Gateway → Catalog", "Get single product"],
        ["GET", "/api/categories", "Gateway → Catalog", "List categories"],
        ["GET", "/api/search?q=", "Gateway → Catalog", "Search products"],
        ["POST", "/api/cart", "Gateway → Cart", "Create new cart"],
        ["GET", "/api/cart/{id}", "Gateway → Cart", "Get cart contents"],
        ["POST", "/api/cart/items", "Gateway → Cart", "Add item to cart"],
        ["PUT", "/api/cart/items/{id}", "Gateway → Cart", "Update item quantity"],
        ["DELETE", "/api/cart/items/{id}", "Gateway → Cart", "Remove item"],
        ["POST", "/api/checkout", "Gateway → Order", "Full checkout flow"],
        ["GET", "/api/orders", "Gateway → Order", "List all orders"],
        ["GET", "/api/orders/{id}", "Gateway → Order", "Get single order"],
        ["POST", "/api/payments", "Gateway → Payment", "Process payment"],
        ["GET", "/api/payments/{id}", "Gateway → Payment", "Get payment"],
        ["GET", "/api/inventory", "Gateway → Inventory", "List inventory"],
        ["POST", "/api/inventory/reserve", "Gateway → Inventory", "Reserve stock"],
        ["POST", "/api/inventory/release", "Gateway → Inventory", "Release stock"],
        ["GET/POST", "/api/simulation", "Gateway (direct)", "Simulation config"],
        ["GET", "/health", "All services", "Health check"],
    ]
    f.append(make_table(
        ["Method", "Endpoint", "Route", "Description"],
        api_rows,
        [16*mm, 40*mm, 40*mm, 74*mm]
    ))
    f.append(sp(4))

    f.append(h2(s, "5.4 Database Schema"))
    f.append(body(s, "All services share a single PostgreSQL database (cloudmart) with the following tables, "
                     "defined in shared/models/models.py using SQLAlchemy declarative_base:"))
    schema_rows = [
        ["products", "id, sku, name, category, price, stock, rating", "Product catalog, seeded with 50 items"],
        ["customers", "id, name, email", "Customer records (1 seeded: John Doe)"],
        ["carts", "id, customer_id (FK→customers)", "Shopping cart containers"],
        ["cart_items", "id, cart_id (FK→carts), product_id (FK→products), quantity", "Cart line items"],
        ["orders", "id, customer_id (FK→customers), total_amount, payment_status, order_status, created_at", "Order records"],
        ["payments", "id, order_id (FK→orders), amount, status, created_at", "Payment transaction records"],
        ["inventory_transactions", "id, product_id (FK→products), quantity, transaction_type, created_at", "Stock movement audit log"],
        ["simulation_config", "key (PK), value", "Runtime simulation settings (payment_mode, inventory_mode, db_mode)"],
    ]
    f.append(make_table(
        ["Table", "Columns", "Purpose"],
        schema_rows,
        [30*mm, 80*mm, 60*mm]
    ))
    f.append(sp(2))

    f.append(h2(s, "5.5 Simulation / Chaos Engineering"))
    f.append(body(s,
        "The application includes a built-in chaos engineering system controlled via the Developer Control Panel "
        "in the frontend footer. Settings are stored in the simulation_config table and checked at runtime."
    ))
    sim_rows = [
        ["payment_mode", "normal | 20_timeout | 50_timeout | declined", "Simulates payment failures: 20% timeout, 50% timeout, or 30% declined"],
        ["inventory_mode", "healthy | low_stock | out_of_stock", "Simulates inventory issues: forces stock to 2 or refuses all reservations"],
        ["db_mode", "normal | slow_queries", "Injects 1.5 second delay into all database operations"],
    ]
    f.append(make_table(
        ["Config Key", "Possible Values", "Effect"],
        sim_rows,
        [30*mm, 55*mm, 85*mm]
    ))
    f.append(sp(2))
    f.append(body(s,
        "The frontend also includes a <b>Traffic Simulator</b> that can generate 10, 50, 100, or 250 concurrent "
        "simulated users performing browse → add-to-cart → checkout flows. This is how organic, realistic "
        "log data is generated for the observability pipeline."
    ))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 6: BUILD FROM ZERO
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "6. Build From Zero — Chronological Roadmap"))
    f.append(body(s, "Reconstructed build sequence based on repository evidence, script dependencies, and deployment order:"))
    f.append(sp(2))

    steps = [
        ("Step 1", "Application Architecture Design",
         "Designed 6-service microservice architecture with shared libraries",
         "Created: shared/logging/logger.py, shared/middleware/tracing.py, shared/models/models.py, shared/utils/database.py",
         "gateway/main.py, services/*/main.py"),
        ("Step 2", "Local Development Environment",
         "Built docker-compose.yml for local development with PostgreSQL + all services",
         "All 6 services run locally on port 8000 behind the gateway; seed data populates 50 products",
         "docker-compose.yml, database/seed_data/seed.py"),
        ("Step 3", "Frontend Development",
         "Built glassmorphism SPA with dashboard, catalog, cart, checkout, orders views",
         "Developer Control Panel for chaos engineering; Traffic Simulator for load generation",
         "frontend/index.html, frontend/app.js, frontend/admin.js, frontend/styles.css"),
        ("Step 4", "Containerization",
         "Created multi-service Dockerfile using SERVICE_NAME build arg for image reuse",
         "Single Dockerfile builds any service by changing the build argument",
         "Dockerfile, Dockerfile.seed"),
        ("Step 5", "Cloud SQL Setup",
         "Provisioned Cloud SQL PostgreSQL 15 (db-f1-micro) in asia-south1",
         "Created database, user, Secret Manager secret, service account with cloudsql.client role",
         "setup_cloudsql.sh"),
        ("Step 6", "Artifact Registry",
         "Created syntrix-cloudmart repository for Docker images",
         "All images tagged and pushed to asia-south1-docker.pkg.dev",
         "deploy_phase1.sh (gcloud auth configure-docker)"),
        ("Step 7", "Cloud Run Deployment (Phase 1)",
         "Deployed gateway, cart, catalog as Cloud Run services; seed as Cloud Run Job",
         "Allow-unauthenticated access, Cloud SQL connector, environment variables",
         "deploy_phase1.sh, update_cloudrun_sql.sh, setup_seed.sh"),
        ("Step 8", "GKE Cluster & Deployment",
         "Created Autopilot cluster syntrix-gke; deployed order + payment services",
         "Kubernetes Deployments (1 replica each), LoadBalancer Services (internal), db-secret for DATABASE_URL",
         "setup_gke_cluster.sh, deploy_gke.sh"),
        ("Step 9", "Compute Engine Deployment",
         "Created e2-micro VM syntrix-inventory with Docker startup script",
         "Pulls image from Artifact Registry, gets DB_URL from instance metadata, firewall rule for internal traffic",
         "deploy_inventory.sh, startup.sh"),
        ("Step 10", "Gateway Integration",
         "Updated gateway with actual service URLs (Cloud Run URLs, GKE internal IPs, GCE internal IP)",
         "VPC egress for Cloud Run → internal services, identity token for Cloud Run → Cloud Run auth",
         "update_cloudrun_sql.sh"),
        ("Step 11", "Structured Logging Implementation",
         "Implemented CustomJsonFormatter with Cloud Logging integration fields",
         "Fields: timestamp, severity, service, environment, request_id, trace_id, logging.googleapis.com/trace",
         "shared/logging/logger.py, shared/middleware/tracing.py"),
        ("Step 12", "Pub/Sub Event System",
         "Added Pub/Sub publishers to Order, Payment, and Inventory services",
         "Topics: order-events, payment-events, inventory-events; events published on key business actions",
         "services/order/main.py, services/payment/main.py, services/inventory/main.py"),
        ("Step 13", "Log Export & BigQuery Load",
         "Created export_logs.sh for initial bulk log extraction + prepare_bq_json.py for sanitization",
         "Reads from Cloud Logging, converts to NDJSON, uploads to GCS, loads into BigQuery",
         "export_logs.sh, prepare_bq_json.py"),
        ("Step 14", "Realtime Log Streamer",
         "Created Python daemon for continuous log polling and BigQuery loading",
         "10-second polling interval, 2000-log batch limit, key sanitization, incremental timestamp tracking",
         "realtime_log_streamer.py"),
        ("Step 15", "BigQuery Analytics Views",
         "Created 6 analytical views for Looker Studio consumption",
         "ETL from raw_logs → cleaned → latency/error/usage/KPI/cost analysis",
         "bq_views.sql"),
        ("Step 16", "Cloud Monitoring Alerts",
         "Created 5 alert policies with 7 notification channels (email)",
         "Cloud Run 5xx, GKE CPU, GCE CPU, BigQuery execution time, Pipeline errors",
         "create_alerts.sh, fix_alerts.py, add_mugunthan.py"),
        ("Step 17", "Looker Studio Dashboard Design",
         "Designed 6-sheet dashboard with complete implementation guide",
         "Executive overview, performance, errors, infrastructure, cost optimization, log explorer",
         "Looker_Dashboard_Design.md, Looker_Dashboard_Design.pdf"),
        ("Step 18", "Traffic Simulation & Testing",
         "Created test scripts and traffic simulators for organic log generation",
         "simulate_traffic.sh, inject_gce_logs.sh, test_checkout.py, test_integration.py",
         "simulate_traffic.sh, test_*.py"),
    ]
    
    for step_num, title, what, detail, files in steps:
        f.append(h3(s, f"{step_num}: {title}"))
        f.append(bullet(s, f"<b>What:</b> {what}"))
        f.append(bullet(s, f"<b>Detail:</b> {detail}"))
        f.append(bullet(s, f"<b>Files:</b> {files}"))
        f.append(sp(2))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 7: CONTAINERIZATION
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "7. Containerization"))
    f.append(body(s,
        "The project uses a single, parameterized Dockerfile that builds any service by changing the "
        "SERVICE_NAME build argument. This is an elegant approach that avoids Dockerfile duplication."
    ))
    f.append(sp(2))
    f.append(h3(s, "Dockerfile Analysis"))
    f.append(bullet(s, "<b>Base Image:</b> python:3.12-slim — minimal Python image for small container size"))
    f.append(bullet(s, "<b>Build Arg:</b> SERVICE_NAME — determines which service code is copied (e.g., services/cart, gateway)"))
    f.append(bullet(s, "<b>Shared Library:</b> shared/ is always copied to /app/shared (logging, middleware, models, DB utils)"))
    f.append(bullet(s, "<b>Frontend:</b> frontend/ is always copied (required by gateway, harmless for other services)"))
    f.append(bullet(s, "<b>Port:</b> EXPOSE 8000; actual port set via PORT env var (default 8080 in CMD)"))
    f.append(bullet(s, "<b>Workers:</b> 2 Uvicorn workers per container"))
    f.append(bullet(s, "<b>PYTHONPATH:</b> Set to /app for proper import resolution"))
    f.append(sp(2))
    f.append(h3(s, "Build Command Pattern"))
    f.append(code(s, "docker buildx build --platform linux/amd64 \\"))
    f.append(code(s, "  -t asia-south1-docker.pkg.dev/PROJECT_ID/syntrix-cloudmart/SERVICE:VERSION \\"))
    f.append(code(s, "  --build-arg SERVICE_NAME=services/cart --push ."))
    f.append(sp(2))
    f.append(callout(s, "<b>Why --platform linux/amd64?</b> The development machine is macOS (likely Apple Silicon/ARM). "
                       "GCP Cloud Run and GKE nodes run on AMD64/x86_64. Cross-platform build is required."))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 8: ARTIFACT REGISTRY
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "8. Artifact Registry"))
    f.append(body(s, "All container images are stored in Google Artifact Registry."))
    ar_rows = [
        ["Repository", "syntrix-cloudmart"],
        ["Location", "asia-south1-docker.pkg.dev"],
        ["Full Path", "asia-south1-docker.pkg.dev/project-4e3f1563-833a-4721-bf7/syntrix-cloudmart"],
        ["Format", "Docker"],
        ["Auth Config", "gcloud auth configure-docker asia-south1-docker.pkg.dev"],
    ]
    f.append(make_table(["Property", "Value"], ar_rows, [40*mm, 130*mm]))
    f.append(sp(2))
    f.append(h3(s, "Known Image Tags"))
    img_rows = [
        ["gateway", "1.0.0"],
        ["cart", "1.0.0"],
        ["catalog", "Not explicit in scripts (deployed via Cloud Run)"],
        ["order", "1.0.1, 1.0.2"],
        ["payment", "1.0.1, 1.0.2"],
        ["inventory", "1.0.0"],
        ["seed", "1.0.0"],
    ]
    f.append(make_table(["Image", "Tags Found"], img_rows, [40*mm, 130*mm]))
    f.append(sp(2))
    f.append(inferred(s, "Order and Payment images have multiple versions (1.0.1, 1.0.2), suggesting at least one re-deployment "
                        "iteration — likely to fix database connectivity or environment configuration issues."))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 9: CLOUD RUN
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "9. Cloud Run"))
    f.append(body(s, "Three services + one job are deployed to Cloud Run:"))
    f.append(sp(2))

    cr_services = [
        ["syntrix-gateway", "asia-south1-docker.pkg.dev/.../gateway:1.0.0", "asia-south1",
         "SERVICE_NAME=gateway, CATALOG_URL=https://syntrix-catalog-..., CART_URL=https://syntrix-cart-..., "
         "ORDER_URL=http://10.160.0.5:8000, PAYMENT_URL=http://10.160.0.7:8000, INVENTORY_URL=http://10.160.0.6:8000, "
         "DATABASE_URL=postgresql://cloudmart_user:...@/cloudmart?host=/cloudsql/...",
         "allUsers (unauthenticated)", "Cloud SQL connector, VPC egress=all-traffic, network=default"],
        ["syntrix-catalog", "asia-south1-docker.pkg.dev/.../catalog:*", "asia-south1",
         "SERVICE_NAME=catalog-service, DATABASE_URL=...",
         "allUsers (unauthenticated)", "Cloud SQL connector"],
        ["syntrix-cart", "asia-south1-docker.pkg.dev/.../cart:1.0.0", "asia-south1",
         "SERVICE_NAME=cart-service, DATABASE_URL=...",
         "allUsers (unauthenticated)", "Cloud SQL connector"],
    ]
    f.append(make_table(
        ["Service", "Image", "Region", "Env Vars (key ones)", "Auth", "Config"],
        cr_services,
        [22*mm, 28*mm, 16*mm, 50*mm, 22*mm, 32*mm]
    ))
    f.append(sp(2))

    f.append(h3(s, "Cloud Run Job: syntrix-seed"))
    f.append(bullet(s, "<b>Image:</b> asia-south1-docker.pkg.dev/.../seed:1.0.0"))
    f.append(bullet(s, "<b>Purpose:</b> One-time database schema creation + seed 50 products + default simulation config"))
    f.append(bullet(s, "<b>VPC:</b> vpc-egress=all-traffic, network=default (required to reach Cloud SQL)"))
    f.append(sp(2))

    f.append(callout(s,
        "<b>Critical Architecture Detail:</b> The gateway connects to GKE and Compute Engine services via "
        "<b>internal IP addresses</b> (10.160.0.5, 10.160.0.6, 10.160.0.7), not via public URLs. This requires "
        "VPC egress configuration on Cloud Run (--vpc-egress=all-traffic --network=default). The gateway also "
        "connects to other Cloud Run services (catalog, cart) via their public HTTPS URLs with identity token authentication."
    ))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 10: GKE
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "10. GKE (Google Kubernetes Engine)"))
    f.append(h2(s, "10.1 Cluster Configuration"))
    gke_rows = [
        ["Cluster Name", "syntrix-gke"],
        ["Type", "Autopilot (created via create-auto)"],
        ["Region", "asia-south1"],
        ["Node Management", "Fully managed by Google (Autopilot)"],
        ["Image Pull Secret", "gcr-json-key (referenced in manifests)"],
    ]
    f.append(make_table(["Property", "Value"], gke_rows, [45*mm, 125*mm]))
    f.append(sp(2))
    
    f.append(h2(s, "10.2 Workloads"))
    f.append(h3(s, "Order Service Deployment"))
    order_k8s = [
        ["Kind", "Deployment"],
        ["Name", "order-deployment"],
        ["Replicas", "1"],
        ["Container Image", "asia-south1-docker.pkg.dev/.../order:1.0.2"],
        ["Container Port", "8080"],
        ["DATABASE_URL", "From Kubernetes Secret (db-secret)"],
        ["Service Type", "LoadBalancer (Internal)"],
        ["Service Port", "8000 → 8080 (targetPort)"],
        ["Selector", "app: order"],
    ]
    f.append(make_table(["Property", "Value"], order_k8s, [40*mm, 130*mm]))
    f.append(sp(2))

    f.append(h3(s, "Payment Service Deployment"))
    pay_k8s = [
        ["Kind", "Deployment"],
        ["Name", "payment-deployment"],
        ["Replicas", "1"],
        ["Container Image", "asia-south1-docker.pkg.dev/.../payment:1.0.2"],
        ["Container Port", "8080"],
        ["DATABASE_URL", "From Kubernetes Secret (db-secret)"],
        ["Service Type", "LoadBalancer (Internal)"],
        ["Service Port", "8000 → 8080 (targetPort)"],
        ["Selector", "app: payment"],
    ]
    f.append(make_table(["Property", "Value"], pay_k8s, [40*mm, 130*mm]))
    f.append(sp(2))

    f.append(callout(s,
        '<b>Why GKE for Order &amp; Payment?</b> These services handle complex orchestration (Order calls Cart → Inventory '
        '→ Payment → Pub/Sub) and financial transactions. GKE provides persistent pods, direct internal networking, '
        'and the ability to demonstrate Kubernetes-native operations. It also creates a distinct resource.type '
        '(k8s_container) in Cloud Logging for multi-platform observability demonstrations.'
    ))
    f.append(sp(2))
    f.append(body(s,
        "<b>Database Secret:</b> The DATABASE_URL is stored as a Kubernetes Secret (db-secret) created via "
        "kubectl create secret generic. The URL points directly to the Cloud SQL instance's public IP "
        "(34.14.131.84) with cloudmart_user credentials."
    ))
    f.append(inferred(s, "GKE connects to Cloud SQL via public IP (34.14.131.84), not via Cloud SQL Auth Proxy. "
                        "This was likely a pragmatic hackathon decision for simplicity."))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 11: COMPUTE ENGINE
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "11. Compute Engine"))
    gce_rows = [
        ["VM Name", "syntrix-inventory"],
        ["Machine Type", "e2-micro (0.25 vCPU, 1 GB RAM)"],
        ["Zone", "asia-south1-a"],
        ["Tags", "http-server"],
        ["Scopes", "cloud-platform (full access)"],
        ["Startup Script", "Installs Docker, pulls inventory image, runs container"],
        ["DATABASE_URL", "Passed via instance metadata (database-url attribute)"],
        ["Container", "inventory:1.0.0 running on port 8000"],
        ["Firewall Rule", "allow-inventory-internal: tcp:8080 from 10.0.0.0/8"],
    ]
    f.append(make_table(["Property", "Value"], gce_rows, [35*mm, 135*mm]))
    f.append(sp(2))
    f.append(callout(s,
        "<b>Why Compute Engine for Inventory?</b> This demonstrates a legacy/stateful workload pattern. The Inventory service "
        "simulates a component that might exist on a traditional VM in a real enterprise migration. It creates gce_instance "
        "resource type in Cloud Logging, completing the three-platform observability story."
    ))
    f.append(sp(2))
    f.append(body(s,
        "The startup script retrieves the database URL from GCE instance metadata using the metadata server "
        "(http://metadata.google.internal/computeMetadata/v1/instance/attributes/database-url). This avoids "
        "hardcoding credentials in the startup script."
    ))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 12: CLOUD SQL
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "12. Cloud SQL"))
    sql_rows = [
        ["Instance Name", "syntrix-postgres"],
        ["Engine", "PostgreSQL 15"],
        ["Tier", "db-f1-micro (shared vCPU, 0.6 GB RAM)"],
        ["Region", "asia-south1"],
        ["Database Name", "cloudmart"],
        ["User", "cloudmart_user"],
        ["Password", "syntrix_admin_123 (hardcoded in deploy scripts; originally generated via openssl)"],
        ["Connection Name", "project-4e3f1563-833a-4721-bf7:asia-south1:syntrix-postgres"],
        ["Tables", "8 (products, customers, carts, cart_items, orders, payments, inventory_transactions, simulation_config)"],
    ]
    f.append(make_table(["Property", "Value"], sql_rows, [35*mm, 135*mm]))
    f.append(sp(2))

    f.append(h3(s, "Connectivity Patterns"))
    conn_rows = [
        ["Cloud Run", "Cloud SQL Auth Proxy (Unix socket via --add-cloudsql-instances)", "CONFIRMED"],
        ["GKE", "Direct TCP to public IP (34.14.131.84:5432)", "CONFIRMED"],
        ["Compute Engine", "Direct TCP to public IP (via metadata-derived URL)", "CONFIRMED"],
        ["Local Dev", "Docker Compose PostgreSQL on localhost:5432", "CONFIRMED"],
    ]
    f.append(make_table(["Platform", "Connection Method", "Status"], conn_rows, [30*mm, 110*mm, 30*mm]))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 13: LOGGING ARCHITECTURE
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "13. Logging Architecture"))
    f.append(body(s,
        "CloudMart implements structured JSON logging using python-json-logger. Every service emits logs to stdout, "
        "which are automatically captured by the respective compute platform's logging agent and forwarded to "
        "Google Cloud Logging."
    ))
    f.append(sp(2))

    f.append(h2(s, "13.1 Log Format"))
    f.append(body(s, "Each log entry contains the following fields (from CustomJsonFormatter in shared/logging/logger.py):"))
    log_fields = [
        ["timestamp", "UTC ISO 8601 (e.g., 2026-08-25T13:45:12.123Z)", "Always"],
        ["severity", "INFO, WARNING, ERROR", "Always"],
        ["message", "Human-readable log message", "Always"],
        ["service", "From SERVICE_NAME env var", "Always"],
        ["environment", "From ENVIRONMENT env var (local/cloud)", "Always"],
        ["request_id", "UUID from X-Request-Id header or auto-generated", "When request context exists"],
        ["trace_id", "UUID from X-Trace-Id header or auto-generated", "When request context exists"],
        ["logging.googleapis.com/trace", "projects/PROJECT_ID/traces/TRACE_ID", "When trace_id exists"],
        ["logging.googleapis.com/spanId", "First 16 chars of trace_id", "When trace_id exists"],
        ["event", "Business event type (e.g., order_created, payment_processed)", "Application logs"],
        ["endpoint", "HTTP path", "Request completion logs"],
        ["method", "HTTP method", "Request completion logs"],
        ["status_code", "HTTP response code", "Request completion logs"],
        ["latency_ms", "Request processing time in milliseconds", "Request completion logs"],
    ]
    f.append(make_table(
        ["Field", "Value", "Presence"],
        log_fields,
        [45*mm, 80*mm, 45*mm]
    ))
    f.append(sp(2))

    f.append(h2(s, "13.2 Distributed Tracing"))
    f.append(body(s,
        "Distributed tracing is implemented via Python ContextVars. The TracingMiddleware (shared/middleware/tracing.py) "
        "extracts or generates X-Request-Id and X-Trace-Id headers on each request, stores them in thread-local context "
        "variables, and injects them into all downstream HTTP calls. This creates a correlation chain:"
    ))
    trace_flow = """Gateway receives request
  → Generates/extracts request_id and trace_id
  → Stores in ContextVars (request_id_var, trace_id_var)
  → Injects into outgoing HTTP headers
  → Each downstream service extracts the same IDs
  → All logs from the same user request share the same trace_id
  → Cloud Logging correlates them via logging.googleapis.com/trace"""
    for line in trace_flow.split('\n'):
        f.append(code(s, line.strip()))
    f.append(sp(2))
    f.append(confirmed(s, "Verified: ContextVars in logger.py, TracingMiddleware in tracing.py, header propagation in gateway/main.py and order/main.py"))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 14: LOG STREAMER DAEMON
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "14. Log Streamer Daemon"))
    f.append(body(s,
        "The Log Streamer (realtime_log_streamer.py) is a custom Python daemon that bridges Google Cloud Logging "
        "to BigQuery. It was built because native Log Sinks to BigQuery were not used in this architecture."
    ))
    f.append(sp(2))
    streamer_rows = [
        ["Polling Method", "gcloud logging read (subprocess)"],
        ["Poll Interval", "10 seconds"],
        ["Batch Size", "Up to 2000 log entries per poll"],
        ["Filter", 'resource.type=(\"cloud_run_revision\" OR \"gce_instance\" OR \"k8s_container\")'],
        ["Deduplication", "Incremental timestamp tracking (last_timestamp + 1 nanosecond)"],
        ["Output Format", "NDJSON (Newline-Delimited JSON)"],
        ["Temp File", "/tmp/stream_batch.ndjson"],
        ["BigQuery Load", "bq load --source_format=NEWLINE_DELIMITED_JSON --schema_update_option=ALLOW_FIELD_ADDITION"],
        ["Target Table", "project-...:syntrix_logs.raw_logs"],
        ["Key Sanitization", "Replaces non-alphanumeric chars with underscores (BigQuery column name requirement)"],
        ["Nested JSON Handling", "Stringifies labels, resource, jsonPayload, protoPayload, sourceLocation, operation fields"],
        ["Initial Window", "60 minutes before daemon start"],
        ["Error Handling", "Continues polling on failure; prints error to stdout"],
    ]
    f.append(make_table(["Property", "Value"], streamer_rows, [40*mm, 130*mm]))
    f.append(sp(2))

    f.append(h3(s, "Why Custom Streamer Instead of Native Log Sink?"))
    f.append(bullet(s, "Log Sinks export raw Cloud Logging format which requires complex BigQuery schema management"))
    f.append(bullet(s, "The custom streamer sanitizes field names and stringifies nested JSON for clean BigQuery loading"))
    f.append(bullet(s, "Provides more control over data transformation before loading"))
    f.append(inferred(s, "This was likely also a practical hackathon decision — the team may have encountered schema issues "
                        "with native sinks and pivoted to a custom solution."))
    f.append(sp(2))
    
    f.append(h3(s, "Why NDJSON?"))
    f.append(body(s,
        "BigQuery's native batch loading format is NDJSON (Newline-Delimited JSON). Each line is a complete JSON object "
        "representing one log entry. This format enables streaming-compatible loading with --schema_update_option="
        "ALLOW_FIELD_ADDITION, which automatically adds new columns as log schemas evolve."
    ))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 15: BIGQUERY
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "15. BigQuery"))
    f.append(h2(s, "15.1 Dataset & Table"))
    bq_rows = [
        ["Dataset", "syntrix_logs"],
        ["Raw Table", "raw_logs"],
        ["Load Method", "bq load (NDJSON, schema auto-detect, ALLOW_FIELD_ADDITION)"],
        ["Partitioning", "Not explicitly configured (auto-detect)"],
        ["Clustering", "Not explicitly configured"],
    ]
    f.append(make_table(["Property", "Value"], bq_rows, [40*mm, 130*mm]))
    f.append(sp(2))
    f.append(h2(s, "15.2 Raw Log Files"))
    f.append(bullet(s, "<b>raw_logs.json:</b> 1.2 MB — full JSON array export from Cloud Logging"))
    f.append(bullet(s, "<b>raw_logs.ndjson:</b> 1.1 MB — sanitized NDJSON version for BigQuery loading"))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 16: ETL & ANALYTICS
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "16. ETL &amp; Analytics"))
    f.append(body(s, "Six BigQuery views transform raw logs into analytical datasets (defined in bq_views.sql):"))
    f.append(sp(2))

    views = [
        ("looker_cleaned_logs", "Base ETL View",
         "Extracts structured fields from raw Cloud Logging data. Determines compute_environment from resource.type, "
         "derives service_name based on platform (Cloud Run → service_name label, GKE → container_name, GCE → hardcoded "
         "'inventory-service'). Extracts endpoint, method, status_code, latency_ms, event_type, error_message from jsonPayload.",
         "Filters to logs where event or latency_ms is present (app-level logs only)",
         "Foundation for all downstream views"),
        ("looker_latency_analysis", "Latency Analysis",
         "Aggregates by hour, service, compute environment, and endpoint. Calculates total_requests, avg_latency_ms, max_latency_ms.",
         "WHERE latency_ms IS NOT NULL; GROUP BY TIMESTAMP_TRUNC(timestamp, HOUR)",
         "Identifies slow services and endpoints; supports SRE latency SLO monitoring"),
        ("looker_error_analysis", "Error Analysis",
         "Counts client errors (4xx), server errors (5xx), and calculates error_rate_percentage per hour/service/environment.",
         "SAFE_DIVIDE(COUNTIF(status_code >= 400), COUNT(1)) * 100",
         "Error trend monitoring; identifies reliability issues by service and platform"),
        ("looker_usage_monitoring", "Usage Monitoring",
         "Daily request counts by compute environment and endpoint.",
         "GROUP BY TIMESTAMP_TRUNC(timestamp, DAY), compute_environment, endpoint",
         "Traffic pattern analysis; identifies most/least used endpoints"),
        ("looker_performance_kpis", "Performance KPIs",
         "Calculates latency percentiles (p50, p90, p99) and success_rate_percentage per service and environment.",
         "APPROX_QUANTILES(latency_ms, 100)[OFFSET(50/90/99)]",
         "SRE golden signals dashboard; SLO compliance tracking"),
        ("looker_cost_optimization_recommendations", "Cost Optimization",
         "Analyzes last-24-hour traffic relative to latest data timestamp. Generates cost recommendations based on "
         "request volume and compute platform.",
         "Rules: <100 reqs on GKE → 'Scale down or migrate to Cloud Run'; <100 on GCE → 'Downgrade VM'; "
         ">10000 on Cloud Run → 'Consider GKE for sustained discounts'",
         "FinOps recommendations; right-sizing guidance"),
    ]
    for vname, vtitle, vdesc, vlogic, vpurpose in views:
        f.append(h3(s, f"{vtitle} — {vname}"))
        f.append(bullet(s, f"<b>Description:</b> {vdesc}"))
        f.append(bullet(s, f"<b>Key Logic:</b> {vlogic}"))
        f.append(bullet(s, f"<b>Business Purpose:</b> {vpurpose}"))
        f.append(sp(2))
    
    f.append(confirmed(s, "All 6 views verified from bq_views.sql"))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 17: CLOUD MONITORING
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "17. Cloud Monitoring"))
    f.append(body(s,
        "Cloud Monitoring is used for alerting based on platform-native metrics. "
        "No custom metrics or dashboards were created in Cloud Monitoring — "
        "visualization is handled entirely by Looker Studio using BigQuery data."
    ))
    f.append(sp(2))
    f.append(callout(s,
        "<b>Logs vs Metrics in this project:</b> Cloud Logging captures detailed per-request data (JSON logs). "
        "Cloud Monitoring tracks platform-level metrics (CPU utilization, request counts, query times). "
        "The project uses logs for analytics (via BigQuery) and metrics for alerting (via Cloud Monitoring)."
    ))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 18: ALERTING
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "18. Alerting"))
    f.append(body(s, "Five alert policies are configured via create_alerts.sh:"))
    f.append(sp(2))

    alert_rows = [
        ["Cloud Run 5xx Errors", "run.googleapis.com/request_count (5xx class)", "> 10 requests", "60s", "Babu, Mugunthan"],
        ["GKE High CPU", "kubernetes.io/container/cpu/limit_utilization", "> 80%", "180s", "Akash"],
        ["GCE High CPU", "compute.googleapis.com/instance/cpu/utilization", "> 85%", "180s", "Roshni, Swathi"],
        ["BigQuery High Exec Time", "bigquery.googleapis.com/query/execution_times", "> 10000ms", "60s", "Ecclesiastes, Emayan"],
        ["Log Pipeline Errors", "logging.googleapis.com/log_entry_count (ERROR)", "> 5 errors", "60s", "Varunshiyam"],
    ]
    f.append(make_table(
        ["Alert Name", "Metric", "Threshold", "Duration", "Notified"],
        alert_rows,
        [30*mm, 45*mm, 25*mm, 15*mm, 40*mm]
    ))
    f.append(sp(2))
    f.append(h3(s, "Notification Channels"))
    f.append(body(s, "7 email notification channels were created, one per team member, each responsible for specific infrastructure:"))
    channel_rows = [
        ["Babu Senthil", "bbabusenthil@gmail.com", "Cloud Run"],
        ["Mugunthan", "mt.mugunthan@gmail.com", "Cloud Run (added later via add_mugunthan.py)"],
        ["Varunshiyam", "varunshiyam.analyst@gmail.com", "Looker Pipeline"],
        ["Akash", "akaashrk02@gmail.com", "GKE"],
        ["Roshni", "roshnigloriya@gmail.com", "GCE"],
        ["Swathi", "swathi062005@gmail.com", "GCE"],
        ["Ecclesiastes", "ecclesiastescherubin1@gmail.com", "BigQuery"],
        ["Emayan", "emayanvijayakumar17@gmail.com", "BigQuery"],
    ]
    f.append(make_table(["Team Member", "Email", "Responsibility"], channel_rows, [35*mm, 65*mm, 35*mm]))
    f.append(sp(2))
    f.append(body(s,
        "<b>Alert lifecycle:</b> When a metric exceeds its threshold for the specified duration, Cloud Monitoring "
        "creates an Incident and sends email notifications to the configured channels. The fix_alerts.py script "
        "was created to add required aggregation parameters (alignmentPeriod, perSeriesAligner) that were "
        "missing from the initial alert policy definitions."
    ))
    f.append(inferred(s, "The existence of fix_alerts.py suggests the initial create_alerts.sh had issues — "
                        "alert policies without aggregation settings fail validation in newer Cloud Monitoring API versions."))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 19-20: LOOKER & FINOPS
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "19. Looker Studio"))
    f.append(body(s,
        "A comprehensive Looker Studio dashboard design is documented in Looker_Dashboard_Design.md (1,143 lines, 57KB). "
        "The dashboard is designed with 6 sheets (tabs) targeting different stakeholders."
    ))
    sheets = [
        ["Sheet 1", "Executive Overview", "CTO / VP Engineering", "Total requests, error rate, top services, latency heatmap"],
        ["Sheet 2", "System Performance & Latency", "SRE / DevOps", "P50/P90/P99 latency, service comparison, slow endpoint detection"],
        ["Sheet 3", "Error Analysis & Reliability", "SRE / DevOps", "4xx/5xx breakdown, error trends, error rate by service"],
        ["Sheet 4", "Infrastructure & Resource Usage", "FinOps / Cloud Mgmt", "Request distribution by compute platform, usage trends"],
        ["Sheet 5", "Cost Optimization", "FinOps / Cloud Mgmt", "Cost recommendations, traffic-to-platform analysis"],
        ["Sheet 6", "Developer Deep Dive", "Developers / QA", "Log explorer, raw log inspection, trace correlation"],
    ]
    f.append(make_table(
        ["Sheet", "Title", "Audience", "Key Visualizations"],
        sheets,
        [16*mm, 38*mm, 30*mm, 86*mm]
    ))
    f.append(sp(2))
    f.append(confirmed(s, "Dashboard design verified from Looker_Dashboard_Design.md. The PDF version also exists."))
    f.append(inferred(s, "The actual Looker Studio dashboard is assumed to be built in the GCP console based on this design document."))
    f.append(sp(4))

    f.append(h1(s, "20. Cost Optimization / FinOps"))
    f.append(body(s,
        "Cost optimization is implemented via <b>custom SQL logic</b> in the looker_cost_optimization_recommendations "
        "BigQuery view — NOT via Google Cloud Recommender API."
    ))
    f.append(sp(2))
    cost_rules = [
        ["< 100 requests/24h", "k8s_container (GKE)", "Scale down GKE nodes or migrate to Cloud Run (Scale to Zero)"],
        ["< 100 requests/24h", "gce_instance (GCE)", "Downgrade VM instance type or migrate to Cloud Run"],
        ["> 10000 requests/24h", "cloud_run_revision", "Consider migrating to GKE for sustained discount usage"],
        ["All other cases", "Any", "Traffic Optimized for Environment"],
    ]
    f.append(make_table(
        ["Traffic Condition", "Platform", "Recommendation"],
        cost_rules,
        [35*mm, 40*mm, 95*mm]
    ))
    f.append(sp(2))
    f.append(callout(s,
        "The view uses a self-referencing window (last 24h relative to MAX(timestamp) in the data, not CURRENT_TIMESTAMP), "
        "which ensures recommendations work correctly even with historical/older demo data."
    ))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 21-22: IAM & NETWORKING
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "21. IAM &amp; Security"))
    iam_rows = [
        ["cloudrun-app-sa", "Cloud Run services", "roles/cloudsql.client, roles/secretmanager.secretAccessor",
         "Allows Cloud Run to connect to Cloud SQL via auth proxy and read database URL from Secret Manager"],
        ["allUsers", "Cloud Run services", "roles/run.invoker",
         "Allows unauthenticated public access to Cloud Run services. Required for public-facing gateway."],
        ["Default Compute SA", "Compute Engine VM", "cloud-platform scope",
         "Broad access scope. Allows VM to pull images from Artifact Registry and write logs."],
        ["Default GKE SA", "GKE Autopilot", "Managed by Autopilot",
         "Autopilot manages node service accounts automatically."],
    ]
    f.append(make_table(
        ["Service Account", "Used By", "Roles/Permissions", "Purpose"],
        iam_rows,
        [30*mm, 25*mm, 50*mm, 65*mm]
    ))
    f.append(sp(2))
    f.append(h3(s, "Security Concerns"))
    f.append(bullet(s, '<b style="color: #EA4335">⚠ Database password hardcoded</b> in deploy scripts (syntrix_admin_123) — acceptable for hackathon, not production'))
    f.append(bullet(s, '<b style="color: #EA4335">⚠ allUsers invoker</b> on all Cloud Run services — only gateway should be public'))
    f.append(bullet(s, '<b style="color: #EA4335">⚠ cloud-platform scope</b> on GCE VM — overly broad; should be scoped to specific APIs'))
    f.append(bullet(s, '<b style="color: #EA4335">⚠ Cloud SQL public IP</b> used by GKE — should use Cloud SQL Auth Proxy or private IP'))
    f.append(sp(4))

    f.append(h1(s, "22. Networking"))
    net_rows = [
        ["User → Gateway", "HTTPS (public)", "Public Cloud Run URL"],
        ["Gateway → Catalog", "HTTPS (public)", "Cloud Run URL with identity token"],
        ["Gateway → Cart", "HTTPS (public)", "Cloud Run URL with identity token"],
        ["Gateway → Order", "HTTP (internal VPC)", "Internal IP 10.160.0.5:8000"],
        ["Gateway → Payment", "HTTP (internal VPC)", "Internal IP 10.160.0.7:8000"],
        ["Gateway → Inventory", "HTTP (internal VPC)", "Internal IP 10.160.0.6:8000"],
        ["Cloud Run → Cloud SQL", "Unix socket", "Cloud SQL Auth Proxy (/cloudsql/CONNECTION_NAME)"],
        ["GKE → Cloud SQL", "TCP (public IP)", "34.14.131.84:5432"],
        ["GCE → Cloud SQL", "TCP (public/internal IP)", "Via metadata-derived URL"],
        ["All → Cloud Logging", "Automatic", "Platform agent (stdout capture)"],
    ]
    f.append(make_table(
        ["Path", "Protocol", "Details"],
        net_rows,
        [35*mm, 30*mm, 105*mm]
    ))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 23: END-TO-END RUNTIME FLOW
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "23. End-to-End Runtime Flow"))
    f.append(body(s,
        "This section traces a single checkout request through the entire architecture, "
        "showing both the data path and the observability path simultaneously."
    ))
    f.append(sp(2))
    f.append(h2(s, "Scenario: User Completes a Purchase"))
    
    runtime_steps = [
        ("1. User clicks 'Confirm Order'", 
         "Browser sends POST /api/checkout {cart_id: 5, customer_id: 1} to Gateway"),
        ("2. Gateway receives request",
         "TracingMiddleware generates request_id + trace_id, stores in ContextVars. "
         "Gateway logs: {event: request_completed, endpoint: /api/checkout}. "
         "Proxies to Order Service at http://10.160.0.5:8000/checkout"),
        ("3. Order Service: Validate Cart",
         "Calls Cart Service (Cloud Run) GET /cart/5. Cart logs: {event: request_completed}. "
         "Returns cart items and total."),
        ("4. Order Service: Reserve Inventory",
         "Calls Inventory Service (GCE) POST /inventory/reserve. "
         "Inventory decrements stock, creates InventoryTransaction, logs: {event: inventory_reserved}. "
         "Publishes to Pub/Sub inventory-events: {event_type: inventory.reserved}"),
        ("5. Order Service: Create Order",
         "Inserts Order record (status=CREATED, payment=PENDING) in Cloud SQL. "
         "Publishes to Pub/Sub order-events: {event_type: order.created}. "
         "Logs: {event: order_created, order_id: 42}"),
        ("6. Order Service: Process Payment",
         "Calls Payment Service (GKE) POST /payments {order_id: 42, amount: 149.99}. "
         "Payment checks simulation_config, processes payment, creates Payment record. "
         "Publishes to Pub/Sub payment-events: {event_type: payment.completed}. "
         "Logs: {event: payment_processed, status: SUCCESS}"),
        ("7. Order Service: Finalize",
         "Updates Order status to COMPLETED. Clears cart items. "
         "Logs: {event: order_completed}. Returns {order_id: 42, status: COMPLETED}"),
        ("8. Gateway: Return Response",
         "Forwards response to browser. Logs total gateway latency. "
         "All logs share the SAME trace_id for correlation."),
    ]
    for step_title, step_detail in runtime_steps:
        f.append(h3(s, step_title))
        f.append(body(s, step_detail))
        f.append(sp(1))
    
    f.append(sp(4))
    f.append(h2(s, "Parallel Observability Path"))
    obs_steps = [
        "All 6+ log entries (Gateway, Cart, Inventory, Order, Payment) are written to stdout as JSON",
        "Cloud Run, GKE, GCE logging agents automatically forward to Google Cloud Logging",
        "Log Streamer Daemon polls Cloud Logging every 10 seconds",
        "Batch of logs sanitized and written to /tmp/stream_batch.ndjson",
        "bq load appends to syntrix_logs.raw_logs in BigQuery",
        "BigQuery views (looker_cleaned_logs → latency/error/usage/KPI) automatically reflect new data",
        "Looker Studio dashboards show updated metrics on next refresh",
        "If any metric exceeds threshold (e.g., 5xx errors > 10), Cloud Monitoring fires alert → email notification",
    ]
    for i, step in enumerate(obs_steps, 1):
        f.append(bullet(s, f"<b>Step {i}:</b> {step}"))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 24: CONFIGURATION MASTER TABLE
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "24. Configuration Master Table"))
    config_rows = [
        ["GCP Project ID", "project-4e3f1563-833a-4721-bf7", "All scripts", "CONFIRMED"],
        ["Region", "asia-south1", "All deployments", "CONFIRMED"],
        ["GKE Zone", "asia-south1 (regional Autopilot)", "setup_gke_cluster.sh", "CONFIRMED"],
        ["GCE Zone", "asia-south1-a", "deploy_inventory.sh", "CONFIRMED"],
        ["Artifact Registry", "syntrix-cloudmart", "All deploy scripts", "CONFIRMED"],
        ["Cloud SQL Instance", "syntrix-postgres", "setup_cloudsql.sh", "CONFIRMED"],
        ["Cloud SQL Tier", "db-f1-micro", "setup_cloudsql.sh", "CONFIRMED"],
        ["Database Name", "cloudmart", "setup_cloudsql.sh", "CONFIRMED"],
        ["Database User", "cloudmart_user", "deploy_gke.sh", "CONFIRMED"],
        ["GKE Cluster", "syntrix-gke", "setup_gke_cluster.sh", "CONFIRMED"],
        ["GKE Type", "Autopilot", "create-auto command", "CONFIRMED"],
        ["GCE Machine Type", "e2-micro", "deploy_inventory.sh", "CONFIRMED"],
        ["GCE VM Name", "syntrix-inventory", "deploy_inventory.sh", "CONFIRMED"],
        ["BigQuery Dataset", "syntrix_logs", "realtime_log_streamer.py", "CONFIRMED"],
        ["BigQuery Table", "raw_logs", "realtime_log_streamer.py", "CONFIRMED"],
        ["Log Poll Interval", "10 seconds", "realtime_log_streamer.py", "CONFIRMED"],
        ["Log Batch Limit", "2000 entries", "realtime_log_streamer.py", "CONFIRMED"],
        ["Pub/Sub Topics", "order-events, payment-events, inventory-events", "Service source code", "CONFIRMED"],
        ["Gateway URL", "https://syntrix-gateway-541833001986.asia-south1.run.app", "simulate_traffic.sh", "CONFIRMED"],
        ["Order Internal IP", "10.160.0.5", "update_cloudrun_sql.sh", "CONFIRMED"],
        ["Inventory Internal IP", "10.160.0.6", "update_cloudrun_sql.sh", "CONFIRMED"],
        ["Payment Internal IP", "10.160.0.7", "update_cloudrun_sql.sh", "CONFIRMED"],
        ["Cloud SQL Public IP", "34.14.131.84", "deploy_gke.sh", "CONFIRMED"],
    ]
    f.append(make_table(
        ["Component", "Value", "Source", "Status"],
        config_rows,
        [35*mm, 60*mm, 40*mm, 25*mm]
    ))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 25: COMMAND REFERENCE
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "25. Command Reference"))
    cmd_rows = [
        ["docker buildx build --platform linux/amd64 ...", "Builds cross-platform Docker image and pushes to Artifact Registry", "deploy_phase1.sh"],
        ["gcloud auth configure-docker asia-south1-docker.pkg.dev", "Configures Docker to authenticate with Artifact Registry", "deploy_phase1.sh"],
        ["gcloud run deploy syntrix-cart ...", "Deploys container as Cloud Run service", "deploy_phase1.sh"],
        ["gcloud run services update ... --add-cloudsql-instances=...", "Adds Cloud SQL connector to existing Cloud Run service", "update_cloudrun_sql.sh"],
        ["gcloud run jobs create syntrix-seed ...", "Creates a Cloud Run Job for database seeding", "setup_seed.sh"],
        ["gcloud run jobs execute syntrix-seed --wait", "Executes seed job and waits for completion", "setup_seed.sh"],
        ["gcloud container clusters create-auto syntrix-gke ...", "Creates GKE Autopilot cluster", "setup_gke_cluster.sh"],
        ["gcloud container clusters get-credentials syntrix-gke ...", "Gets kubectl credentials for GKE cluster", "deploy_gke.sh"],
        ["kubectl create secret generic db-secret ...", "Creates Kubernetes secret for database URL", "deploy_gke.sh"],
        ["kubectl apply -f - (inline YAML)", "Applies Deployment + Service manifests for order and payment", "deploy_gke.sh"],
        ["gcloud sql instances create syntrix-postgres ...", "Creates Cloud SQL PostgreSQL instance", "setup_cloudsql.sh"],
        ["gcloud secrets create database-url ...", "Creates Secret Manager secret", "setup_cloudsql.sh"],
        ["gcloud compute instances create syntrix-inventory ...", "Creates Compute Engine VM", "deploy_inventory.sh"],
        ["gcloud compute firewall-rules create allow-inventory-internal ...", "Creates internal firewall rule for inventory", "deploy_inventory.sh"],
        ["gcloud logging read ... --format=json --limit=2000", "Reads logs from Cloud Logging (used by streamer)", "realtime_log_streamer.py"],
        ["bq load --source_format=NEWLINE_DELIMITED_JSON ...", "Loads NDJSON data into BigQuery", "realtime_log_streamer.py"],
        ["gcloud beta monitoring channels create ...", "Creates email notification channel", "create_alerts.sh"],
        ["gcloud alpha monitoring policies create ...", "Creates alert policy from JSON file", "create_alerts.sh"],
        ["gcloud run services add-iam-policy-binding ... allUsers ...", "Grants public access to Cloud Run service", "deploy_phase1.sh"],
    ]
    f.append(make_table(
        ["Command (abbreviated)", "Purpose", "Source"],
        cmd_rows,
        [70*mm, 65*mm, 35*mm]
    ))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 26: DESIGN DECISIONS
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "26. Design Decisions &amp; Trade-offs"))
    decision_rows = [
        ["Cloud Run for Gateway/Catalog/Cart", "Stateless, fast scaling, scale-to-zero", "GKE for all services", "Cost savings vs. always-on infra", "CONFIRMED"],
        ["GKE for Order/Payment", "Complex orchestration, persistent pods", "Cloud Run", "Higher cost but better for multi-service calls", "INFERRED"],
        ["Compute Engine for Inventory", "Legacy simulation, third resource type", "Cloud Run", "Demonstrates VM-based workloads", "INFERRED"],
        ["Three compute platforms", "Demonstrates multi-platform observability", "Single platform", "Complexity vs. hackathon differentiation", "CONFIRMED"],
        ["Custom Log Streamer", "Control over ETL, schema sanitization", "Native Log Sink", "More work but cleaner BigQuery schema", "INFERRED"],
        ["API Polling (10s interval)", "Simple implementation, no infrastructure", "Pub/Sub or streaming", "Latency vs. simplicity", "CONFIRMED"],
        ["NDJSON format", "BigQuery native format, streaming-compatible", "CSV or Avro", "Standard choice for BigQuery loading", "CONFIRMED"],
        ["BigQuery for analytics", "Serverless SQL, Looker integration", "Cloud SQL analytics", "Better for large-scale log analysis", "CONFIRMED"],
        ["Looker Studio", "Free, native BigQuery connector", "Grafana, DataStudio", "Zero cost, GCP native", "CONFIRMED"],
        ["Cloud SQL (shared DB)", "Simplicity for hackathon", "Per-service databases", "Coupling vs. speed of development", "INFERRED"],
        ["Pub/Sub events", "Event-driven architecture demonstration", "Direct HTTP calls only", "Adds async capability but no subscribers yet", "CONFIRMED"],
        ["Email alerting", "Simple, no extra infrastructure", "Slack, PagerDuty", "Sufficient for hackathon demo", "INFERRED"],
        ["python-json-logger", "Native JSON output, Cloud Logging compatible", "Custom formatter", "Industry standard for GCP", "CONFIRMED"],
        ["FastAPI", "Async support, auto-docs, modern Python", "Flask, Django", "Best fit for microservices + async HTTP", "INFERRED"],
        ["GKE Autopilot", "No node management, pay-per-pod", "GKE Standard", "Simpler, cost-effective for small workloads", "CONFIRMED"],
    ]
    f.append(make_table(
        ["Decision", "Reason", "Alternative", "Trade-off", "Status"],
        decision_rows,
        [32*mm, 35*mm, 25*mm, 38*mm, 20*mm]
    ))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 27-28: LIMITATIONS & IMPLEMENTED VS CONCEPTUAL
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "27. Project Limitations"))
    limitations = [
        "Log Streamer polling introduces 10-second delay — not true real-time",
        "No deduplication guarantee — timestamp increment by 1 nanosecond may miss or duplicate edge cases",
        "Pub/Sub topics have publishers but no subscribers — events are published but not consumed",
        "Shared database across all services creates coupling (anti-pattern for true microservices)",
        "Database password hardcoded in deployment scripts",
        "allUsers invoker on all Cloud Run services (should only be on gateway)",
        "Cloud SQL accessed via public IP from GKE (should use Auth Proxy)",
        "No HTTPS/TLS between internal services (VPC traffic is unencrypted)",
        "BigQuery views are not materialized — query cost on every dashboard refresh",
        "No CI/CD pipeline — all deployments are manual shell scripts",
        "No health check probes configured in Kubernetes manifests (no readiness/liveness probes)",
        "No resource requests/limits defined in GKE Deployments",
        "Alembic configured but no migration scripts generated — schema is created by seed.py directly",
        "Cost optimization rules are simple threshold-based — no ML or actual billing data",
        "GCE logs may need manual injection (inject_gce_logs.sh) if container stdout is not captured",
    ]
    for lim in limitations:
        f.append(bullet(s, lim))
    f.append(sp(4))

    f.append(h1(s, "28. What Is Actually Implemented vs Conceptual"))
    impl_rows = [
        ["FastAPI microservices (6 services)", "FULLY IMPLEMENTED", "Source code verified"],
        ["Docker containerization", "FULLY IMPLEMENTED", "Dockerfile, docker-compose.yml"],
        ["Cloud Run deployment (3 services + 1 job)", "FULLY IMPLEMENTED", "Deploy scripts verified"],
        ["GKE Autopilot cluster + 2 deployments", "FULLY IMPLEMENTED", "K8s manifests in deploy_gke.sh"],
        ["Compute Engine VM", "FULLY IMPLEMENTED", "deploy_inventory.sh"],
        ["Cloud SQL PostgreSQL", "FULLY IMPLEMENTED", "setup_cloudsql.sh"],
        ["Structured JSON logging", "FULLY IMPLEMENTED", "shared/logging/logger.py"],
        ["Distributed tracing (ContextVars)", "FULLY IMPLEMENTED", "shared/middleware/tracing.py"],
        ["Log Streamer Daemon", "FULLY IMPLEMENTED", "realtime_log_streamer.py"],
        ["BigQuery dataset + raw_logs table", "FULLY IMPLEMENTED", "Script evidence + raw_logs.ndjson"],
        ["BigQuery analytical views (6)", "FULLY IMPLEMENTED", "bq_views.sql"],
        ["Cloud Monitoring alert policies (5)", "FULLY IMPLEMENTED", "create_alerts.sh, fix_alerts.py"],
        ["Notification channels (7 email)", "FULLY IMPLEMENTED", "create_alerts.sh"],
        ["Pub/Sub topics (3)", "PARTIALLY IMPLEMENTED", "Publishers exist; no subscribers"],
        ["Looker Studio dashboard", "DESIGN COMPLETED", "1143-line design doc; actual dashboard in GCP console"],
        ["Cost optimization", "IMPLEMENTED (SQL-based)", "Custom logic, not GCP Recommender"],
        ["Frontend SPA", "FULLY IMPLEMENTED", "frontend/ directory"],
        ["Simulation/chaos engineering", "FULLY IMPLEMENTED", "Developer Control Panel + simulation_config"],
        ["Traffic simulator", "FULLY IMPLEMENTED", "Frontend JS + simulate_traffic.sh"],
        ["Secret Manager", "FULLY IMPLEMENTED", "setup_cloudsql.sh"],
        ["CI/CD pipeline", "NOT IMPLEMENTED", "Manual scripts only"],
        ["Cloud Functions", "NOT IMPLEMENTED", "No evidence"],
        ["Native Log Sinks", "NOT IMPLEMENTED", "Custom streamer used instead"],
        ["Workload Identity", "NOT IMPLEMENTED", "Direct credentials used"],
    ]
    f.append(make_table(
        ["Component", "Status", "Evidence"],
        impl_rows,
        [45*mm, 35*mm, 90*mm]
    ))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 29: PRESENTATION TALKING POINTS
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "29. Presentation Talking Points"))
    f.append(h2(s, "30-Second Elevator Pitch"))
    f.append(body(s,
        '"CloudPulse is a cloud-native observability platform that monitors a microservices e-commerce application '
        'deployed across Cloud Run, GKE, and Compute Engine. We built a custom log pipeline that streams structured '
        'JSON logs from all three environments into BigQuery, where SQL-based analytics power Looker Studio dashboards '
        'for real-time performance monitoring, error analysis, and cost optimization recommendations — with Cloud '
        'Monitoring alerts for proactive incident detection."'
    ))
    f.append(sp(4))

    f.append(h2(s, "1-Minute Explanation"))
    f.append(body(s,
        '"We built CloudMart, a realistic e-commerce platform with 6 microservices — a FastAPI gateway, catalog, cart, '
        'order, payment, and inventory services. To demonstrate multi-platform observability, we deliberately deployed '
        'these across three compute platforms: Cloud Run for stateless services, GKE for complex orchestration, and '
        'Compute Engine for legacy workloads. Every service emits structured JSON logs with distributed tracing IDs. '
        'A custom log streamer daemon polls Cloud Logging every 10 seconds and loads data into BigQuery. Six analytical '
        'views transform raw logs into latency analysis, error tracking, usage monitoring, performance KPIs, and cost '
        'optimization recommendations. These feed into a 6-sheet Looker Studio dashboard. We also configured 5 Cloud '
        'Monitoring alert policies with team-member-specific email notifications. The application includes a built-in '
        'chaos engineering panel that can simulate payment failures, inventory shortages, and database slowdowns to '
        'generate organic error telemetry."'
    ))
    f.append(sp(4))

    f.append(h2(s, "2-Minute Architecture Walkthrough"))
    f.append(body(s,
        '"Let me walk you through the architecture. A user visits our CloudMart web portal, which is served by a '
        'FastAPI gateway running on Cloud Run. The gateway proxies API requests to five backend services. Catalog '
        'and Cart run on Cloud Run for stateless, auto-scaling workloads. Order and Payment run on GKE Autopilot '
        'for persistent orchestration — the Order service coordinates a multi-step checkout flow calling Cart, '
        'Inventory, and Payment services. Inventory runs on Compute Engine, simulating a legacy VM workload. All '
        'services connect to a shared Cloud SQL PostgreSQL database and publish events to Pub/Sub topics.'
    ))
    f.append(body(s,
        'On the observability side, every service uses a shared logging library that formats stdout as structured '
        'JSON with timestamps, severity, service identity, request IDs, trace IDs, and latency metrics. These '
        'logs flow automatically into Cloud Logging. Our custom Log Streamer daemon polls Cloud Logging via the '
        'gcloud CLI every 10 seconds, sanitizes the data, and batch-loads it as NDJSON into BigQuery. Six SQL '
        'views perform ETL: a base cleaning view extracts application fields, then specialized views calculate '
        'latency percentiles, error rates, usage patterns, and cost optimization recommendations. Looker Studio '
        'connects to these views for a 6-sheet dashboard covering executive overview, performance, errors, '
        'infrastructure, cost optimization, and developer deep-dive. Five Cloud Monitoring alert policies '
        'watch for 5xx errors on Cloud Run, high CPU on GKE and GCE, BigQuery query slowness, and pipeline '
        'errors — each routed to the responsible team member via email."'
    ))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 30: JUDGE Q&A
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "30. Judge Q&amp;A"))
    f.append(body(s, "Anticipated judge questions with evidence-backed answers:"))
    f.append(sp(2))

    qa_items = [
        ("Why three different compute platforms?",
         "To demonstrate multi-platform observability, which is the core challenge in real enterprise environments. "
         "Cloud Run for stateless/auto-scaling, GKE for orchestration-heavy workloads, Compute Engine for legacy/stateful. "
         "Each produces different resource.type in Cloud Logging, which our analytics pipeline handles.",
         "Our BigQuery views use CASE statements on resource.type to normalize service names across platforms."),
        
        ("Why a custom log streamer instead of native Log Sinks?",
         "Native Log Sinks export raw Cloud Logging format with deeply nested schemas that cause BigQuery schema "
         "management issues. Our custom streamer sanitizes field names (replacing dots/slashes with underscores), "
         "stringifies nested JSON payloads, and uses ALLOW_FIELD_ADDITION for schema flexibility.",
         "We may have initially tried Log Sinks and pivoted due to schema issues — the sanitization code suggests this."),
        
        ("How does distributed tracing work across different platforms?",
         "We use Python ContextVars to store request_id and trace_id. The gateway generates or extracts these from "
         "headers (X-Request-Id, X-Trace-Id) and injects them into all downstream HTTP calls. Every service extracts "
         "the same headers via TracingMiddleware. The logger automatically adds logging.googleapis.com/trace for "
         "Cloud Logging trace correlation.",
         "This means a single checkout request generates 6+ correlated log entries across Cloud Run, GKE, and GCE."),
        
        ("What happens if one service fails?",
         "The Order service implements compensating transactions: if Payment fails, it releases the reserved inventory "
         "and marks the order as FAILED. The gateway returns 502 Bad Gateway for upstream errors. Each failure generates "
         "structured error logs with the specific reason (payment_failed, inventory_insufficient, cart_not_found).",
         "These error events appear in the looker_error_analysis view and can trigger Cloud Monitoring alerts."),
        
        ("How is cost optimization handled?",
         "Via custom SQL logic in BigQuery, not Google Cloud Recommender. The looker_cost_optimization_recommendations "
         "view analyzes the last 24 hours of traffic per compute platform. Low-traffic GKE services get recommended "
         "for Cloud Run migration (scale-to-zero). Low-traffic GCE VMs get downsize recommendations. High-traffic "
         "Cloud Run services get GKE migration recommendations for sustained use discounts.",
         "The view uses MAX(timestamp) as reference instead of CURRENT_TIMESTAMP, so it works with historical data."),
        
        ("How do alerts work? How do you avoid alert fatigue?",
         "Five alert policies monitor different infrastructure layers with team-member-specific routing. Cloud Run "
         "5xx alerts go to the Cloud Run team, GKE CPU to the Kubernetes team, GCE CPU to the VM team. Thresholds "
         "are set with duration windows (60-180 seconds) to avoid false positives from momentary spikes.",
         "In production, we would add suppression rules, severity-based routing, and PagerDuty integration."),
        
        ("What is the latency of the observability pipeline?",
         "The log streamer polls every 10 seconds, so the maximum pipeline latency is ~10-20 seconds from log "
         "generation to BigQuery availability. Looker Studio refreshes on user interaction. Cloud Monitoring "
         "alerts have their own evaluation windows (60-180 seconds) independent of the log pipeline.",
         "For production, we would use Log Sinks or Pub/Sub for near-real-time streaming."),
        
        ("How would this move to production?",
         "Key changes: (1) Replace custom streamer with native Log Sinks or Dataflow pipeline, (2) Implement "
         "Cloud SQL Auth Proxy for all platforms, (3) Add CI/CD with Cloud Build, (4) Restrict IAM to least "
         "privilege, (5) Add Kubernetes health probes and resource limits, (6) Enable BigQuery partitioning and "
         "clustering, (7) Replace email alerts with PagerDuty/Slack, (8) Add per-service databases, "
         "(9) Implement rate limiting and circuit breakers.",
         "The architecture is sound; the gaps are operational maturity items typical of hackathon projects."),
        
        ("What is custom vs. native Google Cloud functionality?",
         "Custom: Log Streamer Daemon, BigQuery ETL views, cost optimization SQL rules, FastAPI gateway proxy, "
         "simulation/chaos engineering system, structured logging formatter, distributed tracing via ContextVars. "
         "Native GCP: Cloud Run, GKE, Compute Engine, Cloud SQL, Cloud Logging (ingestion), Cloud Monitoring "
         "(alerts), BigQuery (storage/compute), Looker Studio (visualization), Artifact Registry, Pub/Sub, "
         "Secret Manager, IAM.",
         "The custom components fill gaps where native GCP services don't directly solve our specific needs."),
    ]
    
    for question, answer, followup in qa_items:
        f.append(h3(s, f"Q: {question}"))
        f.append(body(s, f"<b>Answer:</b> {answer}"))
        f.append(body(s, f"<b>Follow-up:</b> {followup}"))
        f.append(sp(2))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 31: LEARNING ROADMAP
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "31. Personal Learning Roadmap"))
    f.append(body(s, "Study guide organized by topic, connecting each concept to our actual implementation:"))
    f.append(sp(2))

    learning_topics = [
        ("1. Application Architecture (FastAPI Microservices)",
         "How our 6-service architecture works, how the gateway proxies requests, how services communicate via HTTP",
         "Our project uses: FastAPI, httpx async client, SQLAlchemy ORM, shared libraries (logging, middleware, models)",
         "Explain how a checkout request flows through Gateway → Order → Cart + Inventory + Payment"),
        ("2. Docker & Containerization",
         "How a single parameterized Dockerfile builds all services, why cross-platform builds are needed",
         "Single Dockerfile with SERVICE_NAME build arg, python:3.12-slim base, 2 Uvicorn workers",
         "Why does our build use --platform linux/amd64?"),
        ("3. Artifact Registry",
         "Where Docker images are stored, how authentication works, image tagging strategy",
         "syntrix-cloudmart repository in asia-south1-docker.pkg.dev, images tagged with semver (1.0.0, 1.0.2)",
         "How does a container image get from your laptop to Cloud Run?"),
        ("4. Cloud Run",
         "Serverless containers, scale-to-zero, Cloud SQL connectors, VPC egress, IAM invoker bindings",
         "Gateway + Catalog + Cart as services; Seed as a Job; VPC egress for internal service communication",
         "Why does the gateway need --vpc-egress=all-traffic?"),
        ("5. GKE (Autopilot)",
         "Kubernetes Deployments, Pods, Services, Secrets, LoadBalancer types, Autopilot vs Standard",
         "syntrix-gke Autopilot cluster, Order + Payment Deployments, internal LoadBalancer Services, db-secret",
         "Why Autopilot instead of Standard GKE?"),
        ("6. Compute Engine",
         "VM instances, startup scripts, metadata server, firewall rules, Docker on VMs",
         "e2-micro VM running inventory container, metadata for DB_URL, http-server tag, internal firewall",
         "Why not just use Cloud Run for the inventory service?"),
        ("7. Cloud SQL",
         "Managed PostgreSQL, tiers, connection methods (Auth Proxy, direct IP, private IP)",
         "syntrix-postgres (db-f1-micro), connected via Auth Proxy (Cloud Run) and direct IP (GKE, GCE)",
         "What are the security implications of using public IP?"),
        ("8. Cloud Logging",
         "Structured logging, resource types, log severity, trace correlation, log queries",
         "All services emit JSON to stdout; Cloud Logging auto-ingests from all platforms",
         "How does Cloud Logging know which service a log came from?"),
        ("9. Log Streamer & BigQuery Pipeline",
         "Custom polling daemon, NDJSON format, batch loading, schema evolution, key sanitization",
         "realtime_log_streamer.py: polls every 10s, sanitizes keys, batch loads via bq load",
         "Why not use a native Log Sink to BigQuery?"),
        ("10. BigQuery Analytics",
         "Views, SQL aggregations, APPROX_QUANTILES, SAFE_DIVIDE, TIMESTAMP_TRUNC, JSON_EXTRACT_SCALAR",
         "6 views: cleaned_logs, latency_analysis, error_analysis, usage_monitoring, performance_kpis, cost_optimization",
         "Explain what P90 latency means and how we calculate it"),
        ("11. Cloud Monitoring & Alerting",
         "Metric types, alert policies, conditions, aggregation, notification channels, incidents",
         "5 alert policies covering Cloud Run, GKE, GCE, BigQuery, and pipeline errors",
         "What is the difference between alignmentPeriod and duration in an alert policy?"),
        ("12. Looker Studio",
         "Data sources, calculated fields, dimensions vs. metrics, chart types, multi-sheet dashboards",
         "6-sheet dashboard design documented in 1143-line markdown guide, connected to BigQuery views",
         "How does Looker Studio connect to BigQuery?"),
        ("13. FinOps / Cost Optimization",
         "Right-sizing, scale-to-zero, sustained use discounts, traffic analysis",
         "SQL-based rules in looker_cost_optimization_recommendations view",
         "How do you determine if a GKE workload should migrate to Cloud Run?"),
        ("14. IAM & Security",
         "Service accounts, roles, bindings, Secret Manager, principle of least privilege",
         "cloudrun-app-sa with cloudsql.client + secretmanager.secretAccessor, allUsers invoker",
         "What security improvements would you make for production?"),
        ("15. End-to-End Architecture",
         "How everything connects: user → app → logs → analytics → dashboards → alerts",
         "Complete data flow from browser click to Looker Studio chart update",
         "Walk me through what happens when a user clicks 'Confirm Order'"),
    ]
    
    for title, what_to_know, our_project, judge_q in learning_topics:
        f.append(h3(s, title))
        f.append(bullet(s, f"<b>What to Know:</b> {what_to_know}"))
        f.append(bullet(s, f"<b>Our Project Uses:</b> {our_project}"))
        f.append(bullet(s, f"<b>Likely Judge Question:</b> {judge_q}"))
        f.append(sp(2))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # SECTION 32: FINAL CHEAT SHEET
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "32. Final Cheat Sheet"))
    f.append(body(s, "Quick-reference summary of the entire project:"))
    f.append(sp(2))

    cheat_rows = [
        ["What is CloudPulse?", "Cloud-native observability platform for multi-platform microservices"],
        ["What is CloudMart?", "E-commerce application that generates the log telemetry"],
        ["How many services?", "6 (Gateway + Catalog + Cart + Order + Payment + Inventory)"],
        ["How many platforms?", "3 (Cloud Run + GKE Autopilot + Compute Engine)"],
        ["Database?", "Cloud SQL PostgreSQL 15 (db-f1-micro)"],
        ["How are logs collected?", "JSON stdout → Cloud Logging → Custom Streamer → BigQuery"],
        ["How fast is the pipeline?", "~10-20 second latency (polling interval)"],
        ["How many BigQuery views?", "6 (cleaned + latency + errors + usage + KPIs + cost)"],
        ["How many alert policies?", "5 (Cloud Run 5xx, GKE CPU, GCE CPU, BQ time, Pipeline errors)"],
        ["How many team members?", "8 (7 notification channels configured)"],
        ["What makes it unique?", "3-platform observability + custom ETL + chaos engineering + FinOps SQL"],
        ["Key limitation?", "10-second polling delay, no native Log Sinks, shared database"],
        ["Production gap?", "No CI/CD, hardcoded secrets, broad IAM, no health probes"],
    ]
    f.append(make_table(["Question", "Answer"], cheat_rows, [45*mm, 125*mm]))
    f.append(pb())

    # ═══════════════════════════════════════════════════════════════
    # APPENDIX
    # ═══════════════════════════════════════════════════════════════
    f.append(h1(s, "Appendix"))
    f.append(h2(s, "A. Important Files Reference"))
    file_rows = [
        ["gateway/main.py", "FastAPI gateway — API proxy, simulation endpoints, frontend serving"],
        ["services/*/main.py", "5 backend microservice entry points"],
        ["shared/logging/logger.py", "CustomJsonFormatter with Cloud Logging integration"],
        ["shared/middleware/tracing.py", "TracingMiddleware for distributed tracing"],
        ["shared/models/models.py", "SQLAlchemy models (8 tables)"],
        ["shared/utils/database.py", "Database connection factory"],
        ["Dockerfile", "Multi-service parameterized container build"],
        ["docker-compose.yml", "Local development orchestration"],
        ["database/seed_data/seed.py", "Database schema creation + 50 product seed"],
        ["deploy_phase1.sh", "Cloud Run deployment (cart + gateway)"],
        ["deploy_gke.sh", "GKE deployment (order + payment) with K8s manifests"],
        ["deploy_inventory.sh", "Compute Engine deployment (inventory)"],
        ["setup_cloudsql.sh", "Cloud SQL provisioning + IAM + Secret Manager"],
        ["setup_gke_cluster.sh", "GKE Autopilot cluster creation"],
        ["setup_seed.sh", "Cloud Run Job for database seeding"],
        ["update_cloudrun_sql.sh", "Gateway service URL + Cloud SQL connector update"],
        ["realtime_log_streamer.py", "Log Streamer Daemon (Cloud Logging → BigQuery)"],
        ["export_logs.sh", "Bulk log export + BigQuery initial load"],
        ["prepare_bq_json.py", "JSON → NDJSON sanitizer for BigQuery"],
        ["bq_views.sql", "6 BigQuery analytical views"],
        ["create_alerts.sh", "5 Cloud Monitoring alert policies + 7 notification channels"],
        ["fix_alerts.py", "Alert policy fix (aggregation parameters)"],
        ["simulate_traffic.sh", "CLI traffic generator"],
        ["Looker_Dashboard_Design.md", "1143-line Looker Studio dashboard design guide"],
        ["frontend/index.html", "SPA main page with Developer Control Panel"],
        ["frontend/app.js", "Core application logic (routing, API calls)"],
        ["frontend/admin.js", "Developer Control Panel + Traffic Simulator"],
    ]
    f.append(make_table(
        ["File", "Purpose"],
        file_rows,
        [45*mm, 125*mm]
    ))
    f.append(sp(4))

    f.append(h2(s, "B. Project Structure Tree"))
    tree = """SYNTRIX/
├── gateway/main.py                    # API Gateway
├── services/
│   ├── cart/main.py                   # Cart Service
│   ├── catalog/main.py                # Catalog Service
│   ├── order/main.py                  # Order Service
│   ├── payment/main.py                # Payment Service
│   └── inventory/main.py              # Inventory Service
├── shared/
│   ├── logging/logger.py              # Structured JSON logger
│   ├── middleware/tracing.py          # Distributed tracing
│   ├── models/models.py              # SQLAlchemy models
│   └── utils/database.py             # DB connection
├── frontend/
│   ├── index.html                     # SPA main page
│   ├── app.js                         # App logic
│   ├── admin.js                       # Dev panel + traffic sim
│   └── styles.css                     # Glassmorphism CSS
├── database/
│   ├── seed_data/seed.py              # DB seed script
│   ├── migrations/                    # Alembic (configured)
│   └── alembic.ini
├── alerts/                            # Alert policy JSONs
├── Dockerfile                         # Multi-service container
├── Dockerfile.seed                    # Seed job container
├── docker-compose.yml                 # Local dev environment
├── requirements.txt                   # Python dependencies
├── deploy_phase1.sh                   # Cloud Run deploy
├── deploy_gke.sh                      # GKE deploy + K8s manifests
├── deploy_inventory.sh                # Compute Engine deploy
├── setup_cloudsql.sh                  # Cloud SQL setup
├── setup_gke_cluster.sh              # GKE cluster creation
├── setup_seed.sh                      # Cloud Run Job seed
├── update_cloudrun_sql.sh            # Gateway + Cloud SQL update
├── realtime_log_streamer.py          # Log Streamer Daemon
├── export_logs.sh                     # Bulk log export
├── prepare_bq_json.py                # NDJSON sanitizer
├── bq_views.sql                       # BigQuery analytics views
├── create_alerts.sh                   # Alert policies + channels
├── fix_alerts.py                      # Alert fix script
├── simulate_traffic.sh               # Traffic generator
├── Looker_Dashboard_Design.md        # Dashboard design guide
└── README.md                          # Project documentation"""
    for line in tree.split('\n'):
        f.append(code(s, line))
    
    f.append(sp(8))
    f.append(hr())
    f.append(Paragraph(
        "End of Document — Generated by SYNTRIX Project Analysis Tool",
        ParagraphStyle('EndNote', parent=s['Body'], alignment=TA_CENTER, textColor=TEXT_LIGHT, fontSize=9)
    ))

    return f


def generate_pdf(output_path):
    """Generate the PDF document."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=25 * mm,
        bottomMargin=22 * mm,
        title="CLOUDPULSE — Complete Project Architecture & Implementation Guide",
        author="SYNTRIX Team",
    )
    
    styles = build_styles()
    flowables = build_document()
    doc.build(flowables, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"✅ PDF generated: {output_path}")


def generate_docx(output_path):
    """Generate the DOCX document."""
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    
    doc = Document()
    
    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(10)
    
    # Cover
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('\n\n\nSYNTRIX\n')
    run.font.size = Pt(36)
    run.font.color.rgb = RGBColor(0x42, 0x85, 0xF4)
    run.font.bold = True
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('CLOUDPULSE\n')
    run.font.size = Pt(24)
    run.font.bold = True
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('Complete Project Architecture & Implementation Guide\n')
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x44, 0x44, 0x66)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('Reverse-Engineered Technical Documentation\n')
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x88)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f'\nGenerated: {datetime.now().strftime("%d %B %Y, %H:%M IST")}\n')
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    
    doc.add_page_break()
    
    # Sections (simplified version)
    sections = [
        ("1. Executive Summary",
         "CloudPulse (codename: CloudMart) is a cloud-native e-commerce observability platform built by Team SYNTRIX. "
         "It demonstrates a complete observability pipeline across three GCP compute platforms (Cloud Run, GKE, Compute Engine), "
         "with structured JSON logging, a custom log streamer to BigQuery, analytical views, Looker Studio dashboards, "
         "and Cloud Monitoring alerting."),
        ("2. Architecture Overview",
         "• Gateway (Cloud Run) → proxies to 5 backend services\n"
         "• Catalog & Cart → Cloud Run\n"
         "• Order & Payment → GKE Autopilot\n"
         "• Inventory → Compute Engine (e2-micro)\n"
         "• Database → Cloud SQL PostgreSQL 15\n"
         "• Logging → Cloud Logging → Custom Streamer → BigQuery → Looker Studio\n"
         "• Alerting → 5 Cloud Monitoring policies → 7 email channels"),
        ("3. Services",
         "6 FastAPI microservices sharing PostgreSQL via SQLAlchemy ORM. "
         "Order service orchestrates checkout: Cart validation → Inventory reservation → Payment processing. "
         "Pub/Sub topics for order-events, payment-events, inventory-events. "
         "Simulation system for chaos engineering (payment timeouts, inventory shortages, DB delays)."),
        ("4. Log Pipeline",
         "Custom Log Streamer Daemon (realtime_log_streamer.py) polls Cloud Logging every 10 seconds via gcloud CLI, "
         "sanitizes keys for BigQuery compatibility, stringifies nested JSON, and batch loads via bq load. "
         "6 BigQuery views perform ETL for latency, error, usage, KPI, and cost analysis."),
        ("5. Monitoring & Alerting",
         "5 alert policies: Cloud Run 5xx errors, GKE CPU utilization, GCE CPU utilization, "
         "BigQuery query execution time, and log pipeline errors. "
         "7 email notification channels routing alerts to responsible team members."),
    ]
    
    for title, content in sections:
        heading = doc.add_heading(title, level=1)
        for run in heading.runs:
            run.font.color.rgb = RGBColor(0x42, 0x85, 0xF4)
        doc.add_paragraph(content)
        doc.add_paragraph()  # spacer
    
    doc.add_paragraph(
        "\n\nNote: This DOCX is a condensed companion to the full PDF report. "
        "Please refer to CLOUDPULSE_Project_Report.pdf for the complete 30+ page document "
        "with detailed tables, architecture diagrams, Q&A, and configuration references.",
        style='Normal'
    )
    
    doc.save(output_path)
    print(f"✅ DOCX generated: {output_path}")


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    pdf_path = os.path.join(script_dir, "CLOUDPULSE_Project_Report.pdf")
    docx_path = os.path.join(script_dir, "CLOUDPULSE_Project_Report.docx")
    
    print("Generating PDF...")
    generate_pdf(pdf_path)
    
    print("Generating DOCX...")
    generate_docx(docx_path)
    
    print(f"\n{'='*60}")
    print(f"PDF:  {pdf_path}")
    print(f"DOCX: {docx_path}")
    print(f"{'='*60}")
