import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import tempfile

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Timetable Dashboard", layout="wide")
st.title("📅 Timetable Dashboard")
st.caption("Week-wise and term-wide schedule")

# ---------------- LOAD DATA ----------------
FILE_PATH = Path(__file__).parent / "timetable.csv"

if not FILE_PATH.exists():
    st.error("❌ timetable.csv not found.")
    st.stop()

df = pd.read_csv(FILE_PATH)
df.columns = [c.strip().lower().replace("_", " ") for c in df.columns]

# ---------------- PREPROCESS ----------------
df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
df = df.dropna(subset=["date"])

df["weekday"] = df["date"].dt.day_name()

df["start dt"] = pd.to_datetime(
    df["date"].dt.strftime("%Y-%m-%d") + " " + df["start time"],
    errors="coerce"
)

# ---------------- FILTER ----------------
subjects = sorted(df["subject"].dropna().unique())
selected_subjects = st.multiselect("🎓 Select subjects", subjects)

filtered = df[df["subject"].isin(selected_subjects)] if selected_subjects else df.copy()

# ---------------- TERM-WIDE VIEW ----------------
st.divider()
st.subheader("📆 Term-wide Calendar View")

term_df = (
    filtered
    .sort_values(["date", "start dt"])
    [["date", "weekday", "subject", "start time", "end time", "location"]]
)

term_df["date"] = term_df["date"].dt.strftime("%d %b %Y")

st.dataframe(term_df, use_container_width=True)

# ---------------- PDF GENERATION ----------------
def generate_pdf(dataframe):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(tmp.name, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Term-wise Class Schedule", styles["Title"]))
    elements.append(Spacer(1, 12))

    table_data = [
        ["Date", "Day", "Subject", "Time", "Location"]
    ]

    for _, row in dataframe.iterrows():
        table_data.append([
            row["date"],
            row["weekday"],
            row["subject"],
            f"{row['start time']} – {row['end time']}",
            row["location"],
        ])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)
    doc.build(elements)

    return tmp.name

# ---------------- DOWNLOAD PDF ----------------
st.divider()
if st.button("⬇️ Download entire term calendar (PDF)"):
    pdf_path = generate_pdf(term_df)
    with open(pdf_path, "rb") as f:
        st.download_button(
            label="📄 Click to download PDF",
            data=f,
            file_name="Term_Calendar.pdf",
            mime="application/pdf",
        )
