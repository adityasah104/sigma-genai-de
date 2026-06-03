import time
from datetime import datetime
import pandas as pd
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sigma Command Center",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Premium Custom CSS (Matte Black Theme) ────────────────────────────────────
st.markdown("""
<style>
    /* Global Theme & Background */
    .stApp {
        background-color: #0a0a0a;
        color: #e2e8f0;
        font-family: 'Inter', 'Roboto', sans-serif;
    }
    
    /* Hide top header line */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Title */
    h1 {
        font-size: 3rem !important;
        font-weight: 800 !important;
        color: #f8fafc !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Metric Cards Styling (Matte Black) */
    div[data-testid="stMetric"] {
        background-color: #18181b;
        border: 1px solid #27272a;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
        transition: border-color 0.2s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        border: 1px solid #52525b;
    }
    
    /* Metric Values */
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #f8fafc !important;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: #a1a1aa !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    /* Alert / Status Boxes */
    div[data-testid="stAlert"] {
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Success Box (Muted Green) */
    .st-emotion-cache-1215b49 {
        background-color: #064e3b !important;
        border-left: 4px solid #10b981 !important;
        color: #d1fae5 !important;
    }
    
    /* Error Box (Muted Red) */
    .st-emotion-cache-1kqj710 {
        background-color: #450a0a !important;
        border-left: 4px solid #ef4444 !important;
        color: #fee2e2 !important;
    }
    
    /* Dataframe Container */
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #27272a;
    }
    
    /* Refresh Button Styling */
    button[kind="secondary"] {
        background-color: #27272a !important;
        color: #f4f4f5 !important;
        border: 1px solid #3f3f46 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 0.5rem 2rem !important;
        transition: all 0.2s ease !important;
    }
    
    button[kind="secondary"]:hover {
        background-color: #3f3f46 !important;
        border-color: #52525b !important;
    }
    
    /* Expander styling */
    div[data-testid="stExpander"] {
        background-color: #18181b !important;
        border: 1px solid #27272a !important;
        border-radius: 10px !important;
    }
    
    /* Subheaders */
    h3 {
        color: #f8fafc !important;
        font-weight: 600 !important;
        border-bottom: 1px solid #27272a;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)


# ── State Management ──────────────────────────────────────────────────────────
if "app_state" not in st.session_state:
    st.session_state.app_state = "NORMAL"

def set_disaster():
    st.session_state.app_state = "DISASTER"

def set_recovery():
    st.session_state.app_state = "RECOVERY"

def reset_state():
    st.session_state.app_state = "NORMAL"

# ── Sidebar Controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🛠️ Pipeline Controls")
    st.markdown("Use these controls to interact with the pipeline directly from the dashboard.")
    
    st.subheader("1. Chaos Engineering")
    if st.button("🚨 Inject Disaster", use_container_width=True):
        with st.spinner("Injecting silent failure... (takes ~30s)"):
            time.sleep(30.0)
            set_disaster()
        st.success("Disaster injected!")
                
    st.subheader("2. Self-Healing AI")
    if st.button("🧠 Unleash AI Recovery", use_container_width=True):
        with st.spinner("Agents are running... this takes ~2 minutes"):
            time.sleep(120.0)
            set_recovery()
        st.success("Recovery complete!")


# ── Mock Data based on State ──────────────────────────────────────────────────
state = st.session_state.app_state

if state == "NORMAL":
    total_loaded = "1,000"
    records_lost = "0"
    recovered = "0"
    quarantined = "0"
    root_cause = "—"
    fix_applied = "—"
    report_md = ""
    quarantine_df = pd.DataFrame()
    alarms = [
        {"name": "sigma-snowflake-zero-load", "trigger": "Fires if COPY INTO loads 0 rows", "state": "OK"},
        {"name": "sigma-lambda-version-change", "trigger": "Fires on Lambda error spike", "state": "OK"},
        {"name": "sigma-pipeline-row-divergence", "trigger": "Fires if row count diverges", "state": "OK"}
    ]
elif state == "DISASTER":
    total_loaded = "1,000"
    records_lost = "847"
    recovered = "0"
    quarantined = "0"
    root_cause = "—"
    fix_applied = "—"
    report_md = ""
    quarantine_df = pd.DataFrame()
    alarms = [
        {"name": "sigma-snowflake-zero-load", "trigger": "Fires if COPY INTO loads 0 rows", "state": "OK"},
        {"name": "sigma-lambda-version-change", "trigger": "Fires on Lambda error spike", "state": "OK"},
        {"name": "sigma-pipeline-row-divergence", "trigger": "Fires if row count diverges", "state": "ALARM"}
    ]
elif state == "RECOVERY":
    total_loaded = "1,824"
    records_lost = "847"
    recovered = "824"
    quarantined = "23"
    root_cause = "Lambda v2 renamed `merchant_name` to `merchant_nm` and changed the date format to DD-MM-YYYY, causing silent failure in Snowflake COPY INTO."
    fix_applied = "- **Lambda rolled back:** `sigma-data-producer` alias LIVE v2 → v1\n- **Records replayed:** 824 loaded, 0 duplicates skipped"
    
    report_md = f"""# Incident Report — ₹4,72,340 GMV Loss — {datetime.now().strftime('%Y-%m-%d')}

**Severity:** HIGH
**Total downtime:** 4 minutes
**Human interventions:** 0

---

## Summary

Silent pipeline failure detected. 847 records unloaded due to schema drift. Root cause identified and fixed by autonomous agent system.

---

## Root Cause

Lambda v2 auto-deployed at 02:11 UTC and renamed `merchant_name` to `merchant_nm`. This caused Snowflake's COPY INTO command to silently fail. 

---

## Fix Applied

- **Lambda rolled back:** sigma-data-producer alias LIVE v2 → v1
- **Records replayed:** 824 loaded, 0 duplicates skipped
- **Records quarantined:** 23 (null_transaction_id)
"""
    # Mock quarantine data
    quarantine_df = pd.DataFrame({
        "transaction_id": ["—"] * 23,
        "merchant_name": ["QuickMart", "TechZone"] * 11 + ["CafeBlend"],
        "amount": [1250, 450] * 11 + [320],
        "quarantine_reason": ["null_transaction_id"] * 23,
        "quarantined_at": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * 23
    })
    
    alarms = [
        {"name": "sigma-snowflake-zero-load", "trigger": "Fires if COPY INTO loads 0 rows", "state": "OK"},
        {"name": "sigma-lambda-version-change", "trigger": "Fires on Lambda error spike", "state": "OK"},
        {"name": "sigma-pipeline-row-divergence", "trigger": "Fires if row count diverges", "state": "OK"}
    ]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Sigma Command Center")
st.caption(
    f"Bucket: **s3://mock-sigma-bucket** · "
    f"Report: **reports/incident_latest.md** · "
    f"Last refreshed: {datetime.now().strftime('%H:%M:%S')} (DEMO MODE)"
)
if st.button("🔄 Refresh Data"):
    st.rerun()

st.markdown("---")

# ── KPI Cards ─────────────────────────────────────────────────────────────────
st.subheader("System Metrics")
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Total Records Loaded", total_loaded)
with c2:
    st.metric("Records Lost", records_lost)
with c3:
    st.metric("Records Recovered", recovered)
with c4:
    st.metric("Records Quarantined", quarantined)
with c5:
    alarms_ok = sum(1 for a in alarms if a["state"] == "OK")
    st.metric("Alarms Configured", f"{alarms_ok} / {len(alarms)}")

st.markdown("---")

# ── Root Cause + Fix ──────────────────────────────────────────────────────────
left, right = st.columns(2)

with left:
    st.subheader("Root Cause")
    if root_cause != "—":
        st.error(root_cause)
    else:
        st.warning("Root cause not found in report — check S3")

with right:
    st.subheader("Fix Applied")
    if fix_applied != "—":
        st.success(fix_applied)
    else:
        st.warning("Fix details not found in report — check S3")

st.markdown("---")

# ── Prevention Measures ───────────────────────────────────────────────────────
st.subheader("Prevention — CloudWatch Alarms Created")
if alarms:
    cols = st.columns(len(alarms))
    for col, alarm in zip(cols, alarms):
        with col:
            astate = alarm["state"]
            icon  = "🟢" if astate == "OK" else ("🔴" if astate == "ALARM" else "🟡")
            st.markdown(f"**{icon} {alarm['name']}**")
            st.caption(f"State: {astate}")
            if alarm["trigger"] != "—":
                st.caption(alarm["trigger"])
else:
    st.warning("No alarms found — did the Hardening Agent complete?")

st.markdown("---")

# ── Quarantine Table ──────────────────────────────────────────────────────────
st.subheader(f"Quarantined Records ({quarantined})")
if not quarantine_df.empty:
    st.dataframe(quarantine_df, use_container_width=True)
else:
    st.info("No quarantine file found in S3")

st.markdown("---")

# ── Incident Report ───────────────────────────────────────────────────────────
st.subheader("Full Incident Report")
if report_md:
    with st.expander("Click to read the CTO-ready post-mortem", expanded=True):
        st.markdown(report_md)
else:
    st.warning(
        "No incident report found in S3. "
        "Did Phase 3 complete successfully? Click 'Unleash AI Recovery' to generate one."
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    f"Sigma Intelligence Platform · "
    f"Demo Mode · "
    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)
