import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Timetable Dashboard",
    layout="wide",
)

st.title("📅 Timetable Dashboard")
st.caption("Week-wise schedule starting from today")

# ---------------- LOAD DATA ----------------
FILE_PATH = Path(__file__).parent / "timetable.csv"

if not FILE_PATH.exists():
    st.error("❌ timetable.csv not found in the app folder.")
    st.stop()

df = pd.read_csv(FILE_PATH)

# normalize headers
df.columns = [c.strip().lower().replace("_", " ") for c in df.columns]

required = ["date", "day", "subject", "start time", "end time", "location"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error(f"❌ Missing columns in CSV: {', '.join(missing)}")
    st.stop()

# ---------------- PREPROCESS ----------------
df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
df = df.dropna(subset=["date"])

df["weekday"] = df["date"].dt.day_name()
df["start time"] = df["start time"].astype(str)
df["end time"] = df["end time"].astype(str)

# ---------------- FILTERS ----------------
subjects = sorted(df["subject"].dropna().unique())
selected_subjects = st.multiselect(
    "🎓 Select subjects",
    subjects,
)

filtered = df[df["subject"].isin(selected_subjects)] if selected_subjects else df.copy()

# ---------------- WEEK LOGIC ----------------
today = pd.to_datetime(datetime.today().date())
today_name = today.day_name()

current_week_start = today - pd.to_timedelta(today.weekday(), unit="D")

week_options = {}
for i in range(0, 6):
    start = current_week_start + timedelta(weeks=i)
    end = start + timedelta(days=6)
    label = f"Week {i+1}: {start.strftime('%d %b')} – {end.strftime('%d %b')}"
    week_options[label] = (start, end)

selected_week = st.selectbox("🗓️ Select week", list(week_options.keys()))
week_start, week_end = week_options[selected_week]

week_df = filtered[
    (filtered["date"] >= week_start) &
    (filtered["date"] <= week_end)
].sort_values(["date", "start time"])

# ---------------- DISPLAY ----------------
st.divider()
st.subheader(f"📌 Schedule for {week_start.strftime('%d %b')} – {week_end.strftime('%d %b')}")

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
cols = st.columns(7)

for i, day in enumerate(days):
    with cols[i]:

        is_today = (day == today_name and week_start <= today <= week_end)

        header_style = f"""
        <div style="
            padding:8px;
            border-radius:10px;
            text-align:center;
            font-weight:700;
            background-color:{'#ffe9a8' if is_today else '#1f2937'};
            color:{'#000000' if is_today else '#ffffff'};
            margin-bottom:10px;
        ">
            {day}
            {'<br><small>Today</small>' if is_today else ''}
        </div>
        """

        st.markdown(header_style, unsafe_allow_html=True)

        day_df = week_df[week_df["weekday"] == day]

        if day_df.empty:
            st.caption("No classes")
        else:
            for _, row in day_df.iterrows():
                st.markdown(
                    f"""
                    <div style="
                        padding:10px;
                        margin-bottom:10px;
                        border-radius:10px;
                        background-color:{'#fff4cc' if is_today else '#f5f7fa'};
                        border-left:5px solid {'#f59e0b' if is_today else '#4f8bf9'};
                        color:#000000;
                    ">
                    <b>{row['subject']}</b><br>
                    🕒 {row['start time']} – {row['end time']}<br>
                    📍 {row['location']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# ---------------- DOWNLOAD ----------------
st.divider()
csv_bytes = week_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download this week's timetable (CSV)",
    csv_bytes,
    f"timetable_{week_start.strftime('%d_%b')}.csv",
    "text/csv",
)
