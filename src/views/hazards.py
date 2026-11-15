"""
ARES Hazard Analysis View
Provides environmental hazard monitoring, planetary risk classifications,
and vehicle safety criteria grounded in NASA engineering precedents.
"""

from typing import Dict, Any
import streamlit as st


def render_hazards(region: str, data: Dict[str, Any]) -> None:
    """Render the Hazard Analysis risk assessment console."""
    st.markdown(
        f"""
        <div class="hero">
            <div class="small-label">PLANETARY RISK ASSESSMENT / {region.upper()}</div>
            <div class="hero-title">HAZARD ANALYSIS</div>
            <div class="hero-sub">
                Environmental Hazard Monitoring & Rover Traversal Constraints
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Scientific Transparency Note
    st.markdown(
        """
        <div class="disclaimer-box">
            <span class="badge-verified">VERIFIED SCIENTIFIC FACT: ROVER KINEMATICS & SOIL MECHANICS</span>
            <span class="badge-simulated">ILLUSTRATIVE MODELING: COST SCALING</span><br>
            <strong>Engineering Fact:</strong> There is <em>no single universal slope safety limit</em> on Mars. 
            Safe traversal angles depend on chassis suspension (e.g., 6-wheel rocker-bogie), wheel diameter, 
            and soil shear strength. While NASA rovers possess static stability beyond 40° on firm bedrock, 
            mission flight rules typically restrict autonomous driving to slopes below 15°–20° to prevent catastrophic wheel slip.
        </div>
        """,
        unsafe_allow_html=True
    )

    hz1, hz2 = st.columns(2)

    with hz1:
        st.markdown(
            '<div class="section-title">⚠️ PLANETARY HAZARD PROFILES</div>',
            unsafe_allow_html=True
        )

        hazards = [
            (
                "SLOPE INCLINE & WHEEL SLIP",
                "High Risk on Unconsolidated Sand",
                "Kinematic Stability",
                "On bedrock, rovers can ascend moderate inclines safely. However, on loose regolith (sand dunes), wheel slip exceeds 80% on slopes as low as 12°–15°, creating severe motor stall and immobilization risks."
            ),
            (
                "EOLIAN SAND TRAPS & MEGARIPPLES",
                "Critical Immobilization Hazard",
                "Soil Mechanics",
                "Fine-grained basaltic dust and sulfate-rich sands (such as the deposit that permanently entrapped NASA's Spirit rover at 'Troy' in 2009) present negligible bearing capacity, risking wheel sinkage."
            ),
            (
                "DUST STORMS & OPTICAL OPACITY (TAU)",
                "Solar & Sensor Degradation",
                "Atmospheric Hazard",
                "Martian dust storms (local, regional, or global) drastically elevate atmospheric optical depth (tau). This curtails solar array power generation and severely degrades autonomous stereo hazard cameras."
            ),
            (
                "THERMAL CYCLING & SOLAR RADIATION",
                "Subsystem Stress",
                "Environmental Factor",
                "Diurnal temperature swings from -90°C at night to +10°C at midday induce thermal fatigue on welds and electronics. Lack of an intrinsic global magnetic field exposes crews and electronics to cosmic rays."
            )
        ]

        for title, alert_level, category, description in hazards:
            st.markdown(
                f"""
                <div class="panel" style="min-height:105px;margin-bottom:12px">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <span style="font-weight:700;font-size:14px;color:#f1f5fb">{title}</span>
                        <span style="font-size:11px;color:#e3ae69;font-weight:700">{category}</span>
                    </div>
                    <div style="font-size:12px;color:#e16d49;font-weight:600;margin-top:2px">{alert_level}</div>
                    <div class="metric-caption" style="margin-top:6px">{description}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with hz2:
        st.markdown(
            f'<div class="section-title">🛡️ {region.upper()} HAZARD MITIGATION MATRIX</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="panel">
                <div class="small-label">ZONE ASSESSMENT</div>
                <div class="metric-value" style="font-size:22px;color:#54d69a">MONITORED</div>
                <div class="metric-caption">Region: {region} ({data['lat']}° N, {data['lon']}° E)</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="panel">
                <div class="small-label">SAFETY CORRIDOR PROTOCOLS</div>
                <div style="font-size:13px;color:#dce5f2;margin-top:8px;line-height:1.6">
                ● <strong>Autonomous Drive Limit:</strong> Flight rules cap automatic driving when slopes exceed 15°.<br>
                ● <strong>Visual Odometry:</strong> Rover compares successive camera frames to detect wheel slippage before getting stuck.<br>
                ● <strong>Rip-Off Avoidance:</strong> Sharp, wind-sculpted rocks (ventifacts) are actively avoided to preserve aluminum wheel treads.<br>
                ● <strong>Solar Reserve Threshold:</strong> Minimum 30% battery reserve required before entering shaded crater wall areas.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="panel">
                <div class="small-label">PHASE 4 ROUTE INTEGRATION</div>
                <div class="metric-caption" style="margin-top:6px;font-size:12px;color:#a9b5c6">
                In Phase 4, these engineering parameters will directly inform our pathfinding cost function:
                slopes, identified dune ripples, and obstacle clusters will receive high traversal cost penalties,
                automatically guiding routes through gentler bedrock corridors.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

