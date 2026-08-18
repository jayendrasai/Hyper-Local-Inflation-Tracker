"""
tests/test_data_store.py
========================
Unit tests for data/store.py.

Run with:
    pytest tests/test_data_store.py -v
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


# ──────────────────────────────────────────────────────────────────────────────
# FIXTURES
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture()
def sample_df() -> pd.DataFrame:
    """Return a small price DataFrame for testing."""
    return pd.DataFrame(
        [
            {"Date": "2026-07-01", "Item": "Milk",  "Price": 60.0},
            {"Date": "2026-07-10", "Item": "Milk",  "Price": 65.0},
            {"Date": "2026-07-05", "Item": "Eggs",  "Price": 80.0},
            {"Date": "2026-07-15", "Item": "Rice",  "Price": 45.0},
        ]
    )


@pytest.fixture()
def mock_session_state(monkeypatch):
    """Provide a dict-backed mock for st.session_state."""
    state: dict = {}

    class _FakeSessionState(dict):
        pass

    fake = _FakeSessionState()

    with patch("streamlit.session_state", fake):
        yield fake


# ──────────────────────────────────────────────────────────────────────────────
# TESTS — compute_kpi_metrics
# ──────────────────────────────────────────────────────────────────────────────

class TestComputeKpiMetrics:
    """Tests for data.store.compute_kpi_metrics."""

    def test_returns_none_for_missing_item(self, sample_df):
        from data.store import compute_kpi_metrics

        price, delta = compute_kpi_metrics(sample_df, "Bread")
        assert price is None
        assert delta is None

    def test_current_price_is_last_entry(self, sample_df):
        from data.store import compute_kpi_metrics

        price, delta = compute_kpi_metrics(sample_df, "Milk")
        assert price == 65.0

    def test_delta_calculated_correctly(self, sample_df):
        from data.store import compute_kpi_metrics

        _, delta = compute_kpi_metrics(sample_df, "Milk")
        # 65.0 - 60.0 = 5.0
        assert delta == pytest.approx(5.0)

    def test_no_delta_for_single_entry(self, sample_df):
        from data.store import compute_kpi_metrics

        _, delta = compute_kpi_metrics(sample_df, "Rice")
        assert delta is None


# ──────────────────────────────────────────────────────────────────────────────
# TESTS — append_price_entry
# ──────────────────────────────────────────────────────────────────────────────

class TestAppendPriceEntry:
    """Tests for data.store.append_price_entry."""

    def test_appends_row_to_dataframe(self, mock_session_state):
        import pandas as pd
        from data.store import append_price_entry

        mock_session_state["price_df"] = pd.DataFrame(
            columns=["Date", "Item", "Price"]
        )
        append_price_entry("Sugar", 42.5, date(2026, 7, 20))

        df = mock_session_state["price_df"]
        assert len(df) == 1
        assert df.iloc[0]["Item"] == "Sugar"
        assert df.iloc[0]["Price"] == pytest.approx(42.5)

    def test_price_rounded_to_two_decimals(self, mock_session_state):
        import pandas as pd
        from data.store import append_price_entry

        mock_session_state["price_df"] = pd.DataFrame(
            columns=["Date", "Item", "Price"]
        )
        append_price_entry("Oil", 123.456789, date(2026, 7, 21))

        df = mock_session_state["price_df"]
        assert df.iloc[0]["Price"] == pytest.approx(123.46)


# ──────────────────────────────────────────────────────────────────────────────
# TESTS — append_vision_items
# ──────────────────────────────────────────────────────────────────────────────

class TestAppendVisionItems:
    """Tests for data.store.append_vision_items."""

    def test_valid_items_are_appended(self, mock_session_state):
        import pandas as pd
        from data.store import append_vision_items

        mock_session_state["price_df"] = pd.DataFrame(
            columns=["Date", "Item", "Price"]
        )
        items = [
            {"item": "Bread", "price": 35.0},
            {"item": "Dal",   "price": 90.0},
        ]
        count = append_vision_items(items, date(2026, 7, 22))

        assert count == 2
        assert len(mock_session_state["price_df"]) == 2

    def test_invalid_items_are_skipped(self, mock_session_state):
        import pandas as pd
        from data.store import append_vision_items

        mock_session_state["price_df"] = pd.DataFrame(
            columns=["Date", "Item", "Price"]
        )
        items = [
            {"item": "",      "price": 10.0},   # Empty name — skip
            {"item": "Rice",  "price": -5.0},   # Negative price — skip
            {"item": "Eggs",  "price": 72.0},   # Valid
        ]
        count = append_vision_items(items, date(2026, 7, 22))

        assert count == 1

    def test_returns_zero_for_all_invalid(self, mock_session_state):
        import pandas as pd
        from data.store import append_vision_items

        mock_session_state["price_df"] = pd.DataFrame(
            columns=["Date", "Item", "Price"]
        )
        count = append_vision_items([], date(2026, 7, 22))
        assert count == 0
