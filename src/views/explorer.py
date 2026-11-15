"""
ARES Mars Explorer View
Provides interactive MOLA regional cartography with calibrated planetary coordinates,
hardware-accelerated pan and zoom, POI selection, and precision coordinate inputs.
"""

from typing import Dict, Any, List
import streamlit as st

from src.config import REGION_BOUNDS, REGION_POIS
from src.map_engine import (
    load_cached_map_b64,
    build_interactive_mars_map,
    calculate_ground_resolution
)


def render_explorer(region: str, data: Dict[str, Any], image_path: str) -> None:
    """Render the Mars Explorer interactive surface cartography console."""
    st.markdown(
        f"""
        <div class="hero">
            <div class="small-label">SURFACE RECONNAISSANCE / {region.upper()}</div>
            <div class="hero-title">MARS EXPLORER</div>
            <div class="hero-sub">
                Interactive Planetary Cartography & Surface Feature Target Selection
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Scientific Transparency Note
    st.markdown(
        """
        <div class="disclaimer-box">
            <span class="badge-verified">COORDINATE FRAME: PLANETOCENTRIC / EAST LONGITUDE</span>
            <span class="badge-simulated">BASEMAP: MOLA COLORIZED TOPOGRAPHY</span><br>
            <strong>Scientific Context:</strong> This interactive canvas utilizes a calibrated equirectangular projection of NASA's 
            MGS MOLA MEG256 dataset (256 pixels/degree). While latitude scaling is uniform across the map (~231.2 m/pixel), 
            physical ground distance per degree of longitude decreases with the cosine of latitude toward higher elevations.
            This is a visual elevation basemap; precise numerical slope and traversal modeling will use synthetic cost grids.
        </div>
        """,
        unsafe_allow_html=True
    )

    bounds = REGION_BOUNDS[region]
    pois = REGION_POIS.get(region, [])

    # Synchronize Session State for Selected Coordinates per Region
    region_state_key = f"selected_coords_{region}"
    if region_state_key not in st.session_state:
        # Default to first POI (usually landing site) or region center
        default_lat = pois[0]["lat"] if pois else data["lat"]
        default_lon = pois[0]["lon"] if pois else data["lon"]
        default_name = pois[0]["name"] if pois else f"{region} Datum Center"
        st.session_state[region_state_key] = {
            "lat": default_lat,
            "lon": default_lon,
            "name": default_name
        }

    current_target = st.session_state[region_state_key]

    # Zoom State
    zoom_key = f"zoom_level_{region}"
    if zoom_key not in st.session_state:
        st.session_state[zoom_key] = "Full Region (30° × 30°)"

    # Load downsampled map into RAM cache (zero disk writes, instantaneous subsequent access)
    image_b64 = load_cached_map_b64(image_path, max_dim=1536)

    # ---------------- INTERACTIVE CONTROLS BAR ----------------
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1.5, 1.2, 1.3])

    with ctrl_col1:
        poi_options = ["— Select Verified NASA POI —"] + [p["name"] for p in pois]
        poi_choice = st.selectbox(
            "Quick-Select Scientific Site",
            options=poi_options,
            key=f"poi_select_dropdown_{region}"
        )
        if poi_choice != "— Select Verified NASA POI —":
            match_poi = next((p for p in pois if p["name"] == poi_choice), None)
            if match_poi:
                st.session_state[region_state_key] = {
                    "lat": match_poi["lat"],
                    "lon": match_poi["lon"],
                    "name": match_poi["name"]
                }
                current_target = st.session_state[region_state_key]

    with ctrl_col2:
        zoom_choice = st.radio(
            "Camera Framing",
            ["Full Region (30° × 30°)", "Target Focus Window (±3°)"],
            horizontal=True,
            key=f"zoom_radio_{region}"
        )
        st.session_state[zoom_key] = zoom_choice

    with ctrl_col3:
        st.markdown(
            """
            <div style="font-size:11px;color:#8191a8;padding-top:12px">
            <strong>MAP INTERACTION GUIDE:</strong><br>
            • Drag with mouse to <strong>Pan</strong><br>
            • Scroll or use toolbar to <strong>Zoom</strong><br>
            • Click any green <strong>POI marker</strong> to select
            </div>
            """,
            unsafe_allow_html=True
        )

    # Compute zoom bounds if Target Focus is active
    zoom_box = None
    if st.session_state[zoom_key] == "Target Focus Window (±3°)":
        pad = 3.0
        zoom_box = {
            "lat_min": max(bounds["lat_min"], current_target["lat"] - pad),
            "lat_max": min(bounds["lat_max"], current_target["lat"] + pad),
            "lon_min": max(bounds["lon_min"], current_target["lon"] - pad),
            "lon_max": min(bounds["lon_max"], current_target["lon"] + pad)
        }

    # Build the interactive Plotly Figure
    fig = build_interactive_mars_map(
        region_name=region,
        bounds=bounds,
        image_b64=image_b64,
        pois=pois,
        selected_lat=current_target["lat"],
        selected_lon=current_target["lon"],
        selected_name=current_target["name"],
        zoom_bounds=zoom_box
    )

    # ---------------- MAIN DISPLAY: MAP & TELEMETRY ----------------
    map_col, telemetry_col = st.columns([2.2, 1.0])

    with map_col:
        st.markdown(
            f'<div class="section-title">🗺️ INTERACTIVE TOPOGRAPHIC CANVAS — {region.upper()}</div>',
            unsafe_allow_html=True
        )

        # Plotly chart with native point-selection event support
        chart_event = st.plotly_chart(
            fig,
            use_container_width=True,
            on_select="rerun",
            selection_mode=["points"],
            key=f"plotly_mars_canvas_{region}"
        )

        # Handle user selection on the Plotly map (POI click)
        if chart_event and chart_event.get("selection") and chart_event["selection"].get("points"):
            pts = chart_event["selection"]["points"]
            if pts:
                clicked = pts[0]
                clicked_lon = float(clicked.get("x", current_target["lon"]))
                clicked_lat = float(clicked.get("y", current_target["lat"]))
                custom_data = clicked.get("customdata")
                clicked_name = custom_data[1] if (custom_data and len(custom_data) > 1) else "Selected POI"
                
                # Update session state and rerun to reflect selection reticle
                if (clicked_lat != current_target["lat"]) or (clicked_lon != current_target["lon"]):
                    st.session_state[region_state_key] = {
                        "lat": clicked_lat,
                        "lon": clicked_lon,
                        "name": clicked_name
                    }
                    st.rerun()

        st.caption(
            f"Coordinate System: {bounds['lat_convention']} / {bounds['lon_convention']} | "
            f"Projection: {bounds['projection']} | Prime Meridian: {bounds['reference_meridian']}"
        )

    with telemetry_col:
        st.markdown(
            '<div class="section-title">EXPEDITION TARGET TELEMETRY</div>',
            unsafe_allow_html=True
        )

        # Current selection telemetry
        st.markdown(
            f"""
            <div class="panel">
                <div class="small-label">TARGET SITE / FEATURE</div>
                <div class="metric-value" style="font-size:20px;color:#54d69a">{current_target['name']}</div>
                <div style="font-size:14px;color:#ffffff;margin-top:8px">
                    <strong>{current_target['lat']:.4f}° N</strong> &nbsp;|&nbsp; 
                    <strong>{current_target['lon']:.4f}° E</strong>
                </div>
                <div class="metric-caption" style="margin-top:6px">Active expedition waypoint</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Ground resolution calculation at selected latitude
        res = calculate_ground_resolution(current_target["lat"], bounds["pixels_per_degree"])
        st.markdown(
            f"""
            <div class="panel">
                <div class="small-label">LOCAL SPATIAL RESOLUTION</div>
                <div style="font-size:13px;color:#ffffff;margin-top:6px">
                    ● Latitude scale: <strong>{res['meters_per_pixel_lat']} m/px</strong><br>
                    ● Longitude scale: <strong>{res['meters_per_pixel_lon']} m/px</strong><br>
                    ● Cosine scaling factor: <strong>{res['cos_factor']}</strong>
                </div>
                <div class="metric-caption" style="margin-top:6px">
                    Physical longitude spacing compresses by {round((1.0 - res['cos_factor']) * 100, 1)}% 
                    at {current_target['lat']:.1f}° latitude relative to the equator.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Manual Arbitrary Location Selection Controls
        st.markdown(
            """
            <div class="panel">
                <div class="small-label">MANUAL COORDINATE PINNING</div>
                <div class="metric-caption" style="margin-bottom:10px">
                    Input custom landing or exploration coordinates within regional boundary limits:
                </div>
            """,
            unsafe_allow_html=True
        )

        custom_lat = st.number_input(
            "Latitude (°N)",
            min_value=float(bounds["lat_min"]),
            max_value=float(bounds["lat_max"]),
            value=float(current_target["lat"]),
            step=0.05,
            format="%.4f",
            key=f"input_lat_{region}"
        )

        custom_lon = st.number_input(
            "Longitude (°E)",
            min_value=float(bounds["lon_min"]),
            max_value=float(bounds["lon_max"]),
            value=float(current_target["lon"]),
            step=0.05,
            format="%.4f",
            key=f"input_lon_{region}"
        )

        if st.button("📍 Pin Custom Target Location", key=f"btn_pin_{region}"):
            st.session_state[region_state_key] = {
                "lat": custom_lat,
                "lon": custom_lon,
                "name": f"Custom Waypoint ({custom_lat:.2f}°, {custom_lon:.2f}°)"
            }
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
