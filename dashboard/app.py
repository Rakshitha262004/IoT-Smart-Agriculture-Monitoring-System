"""
IoT Smart Agriculture Monitoring System
File: dashboard/app.py

Streamlit dashboard that reads the sensor CSV log
and provides real-time visualization of all sensor
parameters with alerts and pump status.

Run: streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import time
from datetime import datetime

# ─────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Smart Agriculture Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
#  DARK THEME CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0d1117; }
    .block-container { padding-top: 1rem; }

    .metric-card {
        background: linear-gradient(135deg, #161b22, #21262d);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 18px 20px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #58a6ff;
        font-family: 'Courier New', monospace;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #8b949e;
        margin-top: 4px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .metric-status {
        font-size: 0.78rem;
        margin-top: 6px;
        font-weight: 600;
        padding: 2px 10px;
        border-radius: 20px;
        display: inline-block;
    }
    .status-ok   { background:#1f3d2a; color:#3fb950; }
    .status-warn { background:#3d2a1f; color:#d29922; }
    .status-crit { background:#3d1f1f; color:#f85149; }

    .alert-box {
        background: #3d1f1f;
        border-left: 4px solid #f85149;
        border-radius: 6px;
        padding: 10px 14px;
        margin: 6px 0;
        color: #f85149;
        font-size: 0.9rem;
    }
    .info-box {
        background: #1f3d2a;
        border-left: 4px solid #3fb950;
        border-radius: 6px;
        padding: 10px 14px;
        margin: 6px 0;
        color: #3fb950;
        font-size: 0.9rem;
    }
    .pump-on  { color: #3fb950; font-size: 1.4rem; font-weight: bold; }
    .pump-off { color: #8b949e; font-size: 1.4rem; font-weight: bold; }

    h1 { color: #e6edf3 !important; }
    h2, h3 { color: #c9d1d9 !important; }
    .stMarkdown p { color: #c9d1d9; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  THRESHOLDS
# ─────────────────────────────────────────
THRESHOLDS = {
    "soil_dry":  400,
    "soil_wet":  700,
    "water_low": 300,
    "light_low": 200,
    "temp_high": 35.0,
    "hum_low":   30.0,
}

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sensor_log.csv")


# ─────────────────────────────────────────
#  DATA LOADER
# ─────────────────────────────────────────
@st.cache_data(ttl=5)
def load_data():
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame()
    df = pd.read_csv(CSV_PATH, encoding="utf-8", encoding_errors="replace")
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    return df


def get_status_class(metric, value):
    if metric == "soil":
        if value < THRESHOLDS["soil_dry"]:  return "status-crit"
        if value > THRESHOLDS["soil_wet"]:  return "status-warn"
        return "status-ok"
    if metric == "temp":
        return "status-crit" if value > THRESHOLDS["temp_high"] else "status-ok"
    if metric == "hum":
        return "status-crit" if value < THRESHOLDS["hum_low"] else "status-ok"
    if metric == "water":
        return "status-crit" if value < THRESHOLDS["water_low"] else "status-ok"
    if metric == "light":
        return "status-warn" if value < THRESHOLDS["light_low"] else "status-ok"
    return "status-ok"


# ─────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────
st.markdown("# 🌿 IoT Smart Agriculture Monitoring Dashboard")
st.markdown("**Real-time sensor visualization | Threshold monitoring | Irrigation control**")
st.markdown("---")

# ─────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Dashboard Controls")

    auto_refresh = st.toggle("Auto-refresh (5s)", value=False)
    show_raw     = st.toggle("Show raw CSV data", value=False)

    st.markdown("---")
    st.markdown("### 🎛️ Threshold Settings")
    t_soil_dry  = st.slider("Soil Dry Threshold",  0, 600, THRESHOLDS["soil_dry"])
    t_temp_high = st.slider("Temp High (°C)",      25.0, 50.0, THRESHOLDS["temp_high"], step=0.5)
    t_water_low = st.slider("Water Low Threshold", 0, 600, THRESHOLDS["water_low"])

    # Update thresholds from sliders
    THRESHOLDS["soil_dry"]  = t_soil_dry
    THRESHOLDS["temp_high"] = t_temp_high
    THRESHOLDS["water_low"] = t_water_low

    st.markdown("---")
    st.markdown("### 📋 Project Info")
    st.markdown("""
    - **Project**: Smart Agriculture IoT  
    - **Platform**: Arduino UNO / Python Sim  
    - **Sensors**: DHT11, Soil, LDR, Water  
    - **Author**: Rakshitha (2025)
    """)

# ─────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────
df = load_data()

if df.empty:
    st.warning("⚠️ No sensor data found. Run the Python simulation first:")
    st.code("python python_simulation/sensor_simulator.py --scenario dry --readings 30")
    st.stop()

latest = df.iloc[-1]

# ─────────────────────────────────────────
#  LIVE METRIC CARDS (TOP ROW)
# ─────────────────────────────────────────
st.markdown("### 📡 Live Sensor Readings")

c1, c2, c3, c4, c5, c6 = st.columns(6)

metrics = [
    (c1, "🌱", "Soil Moisture", int(latest["Soil_Moisture"]),
     latest["Soil_Status"], "soil"),
    (c2, "🌡️", "Temperature", f"{latest['Temperature_C']:.1f}°C",
     "NORMAL" if latest['Temperature_C'] <= THRESHOLDS['temp_high'] else "HIGH", "temp"),
    (c3, "💧", "Humidity", f"{latest['Humidity_pct']:.1f}%",
     "NORMAL" if latest['Humidity_pct'] >= THRESHOLDS['hum_low'] else "LOW", "hum"),
    (c4, "🪣", "Water Level", int(latest["Water_Level"]),
     latest["Water_Status"], "water"),
    (c5, "☀️", "Light Level", int(latest["Light_Level"]),
     latest["Light_Status"], "light"),
    (c6, "⚙️", "Pump Status", latest["Pump_Status"],
     latest["Pump_Status"], "pump"),
]

for col, icon, label, value, status, metric_key in metrics:
    with col:
        sc = "status-ok"
        if metric_key == "pump":
            sc = "status-ok" if status == "ON" else "status-warn"
        elif metric_key != "pump":
            sc = get_status_class(metric_key, latest.get(
                {"soil":"Soil_Moisture","temp":"Temperature_C",
                 "hum":"Humidity_pct","water":"Water_Level",
                 "light":"Light_Level"}.get(metric_key, "Soil_Moisture")
            ))

        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:1.6rem">{icon}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-status {sc}">{status}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────
#  ALERTS PANEL
# ─────────────────────────────────────────
alert_str = str(latest.get("Alerts", "NONE"))
alerts_list = [a.strip() for a in alert_str.split("|") if a.strip() != "NONE"]

col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### ⚠️ Active Alerts")
    if alerts_list:
        for alert in alerts_list:
            st.markdown(f'<div class="alert-box">⚠ {alert}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">✅ All parameters within normal range</div>',
                    unsafe_allow_html=True)

with col_right:
    st.markdown("### 🚿 Irrigation Status")
    pump_on = latest["Pump_Status"] == "ON"
    if pump_on:
        st.markdown('<p class="pump-on">🟢 PUMP ON — Irrigating</p>', unsafe_allow_html=True)
        st.info("Soil is dry. Automatic irrigation active.")
    else:
        st.markdown('<p class="pump-off">⚫ PUMP OFF — Standby</p>', unsafe_allow_html=True)
        st.success("Moisture levels are adequate. Pump on standby.")

st.markdown("---")

# ─────────────────────────────────────────
#  CHARTS
# ─────────────────────────────────────────
st.markdown("### 📈 Sensor Trends")

tab1, tab2, tab3, tab4 = st.tabs([
    "🌱 Soil & Water", "🌡️ Temp & Humidity", "☀️ Light", "📊 All Sensors"
])

color_map = {
    "Soil":  "#58a6ff",
    "Water": "#1f6feb",
    "Temp":  "#f85149",
    "Hum":   "#3fb950",
    "Light": "#e3b341",
}

with tab1:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=("Soil Moisture", "Water Level"))
    fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["Soil_Moisture"],
                             name="Soil", line=dict(color=color_map["Soil"], width=2),
                             fill="tozeroy", fillcolor="rgba(88,166,255,0.1)"), row=1, col=1)
    fig.add_hline(y=THRESHOLDS["soil_dry"], line_dash="dash",
                  line_color="#f85149", annotation_text="Dry threshold", row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["Water_Level"],
                             name="Water", line=dict(color=color_map["Water"], width=2),
                             fill="tozeroy", fillcolor="rgba(31,111,235,0.1)"), row=2, col=1)
    fig.add_hline(y=THRESHOLDS["water_low"], line_dash="dash",
                  line_color="#f85149", annotation_text="Low water", row=2, col=1)
    fig.update_layout(height=440, paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
                      font_color="#c9d1d9", showlegend=True)
    fig.update_xaxes(gridcolor="#21262d")
    fig.update_yaxes(gridcolor="#21262d")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=("Temperature (°C)", "Humidity (%)"))
    fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["Temperature_C"],
                             name="Temp", line=dict(color=color_map["Temp"], width=2)), row=1, col=1)
    fig.add_hline(y=THRESHOLDS["temp_high"], line_dash="dash",
                  line_color="#e3b341", annotation_text="High temp", row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["Humidity_pct"],
                             name="Humidity", line=dict(color=color_map["Hum"], width=2)), row=2, col=1)
    fig.add_hline(y=THRESHOLDS["hum_low"], line_dash="dash",
                  line_color="#e3b341", annotation_text="Low humidity", row=2, col=1)
    fig.update_layout(height=440, paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
                      font_color="#c9d1d9")
    fig.update_xaxes(gridcolor="#21262d")
    fig.update_yaxes(gridcolor="#21262d")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    fig = px.area(df, x="Timestamp", y="Light_Level",
                  color_discrete_sequence=[color_map["Light"]])
    fig.add_hline(y=THRESHOLDS["light_low"], line_dash="dash",
                  line_color="#f85149", annotation_text="Low light threshold")
    fig.update_layout(height=360, paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
                      font_color="#c9d1d9")
    fig.update_xaxes(gridcolor="#21262d")
    fig.update_yaxes(gridcolor="#21262d")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    # Normalize to 0–100 for comparison
    df_norm = df.copy()
    for col in ["Soil_Moisture", "Temperature_C", "Humidity_pct", "Water_Level", "Light_Level"]:
        df_norm[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min() + 1e-9) * 100

    fig = go.Figure()
    for col, label, color in [
        ("Soil_Moisture",  "Soil",     color_map["Soil"]),
        ("Temperature_C",  "Temp",     color_map["Temp"]),
        ("Humidity_pct",   "Humidity", color_map["Hum"]),
        ("Water_Level",    "Water",    color_map["Water"]),
        ("Light_Level",    "Light",    color_map["Light"]),
    ]:
        fig.add_trace(go.Scatter(x=df["Timestamp"], y=df_norm[col],
                                 name=label, line=dict(color=color, width=2)))
    fig.update_layout(height=400, paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
                      font_color="#c9d1d9", yaxis_title="Normalized (0–100)")
    fig.update_xaxes(gridcolor="#21262d")
    fig.update_yaxes(gridcolor="#21262d")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────
#  PUMP HISTORY BAR
# ─────────────────────────────────────────
st.markdown("### 🔄 Pump Activation History")
df["Pump_ON"] = (df["Pump_Status"] == "ON").astype(int)
fig_pump = px.bar(df, x="Timestamp", y="Pump_ON",
                  color="Pump_ON",
                  color_continuous_scale=[[0, "#21262d"], [1, "#3fb950"]],
                  labels={"Pump_ON": "Pump Active"})
fig_pump.update_layout(height=200, paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
                        font_color="#c9d1d9", showlegend=False, coloraxis_showscale=False)
fig_pump.update_xaxes(gridcolor="#21262d")
st.plotly_chart(fig_pump, use_container_width=True)

# ─────────────────────────────────────────
#  RAW DATA TABLE
# ─────────────────────────────────────────
if show_raw:
    st.markdown("### 🗃️ Raw Sensor Data")
    st.dataframe(df.tail(50), use_container_width=True)
    st.download_button(
        "⬇️ Download Full CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="sensor_log_export.csv",
        mime="text/csv"
    )

# ─────────────────────────────────────────
#  SUMMARY STATS
# ─────────────────────────────────────────
st.markdown("---")
st.markdown("### 📊 Session Statistics")
s1, s2, s3, s4 = st.columns(4)
s1.metric("Total Readings",     len(df))
s2.metric("Avg Soil Moisture",  f"{df['Soil_Moisture'].mean():.0f}")
s3.metric("Avg Temp (°C)",      f"{df['Temperature_C'].mean():.1f}")
s4.metric("Pump ON Count",      int(df["Pump_ON"].sum()))

# ─────────────────────────────────────────
#  AUTO-REFRESH
# ─────────────────────────────────────────
if auto_refresh:
    time.sleep(5)
    st.rerun()
