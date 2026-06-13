import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Database path
DB_PATH = "data/cron_logs.db"

def init_db():
    """Ensure data directory and SQLite table exist."""
    Path("data").mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            job_name TEXT,
            start_time TEXT,
            end_time TEXT,
            duration_seconds REAL,
            exit_code INTEGER
        )
    """)
    conn.commit()
    conn.close()

def run_cron_job(job_name, command_str):
    """Executes a command and logs results to SQLite."""
    init_db() # Ensure DB exists before running
    start_time = datetime.now()
    try:
        result = subprocess.run(command_str, shell=True, capture_output=True, text=True)
        exit_code = result.returncode
    except Exception as e:
        exit_code = 1
        print(f"Error: {e}")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (job_name, start_time, end_time, duration_seconds, exit_code) VALUES (?, ?, ?, ?, ?)",
                   (job_name, start_time.isoformat(), end_time.isoformat(), duration, exit_code))
    conn.commit()
    conn.close()
    return {"exit_code": exit_code, "duration": duration}

def seed_mock_data():
    """
    Seeds the SQLite database with 26 rows of historical telemetry data across 
    4 distinct cron environments to rigorously test charts and UI filters.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM logs") # Clear out previous data for a fresh state
    
    base_time = datetime.now() - timedelta(days=5)
    mock_records = []

    # 1. Job: Database_Backup (Baseline ~100s)
    for i in range(8):
        start_dt = base_time + timedelta(hours=i * 12)
        duration = 100.0 + (i * 1.5) # normal variance
        exit_code = 0
        if i == 6:  # Anomaly: 3x slow spike
            duration = 315.0
        if i == 7:  # Anomaly: Silent crash
            exit_code = 1
        end_dt = start_dt + timedelta(seconds=duration)
        mock_records.append(("Database_Backup", start_dt.isoformat(), end_dt.isoformat(), duration, exit_code))

    # 2. Job: Cache_Refresh (Baseline ~30s)
    for i in range(8):
        start_dt = base_time + timedelta(hours=i * 12 + 2)
        duration = 30.0 + (i * 0.5)
        exit_code = 0
        end_dt = start_dt + timedelta(seconds=duration)
        mock_records.append(("Cache_Refresh", start_dt.isoformat(), end_dt.isoformat(), duration, exit_code))

    # 3. Job: Data_Sync (Baseline ~60s)
    for i in range(6):
        start_dt = base_time + timedelta(hours=i * 18 + 4)
        duration = 60.0 if i != 4 else 185.0 # Anomaly: 3x slow spike on Data Sync
        exit_code = 0
        end_dt = start_dt + timedelta(seconds=duration)
        mock_records.append(("Data_Sync", start_dt.isoformat(), end_dt.isoformat(), duration, exit_code))

    # 4. Job: Log_Cleanup (Baseline ~15s)
    for i in range(4):
        start_dt = base_time + timedelta(days=i, hours=1)
        duration = 15.0
        exit_code = 0 if i != 2 else 4 # Anomaly: Non-zero crash exit code 4
        end_dt = start_dt + timedelta(seconds=duration)
        mock_records.append(("Log_Cleanup", start_dt.isoformat(), end_dt.isoformat(), duration, exit_code))

    cursor.executemany("INSERT INTO logs (job_name, start_time, end_time, duration_seconds, exit_code) VALUES (?, ?, ?, ?, ?)", mock_records)
    conn.commit()
    conn.close()
    print(f"✓ Bulk seeded {len(mock_records)} comprehensive test logs into {DB_PATH}")
if __name__ == "__main__":
    seed_mock_data()