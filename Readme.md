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

- **Performance Anomalies**: A backup job that normally completes in 100 seconds suddenly taking 300+ seconds indicates resource contention, I/O bottlenecks, or deadlocks—but without telemetry, engineers discover this only when the job fails or SLA breaches occur.
- **Silent Failures**: A job exits with code 0 (success) but produces corrupted or incomplete output. Without captured stdout/stderr and execution metrics, root cause analysis becomes a forensic nightmare.
- **Degradation Trends**: Early warning signs—gradual slowdown over days—go unnoticed until critical failure occurs.
- **Operational Blindness**: Without structured logging, troubleshooting requires manual log file inspection across multiple servers, consuming hours of engineering effort per incident.

#### Impact on Production Databases
- **Data Integrity Risk**: Failed backups mean zero recovery options during incidents.
- **Compliance Violations**: Backup SLAs and data retention policies cannot be verified without execution logs.
- **Incident Response Delays**: Debugging production issues without cron metrics extends MTTR (Mean Time To Recovery) from minutes to hours.

#### Why This Solution Matters
The Cron Job Health Dashboard provides:
1. **Structured Telemetry**: Every job execution captures start time, end time, duration, and exit code into a queryable SQLite database.
2. **Real-Time Anomaly Detection**: AI-powered analysis identifies jobs running 3x slower than baseline or exiting with failure codes.
3. **Executive Visibility**: A single-pane dashboard gives operators immediate status of all scheduled tasks.
4. **Minimal Overhead**: Subprocess wrapper adds negligible resource footprints.
5. **Scalability Path**: SQLite is the foundation; migration to PostgreSQL/ClickHouse is a 2-line change.

---

## 2. Team Member Information

| Role | Name | Email | Contact | Responsibilities |
|------|------|-------|---------|------------------|
| **Project Lead / AI Engineer** | POLI NANDINI| nandhinipoli2005@gmail.com | 9676018629 | Prompt engineering, validation constraints, Gemini API SDK client integration |
| **Backend / DevOps Specialist** | POKALA RAJESWARI | rajeswaripokala16@gmail.com | 9390745228 | SQLite metrics data pipelines, subprocess capturing frameworks, pytest configurations |
| **Frontend Engineer** | PETLU ARAVINDH KUMAR | petluaravindhkumar@gmail.com | 9949609804 | Streamlit UI interactive development, Plotly timeline chart renderings |

---

## 3. Features Implemented

### 3.1 Python Subprocess Wrapper with Execution Telemetry
**Module:** `src/processor.py` → `run_cron_job(job_name, command_str)`
Executes arbitrary shell commands, captures precise timing (start/end), records exit code, and handles errors gracefully. Returns structured metrics dictionary.

### 3.2 SQLite Telemetry Logging Database
**Module:** `src/processor.py` → `init_db()`
Persistent SQLite database at `data/cron_logs.db` with schema:
```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY,
    job_name TEXT,
    start_time TEXT,
    end_time TEXT,
    duration_seconds REAL,
    exit_code INTEGER
)
```

### 3.3 Streamlit Web Dashboard UI
**Module:** `app.py`
Interactive single-page dashboard featuring high-level metrics cards, state-preserving session flags, and targeted custom component controls.  

### 3.4 Plotly Express Visual Runtime Analysis
Dynamic interactive timeline chart showing job execution durations over time, built cleanly using Plotly Express elements.  

### 3.5 Gemini AI Anomaly Interpreter
**Module:** `src/llm_helper.py` → `get_anomaly_narration(logs_df)`

Consumes structural logs data dataframes and targets the production `gemini-2.5-flash` environment to narrate silent issues instantly.

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
         ┌───────┴────────────┐
         │                    │
         ▼                    ▼
┌──────────────────────┐  ┌─────────────────────────────────────┐
│   STREAMLIT UI       │  │   GEMINI AI ANOMALY DETECTOR        │
│   (app.py)           │  │   (src/llm_helper.py)               │
│                      │  │                                     │
│ • Metrics Cards      │  │ • Analyze recent logs               │
│ • Duration Chart     │  │ • Identify 3x slowdowns & failures  │
│ • Raw Data Table     │  │ • Generate narration via client SDK │
│ • Filter Insights    │  │                                     │
└──────────────────────┘  └─────────────────────────────────────┘
         ▲                     │
         └─────────────────────┘
         
         USER BROWSERS: http://localhost:8501
```

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

```bash
pip install --only-binary=:all: -r requirements.txt
```

#### Step 3: Populate API Credentials
Create a file named `.env` right inside the `src/` subfolder location and paste your key format line:

```
GEMINI_API_KEY=your_actual_api_studio_key_string
```

#### Step 4: Run Database Test Suite
Confirm your structural configuration is passing validation checks smoothly:

```bash
pytest
```

#### Step 5: Launch the Production Web Server App
Execute Streamlit as a runtime module directly to ensure Windows environment lookup safety:

```bash
python -m streamlit run app.py
```

## 7. Sample Input & Output

### Sample Database Log Entry Telemetry Output

```
id   job_name           duration_seconds   exit_code   Notes
──────────────────────────────────────────────────────────────────────────
1    Database_Backup    100.0              0           ✓ Normal baseline
2    Cache_Refresh      30.0               0           ✓ Normal baseline
13   Database_Backup    315.0              0           🔴 3x Duration Spike (Anomaly)
15   Cache_Refresh      32.5               1           🔴 Silent Crash Error (Anomaly)
```

### Dashboard Markdown Output Examples

- **🚨 Job Failure:** `Cache_Refresh` failed silently returning an operational exit code status of `1`.
- **⚠️ Performance Spike:** `Database_Backup` processing bottleneck flagged: ran 3x slower than its baseline average.

## 8. Explicit Assumptions and Limitations

### Assumptions

1. **Single-Node Infrastructure:** Monitored shell operations process locally on a single machine.
2. **Outbound Network Routes:** The host platform retains valid access to Google API servers over HTTPS routes.

### Limitations

1. **SQLite Storage Scale:** Local file logs scale efficiently up to 10M records before requiring archival shifts.
2. **Free API Rate Boundaries:** Gemini limits request parameters to 15 transactions per minute. Caching layers are used to conserve your allocations.

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
├── app.py                         # Interactive Streamlit data visualization dashboard
├── requirements.txt               # Portability locked execution dependencies
├── prompts.md                     # Engineering breakdown of prompt structures
└── ai_usage_note.md               # Mandatory development AI reflection document
```
## 10. Demo Video & Presentation Materials
### Demo Video Link
👉 **[Watch our End-to-End Demo Video on Google Drive] https://drive.google.com/file/d/1MPoZ4u6pz5WRPj4ovdXhR3QuvmLMzMrg/view?usp=drivesdk **

**Document Version:** 1.1

**Status:** Evaluation Ready

**Last Updated:** 2026-06-13