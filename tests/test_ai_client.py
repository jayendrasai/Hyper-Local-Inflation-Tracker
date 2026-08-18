"""
tests/test_ai_client.py
=======================
Unit tests for core/ai_client.py and config/settings.py.

Run with:
    pytest tests/test_ai_client.py -v
"""

import pytest
from unittest.mock import patch, MagicMock


# ──────────────────────────────────────────────────────────────────────────────
# TESTS — Settings / load_settings
# ──────────────────────────────────────────────────────────────────────────────

class TestLoadSettings:
    """Tests for config.settings.load_settings."""

    def test_reads_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-123")
        monkeypatch.delenv("STORY_MODEL", raising=False)
        monkeypatch.delenv("VISION_MODEL", raising=False)
        monkeypatch.delenv("OPENROUTER_API_URL", raising=False)

        from config.settings import load_settings
        settings = load_settings()

        assert settings.openrouter_api_key == "test-key-123"

    def test_reads_story_model_from_env(self, monkeypatch):
        monkeypatch.setenv("OPENROUTER_API_KEY", "key")
        monkeypatch.setenv("STORY_MODEL", "google/gemma-4-26b-a4b-it:free")

        from config.settings import load_settings
        settings = load_settings()

        assert settings.text_model == "google/gemma-4-26b-a4b-it:free"

    def test_strips_chat_completions_suffix_from_url(self, monkeypatch):
        monkeypatch.setenv("OPENROUTER_API_KEY", "key")
        monkeypatch.setenv(
            "OPENROUTER_API_URL",
            "https://openrouter.ai/api/v1/chat/completions",
        )

        from config.settings import load_settings
        settings = load_settings()

        assert settings.openrouter_api_url == "https://openrouter.ai/api/v1"

    def test_empty_key_is_handled_gracefully(self, monkeypatch):
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

        from config.settings import load_settings
        settings = load_settings()

        assert settings.openrouter_api_key == ""

    def test_default_text_model_is_gemini(self, monkeypatch):
        monkeypatch.delenv("STORY_MODEL", raising=False)
        monkeypatch.setenv("OPENROUTER_API_KEY", "key")

        from config.settings import load_settings
        settings = load_settings()

        assert "gemini" in settings.text_model.lower()


# ──────────────────────────────────────────────────────────────────────────────
# TESTS — get_client
# ──────────────────────────────────────────────────────────────────────────────

class TestGetClient:
    """Tests for core.ai_client.get_client."""

    def test_returns_none_when_api_key_missing(self):
        from config.settings import Settings
        from core.ai_client import get_client

        settings = Settings(openrouter_api_key="")
        client = get_client(settings)
        assert client is None

    def test_returns_openai_client_when_key_present(self):
        from config.settings import Settings
        from core.ai_client import get_client

        settings = Settings(
            openrouter_api_key="sk-test-key",
            openrouter_api_url="https://openrouter.ai/api/v1",
        )
        client = get_client(settings)
        assert client is not None

    def test_client_uses_correct_base_url(self):
        from config.settings import Settings
        from core.ai_client import get_client

        settings = Settings(
            openrouter_api_key="sk-test-key",
            openrouter_api_url="https://openrouter.ai/api/v1",
        )
        client = get_client(settings)
        # The OpenAI SDK exposes base_url on the client
        assert "openrouter.ai" in str(client.base_url)
