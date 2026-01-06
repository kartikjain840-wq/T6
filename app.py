import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Timetable Dashboard", layout="wide")
st.title("Timetable Dashboard")

# ---- LOAD CSV FROM SAME FOLDER ----
FILE_PATH = Path(__file__).parent / "timetable.csv"

if not FILE_PATH.exists():
    st.error("timetable.csv not found in the app folder.")
    st.stop()

df = pd.read_csv(FILE_PATH)

# normalize headers
df.columns = [c.strip().lower().replace("_", " ") for c in df.columns]

required = ["date", "day", "subject", "start time", "end time", "location"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error(f"Missing columns in CSV: {', '.join(missing)}")
    st.stop()

# ---- FILTER ----
subjects = sorted(df["subject"].dropna().unique())
selected = st.multiselect("Select subjects", subjects)

filtered = df[df["subject"].isin(selected)] if selected else df.copy()
filtered = filtered.sort_values(["date", "start time"])

# ---- SHOW TABLE ----
st.subheader("Schedule")
st.dataframe(filtered, use_container_width=True)

# ---- DOWNLOAD ----
csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download timetable (CSV)",
    csv_bytes,
    "timetable.csv",
    "text/csv",
)
