# DE-11: Cron Job Health Dashboard

## Executive Summary
The **Cron Job Health Dashboard** is a production-grade, full-stack monitoring solution for scheduled job execution health, failure detection, and anomaly reporting. This project addresses critical operational gaps in cron job observability by implementing a lightweight, AI-powered telemetry pipeline that captures silent failures, performance degradation, and execution anomalies in real-time.

---
## 1. Project Title & Problem Statement

### 1.1 Project Title
**DE-11: Cron Job Health Dashboard** — AI-Powered Observability for Scheduled Job Execution Metrics

### 1.2 Problem Statement

#### Business Context
Enterprise production environments depend on scheduled jobs (cron tasks) for critical operations: database backups, cache refreshes, log rotations, data synchronization, and maintenance tasks. However, the vast majority of organizations lack visibility into cron job execution behavior.

#### Technical Problem
**Silent Failures:** Cron jobs often fail silently or with performance degradation without triggering alerts. Traditional cron implementations provide minimal feedback—they either succeed (exit code 0) or fail (non-zero exit code), but this binary state provides no insight into:

- **Performance Anomalies**: A backup job that normally completes in 12 seconds suddenly taking 48+ seconds indicates resource contention, I/O bottlenecks, or deadlocks—but without telemetry, engineers discover this only when the job fails or SLA breaches occur.
- **Silent Failures**: A job exits with a non-zero code but prints no direct diagnostic output. Without captured execution metrics, root cause analysis becomes a forensic nightmare.
- **Degradation Trends**: Early warning signs—gradual slowdown over days—go unnoticed until critical failure occurs.
- **Operational Blindness**: Without structured logging, troubleshooting requires manual log file inspection across multiple servers, consuming hours of engineering effort per incident.

#### Impact on Production Databases
- **Data Integrity Risk**: Failed backups mean zero recovery options during incidents.
- **Compliance Violations**: Backup SLAs and data retention policies cannot be verified without execution logs.
- **Incident Response Delays**: Debugging production issues without cron metrics extends MTTR (Mean Time To Recovery) from minutes to hours.

#### Why This Solution Matters
The Cron Job Health Dashboard provides:
1. **Structured Telemetry**: Every job execution captures start time, end time, duration, and exit code into a queryable SQLite database.
2. **Real-Time Anomaly Detection**: AI-powered SRE analysis identifies jobs running 3x slower than baseline or exiting with failure codes.
3. **Premium Executive User Interface**: A modern web workspace styling telemetry logs cleanly into enterprise KPI blocks and responsive timeline components.
4. **Minimal Overhead**: Subprocess wrapper adds negligible resource footprints.
5. **Scalability Path**: SQLite is the foundation; migration to PostgreSQL/ClickHouse is a 2-line change.

---

