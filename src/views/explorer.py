"""
ARES Mars Explorer View
Provides high-visibility MOLA surface cartography, regional coordinate readouts,
and planetary context for the selected Mars exploration zone.
"""

from typing import Dict, Any
import streamlit as st


def render_explorer(region: str, data: Dict[str, Any], image_path: str) -> None:
    """Render the Mars Explorer surface cartography console."""
    st.markdown(
        f"""
        <div class="hero">
            <div class="small-label">SURFACE RECONNAISSANCE / {region.upper()}</div>
            <div class="hero-title">MARS EXPLORER</div>
            <div class="hero-sub">
                Regional Cartography & Topographic Visualization &nbsp; | &nbsp; MOLA DATASET
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Scientific Transparency Note
    st.markdown(
        """
        <div class="disclaimer-box">
            <span class="badge-verified">DATA SOURCE: NASA MGS / MOLA</span>
            <span class="badge-simulated">IMAGE TYPE: COLORIZED RENDERING</span><br>
            <strong>Scientific Context:</strong> This imagery is a rendered colorized elevation tile produced from the 
            Mars Orbiter Laser Altimeter (MOLA) experiment aboard NASA's Mars Global Surveyor (MGS) spacecraft.
            It provides qualitative elevation representation (color ramp) rather than raw numerical elevation matrices (DEMs).
        </div>
        """,
        unsafe_allow_html=True
    )

    left_col, right_col = st.columns([2.2, 1])

    with left_col:
        st.markdown(
            f'<div class="section-title">🗺️ MOLA TOPOGRAPHIC TILE — {region.upper()}</div>',
            unsafe_allow_html=True
        )

        st.image(
            image_path,
            use_container_width=True,
            caption=f"MOLA colorized elevation tile for {region} (Coordinates: {data['lat']}°, {data['lon']}°)"
        )

        st.markdown(
            """
            <div class="metric-caption">
            <strong>Color Key:</strong> Warmer hues (white, red, orange) indicate high topographic relief; 
            intermediate hues (yellow, green) correspond to Martian datum plains; 
            cooler hues (cyan, blue, purple) delineate deep depressions and impact basins.
            </div>
            """,
            unsafe_allow_html=True
        )

    with right_col:
        st.markdown(
            '<div class="section-title">REGIONAL TELEMETRY</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="panel">
                <div class="small-label">COORDINATE FRAME</div>
                <div class="metric-value" style="font-size:20px">{data['lat']}° N / {data['lon']}° E</div>
                <div class="metric-caption">Planetocentric coordinates / East longitude standard</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="panel">
                <div class="small-label">GEOLOGICAL PROVINCE</div>
                <div style="font-size:14px;color:#f1f5fb;font-weight:600;margin-top:6px">{data.get('geology', 'Planetary surface unit')}</div>
                <div class="metric-caption" style="margin-top:6px">Diameter / Extent: {data.get('diameter', 'Regional scale')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="panel">
                <div class="small-label">HISTORICAL MISSION CONTEXT</div>
                <div style="font-size:13px;color:#dce5f2;margin-top:6px">{data.get('mission_context', 'Orbital planetary survey')}</div>
                <div class="metric-caption" style="margin-top:6px">{data.get('description', '')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="panel">
                <div class="small-label">ELEVATION OVERVIEW</div>
                <div style="font-size:13px;color:#54d69a;font-weight:700;margin-top:6px">{data.get('elevation_approx', 'Relative to Mars Datum')}</div>
                <div class="metric-caption" style="margin-top:6px">{data.get('elevation_summary', '')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

