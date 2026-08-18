"""
ui/log_prices.py
================
Renders the "✏️ Log Prices" tab.

Layout:
  Left column  — Manual price entry form (st.form with clear_on_submit).
  Right column — AI Receipt Scanner with two input modes:
                   • 📷 Live camera capture (st.camera_input)
                   • 📁 Upload from local storage (st.file_uploader)
                 Both modes pass image bytes through the same Vision OCR
                 pipeline → extract_prices_from_image → append_vision_items.

All DataFrame writes go through data.store helpers.
"""

from datetime import date

import streamlit as st

from config import Settings
from core import extract_prices_from_image
from data import append_price_entry, append_vision_items, get_price_df
from ui.styles import section_title

# Accepted MIME types for the file uploader
_ACCEPTED_IMAGE_TYPES = ["jpg", "jpeg", "png", "webp", "bmp"]


# ──────────────────────────────────────────────────────────────────────────────
# INTERNAL HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def _process_image_bytes(
    image_bytes: bytes,
    receipt_date: date,
    settings: Settings,
    status_key: str,
    message_key: str,
    image_id_key: str,
    image_id: int,
) -> None:
    """Run Vision OCR on raw image bytes and persist status to session state.

    Shared by both camera and file-upload paths to avoid code duplication.

    Args:
        image_bytes: Raw bytes of the receipt image.
        receipt_date: Date to assign to all extracted entries.
        settings: App settings (model IDs, API key).
        status_key: Session-state key to store "success" | "error" | None.
        message_key: Session-state key to store the human-readable result message.
        image_id_key: Session-state key to track the last processed image hash.
        image_id: Hash of the current image (dedup guard).
    """
    st.session_state[image_id_key] = image_id
    with st.spinner("🔍 Analysing receipt with AI Vision..."):
        try:
            extracted_items = extract_prices_from_image(image_bytes, settings)
            count_added = append_vision_items(extracted_items, receipt_date)
            st.session_state[status_key] = "success"
            st.session_state[message_key] = (
                f"✅ Extracted and logged **{count_added}** item(s) from receipt."
            )
        except RuntimeError as exc:
            st.session_state[status_key] = "error"
            st.session_state[message_key] = str(exc)


def _show_ocr_status(status_key: str, message_key: str) -> None:
    """Render the persistent OCR result badge (success / error)."""
    status = st.session_state.get(status_key)
    if status == "success":
        st.success(st.session_state[message_key], icon="✅")
    elif status == "error":
        st.error(
            f"❌ Scan failed: {st.session_state[message_key]}",
            icon="🚨",
        )


# ──────────────────────────────────────────────────────────────────────────────
# PUBLIC RENDERER
# ──────────────────────────────────────────────────────────────────────────────

