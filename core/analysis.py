"""
core/analysis.py
================
AI-powered budget analysis and inflation prediction.

Takes the Pandas DataFrame logged by the user, builds a structured
f-string prompt, and calls the OpenRouter text model to generate
an economist-style inflation report with budget predictions and
cheaper alternative suggestions.
"""

import logging

import openai
import pandas as pd

from config import Settings
from core.ai_client import get_client

logger = logging.getLogger("inflation_tracker.core.analysis")

# ── System prompt (specified by capstone rubric) ───────────────────────────
_ANALYSIS_SYSTEM_PROMPT = (
    "You are a hyper-local economist. Analyze this grocery spending data. "
    "Calculate inflation percentage. Predict next month's budget. "
    "Suggest 2 cheaper alternative items. "
    "Format your response with clear sections using markdown headers. "
    "Be specific with numbers and percentages."
)


def analyze_spending(df: pd.DataFrame, settings: Settings) -> tuple[str, str]:
    """Send the price DataFrame to the text model for economic analysis.

    Constructs a structured prompt with:
    - Full price log (all rows, human-readable)
    - Summary statistics per item (count, mean, min, max, last)

    The system prompt instructs the model to act as a hyper-local
    economist and return a markdown-formatted report.

    Args:
        df: Price DataFrame with columns ``['Date', 'Item', 'Price']``.
        settings: Application settings (model IDs, API key).

    Returns:
        Tuple of ``(analysis_markdown, raw_llm_response)``.
        Both strings are identical — callers may display one and log the other.

    Raises:
        ValueError: If the DataFrame is empty.
        RuntimeError: If the OpenRouter API call fails.
    """
    if df.empty:
        raise ValueError("Cannot analyze: no price data has been logged yet.")

    client = get_client(settings)
    if client is None:
        raise RuntimeError(
            "OpenRouter API key not configured. "
            "Please set OPENROUTER_API_KEY in your .env file."
        )

    # ── Build context from DataFrame ──────────────────────────────────────
    df_copy = df.copy()
    df_copy["Date"] = pd.to_datetime(df_copy["Date"]).dt.strftime("%Y-%m-%d")
    df_copy["Price"] = df_copy["Price"].astype(float)

    summary_stats = (
        df_copy.groupby("Item")["Price"]
        .agg(["count", "mean", "min", "max", "last"])
        .round(2)
        .to_string()
    )
    full_data = df_copy.to_string(index=False)
    entry_count = len(df_copy)
    date_range = f"{df_copy['Date'].min()} to {df_copy['Date'].max()}"

    # ── f-string prompt injection (rubric requirement) ───────────────────
    prompt = f"""
I am tracking local grocery prices. Here is my complete price log data:

=== FULL PRICE LOG ({entry_count} entries from {date_range}) ===
{full_data}

=== SUMMARY STATISTICS (grouped by item) ===
{summary_stats}

Please provide your full economist analysis now.
"""

    logger.info(
        "Sending %d price entries to text model '%s' for analysis.",
        entry_count,
        settings.text_model,
    )

    try:
        response = client.chat.completions.create(
            model=settings.text_model,
            messages=[
                {"role": "system", "content": _ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=1200,
        )
        raw_text = response.choices[0].message.content
        logger.info("Text model analysis received (%d chars).", len(raw_text))
        return raw_text, raw_text

    except openai.APIError as exc:
        logger.error("OpenRouter text API error: %s", exc)
        raise RuntimeError(f"OpenRouter API error: {exc}") from exc
