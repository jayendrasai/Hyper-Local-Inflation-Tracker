"""
ui/dashboard.py
===============
Renders the "📊 Dashboard" tab.

Responsibilities:
- KPI metric cards (st.metric with delta) for key tracked items.
- Interactive price-trend line chart (st.line_chart) with item filter.
- Inline-editable price history (st.data_editor) synced back to session state.
- Summary statistics table.
"""

import pandas as pd
import streamlit as st

from config import Settings
from data import compute_kpi_metrics, get_price_df, sync_edited_df
from ui.styles import section_title


def render(settings: Settings) -> None:
    """Render the complete Dashboard tab content.

    Args:
        settings: Application settings (provides ``tracked_items``, ``key_items``).
    """
    df: pd.DataFrame = get_price_df()

    if df.empty:
        st.info(
            "📭 No price data yet. Head over to the **✏️ Log Prices** tab to start tracking!",
            icon="💡",
        )
        return

    # ── KPI METRIC CARDS ─────────────────────────────────────────────────────
    section_title("Key Price Indicators")

    kpi_cols = st.columns(len(settings.key_items))
    for col, item in zip(kpi_cols, settings.key_items):
        with col:
            current_price, delta = compute_kpi_metrics(df, item)
            if current_price is not None:
                st.metric(
                    label=f"🛒 {item}",
                    value=f"₹ {current_price:.2f}",
                    delta=f"₹ {delta:+.2f}" if delta is not None else None,
                    # inverse: red = price UP (bad for consumer), green = DOWN (good)
                    delta_color="inverse",
                )
            else:
                st.metric(label=f"🛒 {item}", value="No data", delta=None)

    # ── PRICE TREND LINE CHART ────────────────────────────────────────────────
    section_title("Price Trend Over Time")

    all_items = sorted(df["Item"].unique().tolist())
    selected_items = st.multiselect(
        "Select items to chart",
        options=all_items,
        default=all_items[:3] if len(all_items) >= 3 else all_items,
        key="chart_item_selector",
    )

    if selected_items:
        chart_df = df[df["Item"].isin(selected_items)].copy()
        chart_df["Date"] = pd.to_datetime(chart_df["Date"])
        chart_df["Price"] = chart_df["Price"].astype(float)
        chart_df = chart_df.sort_values("Date")

        pivot_df = chart_df.pivot_table(
            index="Date", columns="Item", values="Price", aggfunc="mean"
        )
        st.line_chart(pivot_df, width="stretch", height=320)
    else:
        st.caption("Select at least one item above to display the chart.")

    # ── EDITABLE PRICE HISTORY ────────────────────────────────────────────────
    section_title("Price Log History")
    st.caption("✏️ You can directly edit cells below. Changes are reflected instantly.")

    edited_df = st.data_editor(
        get_price_df(),
        num_rows="dynamic",
        width="stretch",
        column_config={
            "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "Item": st.column_config.SelectboxColumn(
                "Item", options=list(settings.tracked_items), required=True
            ),
            "Price": st.column_config.NumberColumn(
                "Price (₹)", min_value=0.0, format="₹ %.2f", required=True
            ),
        },
        key="price_data_editor",
    )
    sync_edited_df(edited_df)

    # ── SUMMARY STATISTICS TABLE ──────────────────────────────────────────────
    section_title("Summary Statistics")

    summary_df = (
        df.groupby("Item")["Price"]
        .agg(["count", "mean", "min", "max"])
        .rename(
            columns={
                "count": "Entries",
                "mean": "Avg (₹)",
                "min": "Min (₹)",
                "max": "Max (₹)",
            }
        )
        .round(2)
    )
    st.dataframe(summary_df, width="stretch")
