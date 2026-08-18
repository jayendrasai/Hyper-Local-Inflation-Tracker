"""
core/ai_client.py
=================
OpenRouter API client factory.

Centralises client creation so every AI feature (vision, text) uses
the same configured SDK instance without duplicating setup logic.
"""

import logging
from typing import Optional

import openai

from config import Settings

logger = logging.getLogger("inflation_tracker.core.ai_client")


def get_client(settings: Settings) -> Optional[openai.OpenAI]:
    """Create and return a configured OpenAI SDK client pointing at OpenRouter.

    The client is intentionally not cached at module level to allow
    Streamlit's session-based reloading to always use the latest settings.

    Args:
        settings: Application settings containing the API key and base URL.

    Returns:
        openai.OpenAI instance, or None if the API key is missing.
    """
    if not settings.openrouter_api_key:
        logger.warning("get_client: API key is missing — returning None.")
        return None

    client = openai.OpenAI(
        base_url=settings.openrouter_api_url,
        api_key=settings.openrouter_api_key,
    )
    logger.debug("OpenRouter client created | base_url=%s", settings.openrouter_api_url)
    return client