## 2. Team Information & Problem Statement Reference
### 🏢 Team Name / Problem ID: DE-11
*Live Production Deployment URL:* [![Website Status](https://img.shields.io/badge/Render-Live_Dashboard-2k?style=flat&labelColor=1c1e21&color=3b82f6&logo=render)](https://cron-job-health-dashboard.onrender.com)

| Role | Name | Email | Resume Document Link | Responsibilities |
|------|------|-------|----------------------|------------------|
| *Project Lead / AI Engineer* | POLI NANDINI | nandhinipoli2005@gmail.com | [📄 View PDF Resume](./resumes/NANDINI%20FINAL%20RESUME%20.pdf) | Prompt engineering, validation constraints, Gemini API SDK client integration |
| *Backend / DevOps Specialist* | POKALA RAJESWARI | rajeswaripokala16@gmail.com | [📄 View PDF Resume](./resumes/Pokala_Rajeswari%20(1).pdf) | SQLite metrics data pipelines, subprocess capturing frameworks, pytest configurations |
| *Frontend UI Specialist* | PETLU ARAVINDH KUMAR | petluaravindhkumar@gmail.com | [📄 View PDF Resume](./resumes/Aravindhkumar_resume.pdf) | Streamlit UI interactive development, Plotly timeline chart renderings |

---

## 3. Features Implemented

### 3.1 Python Subprocess Wrapper with Execution Telemetry
**Module:** `src/processor.py` → `run_cron_job(job_name, command_str)`
Executes arbitrary shell commands, captures precise timing (start/end), records exit codes, and handles failures gracefully. Returns a structured metrics dictionary to the logging loop.

### 3.2 SQLite Telemetry Logging Database
**Module:** `src/processor.py` → `init_db()`
Persistent SQLite database at `data/cron_logs.db` with an optimized schema structure.

### 3.3 Premium Executive Streamlit Workspace
**Module:** `app.py`
A high-end single-page visualization application injected with custom corporate CSS layouts. It features isolated workspace title sections, responsive layout configurations, dynamic colored border highlights, and interactive data grids.

### 3.4 Interactive Live Job Dispatcher Form
**Module:** `app.py` → `Live Subprocess Runner Form`
Allows operators to enter arbitrary shell command strings inside the dashboard UI to dispatch tasks in real-time. Successful commands output green operational indicators, while invalid commands register non-zero exit errors on a red panel and automatically update the metrics database.

### 3.5 SRE Streaming Anomaly Parsing Engine
**Module:** `src/llm_helper.py` & `app.py` → `render_dynamic_ai_insights()`
Consumes logs and evaluates them using the `gemini-2.5-flash` model. The UI includes an automated string parsing engine that splits raw textual inputs line-by-line, strips unrendered formatting tags, and isolates errors inside colored system alert cards (Red for critical exceptions, Amber for performance spikes).

---

## 4. System Architecture Overview
```

┌─────────────────────────────────────────────────────────────────┐
│                    CRON JOB SCHEDULER (OS-Level)                │
└────────────────┬─────────────────────────────────────────────────┘
│
▼
┌──────────────────────────────────────────────────────────────────┐
│         PYTHON SUBPROCESS WRAPPER (src/processor.py)             │
│  • Capture start_time & execute command via subprocess          │
│  • Record exit code & calculate duration                        │
│  • Auto-insert metrics into SQLite                              │
└────────────────┬─────────────────────────────────────────────────┘
│
▼
┌──────────────────────────────────────────────────────────────────┐
│         SQLITE3 PERSISTENT TELEMETRY DATABASE                    │
│  data/cron_logs.db (26 bulk sample rows with 4 anomalies)        │
└────────────────┬─────────────────────────────────────────────────┘
│
▼
┌──────────────────────────────────────────────────────────────────┐
│             PREMIUM STREAMLIT WEB FRAMEWORK (app.py)             │
│                                                                  │
│  ├── [Top Header Card] Isolated Title Title Box Component        │
│  ├── [KPI Summary Grid] Total Runs, Fail Rate, & Avg Duration    │
│  ├── [AI SRE Agent Panel] Parsed Multi-Line Severity Boxes       │
│  ├── [System Line Chart] Plotly Metric Performance Timeline      │
│  └── [Data Explorer Panel] Sidebar Filtering & Form Runner       │
└──────────────────────────────────────────────────────────────────┘

```
---

## 5. Tools and Technologies Used

| Technology | Purpose | Justification |
|---|---|---|
| **Python 3.11+** | Runtime | Simple libraries for subprocess files and testing |
| **SQLite 3.x** | Telemetry Database | Serverless, local, zero administrative configuration overhead |
| **Streamlit 1.32.0** | Web User Interface | Fastest framework to compile data prototyping dashboards |
| **Pandas** | Telemetry Data Cleaning | Vectorized log parsing and markdown matrix rendering structures |
| **Plotly Express** | Interactive Data Analysis | Fluid graphing tools natively embedded into the web app frame |
| **google-genai** | Google LLM Client SDK | Official long-term production client for structural summaries |
| **python-dotenv** | Environment Processing | Securely isolates credentials away from tracked git code trees |
| **tabulate** | Formatting Engine | Core engine driving clean string matrix generation workflows |
| **pytest** | Automated Quality Assurance | Simple framework validating table schema configurations |

---

## 6. Local Setup & Run Instructions

### Prerequisites
- Python 3.11+ installed environment
- Valid Gemini API credential generated from Google AI Studio

### Step-by-Step Setup

#### Step 1: Navigate to Project Directory
```bash
cd d:\GitHub\Cron-Job-Health-Dashboard
```

#### Step 2: Install Locked System Dependencies
To prevent compiler generation crashes across standard environments, install using the pre-compiled binary flag instruction:

Bash

```
pip install --only-binary=:all: -r requirements.txt
```

#### Step 3: Populate API Credentials
Create a file named `.env` right inside the `src/` subfolder location and paste your key format line:

```
GEMINI_API_KEY=your_actual_api_studio_key_string
```

#### Step 4: Run Database Test Suite
Confirm your structural configuration is passing validation checks smoothly:

Bash

```
pytest
```

#### Step 5: Launch the Production Web Server App
Execute Streamlit as a runtime module directly to ensure Windows environment lookup safety:

Bash

```
python -m streamlit run app.py
```

## 7. AI Capability Demonstrated

### LLM Model: Google Gemini 2.5 Flash (`google-genai` SDK)
**Core Diagnostic Capabilities:**

1. **Multi-Line Trend Evaluation**: Segregates independent system warnings cleanly onto distinct lines to optimize dashboard presentation parameters.
2. **Predictive Root Cause Analysis (RCA)**: Evaluates structural numerical anomalies to predict *why* an environment crashed or experienced disk contention.
3. **Actionable Recovery Steps**: Prescribes immediate technical troubleshooting guidelines for an on-call engineer, lowering Mean Time To Recovery (MTTR).

## 8. Sample Input & Output

### 8.1 Captured Database Telemetry Records (Active Production Store)
When the background subprocess intercepts system execution tasks, metrics are structured directly into the local SQLite logging table schema layout:

| id | job_name | start_time | end_time | duration_seconds | exit_code |
|---|---|---|---|---|---|
| 1 | `Database_Backup` | `2026-06-10 06:13:26` | `2026-06-10 06:13:38` | **12.7500** | 0 *(Normal Baseline)* |
| 7 | `Database_Backup` | `2026-06-12 18:13:26` | `2026-06-12 18:14:14` | **48.5000** | 0 *(⚠️ 3x Slow Duration Anomaly)* |
| 8 | `Database_Backup` | `2026-06-13 06:13:26` | `2026-06-13 06:13:40` | **14.2500** | 1 *(🚨 Silent Execution Script Crash)* |
| 9 | `Cache_Refresh` | `2026-06-09 20:13:26` | `2026-06-09 20:13:26` | **0.4500** | 0 *(Normal Sub-Second Run)* |

### 8.2 Dashboard Refined Parsing Box Output Layout
The application's background processing engine strips raw markdown syntax strings automatically and organizes incidents into dedicated corporate style warning blocks:

#### Case A: Critical Background Error Card
```html
🚨 Job Failure: Database_Backup failed silently with exit code 1 on 2026-06-13 at 20:05.

**🔍 Probable Cause:** Likely caused by insufficient permissions to the backup destination, a missing dependency, or a corrupted database.

**🛠️ Recommended Action:** Check the backup user's permissions, verify necessary tools are installed, and review the database logs for errors preceding the backup.
```

#### Case B: Performance Slowdown Warning Card
```html
⚠️ Performance Bottleneck: Data_Sync ran 3.5x slower than its weekly rolling baseline.

**🔍 Probable Cause:** High transaction payloads, unindexed lookup columns, or network latency overhead on a remote API route.

**🛠️ Recommended Action:** Refactor query lookup indexes or shift execution windows to off-peak infrastructure hours.
```

This ensures your input and output examples are consistent with your final user interface.

## 9. Appendix: Project Folder Structure Blueprint

```
Cron-Job-Health-Dashboard/
├── data/
│   └── cron_logs.db               # Live SQLite telemetry tracking database
├── outputs/
│   └── final_report.md            # Automatically exported AI analysis reports
├── src/
│   ├── .env                       # Local protected api credentials storage file
│   ├── __init__.py
│   ├── processor.py               # Job subprocess wrapper monitoring engine
│   └── llm_helper.py              # Gemini client SDK prompt manager
├── tests/
│   └── test_basic.py              # Automated pytest validation components
├── app.py                         # Premium interactive visualization dashboard
├── requirements.txt               # Portability locked execution dependencies
├── prompts.md                     # Engineering breakdown of prompt structures
└── ai_usage_note.md               # Mandatory development AI reflection document
```

## 10. Demo Video & Presentation Materials

### Demo Video Link
👉 **[Watch our End-to-End Demo Video on Google Drive]** https://drive.google.com/file/d/19tPdfG0kKy2rJ4weUu9F2hia2STX_pQY/view?usp=sharing

**Document Version:** 1.2

**Status:** Evaluation Ready

**Last Updated:** June 15, 2026

💡 What changed in this version:
* Swapped the outdated **System Architecture Overview** diagram flowchart to reflect your single-pane title card layout.
* Updated Section **3.3 (Streamlit UI)** and **3.5 (AI Anomaly Narration)** to clearly highlight the addition of the new custom parsing architecture and container systems.
* Adjusted the text references to match the design updates in your codebase.
