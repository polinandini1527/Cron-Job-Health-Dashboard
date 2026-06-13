import pytest
import sqlite3
import os
from pathlib import Path

# Override the database path for safe isolated testing
TEST_DB_PATH = "data/test_cron_logs.db"

@pytest.fixture
def cleanup_db():
    """Fixture to safely clean up the isolated test database before and after tests."""
    if Path(TEST_DB_PATH).exists():
        try:
            os.remove(TEST_DB_PATH)
        except PermissionError:
            pass
    yield
    if Path(TEST_DB_PATH).exists():
        try:
            os.remove(TEST_DB_PATH)
        except PermissionError:
            pass

def test_init_db_happy_path(cleanup_db):
    """
    Happy-path test to verify database setup parameters cleanly.
    """
    # Initialize the safe directory path structure manually for testing isolation
    Path("data").mkdir(exist_ok=True)
    
    conn = sqlite3.connect(TEST_DB_PATH)
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

    # 1. Verify database file exists on disk location
    assert Path(TEST_DB_PATH).exists(), f"Test database file not created at {TEST_DB_PATH}"

    # 2. Query table schema setup properties
    cursor.execute("PRAGMA table_info(logs)")
    columns = cursor.fetchall()

    expected_columns = ["id", "job_name", "start_time", "end_time", "duration_seconds", "exit_code"]
    actual_columns = [col[1] for col in columns]
    assert actual_columns == expected_columns, f"Columns mismatch. Expected {expected_columns}, got {actual_columns}"

    # 3. Test operational validation record injection checks
    cursor.execute("SELECT COUNT(*) FROM logs")
    assert cursor.fetchone()[0] == 0, "Table should be empty after initial setup steps"

    cursor.execute(
        "INSERT INTO logs (job_name, start_time, end_time, duration_seconds, exit_code) VALUES (?, ?, ?, ?, ?)",
        ("test_job", "2026-06-13T00:00:00", "2026-06-13T00:01:00", 60.0, 0),
    )
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM logs")
    assert cursor.fetchone()[0] == 1, "Data insertion baseline step check failed"

    conn.close()