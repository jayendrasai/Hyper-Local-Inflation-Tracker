"""ui/__init__.py — Exposes tab renderers at package level."""

from .ai_analysis import render as render_ai_analysis
from .dashboard import render as render_dashboard
from .log_prices import render as render_log_prices
from .styles import inject_styles, render_app_header

__all__ = [
    "inject_styles",
    "render_app_header",
    "render_dashboard",
    "render_log_prices",
    "render_ai_analysis",
]
