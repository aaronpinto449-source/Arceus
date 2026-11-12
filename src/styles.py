"""
ARES Mission Control Aerospace Styling
Encapsulates dark-mode sci-fi CSS theme and reusable UI layout components.
"""

import streamlit as st


def apply_custom_styles() -> None:
    """Inject custom aerospace mission control CSS into the Streamlit app."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: #090d14;
            color: #e8edf5;
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }

        section[data-testid="stSidebar"] {
            background: #0d131e;
            border-right: 1px solid #222c3b;
        }

        section[data-testid="stSidebar"] * {
            color: #dce5f2;
        }

        h1, h2, h3, h4 {
            color: #f1f5fb !important;
        }

        .small-label {
            color: #8392a8;
            font-size: 11px;
            letter-spacing: 2px;
            font-weight: 700;
        }

        .hero {
            background: linear-gradient(110deg, #171e2c, #261b1b);
            border: 1px solid #34313a;
            border-radius: 14px;
            padding: 25px;
            margin-bottom: 20px;
        }

        .hero-title {
            font-size: 32px;
            font-weight: 800;
            letter-spacing: 2px;
            color: #ffffff;
        }

        .hero-sub {
            color: #a9b5c6;
            font-size: 13px;
            margin-top: 5px;
        }

        .panel {
            background: #111a27;
            border: 1px solid #273447;
            border-radius: 12px;
            padding: 20px;
            min-height: 120px;
            margin-bottom: 16px;
        }

        .metric-value {
            font-size: 26px;
            font-weight: 700;
            color: #ffffff;
            margin-top: 8px;
        }

        .metric-caption {
            color: #8191a8;
            font-size: 12px;
            line-height: 1.4;
        }

        .status {
            color: #54d69a;
            font-size: 12px;
            font-weight: 700;
        }

        .section-title {
            font-size: 17px;
            font-weight: 700;
            margin-bottom: 15px;
            color: #ffffff;
            letter-spacing: 0.5px;
        }

        .footer {
            color: #66758b;
            font-size: 11px;
            text-align: center;
            padding: 24px 10px;
            border-top: 1px solid #1a2332;
            margin-top: 30px;
            letter-spacing: 1px;
        }

        .disclaimer-box {
            background: rgba(18, 25, 38, 0.7);
            border-left: 3px solid #e3ae69;
            border-radius: 6px;
            padding: 12px 16px;
            margin: 14px 0;
            font-size: 12px;
            color: #b5c2d4;
            line-height: 1.5;
        }

        .badge-verified {
            display: inline-block;
            background: rgba(84, 214, 154, 0.15);
            color: #54d69a;
            border: 1px solid rgba(84, 214, 154, 0.4);
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }

        .badge-simulated {
            display: inline-block;
            background: rgba(227, 174, 105, 0.15);
            color: #e3ae69;
            border: 1px solid rgba(227, 174, 105, 0.4);
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }

        div[data-testid="stSelectbox"] label {
            color: #aab7c9;
            font-size: 12px;
            font-weight: 600;
        }

        .stButton button {
            background: #c65c3d;
            color: white;
            border: none;
            border-radius: 7px;
            font-weight: 600;
            padding: 8px 16px;
        }

        .stButton button:hover {
            background: #e16d49;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

