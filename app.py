import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Timetable", layout="wide")
st.title("Timetable Dashboard")

DATA = """
date,day,subject,start time,end time,location
2026-01-05,Monday,Math,09:00,10:00,Room 101
2026-01-05,Monday,Physics,10:00,11:00,Room 202
2026-01-06,Tuesday,Chemistry,09:00,10:00,Lab 1
2026-01-06,Tuesday,Biology,11:00,12:00,Room 220
"""

df = pd.read_csv(StringIO(DATA))

subjects = sorted(df["subject"].dropna().unique())
selected = st.multiselect("Select subjects", subjects)

filtered = df[df["subject"].isin(selected)] if selected else df.copy()
filtered = filtered.sort_values(["date", "start time"])

st.subheader("Schedule")
st.dataframe(filtered, use_container_width=True)

csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download timetable (CSV)",
    csv_bytes,
    "timetable.csv",
    "text/csv",
)
