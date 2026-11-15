"""
ARES Mission Overview View
Preserves the primary mission-control overview dashboard, telemetry readouts,
and MOLA surface visualization.
"""

from typing import Dict, Any
import streamlit as st


def render_overview(region: str, data: Dict[str, Any], image_path: str) -> None:
    """Render the primary Mission Overview dashboard."""
    # ---------------- HEADER ----------------
    st.markdown(
        """
        <div class="hero">
            <div class="small-label">PLANETARY EXPLORATION PLATFORM / SOL 001</div>
            <div class="hero-title">ARES MISSION CONTROL</div>
            <div class="hero-sub">
                Astronaut Route Exploration & Survival &nbsp; | &nbsp; TEAM ARCEUS
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="small-label">CURRENT EXPLORATION ZONE / {region.upper()}</div>',
        unsafe_allow_html=True
    )
    st.write("")

    # ---------------- TELEMETRY ----------------
    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        (c1, "MISSION STATUS", "ACTIVE", "Prototype environment"),
        (c2, "TARGET REGION", region, "Selected exploration zone"),
        (c3, "LATITUDE", f'{data["lat"]}°', "Planetocentric coordinate"),
        (c4, "LONGITUDE", f'{data["lon"]}°', "East longitude")
    ]

    for col, label, value, caption in metrics:
        with col:
            st.markdown(
                f"""
                <div class="panel">
                    <div class="small-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-caption">{caption}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # ---------------- MAIN DASHBOARD ----------------
    left, right = st.columns([2.1, 1])

    with left:
        st.markdown(
            '<div class="section-title">🪐 MARS SURFACE INTELLIGENCE</div>',
            unsafe_allow_html=True
        )

        st.caption(f"MOLA COLORIZED ELEVATION DATA | {region.upper()}")

        # Load actual MOLA image
        st.image(
            image_path,
            use_container_width=True,
            caption=f"MOLA elevation tile — {region}"
        )

        st.markdown(
            '<div class="metric-caption">'
            'Source: Arizona State University MOLA dataset. '
            'Rendered elevation imagery; not a live satellite feed.'
            '</div>',
            unsafe_allow_html=True
        )

    with right:
        st.markdown(
            '<div class="section-title">MISSION INTELLIGENCE</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="panel">
                <div class="small-label">EXPLORATION TARGET</div>
                <div class="metric-value" style="font-size:22px">{region}</div>
                <br>
                <div class="metric-caption">{data["description"]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="panel">
                <div class="small-label">SCIENTIFIC OBJECTIVE</div>
                <br>
                <div style="font-size:14px;color:#dce5f2">{data.get("objective", "Geological investigation and site exploration")}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="panel">
                <div class="small-label">SYSTEM MODULES</div>
                <br>
                <span class="status">● Dashboard operational</span><br><br>
                <span class="status">● Mars Explorer ready</span><br><br>
                <span style="color:#e3ae69">● Terrain module (Phase 2 navigation active)</span><br><br>
                <span style="color:#e3ae69">● Hazard module (Phase 2 navigation active)</span><br><br>
                <span style="color:#e3ae69">● Route planner (Phase 2 navigation active)</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------------- LOWER PANELS ----------------
    st.markdown("---")
    st.markdown("## EXPLORATION SYSTEMS")

    a, b, c = st.columns(3)

    with a:
        st.markdown(
            """
            <div class="panel">
                <div style="font-size:25px">🧭</div>
                <div class="section-title">ROUTE PLANNER</div>
                <div class="metric-caption">
                Plan terrain-aware astronaut exploration routes across Martian terrain.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with b:
        st.markdown(
            """
            <div class="panel">
                <div style="font-size:25px">⛰️</div>
                <div class="section-title">TERRAIN INTELLIGENCE</div>
                <div class="metric-caption">
                Analyse elevation gradients, slope risks, and surface roughness.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c:
        st.markdown(
            """
            <div class="panel">
                <div style="font-size:25px">🔬</div>
                <div class="section-title">SCIENCE DISCOVERY</div>
                <div class="metric-caption">
                Identify scientifically interesting exploration sites and sample targets.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

