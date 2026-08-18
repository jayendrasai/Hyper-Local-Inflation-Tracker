"""
config/settings.py
==================
Centralised application settings loaded securely from the .env file.

All environment variables are read here once via `os.environ.get()`.
No other module should call `os.environ` directly — import from here instead.
"""

import logging
import os
from dataclasses import dataclass, field

logger = logging.getLogger("inflation_tracker.config")


# ──────────────────────────────────────────────────────────────────────────────
# APPLICATION SETTINGS DATACLASS
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Settings:
    """Immutable application configuration loaded from environment variables.

    Attributes:
        openrouter_api_key: Secret key for OpenRouter API (NEVER hardcoded).
        openrouter_api_url: Base URL for OpenRouter's OpenAI-compatible API.
        text_model: Model ID used for budget analysis / text generation.
        vision_model: Model ID used for receipt OCR via vision.
        app_title: Display title shown in the Streamlit page config.
        app_icon: Emoji icon for the browser tab.
        tracked_items: Grocery items available for selection in the log form.
        key_items: Items rendered as KPI metric cards on the Dashboard.
        df_columns: Column schema for the price DataFrame.
    """

    # ── API / Security ────────────────────────────────────────────────────────
    openrouter_api_key: str = field(default="")
    openrouter_api_url: str = field(default="https://openrouter.ai/api/v1")

    # ── Model Selection ───────────────────────────────────────────────────────
    text_model: str = field(default="google/gemini-2.5-flash")
    vision_model: str = field(default="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free")

    # ── App Identity ──────────────────────────────────────────────────────────
    app_title: str = "Hyper-Local Inflation Tracker"
    app_icon: str = "📊"

    # ── Domain Constants ──────────────────────────────────────────────────────
    tracked_items: tuple = (
        "Milk", "Eggs", "Rice", "Bread", "Oil", "Sugar", "Dal", "Other"
    )
    key_items: tuple = ("Milk", "Eggs", "Rice")
    df_columns: tuple = ("Date", "Item", "Price")


def load_settings() -> Settings:
    """Load and validate application settings from environment variables.

    Models can be overridden via .env. Falls back to safe defaults if
    optional variables are not set.

    Returns:
        Settings: Fully populated, immutable settings object.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    api_url = os.environ.get(
        "OPENROUTER_API_URL", "https://openrouter.ai/api/v1"
    )
    # Strip trailing path components — the SDK appends /chat/completions itself
    api_url = api_url.rstrip("/chat/completions").rstrip("/")

    text_model = os.environ.get("STORY_MODEL", "google/gemini-2.5-flash")
    vision_model = os.environ.get(
        "VISION_MODEL", "google/gemini-2.5-flash"
    )

    if not api_key:
        logger.warning(
            "OPENROUTER_API_KEY is not set. AI features will be disabled."
        )

    settings = Settings(
        openrouter_api_key=api_key,
        openrouter_api_url=api_url,
        text_model=text_model,
        vision_model=vision_model,
    )

    logger.info(
        "Settings loaded | text_model=%s | vision_model=%s | api_key_set=%s",
        settings.text_model,
        settings.vision_model,
        bool(settings.openrouter_api_key),
    )
    return settings
