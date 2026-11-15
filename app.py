"""
ARES (Astronaut Route Exploration & Survival)
NASA Space Apps Challenge 2026 | Team Arceus
Main Streamlit Application Controller & Router
"""

import streamlit as st

# Application Configuration & Shared State
from src.config import REGIONS, MAP_FILES, REGION_POIS, NAVIGATION_PAGES
from src.styles import apply_custom_styles

# View Modules
from src.views.overview import render_overview
from src.views.explorer import render_explorer
from src.views.route_planner import render_route_planner
from src.views.terrain import render_terrain
from src.views.hazards import render_hazards
from src.views.science import render_science


# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="ARES | Mission Control",
    page_icon="🚀",
    layout="wide"
)

# Apply Dark Aerospace Theme
apply_custom_styles()


# ---------------- SESSION STATE MANAGEMENT ----------------
# Maintain consistent global region and navigation state across all views
if "selected_region" not in st.session_state:
    st.session_state["selected_region"] = "Gale Crater"

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Mission Overview"


# ---------------- SIDEBAR NAVIGATION ----------------
with st.sidebar:
    st.markdown(
        """
        <div style="padding:12px 0 25px 0">
            <div style="font-size:27px;font-weight:800;letter-spacing:3px">
                🚀 ARES
            </div>
            <div style="font-size:10px;color:#8290a5;letter-spacing:2px">
                MISSION CONTROL SYSTEM
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### NAVIGATION")

    current_page_idx = (
        NAVIGATION_PAGES.index(st.session_state["current_page"])
        if st.session_state["current_page"] in NAVIGATION_PAGES
        else 0
    )

    page = st.radio(
        "Navigation",
        NAVIGATION_PAGES,
        index=current_page_idx,
        label_visibility="collapsed"
    )
    st.session_state["current_page"] = page

    st.markdown("---")
    st.markdown("### MISSION SETTINGS")

    region_options = list(REGIONS.keys())
    current_reg_idx = (
        region_options.index(st.session_state["selected_region"])
        if st.session_state["selected_region"] in region_options
        else 0
    )

    selected_region = st.selectbox(
        "Exploration region",
        region_options,
        index=current_reg_idx
    )
    st.session_state["selected_region"] = selected_region

    st.markdown("---")

    st.markdown(
        """
        <div style="font-size:11px;color:#8191a8">
        SYSTEM STATUS<br>
        <span style="color:#54d69a">● OPERATIONAL</span><br><br>
        PROJECT<br>
        NASA SPACE APPS 2026<br><br>
        TEAM<br>
        ARCEUS
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------- DATA DISPATCHING ----------------
region_key = st.session_state["selected_region"]
region_data = REGIONS[region_key]
map_file_path = MAP_FILES[region_key]
region_pois = REGION_POIS.get(region_key, [])
active_page = st.session_state["current_page"]


# ---------------- VIEW ROUTER ----------------
if active_page == "Mission Overview":
    render_overview(region_key, region_data, map_file_path)
elif active_page == "Mars Explorer":
    render_explorer(region_key, region_data, map_file_path)
elif active_page == "Route Planner":
    render_route_planner(region_key, region_data, region_pois)
elif active_page == "Terrain Intelligence":
    render_terrain(region_key, region_data)
elif active_page == "Hazard Analysis":
    render_hazards(region_key, region_data)
elif active_page == "Science Discovery":
    render_science(region_key, region_data, region_pois)
else:
    render_overview(region_key, region_data, map_file_path)


# ---------------- FOOTER ----------------
st.markdown(
    """
    <div class="footer">
    ARES | TEAM ARCEUS | NASA SPACE APPS CHALLENGE 2026<br>
    PROTOTYPE — NOT CERTIFIED FOR HUMAN MISSION NAVIGATION
    </div>
    """,
    unsafe_allow_html=True
)
