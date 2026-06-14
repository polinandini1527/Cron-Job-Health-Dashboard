import os
import pandas as pd
from google import genai  # Latest Google module
from dotenv import load_dotenv
from pathlib import Path

# Explicitly load the .env file located inside the src directory
src_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=src_dir / ".env")

# Initialize the new Client wrapper securely
# It automatically picks up the GEMINI_API_KEY from the environment
api_key_val = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key_val)

def get_anomaly_narration(logs_df: pd.DataFrame) -> str:
    """
    Converts log trends into a structured prompt and extracts insights 
    using the newest google-genai SDK.
    """
    if logs_df.empty:
        return "No execution data available to analyze."
        
    if not api_key_val:
        return "AI Narration Unavailable: Missing API Key Configuration in src/.env."

    # Keep string conversion minimal to reduce input token usage
    latest_logs_summary = logs_df.tail(10).to_markdown(index=False)

    prompt = f"""
    You are an automated Site Reliability Engineer (SRE) assistant. Analyze these system cron execution logs:
    
    {latest_logs_summary}
    
    Task Instructions:
    1. Scan the tail-end records and identify critical anomalies: tasks running 3x slower than their historical baseline average, or tasks terminating with a non-zero exit code.
    2. For EVERY individual anomaly detected, you MUST print it on a NEW LINE. Do not group them into a single paragraph.
    3. For each failure or spike, provide a 1-sentence analytical guess as to WHY it happened (Root Cause Analysis), and a 1-sentence operational SOLUTION.

    Strict Output Format Rules:
    - Use '🚨' for silent execution failures (exit code != 0).
    - Use '⚠️' for performance bottlenecks ( runtimes >= 3x baseline).
    - Use markdown bullet points ('- ') to force a newline break for each individual alert.
    - Wrap job identifiers and exit statuses in backticks (e.g., `Database_Backup`).

    Example Output Structure to Emulate:
    - 🚨 **Job Failure:** `Database_Backup` failed silently with exit code `1` on 2026-06-12 at 05:23. 
      * *Possible Root Cause:* Likely caused by database locking, a broken credential chain, or an unmounted backup drive volume.
      * *Recommended Action:* Verify database port availability, check connection string environment variables, and inspect raw `stderr` logs.
    - ⚠️ **Performance Bottleneck:** `Data_Sync` ran 3x slower than its weekly rolling average at 21:23.
      * *Possible Root Cause:* Network latency spikes, massive transaction payloads, or underlying disk I/O throat contention.
      * *Recommended Action:* Optimize the target SQL query indexing patterns or adjust the task scheduler execution matrix to off-peak processing hours.

    If everything looks completely healthy across all records, say exactly: 'All systems operating within normal parameters.'
    """
    try:
        # FIX: Using the newest, globally supported model identifier string
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Error gathering AI narrative tracking parameters: {str(e)}"