"""
ARES Route Planner View
Provides the mission-planning console foundation: waypoint selection,
rover traversal profile configuration, and route telemetry staging.
(Algorithmic A* pathfinding and survival modeling are scheduled for Phase 4 & 5).
"""

from typing import Dict, Any, List
import streamlit as st


def render_route_planner(region: str, data: Dict[str, Any], pois: List[Dict[str, Any]]) -> None:
    """Render the Route Planner expedition navigation console."""
    st.markdown(
        f"""
        <div class="hero">
            <div class="small-label">EXPEDITION NAVIGATION / {region.upper()}</div>
            <div class="hero-title">ROUTE PLANNER</div>
            <div class="hero-sub">
                Astronaut Surface Traversal Planning & Mission Waypoint Console
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Scientific Transparency Note
    st.markdown(
        """
        <div class="disclaimer-box">
            <span class="badge-simulated">EXPEDITION SIMULATION FOUNDATION</span><br>
            <strong>Engineering Notice:</strong> This console establishes the mission parameters and waypoint selections.
            Algorithmic pathfinding (A* cost-grid routing) and dynamic life-support telemetry will be integrated in Phase 4.
        </div>
        """,
        unsafe_allow_html=True
    )

    col_config, col_preview = st.columns([1.2, 1.8])

    with col_config:
        st.markdown(
            '<div class="section-title">EXPEDITION CONFIGURATION</div>',
            unsafe_allow_html=True
        )

        poi_names = [poi["name"] for poi in pois] if pois else ["Default Landing Site", "Primary Science Zone"]

        start_poi = st.selectbox(
            "Departure Point (Start Waypoint)",
            options=poi_names,
            index=0,
            key="route_start_poi"
        )

        dest_options = [p for p in poi_names if p != start_poi] or poi_names
        dest_poi = st.selectbox(
            "Target Destination (End Waypoint)",
            options=dest_options,
            index=0 if len(dest_options) == 1 else 1 if len(dest_options) > 1 else 0,
            key="route_dest_poi"
        )

        rover_profile = st.selectbox(
            "Surface Vehicle Configuration",
            [
                "Pressurized Crew Rover (PCR-1) — Nominal speed 12 km/h",
                "Lightweight Unpressurized Scout (LUV) — Nominal speed 18 km/h",
                "Heavy Cargo & Habitat Hauler (HCH) — Nominal speed 6 km/h"
            ],
            key="rover_profile_select"
        )

        traversal_mode = st.radio(
            "Route Optimization Priority",
            [
                "Balanced (Optimal Energy & Moderate Slope)",
                "Minimum Slope (Conservative Safety First)",
                "Direct Traversal (Distance Minimization)"
            ],
            key="traversal_priority"
        )

    with col_preview:
        st.markdown(
            '<div class="section-title">MISSION ROUTE TELEMETRY PREVIEW</div>',
            unsafe_allow_html=True
        )

        # Telemetry cards for route parameters
        t1, t2 = st.columns(2)
        with t1:
            st.markdown(
                f"""
                <div class="panel">
                    <div class="small-label">EXPEDITION STATUS</div>
                    <div class="metric-value" style="font-size:20px;color:#e3ae69">PLANNING</div>
                    <div class="metric-caption">Waypoints configured; path calculation engine staged</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(
                f"""
                <div class="panel">
                    <div class="small-label">START WAYPOINT</div>
                    <div style="font-size:15px;font-weight:700;color:#ffffff;margin-top:8px">{start_poi}</div>
                    <div class="metric-caption">Region: {region}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with t2:
            st.markdown(
                """
                <div class="panel">
                    <div class="small-label">PATHFINDING ENGINE</div>
                    <div class="metric-value" style="font-size:20px;color:#8290a5">PHASE 4</div>
                    <div class="metric-caption">A* Graph Cost Matrix scheduled for next milestone</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(
                f"""
                <div class="panel">
                    <div class="small-label">DESTINATION TARGET</div>
                    <div style="font-size:15px;font-weight:700;color:#ffffff;margin-top:8px">{dest_poi}</div>
                    <div class="metric-caption">Priority: {traversal_mode.split('(')[0]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            """
            <div class="panel">
                <div class="small-label">EXPEDITION ARCHITECTURE SUMMARY</div>
                <div class="metric-caption" style="margin-top:8px;font-size:13px;color:#dce5f2">
                In Phase 4, the route planning module will connect these waypoints via a terrain-aware graph.
                The navigation solver will evaluate surface cost factors including elevation variance, slope penalties,
                and known rock fields to plot safe traversal corridors for astronaut crews.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

