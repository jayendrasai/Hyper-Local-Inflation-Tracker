"""config/__init__.py — Exposes load_settings at package level."""

from .settings import Settings, load_settings

__all__ = ["Settings", "load_settings"]
