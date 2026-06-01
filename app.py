import streamlit as st
import pandas as pd
from docx import Document
from io import BytesIO
from datetime import datetime

st.title("📊 Data Logging Web App")

file = st.file_uploader("Upload CSV", type=["csv"])

def generate_word_report(df):
    doc = Document()

    # Title
    doc.add_heading("Data Analysis Report", level=1)

    # Metadata
    doc.add_paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc.add_paragraph(f"Rows: {df.shape[0]}")
    doc.add_paragraph(f"Columns: {df.shape[1]}")

    doc.add_heading("Column Overview", level=2)
    doc.add_paragraph(", ".join(df.columns))

    # Numeric summary
    numeric_df = df.select_dtypes(include="number")
    if not numeric_df.empty:
        doc.add_heading("Numeric Summary", level=2)
        doc.add_paragraph(str(numeric_df.describe()))

    # Save to memory
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


if file is not None:
    df = pd.read_csv(file)

    st.subheader("Data Preview")
    st.dataframe(df.head(100))

    st.subheader("Dataset Information")
    st.write(f"Rows: {df.shape[0]}")
    st.write(f"Columns: {df.shape[1]}")

    # 👉 Generate Report Button
    if st.button("📄 Generate Word Report"):
        report = generate_word_report(df)

        st.download_button(
            label="⬇️ Download Report",
            data=report,
            file_name="data_report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )