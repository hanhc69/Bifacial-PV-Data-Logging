import streamlit as st
import pandas as pd

def show_dashboard(df):

    st.title("☀️ PV SCADA Control Panel")

    # =========================
    # 🟢 SYSTEM STATUS BAR
    # =========================
    st.markdown("### 🟢 System Status")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("System", "ONLINE")
    col2.metric("Inverter", "OK")
    col3.metric("Sensors", "ACTIVE")
    col4.metric("Mode", "AUTO")

    st.divider()

    # =========================
    # 📊 KEY METRICS
    # =========================
    st.markdown("### ⚡ Live PV Metrics")

    c1, c2, c3 = st.columns(3)

    c1.metric("Power (W)", "1250")
    c2.metric("Voltage (V)", "230")
    c3.metric("Current (A)", "5.4")

    st.divider()

    # =========================
    # 📈 DATA VIEW
    # =========================
    st.markdown("### 📊 Live Data Feed")

    st.dataframe(df.tail(50), use_container_width=True)

    st.divider()

    # =========================
    # 🎛️ CONTROL PANEL
    # =========================
    st.markdown("### 🎛️ Control Panel")

    col1, col2 = st.columns(2)

    if col1.button("🔄 Restart System"):
        st.warning("Restart command triggered")

    if col2.button("⛔ Shutdown System"):
        st.error("Shutdown command triggered")