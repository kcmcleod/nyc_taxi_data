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
def test_comp_table_renders_dataframe(mock_get_table_data, valid_chart_df):
    """Test that the table component successfully loads and renders a dataframe."""

    mock_get_table_data.return_value = valid_chart_df

    at = AppTest.from_file("../components/comp_table.py")
    at.run()

    assert not at.exception

    assert len(at.selectbox) == 1
    assert len(at.multiselect) == 2
    assert len(at.subheader) == 1
    assert at.subheader[0].value == "Daily level aggregation data"

    assert len(at.dataframe) == 1  # there is a table
    rendered_df = at.dataframe[0].value
    assert rendered_df.shape[1] == 8
    assert rendered_df.shape[0] == 2


@patch("data_access.get_table_data")
def test_comp_table_renders_no_df(mock_get_table_data):
    """Test that the table component handles empty return. This happens if no data or an underlying error"""

    mock_get_table_data.return_value = pd.DataFrame()

    at = AppTest.from_file("../components/comp_table.py")
    at.run()

    assert not at.exception

    assert len(at.dataframe) == 0  # there is NO table
    assert at.info[0].value == "No trips found for this date range."


@patch("data_access.get_table_data")
def test_comp_table_renders_error(mock_get_table_data):
    """Test that the function can handle an error"""

    mock_get_table_data.side_effect = RuntimeError("This is a simulated error")

    at = AppTest.from_file("../components/comp_table.py")
    at.run()

    assert not at.exception  # exception was thrown but also caught
    assert not at.info

    assert len(at.dataframe) == 0  # there is NO table
    assert len(at.error) > 0
    assert (
        at.error[0].value == "Failed to load data mart. Please verify dbt build status."
    )


@patch("data_access.get_table_data")
def test_comp_table_changes_agg_level(mock_get_table_data):
    """Test that changing the dropdown updates the backend query."""

    mock_get_table_data.return_value = pd.DataFrame({"dummy": [1, 2]})

    at = AppTest.from_file("../components/comp_table.py")
    at.run()

    # Verify the mock was called with the default 'Daily' argument.
    initial_args = mock_get_table_data.call_args.args
    assert "Daily" in initial_args

    # Verify the mock was called with the updated argument
    at.selectbox[0].set_value("Monthly")
    at.run()
    new_args = mock_get_table_data.call_args.args
    assert "Monthly" in new_args
    assert at.subheader[0].value == "Monthly level aggregation data"


@patch("data_access.get_table_data")
def test_comp_table_changes_boroughs(mock_get_table_data):
    """Test that changing the dropdown updates the backend query."""

    mock_get_table_data.return_value = valid_chart_df

    at = AppTest.from_file("../components/comp_table.py")
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
