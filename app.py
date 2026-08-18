"""
app.py — Hyper-Local Inflation Tracker
=======================================
Entry point for the Streamlit application.

This file is intentionally thin: it handles only:
  1. .env loading (MUST be first)
  2. Logging bootstrap
  3. Streamlit page config
  4. One-time settings load + session-state init
  5. Rendering the three tabs by delegating to ui.*

All business logic lives in dedicated modules:
  - config/   : settings loaded from .env
  - core/     : OpenRouter AI (vision OCR, text analysis)
  - data/     : session-state DataFrame management
  - ui/       : tab renderers and CSS

Author : [YOUR NAME]
Date   : 2026
"""

# ──────────────────────────────────────────────────────────────────────────────
# 1. SECURITY — load .env BEFORE any other import that might read os.environ
# ──────────────────────────────────────────────────────────────────────────────
from dotenv import load_dotenv

load_dotenv()  # reads .env → populates os.environ

# ──────────────────────────────────────────────────────────────────────────────
# 2. STDLIB & THIRD-PARTY IMPORTS
# ──────────────────────────────────────────────────────────────────────────────
import logging

import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# 3. LOGGING BOOTSTRAP
# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("inflation_tracker.app")

# ──────────────────────────────────────────────────────────────────────────────
# 4. LOCAL PACKAGE IMPORTS (after load_dotenv so settings see the env)
# ──────────────────────────────────────────────────────────────────────────────
from config import load_settings
from data import init_session_state
from ui import (
    inject_styles,
    render_ai_analysis,
    render_app_header,
    render_dashboard,
    render_log_prices,
)

# ──────────────────────────────────────────────────────────────────────────────
# 5. PAGE CONFIG (must be the first Streamlit call)
# ──────────────────────────────────────────────────────────────────────────────
settings = load_settings()

st.set_page_config(
    page_title=settings.app_title,
    page_icon=settings.app_icon,
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": "https://openrouter.ai/docs",
        "Report a bug": None,
        "About": (
            f"# {settings.app_title}\n"
            "B.Tech Capstone Project — Track your real grocery inflation."
        ),
    },
)

# ──────────────────────────────────────────────────────────────────────────────
# 6. ONE-TIME INITIALISATION (CSS + session state)
# ──────────────────────────────────────────────────────────────────────────────
inject_styles()
init_session_state()

# ──────────────────────────────────────────────────────────────────────────────
# 7. APP HEADER
# ──────────────────────────────────────────────────────────────────────────────
render_app_header()

# ──────────────────────────────────────────────────────────────────────────────
# 8. TABS
# ──────────────────────────────────────────────────────────────────────────────
tab_dashboard, tab_log, tab_ai = st.tabs(
    ["📊 Dashboard", "✏️ Log Prices", "🤖 AI Analysis"]
)

with tab_dashboard:
    render_dashboard(settings)

with tab_log:
    render_log_prices(settings)

with tab_ai:
    render_ai_analysis(settings)

logger.debug("app.py render cycle complete.")
