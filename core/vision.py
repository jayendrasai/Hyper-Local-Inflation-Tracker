"""
core/vision.py
==============
Receipt OCR via OpenRouter Vision model.

Encodes camera images as base64, sends them to the configured vision
model, and parses the strictly-JSON response into a list of
{item, price} dicts that the data store can consume.
"""

import base64
import json
import logging
import re

import openai

from config import Settings
from core.ai_client import get_client

logger = logging.getLogger("inflation_tracker.core.vision")

# ── System prompt (specified by capstone rubric) ───────────────────────────
_VISION_SYSTEM_PROMPT = (
    "You are an OCR expert. Extract item names and prices from this receipt. "
    "Output STRICTLY as a JSON array of objects with keys 'item' and 'price'. "
    'Example: [{"item": "Milk", "price": 45.00}, {"item": "Eggs", "price": 72.00}]. '
    "Do NOT include any explanation or text outside the JSON array."
)


def extract_prices_from_image(image_bytes: bytes, settings: Settings) -> list[dict]:
    """Send a receipt image to the Vision model and extract price data.

    Workflow:
        1. Encode raw bytes as a base64 data URI.
        2. POST to OpenRouter vision model with strict JSON output prompt.
        3. Strip any markdown code fences from the response.
        4. Parse and return the JSON array.

    Args:
        image_bytes: Raw JPEG/PNG bytes from ``st.camera_input``.
        settings: Application settings (model IDs, API key).

    Returns:
        List of dicts, each with ``'item'`` (str) and ``'price'`` (float) keys.

    Raises:
        RuntimeError: If the API call fails, or the response cannot be parsed
                      as a valid JSON array.
    """
    client = get_client(settings)
    if client is None:
        raise RuntimeError(
            "OpenRouter API key not configured. "
            "Please set OPENROUTER_API_KEY in your .env file."
        )

    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    image_data_uri = f"data:image/jpeg;base64,{b64_image}"

    logger.info(
        "Sending receipt image to vision model '%s' (%.1f KB).",
        settings.vision_model,
        len(image_bytes) / 1024,
    )

    try:
        response = client.chat.completions.create(
            model=settings.vision_model,
            messages=[
                {"role": "system", "content": _VISION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": image_data_uri},
                        },
                        {
                            "type": "text",
                            "text": "Extract all items and prices from this grocery receipt as JSON.",
                        },
                    ],
                },
            ],
            temperature=0.1,
            max_tokens=800,
        )

        raw_content = response.choices[0].message.content
        logger.info("Vision model response received: %s", raw_content[:200])

        # Strip markdown code fences if the model wrapped the JSON
        json_match = re.search(r"\[.*\]", raw_content, re.DOTALL)
        if not json_match:
            raise RuntimeError(
                f"Vision model did not return a valid JSON array. "
                f"Response: {raw_content[:300]}"
            )

        extracted_items: list[dict] = json.loads(json_match.group())
        logger.info("Extracted %d items from receipt.", len(extracted_items))
        return extracted_items

    except json.JSONDecodeError as exc:
        logger.error("Failed to parse vision model JSON: %s", exc)
        raise RuntimeError(
            f"Could not parse receipt data as JSON: {exc}"
        ) from exc
    except openai.APIError as exc:
        logger.error("OpenRouter vision API error: %s", exc)
        raise RuntimeError(f"OpenRouter API error: {exc}") from exc
