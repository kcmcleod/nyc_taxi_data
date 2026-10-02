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
def test_comp_line_renders_basic(mock_get_table_data, valid_chart_df):
    """Test that the table component successfully loads; cant check the chart apparently."""

    mock_get_table_data.return_value = valid_chart_df

    at = AppTest.from_file("../components/comp_line.py")
    at.run()

    assert not at.exception

    assert len(at.selectbox) == 2
    assert len(at.multiselect) == 2
    assert len(at.subheader) == 1
    assert (
        "Total Trip Count by Trip Date at a daily level for each pick up borough"
        == at.subheader[0].value
    )
    # Streamlit AppTest does not currently expose Vega-Lite chart properties; verifying subheader as a proxy for successful chart rendering.


@patch("data_access.get_table_data")
def test_comp_line_renders_no_df(mock_get_table_data):
    """Test that the line component handles empty return. This happens if no data or an underlying error"""

    mock_get_table_data.return_value = pd.DataFrame()

    at = AppTest.from_file("../components/comp_line.py")
    at.run()

    assert not at.exception
    assert at.info[0].value == "No trips found for this date range."


@patch("data_access.get_table_data")
def test_comp_line_renders_error(mock_get_table_data):
    """Test that the function can handle an error"""

    mock_get_table_data.side_effect = RuntimeError("This is a simulated error")

    at = AppTest.from_file("../components/comp_line.py")
    at.run()

    assert not at.exception  # exception was thrown but also caught
    assert not at.info

    assert len(at.error) > 0
    assert (
        at.error[0].value == "Failed to load data mart. Please verify dbt build status."
    )


@patch("data_access.get_table_data")
def test_comp_line_missing_cols(mock_get_table_data):
    """Test what happens when cols are missing from data"""

    mock_get_table_data.return_value = pd.DataFrame({"dummy": [1, 2]})

    at = AppTest.from_file("../components/comp_line.py")
    at.run()

    assert not at.exception  # exception was thrown but also caught
    assert not at.info

    assert len(at.error) > 0
    assert at.error[0].value == "Failed to load required data."


@patch("data_access.get_table_data")
def test_comp_line_changes_agg_level(mock_get_table_data, valid_chart_df):
    """Test that changing the dropdown updates the backend query."""

    mock_get_table_data.return_value = valid_chart_df

    at = AppTest.from_file("../components/comp_line.py")
    at.run()

    initial_args = mock_get_table_data.call_args.args
    assert "Daily" in initial_args
    assert (
        "Total Trip Count by Trip Date at a daily level for each pick up borough"
        == at.subheader[0].value
    )

    # Verify the mock was called with the updated argument
    at.selectbox[0].set_value("Monthly")
    at.selectbox[1].set_value("total_passenger_count")
    at.run()
    new_args = mock_get_table_data.call_args.args
    assert "Monthly" in new_args
    assert (
        "Total Passenger Count by Trip Date at a monthly level for each pick up borough"
        == at.subheader[0].value
    )


@patch("data_access.get_table_data")
def test_comp_line_changes_boroughs(mock_get_table_data, valid_chart_df):
    """Test that changing the dropdown updates the backend query."""

    mock_get_table_data.return_value = valid_chart_df

    at = AppTest.from_file("../components/comp_line.py")
    at.run()

    # Verify the mock was called with the default 'EWR' argument.
    initial_args = mock_get_table_data.call_args.args
    assert "EWR" in initial_args[2]
    assert "EWR" in initial_args[3]

    # Verify the mock was called with the updated argument
    at.multiselect[0].set_value(["Bronx"])
    at.multiselect[1].set_value(["Bronx"])
    at.run()
    new_args = mock_get_table_data.call_args.args
    assert "EWR" not in new_args[2]
    assert "EWR" not in new_args[3]
    assert "Bronx" in new_args[2]
    assert "Bronx" in new_args[3]
