"""
ui/styles.py
============
Global CSS injection for the professional fintech dashboard aesthetic.

Call ``inject_styles()`` once at app startup — before any tabs or widgets.

Design rules:
- NO neon colours.
- Palette: deep blues (#1a2332, #1e3a5f), slate greys (#7f8c8d, #8ab4d4),
  off-white text (#e8f0fe).
- Price-up indicator: muted red  (#c0392b).
- Price-down indicator: muted green (#27ae60).
"""

import streamlit as st

# ── Named palette tokens ───────────────────────────────────────────────────
COLOR_UP = "#c0392b"       # Muted red   — price increased (bad)
COLOR_DOWN = "#27ae60"     # Muted green — price decreased (good)
COLOR_NEUTRAL = "#7f8c8d"  # Slate grey  — no change

_CSS = """
<style>
    /* ── Hide default Streamlit chrome ───────────────────────────────── */
    #MainMenu {visibility: hidden;}
    footer     {visibility: hidden;}
    header     {visibility: hidden;}

    /* ── Root font ───────────────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    }

    /* ── Main container ─────────────────────────────────────────────── */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* ── App header banner ───────────────────────────────────────────── */
    .app-header {
        background: linear-gradient(135deg, #1a2332 0%, #243447 100%);
        border-radius: 12px;
        padding: 1.25rem 2rem;
        margin-bottom: 1.5rem;
        border: 1px solid #2d4a6e;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .app-header h1 {
        color: #e8f0fe;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .app-header p {
        color: #8ab4d4;
        font-size: 0.85rem;
        margin: 0.2rem 0 0 0;
    }

    /* ── KPI metric cards ────────────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: #1c2b3a;
        border: 1px solid #2d4a6e;
        border-radius: 10px;
        padding: 1rem 1.25rem;
    }
    [data-testid="stMetricLabel"] {
        color: #8ab4d4 !important;
        font-size: 0.8rem !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="stMetricValue"] {
        color: #e8f0fe !important;
        font-size: 1.75rem !important;
        font-weight: 700;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.85rem !important;
        font-weight: 600;
    }

    /* ── Tabs ────────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: transparent;
        border-bottom: 2px solid #2d4a6e;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #8ab4d4;
        border: 1px solid transparent;
        border-radius: 8px 8px 0 0;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        font-size: 0.9rem;
    }
    .stTabs [aria-selected="true"] {
        background: #1c2b3a !important;
        color: #e8f0fe !important;
        border-color: #2d4a6e !important;
        border-bottom-color: #1c2b3a !important;
    }

    /* ── Section label ───────────────────────────────────────────────── */
    .section-title {
        color: #8ab4d4;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #2d4a6e;
    }

    /* ── Status badges ───────────────────────────────────────────────── */
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-success { background:#1a4731; color:#4caf82; border:1px solid #2d6b4a; }
    .badge-warning { background:#4a2c00; color:#f0a500; border:1px solid #6b4200; }
    .badge-info    { background:#1a2e4a; color:#5c8ab5; border:1px solid #2a4a6e; }

    /* ── Expander ────────────────────────────────────────────────────── */
    .streamlit-expanderHeader {
        background: #1c2b3a;
        border: 1px solid #2d4a6e;
        border-radius: 8px;
        color: #8ab4d4;
    }

    /* ── Data editor ─────────────────────────────────────────────────── */
    [data-testid="stDataEditor"] {
        border: 1px solid #2d4a6e;
        border-radius: 8px;
    }

    /* ── Primary button ──────────────────────────────────────────────── */
    .stButton > button[kind="primary"] {
        background: #1e3a5f;
        border: 1px solid #4a90d9;
        color: #e8f0fe;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"]:hover {
        background: #2d5484;
        border-color: #5ca8f5;
    }

    /* ── Alerts ──────────────────────────────────────────────────────── */
    .stAlert { border-radius: 8px; }
</style>
"""


def inject_styles() -> None:
    """Inject the application-wide CSS into the Streamlit page.

    Must be called once, after ``st.set_page_config``, before rendering
    any widgets.
    """
    st.markdown(_CSS, unsafe_allow_html=True)


def render_app_header() -> None:
    """Render the branded gradient header banner."""
    st.markdown(
        """
        <div class="app-header">
            <div>
                <h1>📊 Hyper-Local Inflation Tracker</h1>
                <p>Track real grocery prices · Visualize your personal inflation · Predict your next budget with AI</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(label: str) -> None:
    """Render a styled uppercase section-title label.

    Args:
        label: The text to display as the section heading.
    """
    st.markdown(
        f'<p class="section-title">{label}</p>',
        unsafe_allow_html=True,
    )
