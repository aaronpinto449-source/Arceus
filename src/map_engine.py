"""
ARES Mars Interactive Map Engine
Provides high-performance in-memory MOLA cartography rendering,
equirectangular coordinate transforms, and interactive Plotly canvas generation.
"""

import io
import math
import base64
from typing import Dict, Any, List, Optional
from PIL import Image
import streamlit as st
import plotly.graph_objects as go

from src.config import MARS_EQUATORIAL_RADIUS_KM


@st.cache_data(show_spinner=False)
def load_cached_map_b64(image_path: str, max_dim: int = 1536) -> str:
    """
    Load a raw MOLA PNG tile, downsample in memory for web performance,
    and return an in-memory base64 JPEG data URI.

    Performance & Safety Guarantee:
    - Original raw files in data/raw/ are read in RAM and NEVER modified or overwritten.
    - Zero image files are written to disk.
    - Result is cached in RAM via @st.cache_data for instant subsequent renders.
    """
    raw_img = Image.open(image_path)
    
    # Maintain aspect ratio (tiles are 1:1 square)
    resized_img = raw_img.resize((max_dim, max_dim), Image.Resampling.LANCZOS)
    
    buffer = io.BytesIO()
    # JPEG quality 85 delivers high visual clarity with ~0.8 MB payload (vs 45 MB uncompressed)
    resized_img.save(buffer, format="JPEG", quality=85)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def calculate_ground_resolution(lat_deg: float, pixels_per_degree: float = 256.0) -> Dict[str, float]:
    """
    Calculate local ground spatial resolution in metres per pixel at a given latitude.

    Scientific Principle:
    In equirectangular projection, latitude degrees are uniform, but physical metres per
    degree of longitude shrink as R * cos(lat) moving toward the poles.
    """
    lat_rad = math.radians(lat_deg)
    
    # 1 degree of latitude distance on Mars
    meters_per_deg_lat = (2.0 * math.pi * MARS_EQUATORIAL_RADIUS_KM * 1000.0) / 360.0
    meters_per_pixel_lat = meters_per_deg_lat / pixels_per_degree
    
    # 1 degree of longitude distance at latitude phi
    meters_per_pixel_lon = meters_per_pixel_lat * math.cos(lat_rad)
    
    return {
        "lat_deg": lat_deg,
        "meters_per_pixel_lat": round(meters_per_pixel_lat, 1),
        "meters_per_pixel_lon": round(meters_per_pixel_lon, 1),
        "cos_factor": round(math.cos(lat_rad), 4)
    }


def build_interactive_mars_map(
    region_name: str,
    bounds: Dict[str, Any],
    image_b64: str,
    pois: List[Dict[str, Any]],
    selected_lat: Optional[float] = None,
    selected_lon: Optional[float] = None,
    selected_name: Optional[str] = None,
    zoom_bounds: Optional[Dict[str, float]] = None
) -> go.Figure:
    """
    Construct an interactive Plotly figure calibrated to Martian coordinates.
    """
    fig = go.Figure()

    # 1. Background MOLA Topographic Cartography Layer
    fig.add_layout_image(
        dict(
            source=image_b64,
            xref="x",
            yref="y",
            x=bounds["lon_min"],
            y=bounds["lat_max"],
            sizex=bounds["lon_max"] - bounds["lon_min"],
            sizey=bounds["lat_max"] - bounds["lat_min"],
            xanchor="left",
            yanchor="top",
            sizing="stretch",
            layer="below"
        )
    )

    # 2. Verified NASA Scientific Points of Interest (POIs) Layer
    if pois:
        poi_x = [p["lon"] for p in pois]
        poi_y = [p["lat"] for p in pois]
        poi_names = [p["name"] for p in pois]
        poi_customdata = [
            [p["id"], p["name"], p["type"], p.get("source_reference", "NASA Planetary Archive")]
            for p in pois
        ]

        fig.add_trace(
            go.Scatter(
                x=poi_x,
                y=poi_y,
                mode="markers+text",
                text=poi_names,
                textposition="top center",
                textfont=dict(color="#ffffff", size=11, family="Inter, sans-serif"),
                marker=dict(
                    size=13,
                    color="#54d69a",
                    symbol="circle",
                    line=dict(color="#ffffff", width=2)
                ),
                customdata=poi_customdata,
                hovertemplate=(
                    "<b>%{customdata[1]}</b><br>"
                    "ID: %{customdata[0]}<br>"
                    "Type: %{customdata[2]}<br>"
                    "Latitude: %{y:.4f}° N<br>"
                    "Longitude: %{x:.4f}° E<br>"
                    "Source: %{customdata[3]}<extra></extra>"
                ),
                name="Scientific POIs"
            )
        )

    # 3. Selected Target Reticle / Expedition Location
    if selected_lat is not None and selected_lon is not None:
        target_label = selected_name or "Target Coordinates"
        fig.add_trace(
            go.Scatter(
                x=[selected_lon],
                y=[selected_lat],
                mode="markers",
                marker=dict(
                    size=18,
                    color="#e16d49",
                    symbol="cross",
                    line=dict(color="#ffffff", width=2.5)
                ),
                hovertemplate=(
                    f"<b>{target_label}</b><br>"
                    "Latitude: %{y:.4f}° N<br>"
                    "Longitude: %{x:.4f}° E<extra></extra>"
                ),
                name="Selected Target"
            )
        )

    # 4. Axes & Camera Bounds Calibration
    x_range = (
        [zoom_bounds["lon_min"], zoom_bounds["lon_max"]]
        if zoom_bounds
        else [bounds["lon_min"], bounds["lon_max"]]
    )
    y_range = (
        [zoom_bounds["lat_min"], zoom_bounds["lat_max"]]
        if zoom_bounds
        else [bounds["lat_min"], bounds["lat_max"]]
    )

    fig.update_xaxes(
        title=dict(text="East Longitude (°E)", font=dict(color="#a9b5c6", size=12)),
        range=x_range,
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.08)",
        gridwidth=1,
        zeroline=False,
        tickfont=dict(color="#a9b5c6", size=10),
        ticksuffix="° E",
        constrain="domain"
    )

    fig.update_yaxes(
        title=dict(text="Planetocentric Latitude (°N)", font=dict(color="#a9b5c6", size=12)),
        range=y_range,
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.08)",
        gridwidth=1,
        zeroline=False,
        tickfont=dict(color="#a9b5c6", size=10),
        ticksuffix="° N",
        scaleanchor="x",
        scaleratio=1.0,
        constrain="domain"
    )

    # 5. Aerospace Mission-Control Theming & Toolbar Controls
    fig.update_layout(
        plot_bgcolor="#090d14",
        paper_bgcolor="#090d14",
        font=dict(color="#dce5f2", family="Inter, sans-serif"),
        margin=dict(l=60, r=20, t=35, b=60),
        height=620,
        dragmode="pan",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#dce5f2"),
            bgcolor="rgba(13, 19, 30, 0.8)",
            bordercolor="#273447",
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor="#111a27",
            bordercolor="#344357",
            font=dict(color="#ffffff", size=12, family="Inter")
        )
    )

    return fig

