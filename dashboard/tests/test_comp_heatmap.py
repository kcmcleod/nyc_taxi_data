from unittest.mock import patch

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def valid_chart_df():
    """Provides a standard valid dataframe for happy-path testing."""
    return pd.DataFrame(
        {
            "agg_trip_date": pd.to_datetime(["2023-01-01", "2023-01-02"]),
            "pick_up_borough": ["Manhattan", "EWR"],
            "drop_off_borough": ["Brooklyn", "Queens"],
            "total_trip_count": [1, 2],
            "total_passenger_count": [10.0, 2.0],
            "total_trip_distance_miles": [5.5, 12.0],
            "total_fare_amount": [25.0, 45.0],
            "total_amount_charged": [30.0, 50.0],
        }
    )


@patch("data_access.get_table_data")
def test_comp_heatmap_renders_basic(mock_get_table_data, valid_chart_df):
    """Test that the heatmap component successfully loads"""

    mock_get_table_data.return_value = valid_chart_df

    at = AppTest.from_file("../components/comp_heatmap.py")
    at.run()

    assert "Total" in at.selectbox[0].value
    assert "total_trip_count" in at.selectbox[1].value

    assert not at.exception
    assert len(at.selectbox) == 2
    assert len(at.subheader) == 0

    # agg_level != "Total"
    at.selectbox[0].set_value("Weekly")
    at.selectbox[1].set_value("total_passenger_count")
    at.run()

    assert "Weekly" in at.selectbox[0].value
    assert "total_passenger_count" in at.selectbox[1].value
    assert not at.exception
    assert len(at.selectbox) == 2
    assert len(at.subheader) == 0


@patch("data_access.get_table_data")
def test_comp_heatmap_renders_no_df(mock_get_table_data):
    """Test that the line component handles empty return. This happens if no data or an underlying error"""

    mock_get_table_data.return_value = pd.DataFrame()

    at = AppTest.from_file("../components/comp_heatmap.py")
    at.run()

    assert not at.exception
    assert at.info[0].value == "No trips found for this date range."


@patch("data_access.get_table_data")
def test_comp_heatmap_renders_error(mock_get_table_data):
    """Test that the function can handle an error"""

    mock_get_table_data.side_effect = RuntimeError("This is a simulated error")

    at = AppTest.from_file("../components/comp_heatmap.py")
    at.run()

    assert not at.exception  # exception was thrown but also caught
    assert not at.info

    assert len(at.error) > 0
    assert (
        at.error[0].value == "Failed to load data mart. Please verify dbt build status."
    )


@patch("data_access.get_table_data")
def test_comp_heatmap_missing_cols(mock_get_table_data):
    """Test what happens when cols are missing from data"""

    mock_get_table_data.return_value = pd.DataFrame({"dummy": [1, 2]})

    at = AppTest.from_file("../components/comp_heatmap.py")
    at.run()

    assert not at.exception  # exception was thrown but also caught
    assert not at.info

    assert len(at.error) > 0
    assert at.error[0].value == "Failed to load required data."
