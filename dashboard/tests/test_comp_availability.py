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
def test_comp_avail_renders_basic(mock_get_table_data, valid_chart_df):
    """Test that the table component successfully loads."""

    mock_get_table_data.return_value = valid_chart_df

    at = AppTest.from_file("../components/comp_availability.py")
    at.run()

    assert not at.exception

    assert len(at.selectbox) == 2
    assert len(at.subheader) == 1
    assert (
        "Total Number of Trips by Trip Date at a monthly level" == at.subheader[0].value
    )
    # Streamlit AppTest does not currently expose Vega-Lite chart properties; verifying subheader as a proxy for successful chart rendering.

    # Time rage
    at.selectbox[1].set_value("Full range (ie all time)")
    at.run()

    assert len(at.selectbox) == 2
    assert len(at.subheader) == 1
    assert (
        "Total Number of Trips by Trip Date at a monthly level" == at.subheader[0].value
    )


@patch("data_access.get_table_data")
def test_comp_avail_renders_no_df(mock_get_table_data):
    """Test that the line component handles empty return. This happens if no data or an underlying error"""

    mock_get_table_data.return_value = pd.DataFrame()

    at = AppTest.from_file("../components/comp_availability.py")
    at.run()

    assert not at.exception
    assert at.info[0].value == "No trips found for this date range."


@patch("data_access.get_table_data")
def test_comp_avail_renders_error(mock_get_table_data):
    """Test that the function can handle an error"""

    mock_get_table_data.side_effect = RuntimeError("This is a simulated error")

    at = AppTest.from_file("../components/comp_availability.py")
    at.run()

    assert not at.exception  # exception was thrown but also caught
    assert not at.info

    assert len(at.error) > 0
    assert (
        at.error[0].value == "Failed to load data mart. Please verify dbt build status."
    )


@patch("data_access.get_table_data")
def test_comp_avail_missing_cols(mock_get_table_data):
    """Test what happens when cols are missing from data"""

    mock_get_table_data.return_value = pd.DataFrame({"dummy": [1, 2]})

    at = AppTest.from_file("../components/comp_availability.py")
    at.run()

    assert not at.exception  # exception was thrown but also caught
    assert not at.info

    assert len(at.error) > 0
    assert at.error[0].value == "Failed to load required data."


@patch("data_access.get_table_data")
def test_comp_avail_changes_agg_level(mock_get_table_data, valid_chart_df):
    """Test that changing the dropdown updates the backend query."""

    mock_get_table_data.return_value = valid_chart_df

    at = AppTest.from_file("../components/comp_availability.py")
    at.run()

    initial_args = mock_get_table_data.call_args.args
    assert "Monthly" in initial_args
    assert (
        "Total Number of Trips by Trip Date at a monthly level" == at.subheader[0].value
    )

    # Verify the mock was called with the updated argument
    at.selectbox[0].set_value("Weekly")
    at.run()
    new_args = mock_get_table_data.call_args.args
    assert "Weekly" in new_args
    assert (
        "Total Number of Trips by Trip Date at a weekly level" == at.subheader[0].value
    )
