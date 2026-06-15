import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from src.processor import init_db, seed_mock_data, DB_PATH
from src.llm_helper import get_anomaly_narration

# Page config configured for an expansive, modern dashboard view
st.set_page_config(
    page_title="Cron Job Health Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Corporate CSS for metrics and layout structure
st.markdown("""
    <style>
        /* Base background container adjustments */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 1.5rem !important;
            background-color: #f8fafc;
        }
        
        /* Premium title header panel style */
        .header-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-top: 5px solid #3b82f6;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.05);
            margin-bottom: 25px;
        }
        
        /* Premium metric presentation frames */
        .kpi-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 5px solid #3b82f6;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.05);
            margin-bottom: 15px;
        }
        .kpi-card.fail {
            border-left: 5px solid #ef4444;
        }
        .kpi-card-val {
            font-size: 28px;
            font-weight: 700;
            color: #0f172a;
            line-height: 1.2;
        }
        .kpi-card-lbl {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
            margin-bottom: 4px;
            font-weight: 600;
        }
        
        /* Beautiful Anomaly Alert Box Layouts */
        .alert-box {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .alert-box.critical {
            border-left: 6px solid #ef4444;
            background-color: #fffafb;
        }
        .alert-box.warning {
            border-left: 6px solid #f59e0b;
            background-color: #fefdfb;
        }
        .alert-title {
            font-size: 15px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 8px;
        }
        .alert-desc {
            font-size: 13.5px;
            color: #475569;
            line-height: 1.6;
            padding-left: 2px;
        }
        
        /* Quota Failure Error Banner Layout */
        .quota-error-box {
            background-color: #fdf2f2;
            border: 1px solid #fde8e8;
            border-radius: 10px;
            padding: 18px;
            color: #9b1c1c;
            font-size: 14px;
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize database on first execution trace
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

def render_dynamic_ai_insights(narration_text):
    """
    Dynamically parses raw markdown output from the LLM, handles API errors,
    and maps individual anomalies to structured, clean notification blocks
    while stripping unrendered raw markdown formatting keys.
    """
    # Intercept Quota Limit Exhaustion (429) gracefully
    if "RESOURCE_EXHAUSTED" in narration_text or "429" in narration_text:
        st.markdown("""
            <div class='quota-error-box'>
                <strong>⚠️ Gemini API Rate Limit Exceeded (Quota 429)</strong><br>
                The automated SRE agent is currently experiencing free-tier resource limitations. 
                Please wait a few moments before re-triggering metrics operations.
            </div>
        """, unsafe_allow_html=True)
        return

    if "All systems operating within normal parameters" in narration_text:
        st.success("🟢 **All systems operating within normal parameters.** No infrastructure deviations detected.")
        return

    # Split lines cleanly by newlines
    raw_lines = narration_text.split('\n')
    current_alert = None
    alerts_compiled = []

    for line in raw_lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        # Detect alert entry points via structural markers
        if line_stripped.startswith("- 🚨") or line_stripped.startswith("- ⚠️") or line_stripped.startswith("🚨") or line_stripped.startswith("⚠️"):
            if current_alert:
                alerts_compiled.append(current_alert)
            
            is_critical = "🚨" in line_stripped
            severity_class = "critical" if is_critical else "warning"
            
            # Refined Cleaning Step: Strip structural bullet markers and raw markdown bold characters (**)
            clean_title = line_stripped.replace("- 🚨", "🚨").replace("- ⚠️", "⚠️").replace("**", "").strip()
            
            current_alert = {
                "class": severity_class,
                "header": clean_title,
                "details": []
            }
        elif current_alert and (line_stripped.startswith("*") or line_stripped.startswith("-")):
            # Format supporting details cleanly
            clean_detail = line_stripped.lstrip("* -").strip()
            current_alert["details"].append(clean_detail)
        elif current_alert:
            current_alert["details"].append(line_stripped)

    if current_alert:
        alerts_compiled.append(current_alert)

    # Render out custom stylized alert cards
    if not alerts_compiled:
        st.markdown(f"<div class='alert-box warning'><div class='alert-desc'>{narration_text}</div></div>", unsafe_allow_html=True)
        return

    for alert in alerts_compiled:
        details_html = ""
        for detail in alert["details"]:
            # Clean up inline raw formatting marks (*) from the detail descriptions
            clean_detail_text = detail.replace("*", "").strip()
            
            # Format inline bullet headers for root causes vs recommended solutions
            if clean_detail_text.startswith("Possible Root Cause:"):
                details_html += f"<p style='margin: 4px 0;'><strong>🔍 Probable Cause:</strong> {clean_detail_text.replace('Possible Root Cause:', '').strip()}</p>"
            elif clean_detail_text.startswith("Recommended Action:"):
                details_html += f"<p style='margin: 4px 0;'><strong>🛠️ Recommended Action:</strong> {clean_detail_text.replace('Recommended Action:', '').strip()}</p>"
            else:
                details_html += f"<p style='margin: 4px 0;'>• {clean_detail_text}</p>"
                
        st.markdown(f"""
            <div class='alert-box {alert["class"]}'>
                <div class='alert-title'>{alert["header"]}</div>
                <div class='alert-desc'>{details_html}</div>
            </div>
        """, unsafe_allow_html=True)

def main():
    # --- Separate Top Header Container Box ---
    st.markdown("""
        <div class="header-card">
            <h2 style="margin-top: 0px; margin-bottom: 4px; font-weight: 700; color: #0f172a;">🚀 Cron Job Health Dashboard</h2>
            <p style="color: #64748b; font-size: 0.95rem; margin-bottom: 0px;">AI-Powered Observability & Scheduled Job Telemetry Logs Pipeline</p>
        </div>
    """, unsafe_allow_html=True)

    # Fetch logs from persistent database
    logs_df = load_logs()

    # --- Sidebar Presentation Controls & Filters ---
    st.sidebar.markdown("### 🔍 Global Filter Settings")
    
    if not logs_df.empty:
        display_df = logs_df.copy()
        display_df["start_time"] = pd.to_datetime(display_df["start_time"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        display_df["end_time"] = pd.to_datetime(display_df["end_time"]).dt.strftime("%Y-%m-%d %H:%M:%S")

        selected_job = st.sidebar.multiselect(
            "Filter by Job Name", 
            options=display_df["job_name"].unique(), 
            default=display_df["job_name"].unique()
        )
        show_failures_only = st.sidebar.checkbox("Isolate Non-Zero Failures Only", value=False)
        
        # Execute filtering parameters
        filtered_df = display_df[display_df["job_name"].isin(selected_job)]
        if show_failures_only:
            filtered_df = filtered_df[filtered_df["exit_code"] != 0]
    else:
        filtered_df = pd.DataFrame()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Administrative Actions")
    
    if st.sidebar.button("🌱 Seed Synthetic Production Logs", use_container_width=True):
        seed_mock_data()
        if "cached_narration" in st.session_state:
            del st.session_state["cached_narration"]
        st.toast("Database seeded successfully with expanded logs!")
        st.rerun()

    if st.sidebar.button("🗑️ Clear Active Data Store", use_container_width=True):
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

    # Empty State Configuration
    if logs_df.empty:
        st.warning("📭 No log data available. Use sidebar controls to seed mock data entries.")
        return

    # Process data sorting metrics
    cron_history_sorted = logs_df.copy()
    cron_history_sorted["start_time"] = pd.to_datetime(cron_history_sorted["start_time"])
    cron_history_sorted = cron_history_sorted.sort_values("start_time")

    # --- Executive KPI Summary Cards Row ---
    total_runs = len(logs_df)
    failed_jobs = len(logs_df[logs_df["exit_code"] != 0])
    avg_runtime = logs_df["duration_seconds"].mean()
    fail_rate_pct = (failed_jobs / total_runs * 100) if total_runs > 0 else 0

    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.markdown(f"<div class='kpi-card'><div class='kpi-card-lbl'>Total Captured Runs</div><div class='kpi-card-val'>{total_runs} Runs</div></div>", unsafe_allow_html=True)
    with m_col2:
        card_class = "kpi-card fail" if failed_jobs > 0 else "kpi-card"
        st.markdown(f"<div class='{card_class}'><div class='kpi-card-lbl'>Silent Script Failures</div><div class='kpi-card-val'>{failed_jobs} <span style='font-size: 15px; font-weight: 500; color: #ef4444;'>({fail_rate_pct:.1f}% Rate)</span></div></div>", unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"<div class='kpi-card'><div class='kpi-card-lbl'>System Running Average</div><div class='kpi-card-val'>{avg_runtime:.3f}s</div></div>", unsafe_allow_html=True)

    # --- Section 1: AI Anomaly Narration Panel ---
    st.markdown("<h4 style='margin-top: 15px; margin-bottom: 10px;'>🤖 Real-Time AI Observability Narration</h4>", unsafe_allow_html=True)
    
    if "cached_narration" not in st.session_state:
        with st.spinner("Gemini AI infrastructure model identifying data engineering anomalies..."):
            st.session_state.cached_narration = get_anomaly_narration(cron_history_sorted)
            
            try:
                os.makedirs("outputs", exist_ok=True)
                with open("outputs/final_report.md", "w", encoding="utf-8") as f:
                    f.write("# 📊 System Generated AI Anomaly Report\n\n")
                    f.write(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("### 🔍 Identified Infrastructure Anomalies:\n")
                    f.write(st.session_state.cached_narration)
            except Exception as e:
                st.sidebar.error(f"Failed to auto-export report: {e}")

    # Render out parsed text items inside styled alert matrices cleanly
    render_dynamic_ai_insights(st.session_state.cached_narration)
    st.markdown("<p style='font-size: 11px; color: #64748b; margin-top: -5px; margin-bottom: 20px;'>💾 Production Insights compiled and auto-exported to <code>outputs/final_report.md</code></p>", unsafe_allow_html=True)

    # --- Section 2: Full Width Interactive Visualizations Metrics ---
    st.markdown("<h4 style='margin-top: 10px; margin-bottom: 5px;'>⏱️ System Execution Metrics Timeline</h4>", unsafe_allow_html=True)
    fig = px.line(
        cron_history_sorted,
        x="start_time",
        y="duration_seconds",
        color="job_name",
        markers=True,
        labels={"start_time": "Timestamp", "duration_seconds": "Duration (Seconds)", "job_name": "Job Task"},
        color_discrete_map={"Database_Backup": "#EF553B", "Cache_Refresh": "#636EFA", "Data_Sync": "#00CC96", "Log_Cleanup": "#AB63FA"}
    )
    fig.update_layout(
        height=300, 
        margin=dict(l=10, r=10, t=15, b=10),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    fig.update_xaxes(showgrid=True, gridcolor='#e2e8f0')
    fig.update_yaxes(showgrid=True, gridcolor='#e2e8f0')
    st.plotly_chart(fig, use_container_width=True)

    # --- Section 3: Data Explorer DataGrid & Filtered Charts ---
    st.markdown("<h4 style='margin-top: 20px; margin-bottom: 10px;'>📋 Interactive Filter Results & Dynamic Analytics</h4>", unsafe_allow_html=True)
    
    if not filtered_df.empty:
        v_col1, v_col2 = st.columns([1.1, 0.9], gap="large")
        with v_col1:
            st.markdown("<p style='font-size:12px; color:#64748b; margin-bottom:6px;'>Active Telemetry Database Records:</p>", unsafe_allow_html=True)
            st.dataframe(filtered_df, use_container_width=True, height=260)
        with v_col2:
            filtered_chart_df = filtered_df.copy()
            filtered_chart_df["start_time"] = pd.to_datetime(filtered_chart_df["start_time"])
            filtered_chart_df = filtered_chart_df.sort_values("start_time")
            
            fig_filtered = px.bar(
                filtered_chart_df,
                x="start_time",
                y="duration_seconds",
                color="job_name",
                title="Execution Runtimes for Filtered Selection Only",
                labels={"start_time": "Time", "duration_seconds": "Duration (s)"}
            )
            fig_filtered.update_layout(
                height=260, 
                margin=dict(l=10, r=10, t=30, b=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_filtered, use_container_width=True)
    else:
        st.info("Adjust the sidebar filter options to inspect matching log metrics.")

    # --- Section 4: Live Subprocess Command Runner Form Component ---
    st.markdown("<h4 style='margin-top: 25px; margin-bottom: 5px;'>⚡ Live Active Subprocess Runner Form</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 0.9rem; margin-bottom: 15px;'>Simulate cron job activity live by dispatching a terminal instruction straight into the pipeline wrapper.</p>", unsafe_allow_html=True)
    
    with st.form("live_job_runner", clear_on_submit=False):
        run_col1, run_col2 = st.columns(2)
        with run_col1:
            c_name = st.text_input("Target Task Label Identifier", value="AdHoc_DataSync")
        with run_col2:
            c_command = st.text_input("Custom Shell Instruction Line String", value="echo 'Pipeline Intercept Success'")
            
        submit_run = st.form_submit_button("🚀 Dispatch Active Job Wrapper", use_container_width=True)
        
        if submit_run:
            with st.spinner("Subprocess invoking kernel hooks..."):
                from src.processor import run_cron_job
                result_metrics = run_cron_job(c_name, c_command)
                
                if "cached_narration" in st.session_state:
                    del st.session_state["cached_narration"]
                
                if result_metrics["exit_code"] == 0:
                    st.success(f"Execution complete. Captured runtime context cleanly: {result_metrics['duration']:.4f}s (Exit Code: 0)")
                else:
                    st.error(f"Execution failed. Intercepted non-zero system flag anomaly termination (Exit Code: {result_metrics['exit_code']})")
                st.rerun()

if __name__ == "__main__":
    main()