def render(settings: Settings) -> None:
    """Render the complete Log Prices tab content.

    Args:
        settings: Application settings (provides ``tracked_items``, API key).
    """
    col_manual, col_vision = st.columns([1, 1], gap="large")

    # ──────────────────────────────────────────────────────────────────────────
    # LEFT COLUMN — MANUAL ENTRY FORM
    # ──────────────────────────────────────────────────────────────────────────
    with col_manual:
        section_title("Manual Price Entry")

        with st.form(key="manual_price_form", clear_on_submit=True):
            selected_item = st.selectbox(
                "Grocery Item",
                options=list(settings.tracked_items),
                index=0,
                key="form_item_select",
            )
            price_input = st.number_input(
                "Price (₹)",
                min_value=0.01,
                max_value=100_000.0,
                value=50.00,
                step=0.50,
                format="%.2f",
                key="form_price_input",
            )
            date_input = st.date_input(
                "Date Observed",
                value=date.today(),
                max_value=date.today(),
                key="form_date_input",
            )
            submitted = st.form_submit_button(
                "➕ Log Price Entry",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if price_input <= 0:
                st.error("Price must be greater than zero.")
            else:
                append_price_entry(selected_item, price_input, date_input)
                st.success(
                    f"✅ Logged: **{selected_item}** @ ₹{price_input:.2f} on {date_input}",
                    icon="✅",
                )
                st.balloons()

    # ──────────────────────────────────────────────────────────────────────────
    # RIGHT COLUMN — AI RECEIPT SCANNER
    # ──────────────────────────────────────────────────────────────────────────
    with col_vision:
        section_title("AI Receipt Scanner")

        api_key_present = bool(settings.openrouter_api_key)
        if not api_key_present:
            st.warning(
                "⚠️ **OPENROUTER_API_KEY not set.** "
                "Receipt scanning requires a valid API key in your `.env` file.",
                icon="🔑",
            )

        # ── Shared receipt date picker ────────────────────────────────────────
        receipt_date = st.date_input(
            "Receipt Date",
            value=date.today(),
            max_value=date.today(),
            key="receipt_date_input",
        )

        # ── Sub-tabs: Camera vs Upload ────────────────────────────────────────
        scan_tab, upload_tab = st.tabs(["📷 Camera Capture", "📁 Upload Image"])

        # ── Camera capture ────────────────────────────────────────────────────
        with scan_tab:
            st.caption(
                "Take a live photo of your grocery receipt. "
                "AI Vision will extract item names and prices automatically."
            )
            camera_image = st.camera_input(
                "Point camera at receipt and click capture",
                key="receipt_camera",
                disabled=not api_key_present,
            )

            if camera_image is not None:
                image_id = hash(camera_image.getvalue())
                if image_id != st.session_state.get("last_camera_image_id"):
                    _process_image_bytes(
                        image_bytes=camera_image.getvalue(),
                        receipt_date=receipt_date,
                        settings=settings,
                        status_key="vision_status",
                        message_key="vision_message",
                        image_id_key="last_camera_image_id",
                        image_id=image_id,
                    )
                _show_ocr_status("vision_status", "vision_message")

        # ── File upload ───────────────────────────────────────────────────────
        with upload_tab:
            st.caption(
                "Upload a saved photo of your grocery bill from your device. "
                "Supported formats: JPG, PNG, WEBP, BMP."
            )

            uploaded_file = st.file_uploader(
                "Choose a bill / receipt image",
                type=_ACCEPTED_IMAGE_TYPES,
                accept_multiple_files=False,
                disabled=not api_key_present,
                key="receipt_file_uploader",
                help=(
                    "Upload a clear, well-lit photo of your grocery receipt. "
                    "The AI will extract all item names and prices automatically."
                ),
            )

            if uploaded_file is not None:
                # ── Preview the uploaded image ────────────────────────────────
                st.image(
                    uploaded_file,
                    caption=f"📄 {uploaded_file.name}  "
                            f"({uploaded_file.size / 1024:.1f} KB)",
                    use_container_width=True,
                )

                # ── Dedup: only process once per unique file ──────────────────
                file_id = hash(uploaded_file.getvalue())
                if file_id != st.session_state.get("last_upload_file_id"):
                    _process_image_bytes(
                        image_bytes=uploaded_file.getvalue(),
                        receipt_date=receipt_date,
                        settings=settings,
                        status_key="upload_status",
                        message_key="upload_message",
                        image_id_key="last_upload_file_id",
                        image_id=file_id,
                    )

                _show_ocr_status("upload_status", "upload_message")

                # ── File metadata expander ────────────────────────────────────
                with st.expander("📋 File Details", expanded=False):
                    st.markdown(
                        f"""
| Field | Value |
|-------|-------|
| **Filename** | `{uploaded_file.name}` |
| **File Type** | `{uploaded_file.type}` |
| **Size** | {uploaded_file.size / 1024:.1f} KB |
| **Receipt Date** | {receipt_date} |
                        """
                    )

    # ── RECENT ENTRIES PREVIEW ────────────────────────────────────────────────
    section_title("Recent Entries")
    current_df = get_price_df()
    if current_df.empty:
        st.caption("No entries yet. Log prices above or scan a receipt.")
    else:
        recent = current_df.tail(8).iloc[::-1]
        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Price": st.column_config.NumberColumn("Price (₹)", format="₹ %.2f")
            },
        )
        st.caption(f"Total entries: **{len(current_df)}**")
