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