"""
ARES Science Discovery View
Catalogs verified NASA planetary science exploration sites, sample-return targets,
and astrobiological habitability markers for each Martian region.
"""

from typing import Dict, Any, List
import streamlit as st


def render_science(region: str, data: Dict[str, Any], pois: List[Dict[str, Any]]) -> None:
    """Render the Science Discovery catalog console."""
    st.markdown(
        f"""
        <div class="hero">
            <div class="small-label">PLANETARY GEOLOGY / {region.upper()}</div>
            <div class="hero-title">SCIENCE DISCOVERY</div>
            <div class="hero-sub">
                Planetary Science Exploration Targets & Astrobiological Sample Sites
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Scientific Transparency Note
    st.markdown(
        """
        <div class="disclaimer-box">
            <span class="badge-verified">DATA SOURCE: NASA MARS EXPLORATION PROGRAM</span><br>
            <strong>Verified Science Sites:</strong> The sites below are compiled from published NASA mission archives 
            (Curiosity MSL, Perseverance Mars 2020, and MGS/MRO orbital surveys). Coordinates represent true planetocentric locations.
        </div>
        """,
        unsafe_allow_html=True
    )

    sc_left, sc_right = st.columns([1.8, 1.2])

    with sc_left:
        st.markdown(
            f'<div class="section-title">🔬 SCIENTIFIC TARGETS IN {region.upper()}</div>',
            unsafe_allow_html=True
        )

        for poi in pois:
            st.markdown(
                f"""
                <div class="panel" style="margin-bottom:14px;padding:18px">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <span style="font-weight:700;font-size:16px;color:#ffffff">{poi['name']}</span>
                        <span class="badge-verified">{poi['id']}</span>
                    </div>
                    <div style="font-size:12px;color:#54d69a;font-weight:700;margin-top:4px">
                        Coordinates: {poi['lat']}° N, {poi['lon']}° E &nbsp; | &nbsp; Classification: {poi['type']}
                    </div>
                    <div style="font-size:13px;color:#dce5f2;margin-top:8px;line-height:1.5">
                        {poi['description']}
                    </div>
                    <div class="metric-caption" style="margin-top:8px;border-top:1px solid #1e293b;padding-top:8px">
                        <strong>Exploration Value:</strong> {poi['significance']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with sc_right:
        st.markdown(
            '<div class="section-title">REGIONAL OBJECTIVES</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="panel">
                <div class="small-label">PRIMARY SCIENTIFIC GOAL</div>
                <div style="font-size:15px;color:#ffffff;font-weight:700;margin-top:6px">{data.get('objective', '')}</div>
                <div class="metric-caption" style="margin-top:8px">{data.get('description', '')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="panel">
                <div class="small-label">HISTORICAL MISSION REFERENCE</div>
                <div style="font-size:14px;color:#54d69a;font-weight:700;margin-top:6px">{data.get('mission_context', '')}</div>
                <div class="metric-caption" style="margin-top:8px">
                NASA surface rovers utilize multispectral imaging, alpha-particle X-ray spectrometers (APXS),
                and robotic rock drills at these exact geological formations.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="panel">
                <div class="small-label">EXPEDITION SAMPLE CACHING</div>
                <div style="font-size:13px;color:#dce5f2;margin-top:8px">
                ● <strong>Igneous Core Samples:</strong> Provide radiometric age dating.<br><br>
                ● <strong>Fine-grained Mudstones:</strong> Highest potential to preserve organic molecular biosignatures.<br><br>
                ● <strong>Sulfates & Clays:</strong> Reveal timing of ancient surface water desiccation.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

