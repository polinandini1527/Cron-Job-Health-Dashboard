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

    # 1. Job: Database_Backup (Real Enterprise Baseline ~12.0s to 15.0s)
    for i in range(8):
        start_dt = base_time + timedelta(hours=i * 12)
        duration = 12.5 + (i * 0.25) # Realistic incremental data growth variance
        exit_code = 0
        if i == 6:  # Authentic Anomaly: 3x slow spike (Resource block/IO bottleneck)
            duration = 48.5
        if i == 7:  # Authentic Anomaly: Silent script crash
            exit_code = 1
        end_dt = start_dt + timedelta(seconds=duration)
        mock_records.append(("Database_Backup", start_dt.isoformat(), end_dt.isoformat(), duration, exit_code))

    # 2. Job: Cache_Refresh (Real Production Baseline ~0.4s to 0.8s)
    for i in range(8):
        start_dt = base_time + timedelta(hours=i * 12 + 2)
        duration = 0.45 + (i * 0.02) # Sub-second cache performance execution
        exit_code = 0
        end_dt = start_dt + timedelta(seconds=duration)
        mock_records.append(("Cache_Refresh", start_dt.isoformat(), end_dt.isoformat(), duration, exit_code))

    # 3. Job: Data_Sync (Real Production Baseline ~4.0s to 6.0s)
    for i in range(6):
        start_dt = base_time + timedelta(hours=i * 18 + 4)
        duration = 4.8 if i != 4 else 19.5 # Authentic Anomaly: 3x slow spike on remote API hang
        exit_code = 0
        end_dt = start_dt + timedelta(seconds=duration)
        mock_records.append(("Data_Sync", start_dt.isoformat(), end_dt.isoformat(), duration, exit_code))

    # 4. Job: Log_Cleanup (Real Production Baseline ~0.1s to 0.3s)
    for i in range(4):
        start_dt = base_time + timedelta(days=i, hours=1)
        duration = 0.18
        exit_code = 0 if i != 2 else 4 # Authentic Anomaly: Corrupted permissions code 4
        end_dt = start_dt + timedelta(seconds=duration)
        mock_records.append(("Log_Cleanup", start_dt.isoformat(), end_dt.isoformat(), duration, exit_code))
    cursor.executemany("INSERT INTO logs (job_name, start_time, end_time, duration_seconds, exit_code) VALUES (?, ?, ?, ?, ?)", mock_records)
    conn.commit()
    conn.close()
    print(f"✓ Bulk seeded {len(mock_records)} comprehensive test logs into {DB_PATH}")
if __name__ == "__main__":
    seed_mock_data()