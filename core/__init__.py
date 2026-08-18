"""core/__init__.py — Exposes core AI functions at package level."""

from .ai_client import get_client
from .analysis import analyze_spending
from .vision import extract_prices_from_image

__all__ = ["get_client", "analyze_spending", "extract_prices_from_image"]
