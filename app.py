import streamlit as st
import pandas as pd
from docx import Document
from io import BytesIO
from datetime import datetime
import os
import hashlib
import matplotlib.pyplot as plt

# =========================
# 🔐 AUTHENTICATION
# =========================

SALT = "pv_secure_salt_2026"

def hash_password(password: str) -> str:
    return hashlib.sha256((password + SALT).encode()).hexdigest()

PASSWORD_HASH = hash_password("admin123")

def check_password(password: str) -> bool:
    return hash_password(password) == PASSWORD_HASH


if "auth" not in st.session_state:
    st.session_state.auth = False


def login():
    st.title("🔐 Admin Login")

    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        if check_password(password):
            st.session_state.auth = True
            st.success("Access granted")
            st.rerun()
        else:
            st.error("Wrong password")
            st.session_state.auth = False


if not st.session_state.auth:
    login()
    st.stop()

# =========================
# 🚪 LOGOUT
# =========================

st.sidebar.subheader("Session")

if st.sidebar.button("🚪 Logout"):
    st.session_state.auth = False
    st.rerun()

# =========================
# 📊 PLOTTING FUNCTION
# =========================

def fig_to_image_bytes(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)
    return buf
    
def plot_weather_signals(time, temperatures, irradiance, title="Weather Data"):
    fig, ax1 = plt.subplots()

    # multiple temperature lines
    for label, temp_values in temperatures.items():
        ax1.plot(time, temp_values, label=label)

    ax1.set_xlabel("Time")
    ax1.set_ylabel("Temperature (°C)")

    # irradiance axis
    ax2 = ax1.twinx()
    ax2.plot(time, irradiance, color="orange", label="Irradiance")
    ax2.set_ylabel("Irradiance (W/m²)")

    plt.title(title)

    # combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2)

    fig.tight_layout()
    return fig


# =========================
# 📄 WORD REPORT
# =========================

def generate_word_report(df, report_title, observation):

    doc = Document()

    doc.add_heading(report_title, level=1)

    table = doc.add_table(rows=6, cols=2)
    table.style = "Table Grid"

    start_time = f"{df['Date'].iloc[0]} {df['Time'].iloc[0]}" if "Date" in df.columns and "Time" in df.columns else "N/A"
    end_time = f"{df['Date'].iloc[-1]} {df['Time'].iloc[-1]}" if "Date" in df.columns and "Time" in df.columns else "N/A"

    info = [
        ("Generated Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("Total Records", str(df.shape[0])),
        ("Total Columns", str(df.shape[1])),
        ("Start Time", start_time),
        ("End Time", end_time),
        ("Observation Notes", observation)
    ]

    for i, (k, v) in enumerate(info):
        table.cell(i, 0).text = k
        table.cell(i, 1).text = v

    doc.add_heading("Column Overview", level=2)
    doc.add_paragraph(", ".join(df.columns))

    numeric_df = df.select_dtypes(include="number")

    if not numeric_df.empty:
        doc.add_heading("Numeric Summary", level=2)

        summary = doc.add_table(rows=len(numeric_df.columns) + 1, cols=4)
        summary.style = "Table Grid"

        summary.cell(0, 0).text = "Column"
        summary.cell(0, 1).text = "Mean"
        summary.cell(0, 2).text = "Min"
        summary.cell(0, 3).text = "Max"

        for i, col in enumerate(numeric_df.columns, start=1):
            summary.cell(i, 0).text = col
            summary.cell(i, 1).text = f"{numeric_df[col].mean():.2f}"
            summary.cell(i, 2).text = f"{numeric_df[col].min():.2f}"
            summary.cell(i, 3).text = f"{numeric_df[col].max():.2f}"
    doc.add_heading("Weather Graph", level=2)

    img_stream = fig_to_image_bytes(fig)
    doc.add_picture(img_stream)
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer


# =========================
# 📂 MAIN APP
# =========================

st.title("📊 Bifacial PV Data Logging System")

file = st.file_uploader("Upload CSV", type=["csv"])

report_title = st.text_input("Report Title", "Bifacial PV Performance Report")
observation = st.text_area("Observation Notes")


if file is not None:

    df = pd.read_csv(file)

    st.subheader("📊 Data Preview")
    st.dataframe(df.head(100))

    st.subheader("📌 Dataset Info")
    st.write(f"Rows: {df.shape[0]}")
    st.write(f"Columns: {df.shape[1]}")

    # =========================
    # BUILD PLOT INPUTS
    # =========================

    time = df["Time"] if "Time" in df.columns else df.index

    # detect temperature columns automatically
    temperature_cols = [col for col in df.columns if "temp" in col.lower()]

    temperatures = {
        col: df[col].tolist()
        for col in temperature_cols
    }

    irradiance = df["Irradiance"] if "Irradiance" in df.columns else [0] * len(df)

    # =========================
    # PLOT
    # =========================

    fig = plot_weather_signals(time, temperatures, irradiance)

    st.pyplot(fig)
    plt.close(fig)

    # =========================
    # REPORT BUTTON
    # =========================

    if st.button("📄 Generate Word Report"):

        report = generate_word_report(df, report_title, observation)

        st.download_button(
            label="⬇️ Download Report",
            data=report,
            file_name="PV_Report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )


# =========================
# ⚙️ ADMIN PANEL
# =========================

st.divider()
st.subheader("🔴 Admin Controls")

if st.button("🔄 Restart Raspberry Pi"):
    os.system("sudo reboot")

if st.button("⛔ Shutdown Raspberry Pi"):
    os.system("sudo shutdown -h now")
