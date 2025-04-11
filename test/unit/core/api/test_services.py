from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from core.api.services import SummaryCache


@pytest.fixture
def summary_cache() -> SummaryCache:
    return SummaryCache()


@pytest.fixture
def user() -> SimpleNamespace:
    return SimpleNamespace(username="hello")


# Case 1: summary_cache_map is empty
@patch("core.api.services.cache.set")
@patch("core.api.services.cache.get")
def test_update_user_not_in_cache_map(
    mock_get: MagicMock,
    mock_set: MagicMock,
    user: SimpleNamespace,
    summary_cache: SummaryCache,
) -> None:
    """Test user is not in summary cache map"""
    mock_get.return_value = {}
    summary_cache.update(user, date(2025, 4, 10), 10.00, "Food")
    mock_set.assert_not_called()


# Case 2: txn_date > end_date
@patch("core.api.services.cache.set")
@patch("core.api.services.cache.get")
def test_update_txn_date_after_range(
    mock_get: MagicMock,
    mock_set: MagicMock,
    user: SimpleNamespace,
    summary_cache: SummaryCache,
) -> None:
    """Test update txn date is greater than date range"""
    # Cached summary cache map
    mock_get.return_value = {"hello": {"hello:summary:2025-04-01:2025-04-30"}}
    summary_cache.update(user, date(2025, 5, 1), 10.00, "Food")
    assert mock_get.call_count == 1
    mock_set.assert_not_called()


# Case 3: txn_date < start_date
@patch("core.api.services.cache.set")
@patch("core.api.services.cache.get")
def test_update_txn_date_before_range(
    mock_get: MagicMock,
    mock_set: MagicMock,
    user: SimpleNamespace,
    summary_cache: SummaryCache,
) -> None:
    """Test update txn date is less than date range"""
    # Cached summary cache map
    mock_get.return_value = {"hello": {"hello:summary:2025-04-01:2025-04-30"}}
    summary_cache.update(user, date(2025, 3, 1), 10.00, "Food")
    assert mock_get.call_count == 1
    mock_set.assert_not_called()


# Case 4: txn_date inside range, category exists
@patch("core.api.services.cache.set")
@patch("core.api.services.cache.get")
def test_update_inside_range_existing_category(
    mock_get: MagicMock,
    mock_set: MagicMock,
    user: SimpleNamespace,
    summary_cache: SummaryCache,
) -> None:
    """Test update when txn is in date"""
    mock_get.side_effect = [
        {"hello": {"hello:summary:2025-04-01:2025-04-30"}},  # summary key map
        {  # summary resulting from cache
            "date_range": ["2025-04-01", "2025-04-30"],
            "total": 100.12,
            "total_by_cat": {"Food": 40.12, "Gas": 60.00},
        },
    ]
    summary_cache.update(user, date(2025, 4, 10), 10.96, "Food")
    expected = {
        "date_range": ["2025-04-01", "2025-04-30"],
        "total": 111.08,
        "total_by_cat": {"Food": 51.08, "Gas": 60.00},
    }
    mock_set.assert_called_with(
        "hello:summary:2025-04-01:2025-04-30", expected, timeout=1800
    )


# Case 5: new category
@patch("core.api.services.cache.set")
@patch("core.api.services.cache.get")
def test_update_new_category_added(
    mock_get: MagicMock,
    mock_set: MagicMock,
    user: SimpleNamespace,
    summary_cache: SummaryCache,
) -> None:
    mock_get.side_effect = [
        {"hello": {"hello:summary:2025-04-01:2025-04-30"}},  # summary key map
        {  # summary resulting from cache
            "date_range": ["2025-04-01", "2025-04-30"],
            "total": 100.00,
            "total_by_cat": {"Groceries": 100.00},
        },
    ]
    summary_cache.update(user, date(2025, 4, 10), 20.48, "Entertainment")
    expected = {
        "date_range": ["2025-04-01", "2025-04-30"],
        "total": 120.48,
        "total_by_cat": {"Groceries": 100.00, "Entertainment": 20.48},
    }
    mock_set.assert_called_with(
        "hello:summary:2025-04-01:2025-04-30", expected, timeout=1800
    )


# Case 6: category drops to 0 and should be removed
@patch("core.api.services.cache.set")
@patch("core.api.services.cache.get")
def test_update_category_drops_to_zero(
    mock_get: MagicMock,
    mock_set: MagicMock,
    user: SimpleNamespace,
    summary_cache: SummaryCache,
) -> None:
    mock_get.side_effect = [
        {"hello": {"hello:summary:2025-04-01:2025-04-30"}},  # summary key map
        {  # summary resulting from cache
            "date_range": ["2025-04-01", "2025-04-30"],
            "total": 50.24,
            "total_by_cat": {"Dining": 50.24},
        },
    ]
    summary_cache.update(user, date(2025, 4, 10), -50.24, "Dining")
    expected = {
        "date_range": ["2025-04-01", "2025-04-30"],
        "total": 0.0,
        "total_by_cat": {},
    }
    mock_set.assert_called_with(
        "hello:summary:2025-04-01:2025-04-30", expected, timeout=1800
    )
