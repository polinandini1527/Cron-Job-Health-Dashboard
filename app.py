import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px
from src.processor import init_db, seed_mock_data, DB_PATH
from src.llm_helper import get_anomaly_narration

# Page config according to guidelines [cite: 19, 92]
st.set_page_config(page_title="Cron Job Health Dashboard", layout="wide")

# Initialize database on first load
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

def load_logs():
    """Load fresh, real-time logs from the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM logs", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Failed to load logs from database configuration: {e}")
        return pd.DataFrame()

def main():
    st.title("🚀 Cron Job Health Dashboard")
    st.markdown("Real-time monitoring of scheduled job execution metrics and AI-powered anomaly detection.")

    # Fetch fresh logs
    logs_df = load_logs()

    # --- Sidebar Presentation Controls ---
    st.sidebar.header("🛠️ Operational Controls")
    
    if st.sidebar.button("🌱 Seed Bulk Mock Data (with Anomalies)"):
        seed_mock_data()
        # Force AI narration to refresh when database changes
        if "cached_narration" in st.session_state:
            del st.session_state["cached_narration"]
        st.toast("Database seeded successfully with expanded logs!")
        st.rerun()

    if st.sidebar.button("🗑️ Clear Database Records"):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM logs")
            conn.commit()
            conn.close()
            if "cached_narration" in st.session_state:
                del st.session_state["cached_narration"]
            st.toast("Database cleared!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Wipe exception encountered: {e}")

    # Empty State Handlers [cite: 19]
    if logs_df.empty:
        st.warning("📭 No log data available. Use sidebar controls to seed mock data entries.")
        return

    # --- Executive Summary Section ---
    st.header("📊 Executive Summary")
    col1, col2, col3 = st.columns(3)

    total_runs = len(logs_df)
    failed_jobs = len(logs_df[logs_df["exit_code"] != 0])
    avg_runtime = logs_df["duration_seconds"].mean()

    col1.metric("Total Runs", total_runs)
    col2.metric("Failed Jobs (Silent Errors)", failed_jobs, delta=f"({failed_jobs/total_runs*100:.1f}%) Fail Rate" if total_runs > 0 else "0%")
    col3.metric("Avg Runtime Duration", f"{avg_runtime:.2f}s")

    st.divider()

   # --- AI Anomaly Narration Section (WITH AUTOMATIC FILE EXPORT) ---
    st.header("🤖 AI Anomaly Narration")
    
    cron_history_sorted = logs_df.copy()
    cron_history_sorted["start_time"] = pd.to_datetime(cron_history_sorted["start_time"])
    cron_history_sorted = cron_history_sorted.sort_values("start_time")

    if "cached_narration" not in st.session_state:
        with st.spinner("Gemini AI infrastructure model identifying data engineering anomalies..."):
            st.session_state.cached_narration = get_anomaly_narration(cron_history_sorted)
            
            try:
                import os
                from datetime import datetime  # Standard Python datetime module
                
                os.makedirs("outputs", exist_ok=True)
                with open("outputs/final_report.md", "w", encoding="utf-8") as f:
                    f.write("# 📊 System Generated AI Anomaly Report\n\n")
                    # FIX: Changed pd.datetime to datetime.now()
                    f.write(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("### 🔍 Identified Infrastructure Anomalies:\n")
                    f.write(st.session_state.cached_narration)
            except Exception as e:
                st.sidebar.error(f"Failed to auto-export report: {e}")
            
    st.info(st.session_state.cached_narration)
    st.caption("💾 A copy of this live analysis has been automatically exported to `outputs/final_report.md`")

    st.divider()

    # --- Global Duration Timeline Chart ---
    st.header("⏱️ Overall Execution Duration Timeline")
    fig = px.line(
        cron_history_sorted,
        x="start_time",
        y="duration_seconds",
        color="job_name",
        markers=True,
        title="All Jobs Performance Timelines (Seconds)",
        color_discrete_map={"Database_Backup": "#EF553B", "Cache_Refresh": "#636EFA", "Data_Sync": "#00CC96", "Log_Cleanup": "#AB63FA"}
    )
    fig.update_layout(height=350, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- Raw Log Data Table & Local Filtering ---
    st.header("📋 Interactive Filter Options & Dynamic Analytics")

    display_df = logs_df.copy()
    display_df["start_time"] = pd.to_datetime(display_df["start_time"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    display_df["end_time"] = pd.to_datetime(display_df["end_time"]).dt.strftime("%Y-%m-%d %H:%M:%S")

    # Interactive filtering components
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        selected_job = st.multiselect("Filter by Job Name", display_df["job_name"].unique(), default=display_df["job_name"].unique())
    with f_col2:
        show_failures_only = st.checkbox("Show Failed Jobs Only (Non-Zero Exit Codes)")

    # Execute dynamic filtering steps
    filtered_df = display_df[display_df["job_name"].isin(selected_job)]
    if show_failures_only:
        filtered_df = filtered_df[filtered_df["exit_code"] != 0]

    # Show the table [cite: 13, 19]
    st.dataframe(filtered_df, use_container_width=True, height=250)

    # NEW FEATURE: Separate Plot for the Filtered Table Data 
    if not filtered_df.empty:
        st.subheader("🎯 Filtered Data Insights")
        filtered_chart_df = filtered_df.copy()
        filtered_chart_df["start_time"] = pd.to_datetime(filtered_chart_df["start_time"])
        filtered_chart_df = filtered_chart_df.sort_values("start_time")
        
        fig_filtered = px.bar(
            filtered_chart_df,
            x="start_time",
            y="duration_seconds",
            color="job_name",
            barmode="group",
            title="Execution Runtimes for Filtered Selection Only",
            labels={"start_time": "Time", "duration_seconds": "Duration (Seconds)"}
        )
        fig_filtered.update_layout(height=300)
        st.plotly_chart(fig_filtered, use_container_width=True)
    else:
        st.info("Adjust filters to view custom visual charts.")

    st.divider()
    st.header("⚡ Live Subprocess Wrapper Execution")
    st.markdown("Simulate and run a real-time cron job command to test the tracking pipeline live.")
    
    with st.form("live_job_runner"):
        c_name = st.text_input("Job Name", value="AdHoc_DataSync")
        c_command = st.text_input("Shell Command String", value="echo 'Pipeline Processing Run Complete'")
        submit_run = st.form_submit_button("🚀 Dispatch Task Wrapper")
        
        if submit_run:
            with st.spinner("Subprocess executing..."):
                from src.processor import run_cron_job
                result_metrics = run_cron_job(c_name, c_command)
                
                # Clear narrative cache to force Gemini to analyze the new entry
                if "cached_narration" in st.session_state:
                    del st.session_state["cached_narration"]
                
                # FIX: Changed 'duration_seconds' to 'duration' to match src/processor.py return schema
                if result_metrics["exit_code"] == 0:
                    st.success(f"Task executed smoothly in {result_metrics['duration']:.4f}s (Exit Code: 0)")
                else:
                    st.error(f"Task encountered a non-zero exit crash state! (Exit Code: {result_metrics['exit_code']})")
                st.rerun()

if __name__ == "__main__":
    main()