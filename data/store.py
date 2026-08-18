"""
data/store.py
=============
Session-state DataFrame management and mutation helpers.

All reads from and writes to ``st.session_state["price_df"]`` are
funnelled through this module.  No UI file should manipulate the
DataFrame directly — they call these functions instead.
"""

import logging
from datetime import date
from typing import Optional

import pandas as pd
import streamlit as st

logger = logging.getLogger("inflation_tracker.data.store")

# DataFrame column schema
DF_COLUMNS: list[str] = ["Date", "Item", "Price"]


# ──────────────────────────────────────────────────────────────────────────────
# STATE INITIALISATION
# ──────────────────────────────────────────────────────────────────────────────

def init_session_state() -> None:
    """Initialise all session state keys exactly once per browser session.

    Safe to call on every Streamlit rerun — keys are only written if absent.
    """
    defaults: dict = {
        "price_df": pd.DataFrame(columns=DF_COLUMNS),
        "ai_analysis_result": None,
        "ai_raw_response": None,
        "vision_status": None,          # None | "success" | "error"
        "vision_message": "",
        "last_camera_image_id": None,
        "upload_status": None,          # None | "success" | "error"
        "upload_message": "",
        "last_upload_file_id": None,
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
            logger.debug("session_state['%s'] initialised.", key)

    logger.info("Session state initialisation complete.")


# ──────────────────────────────────────────────────────────────────────────────
# READ HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def get_price_df() -> pd.DataFrame:
    """Return the current price DataFrame from session state.

    Returns:
        pd.DataFrame with columns ['Date', 'Item', 'Price'].
    """
    df = st.session_state["price_df"]
    # Ensure Date column is a datetime type for Streamlit compatibility
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def compute_kpi_metrics(
    df: pd.DataFrame, item: str
) -> tuple[Optional[float], Optional[float]]:
    """Calculate the latest price and price delta for a tracked item.

    Delta = last price − second-to-last price for the same item.
    Used to populate ``st.metric``'s ``value`` and ``delta`` parameters.

    Args:
        df: The price DataFrame.
        item: Grocery item name to compute metrics for.

    Returns:
        ``(current_price, delta)`` — both are ``None`` if no data exists.
        ``delta`` is ``None`` if fewer than two entries exist for the item.
    """
    item_df = df[df["Item"] == item].copy()
    item_df["Date"] = pd.to_datetime(item_df["Date"])
    item_df = item_df.sort_values("Date").reset_index(drop=True)

    if item_df.empty:
        return None, None

    current_price = float(item_df["Price"].iloc[-1])
    delta: Optional[float] = None
    if len(item_df) >= 2:
        previous_price = float(item_df["Price"].iloc[-2])
        delta = round(current_price - previous_price, 2)

    return current_price, delta


# ──────────────────────────────────────────────────────────────────────────────
# WRITE HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def append_price_entry(item: str, price: float, entry_date: date) -> None:
    """Append one manually-entered price row to the session state DataFrame.

    Args:
        item: Grocery item name (must match TRACKED_ITEMS).
        price: Price in local currency (₹).  Must be > 0.
        entry_date: Date of price observation.
    """
    new_row = pd.DataFrame(
        [{"Date": pd.to_datetime(entry_date), "Item": item, "Price": round(float(price), 2)}]
    )
    st.session_state["price_df"] = pd.concat(
        [st.session_state["price_df"], new_row], ignore_index=True
    )
    logger.info(
        "AUDIT | Manual entry: item=%s price=%.2f date=%s",
        item, price, entry_date,
    )


def append_vision_items(extracted_items: list[dict], entry_date: date) -> int:
    """Validate and append vision-OCR extracted items to the DataFrame.

    Skips any entry that is missing keys, has an empty item name, or has
    a non-positive price.  All valid rows are appended atomically.

    Args:
        extracted_items: List of ``{'item': str, 'price': float}`` dicts
                         returned by :func:`core.vision.extract_prices_from_image`.
        entry_date: Date to assign to all appended rows.

    Returns:
        Number of valid rows successfully appended.
    """
    valid_rows: list[dict] = []
    for obj in extracted_items:
        try:
            item_name = str(obj.get("item", "")).strip()
            price_val = float(obj.get("price", 0))
            if not item_name or price_val <= 0:
                logger.warning("Skipping invalid vision item: %s", obj)
                continue
            valid_rows.append(
                {
                    "Date": pd.to_datetime(entry_date),
                    "Item": item_name,
                    "Price": round(price_val, 2),
                }
            )
        except (ValueError, TypeError) as exc:
            logger.warning("Could not parse vision item %s: %s", obj, exc)

    if valid_rows:
        new_rows_df = pd.DataFrame(valid_rows)
        st.session_state["price_df"] = pd.concat(
            [st.session_state["price_df"], new_rows_df], ignore_index=True
        )
        logger.info(
            "AUDIT | Vision scan: %d items appended for date=%s",
            len(valid_rows), entry_date,
        )

    return len(valid_rows)


def sync_edited_df(edited_df: pd.DataFrame) -> None:
    """Sync a ``st.data_editor`` result back to session state.

    Only writes if the DataFrame actually changed to avoid spurious reruns.

    Args:
        edited_df: DataFrame returned by ``st.data_editor``.
    """
    if not edited_df.equals(st.session_state["price_df"]):
        st.session_state["price_df"] = edited_df
        logger.info("AUDIT | data_editor: session_state DataFrame updated by user.")
