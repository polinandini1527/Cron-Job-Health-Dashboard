# 📝 Prompt Engineering Documentation

This document records the exact system prompts engineered to construct, simulate, and analyze the **DE-11: Cron-Job Health Dashboard** prototype, satisfying the compliance metrics requested by the evaluation criteria.

---

## 1. Database Table Design Schema Initialization

* **Target Environment:** VS Code Copilot Chat
* **Objective:** Establish an isolated, lightweight database table to capture silent execution markers safely without system overhead.

### Prompt String

```text
Create a Python script for 'src/processor.py' that initializes a local SQLite database at 'data/cron_logs.db'.
The schema must contain a table named 'logs' with the columns:
- id (INTEGER PRIMARY KEY AUTOINCREMENT)
- job_name (TEXT)
- start_time (TEXT)
- end_time (TEXT)
- duration_seconds (REAL)
- exit_code (INTEGER)
Keep the database connection clean, using try/except blocks, and ensure it creates the 'data/' directory safely if it doesn't exist yet on disk.
```

---

## 2. Bulk Synthetic Telemetry and Anomaly Generation Data Seeding

* **Target Environment:** VS Code Copilot Inline Editor (`Ctrl + I`)
* **Objective:** Inject clean test data structures with embedded performance bottlenecks to test our visualization charts and AI anomaly engine rigorously.

### Prompt String

```text
Write a helper function `seed_mock_data()` inside 'src/processor.py'. It needs to seed a total of 26 historical logs spanning the last 5 days across 4 distinct cron environments: 'Database_Backup', 'Cache_Refresh', 'Data_Sync', and 'Log_Cleanup'.
Ensure you deliberately insert two specific anomaly profiles in the tail end records:
1. Make 'Database_Backup' take 315 seconds (representing a 3x runtime spike above its normal 100-second baseline average).
2. Make 'Cache_Refresh' terminate with an exit_code of 1, simulating a silent background system execution failure.
Ensure old records are cleared when executed so we can use this button repeatedly during evaluations without duplicate primary key clashes.
```

---

## 3. High-Impact, Emoji-Enriched AI Monitoring Summaries

* **Target Environment:** `src/llm_helper.py` Application Layer Configuration
* **Objective:** Configure a strict, professional system instruction framework for the `gemini-1.5-flash` endpoint to transform messy text database matrices into clean, executive-level dashboard insights.

### Prompt String

```text
You are an automated Site Reliability Engineer assistant. Look at these cron execution logs:

{latest_logs_summary}

Identify any critical anomalies such as jobs running 3x slower than their historical baseline average or jobs exiting with a non-zero exit code.

Format rules for your output:
1. Use emojis cleanly to indicate severity (🚨 for failures, ⚠️ for duration spikes).
2. Wrap job names and exit codes in backticks so they stand out as code (e.g., `Database_Backup`).
3. Keep sentences short, actionable, and professional.

Example Output Style:
- 🚨 **Job Failure:** `Database_Backup` failed silently with exit code `1` on 2026-06-12 at 05:23.
- ⚠️ **Performance Spike:** `Cache_Refresh` ran 3x slower than its weekly average baseline.

If everything looks healthy, say 'All systems operating within normal parameters.'
```

---

## 4. Local Table Responsive Filtering Framework

* **Target Environment:** VS Code Copilot Chat
* **Objective:** Design the frontend interaction components to split the global AI data rendering scope from local client chart adjustments, ensuring lag-free user processing loops.

### Prompt String

```text
Write a clean layout structure for a Streamlit dashboard. 
We need a multi-select filter called 'Filter by Job Name' and a single checkbox called 'Show Failed Jobs Only'. 
Filter the logs pandas DataFrame according to these selections and display the results in a full-width container using `st.dataframe`. 
Directly below the filtered table data, map a dynamic secondary bar chart using Plotly Express that displays 'duration_seconds' over 'start_time' for ONLY the columns currently matching the user's filtered criteria layout.
```

---

**Document Version:** 1.0

**Status:** Complete

**Last Updated:** 2026-06-13
