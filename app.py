
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="ARES | Mars Explorer",
    page_icon="🚀",
    layout="wide"
)

# Application title
st.title("🚀 ARES")
st.subheader("Astronaut Route Exploration & Survival")

st.markdown("---")

# Introduction
st.header("Welcome to Mars")

st.write(
    """
    ARES is an interactive Mars exploration and
    mission-planning platform developed by Team Arceus
    for NASA Space Apps Challenge 2026.

    Our goal is to help future astronauts explore
    the Martian surface using terrain intelligence,
    hazard analysis and route planning.
    """
)

# Sidebar
st.sidebar.title("Mission Control")

region = st.sidebar.selectbox(
    "Select Mars Region",
    ["Gale Crater", "Jezero Crater", "Olympus Mons"]
)

st.sidebar.write("Selected Region:", region)

# Main dashboard
col1, col2 = st.columns(2)

with col1:
    st.subheader("🗺️ Mars Map")
    st.info("Mars map visualization coming soon.")

with col2:
    st.subheader("🧭 Mission Planner")
    st.info("Route planning system coming soon.")

st.markdown("---")
st.caption("ARES | Team Arceus | NASA Space Apps Challenge 2026")

