# AI Usage Note

## 1. What AI Assisted With
* **Subprocess Execution Wrapper:** Copilot helped generate the core terminal execution wrapper logic using Python's `subprocess` library to track script start times, end times, and capture raw system exit codes.
* **Interactive UI Component Design:** Assisted in designing a single-page Streamlit layout with high-level metric cards for total runs, silent errors, and running averages.
* **Data Visualization Integration:** Provided the template configuration for Plotly Express to visualize duration timelines grouped cleanly by cron job names.

## 2. What AI Got Wrong & Human Interventions
* **Deprecated SDK Libraries:** Copilot initially generated code using the deprecated `google.generativeai` package. We manually refactored the script to utilize Google's latest, long-term supported `google-genai` client library featuring the `gemini-2.5-flash` endpoint.
* **Streamlit State & Cache Loop Mismatch:** The AI initially recommended using static `@st.cache_data` logic, which permanently blocked data updates when new rows were written to the database. We manually removed this and replaced it with `st.session_state` parsing to keep the AI narration alive and responsive to direct changes while isolating it from UI table filters.
* **Schema Schema KeyError Flaw:** When adding the live subprocess dispatcher form, AI misread the backend dictionary return schema as `duration_seconds` instead of `duration`. This threw a terminal crash which we manually resolved by aligning keys in `app.py`.
* **Pandas Datetime Deprecation Error:** The automated export layer crashed with a message stating `module 'pandas' has no attribute 'datetime'`. We patched this by removing the old Pandas attribute and introducing Python's native `from datetime import datetime` call.
* **Single-Line Formatting Clump:** The AI model initially generated all anomaly narratives in a single continuous text wrap, which looked messy. We re-engineered the prompt instructions with markdown constraints to force each failure to separate, distinct lines.

## 3. Best Prompts Used
The single most effective prompt utilized was our structured system instruction designed to convert raw database frames into multi-line Root Cause summaries:

```text
You are an automated Site Reliability Engineer (SRE) assistant. Analyze these system cron execution logs:
{latest_logs_summary}

Task Instructions:
1. Scan the tail-end records and identify critical anomalies: tasks running 3x slower than their historical baseline average, or tasks terminating with a non-zero exit code.
2. For EVERY individual anomaly detected, you MUST print it on a NEW LINE. Do not group them into a single paragraph.
3. For each failure or spike, provide a 1-sentence analytical guess as to WHY it happened (Root Cause Analysis), and a 1-sentence operational SOLUTION.
```