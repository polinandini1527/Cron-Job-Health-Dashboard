# 📝 Prompt Engineering Documentation

This document records the exact system prompts engineered to construct, simulate, and analyze the **DE-11: Cron-Job Health Dashboard** prototype, satisfying the compliance metrics requested by the evaluation criteria.

---

## 1. Database Table Design Schema Initialization
* **Target Environment:** VS Code Copilot Chat
* **Objective:** Establish an isolated, lightweight database table to capture silent execution markers safely without system overhead.

### Prompt String
```text
Create a Python script for 'src/processor.py' that initializes a local SQLite database at 'data/cron_logs.db'.
The schema must contain a table named 'logs' with the columns: id, job_name, start_time, end_time, duration_seconds, exit_code.
Keep the database connection clean, using try/except blocks, and ensure it creates the 'data/' directory safely if it doesn't exist yet on disk.
```

## 2. Bulk Synthetic Telemetry and Anomaly Generation Data Seeding

- **Target Environment:** VS Code Copilot Inline Editor (`Ctrl + I`)
- **Objective:** Inject production-authentic baseline ranges (milliseconds for fast log clearings and 12-15 seconds for backups) with distinct 3x spikes to rigorously test visual thresholds.

### Prompt String
Plaintext

```
Write a helper function `seed_mock_data()` inside 'src/processor.py'. It needs to seed a total of 26 historical logs spanning the last 5 days across 4 distinct cron environments. 
Calibrate the durations to look highly authentic: Database_Backup around 12 seconds, Data_Sync around 5 seconds, Cache_Refresh around 0.4 seconds, and Log_Cleanup around 0.1 seconds. 
Ensure you deliberately insert a 48-second runtime spike on Database_Backup (representing a 3x slow anomaly) and an exit code of 1 to represent a silent background failure.
```

## 3. High-Impact, Emoji-Enriched AI Monitoring Summaries

- **Target Environment:** `src/llm_helper.py` Application Layer Configuration
- **Objective:** Configure a strict, professional system instruction framework for the `gemini-2.5-flash` endpoint to extract logs, force separate newlines, guess root causes, and prescribe remedies.

### Prompt String
Plaintext

```
You are an automated Site Reliability Engineer assistant. Analyze these system cron execution logs:
{latest_logs_summary}

Identify any critical anomalies such as jobs running 3x slower than their historical baseline average or jobs exiting with a non-zero exit code.

Format rules for your output:
1. For EVERY individual anomaly detected, you MUST print it on a NEW LINE using bullet points. Do not group them into a paragraph.
2. For each failure or spike, provide a 1-sentence analytical guess as to WHY it happened (Root Cause Analysis), and a 1-sentence operational SOLUTION.
3. Use emojis cleanly to indicate severity (🚨 for failures, ⚠️ for duration spikes).
```

## 4. Local Table Responsive Filtering Framework

- **Target Environment:** VS Code Copilot Chat
- **Objective:** Design the frontend interaction components to split the global AI data rendering scope from local client chart adjustments, ensuring lag-free user processing loops.

### Prompt String
Plaintext

```
Write a clean layout structure for a Streamlit dashboard. 
We need a multi-select filter called 'Filter by Job Name' and a single checkbox called 'Show Failed Jobs Only'. 
Filter the logs pandas DataFrame according to these selections and display the results in a full-width container using `st.dataframe`. 
Directly below the filtered table data, map a dynamic secondary bar chart using Plotly Express that displays 'duration_seconds' over 'start_time' for ONLY the rows matching the user's filtered criteria layout.
```

## 5. Live Active Subprocess Dispatcher Form

- **Target Environment:** VS Code Copilot Chat
- **Objective:** Fulfill the instructor's core requirement of active testing by adding an interactive, real-time command input form at the bottom of the dashboard.

### Prompt String
Plaintext

```
Add an interactive form component to the bottom of app.py using `st.form("live_job_runner")`. 
Provide text inputs for 'Job Name' and 'Shell Command String' along with a dispatch button. 
When clicked, pass these parameters directly to our backend `run_cron_job()` method, check the returning dictionary's exit code, display a green success banner if it's 0, or display a prominent red error banner if it returns a failure code. 
Clear the session state AI cache upon completion so the narration automatically includes this newly dis
```