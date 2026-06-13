# AI Usage Note

## 1. What AI Assisted With
* **Subprocess Execution Wrapper:** Copilot helped generate the core terminal execution wrapper logic using Python's `subprocess` library to safely track script start times, end times, and capture raw system exit codes[cite: 57].
* **Interactive UI Component Design:** Assisted in designing a single-page Streamlit layout with high-level metric cards for total runs, silent errors, and running averages[cite: 19, 57].
* **Data Visualization Integration:** Provided the template configuration for Plotly Express to visualize duration timelines grouped cleanly by cron job names[cite: 15].

## 2. What AI Got Wrong & Human Interventions
* **Deprecated SDK Libraries:** Copilot initially generated code using the deprecated `google.generativeai` package. We manually refactored the script to utilize Google's latest, long-term supported `google-genai` client library featuring the `gemini-2.5-flash` endpoint.
* **Streamlit State & Cache Loop Mismatch:** The AI initially recommended using static `@st.cache_data` logic, which permanently blocked data updates when new rows were written to the database. We manually removed this and replaced it with `st.session_state` parsing to keep the AI narration alive and responsive to direct changes while isolating it from UI table filters.
* **Broken Unit Testing Code:** The AI commented out our `pytest` database cleanup fixtures, causing the test suite to throw runner context exceptions. [cite_start]We manually fixed and isolated the fixtures to point to a safe, independent `test_cron_logs.db` environment.
* **Missing Dependency Errors:** The code initially crashed on execution due to a missing dependency configuration error for Pandas' markdown data rendering tool (`tabulate`). We manually identified this and updated our environmental variables and package lists to handle it globally.

## 3. Best Prompts Used
The single most effective prompt utilized was the structured system prompt designed to build the automated Site Reliability Engineer (SRE) persona for our telemetry parsing pipeline:

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