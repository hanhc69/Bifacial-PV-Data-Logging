import streamlit as st
import pandas as pd
from docx import Document
from io import BytesIO
from datetime import datetime
import os
import hashlib

# =========================
# 🔐 AUTHENTICATION
# =========================

PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()

def check_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest() == PASSWORD_HASH


if "auth" not in st.session_state:
    st.session_state.auth = False


def login():
    st.title("🔐 Admin Login")

    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        if password == "admin":
            st.session_state.auth = True
            st.success("Access granted")
        else:
            st.error("Wrong password")

    st.stop()


if not st.session_state.auth:
    login()

# =========================
# 📊 MAIN APP
# =========================

st.title("📊 Bifacial PV Data Logging System")

file = st.file_uploader("Upload CSV", type=["csv"])

# =========================
# 📄 REPORT INPUTS
# =========================

report_title = st.text_input(
    "Report Title",
    "Bifacial PV Performance Report"
)

observation = st.text_area("Observation Notes")

# =========================
# 📄 WORD REPORT FUNCTION
# =========================

def generate_word_report(df, report_title, observation):

    doc = Document()

    # Title
    doc.add_heading(report_title, level=1)

    # Info table
    table = doc.add_table(rows=6, cols=2)
    table.style = "Table Grid"

    start_time = f"{df['Date'].iloc[0]} {df['Time'].iloc[0]}" if "Date" in df.columns else "N/A"
    end_time = f"{df['Date'].iloc[-1]} {df['Time'].iloc[-1]}" if "Date" in df.columns else "N/A"

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

    # Column overview
    doc.add_heading("Column Overview", level=2)
    doc.add_paragraph(", ".join(df.columns))

    # Numeric summary
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

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer


# =========================
# 📂 DATA SECTION
# =========================

if file is not None:

    df = pd.read_csv(file)

    st.subheader("📊 Data Preview")
    st.dataframe(df.head(100))

    st.subheader("📌 Dataset Info")
    st.write(f"Rows: {df.shape[0]}")
    st.write(f"Columns: {df.shape[1]}")

    # =========================
    # 📄 REPORT BUTTON
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
