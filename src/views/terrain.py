"""
ARES Terrain Intelligence View
Provides topographic interpretation, elevation classification,
and planetary surface characterization guides for Mars exploration.
"""

from typing import Dict, Any
import streamlit as st


def render_terrain(region: str, data: Dict[str, Any]) -> None:
    """Render the Terrain Intelligence console."""
    st.markdown(
        f"""
        <div class="hero">
            <div class="small-label">SURFACE TOPOGRAPHY / {region.upper()}</div>
            <div class="hero-title">TERRAIN INTELLIGENCE</div>
            <div class="hero-sub">
                Topographic Elevation Analysis & Surface Classification Guide
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Scientific Transparency Note
    st.markdown(
        """
        <div class="disclaimer-box">
            <span class="badge-verified">SCIENTIFIC FOUNDATION: MARS DATUM STANDARD</span>
            <span class="badge-simulated">MODEL LIMITATION: COLOR PALETTE DERIVATION</span><br>
            <strong>Scientific Principle:</strong> Mars has no sea level. Topographic elevations are officially defined relative 
            to an equipotential surface (the Martian 'areoid' or datum) where average atmospheric pressure is 610 Pascals (the triple point of water).
            Our MOLA color tiles map relative heights qualitatively. High-precision numerical slope calculations require calibrated 32-bit DEM matrices.
        </div>
        """,
        unsafe_allow_html=True
    )

    t_col1, t_col2 = st.columns(2)

    with t_col1:
        st.markdown(
            '<div class="section-title">📊 MOLA ELEVATION PALETTE INTERPRETATION</div>',
            unsafe_allow_html=True
        )

        elevation_bands = [
            ("VIOLET / DARK BLUE", "Deep Basins & Depressions", "< -4,000 m", "Impact basin floors, deep crater interiors (e.g., Hellas basin, Gale crater floor)"),
            ("CYAN / LIGHT BLUE", "Lowland Plains", "-4,000 to -1,500 m", "Vast northern plains (Vastitas Borealis), ancient depositional surfaces"),
            ("GREEN / YELLOW", "Martian Datum Plains", "-1,500 to +2,000 m", "Equatorial terrain, delta surfaces, average planetary datum"),
            ("ORANGE / RED", "Highlands & Plateaus", "+2,000 to +8,000 m", "Southern cratered highlands, volcanic province aprons"),
            ("WHITE / LIGHT PINK", "Volcanic Summits", "+8,000 to +21,000 m+", "Massive volcanic peaks of Tharsis (Olympus, Ascraeus, Pavonis, Arsia Mons)")
        ]

        for color, name, height, example in elevation_bands:
            st.markdown(
                f"""
                <div class="panel" style="min-height:90px;margin-bottom:10px;padding:14px">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <span style="font-weight:700;font-size:13px;color:#f1f5fb">{color}</span>
                        <span style="font-size:12px;color:#54d69a;font-weight:700">{height}</span>
                    </div>
                    <div style="font-size:13px;color:#e3ae69;margin-top:2px">{name}</div>
                    <div class="metric-caption" style="margin-top:4px">{example}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with t_col2:
        st.markdown(
            f'<div class="section-title">🪐 {region.upper()} TOPOGRAPHIC PROFILE</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="panel">
                <div class="small-label">ELEVATION RANGE</div>
                <div class="metric-value" style="font-size:22px">{data.get('elevation_approx', 'Relative to datum')}</div>
                <div class="metric-caption">{data.get('elevation_summary', '')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="panel">
                <div class="small-label">SURFACE MORPHOLOGY</div>
                <div style="font-size:14px;color:#ffffff;font-weight:600;margin-top:8px">{data.get('geology', '')}</div>
                <div class="metric-caption" style="margin-top:8px">
                NASA planetary surveys indicate varied morphological units in this zone, ranging from smooth bedrock pavements 
                to rugged crater ejecta blankets and eolian sand fields.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="panel">
                <div class="small-label">SURFACE TRAVERSAL CLASSIFICATION</div>
                <div style="font-size:13px;color:#dce5f2;margin-top:8px">
                ● <strong>Pavement Bedrock:</strong> High mechanical traction, minimal wheel sinkage.<br><br>
                ● <strong>Delta / Sedimentary Layers:</strong> Moderate slope challenges, bench scarps.<br><br>
                ● <strong>Active Ripple Fields:</strong> Unconsolidated fine grains; high risk of rover wheel slip.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

