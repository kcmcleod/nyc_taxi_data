from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import duckdb
import pandas as pd
import pytest
import pytz
from data_access import (
    get_dataset_date_bounds,
    get_table_data,
    list_all_boroughs,
    run_query,
)


########################################################################################
# run_query(sql: str, params: list | tuple | None = None)
def test_run_query_invalid_sql():
    """test passing in invalid SQL"""
    query = 124
    error_message = f"Not valid SQL: {query}"

    with pytest.raises(TypeError, match=error_message):
        run_query(sql=query)


def test_run_query_no_table():
    """test passing in SQL with no from and thus no table"""
    query = "select apple, banana where apple > 12"
    error_message = f"Not valid SQL: {query}"

    with pytest.raises(duckdb.InvalidInputException, match=error_message):
        run_query(sql=query)


def test_run_query_invalid_table():
    """test passing in valid SQL with an invalid table"""
    table_name = "fruit"
    query = f"select apple, banana from {table_name} where apple > 12"
    error_message = f"Invalid table: {table_name}"

    with pytest.raises(duckdb.InvalidInputException, match=error_message):
        run_query(sql=query)


@patch("dashboard.data_access.os.path.exists")
def test_run_query_cant_find_db(mock_exists):
    """cannot find database"""

    mock_exists.return_value = False

    query = "SELECT DISTINCT borough_name FROM taxi_zone_lookup ORDER BY borough_name"

    with pytest.raises(duckdb.ConnectionException, match="Database not found"):
        run_query(sql=query)


@patch("dashboard.data_access.duckdb.connect")
@patch("dashboard.data_access.os.path.exists")
def test_run_query_execution_error(mock_exists, mock_connect):
    """general error"""

    mock_exists.return_value = True

    mock_con = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_con

    # Force the execute method to raise a DuckDB error
    mock_con.execute.side_effect = duckdb.Error("Simulated syntax error")

    query = "SELECT DISTINCT borough_name FROM taxi_zone_lookup ORDER BY borough_name"

    with pytest.raises(duckdb.Error, match="Simulated syntax error"):
        run_query(sql=query)


def test_run_query_valid_no_params():
    """valid sql should work"""

    project_root = Path(__file__).parents[2]
    seed_file = project_root / "taxi_transforms/seeds/taxi_zone_lookup.csv"
    zone_df = pd.read_csv(
        seed_file,
        dtype={"id": str, "borough_name": str, "zone_name": str, "service_zone": str},
    ).dropna()
    all_boros = zone_df["borough_name"].unique()
    all_boros = list(all_boros)
    all_boros.append("Unknown")
    all_boros.sort()

    query = "SELECT DISTINCT borough_name FROM taxi_zone_lookup ORDER BY borough_name"
    df = run_query(query)
    boro_list = df["borough_name"].to_list()
    boro_list.remove("N/A")
    assert boro_list == all_boros


def test_run_query_valid_with_params():
    """valid sql should work"""

    project_root = Path(__file__).parents[2]
    seed_file = project_root / "taxi_transforms/seeds/taxi_zone_lookup.csv"
    zone_df = pd.read_csv(
        seed_file,
        dtype={"id": str, "borough_name": str, "zone_name": str, "service_zone": str},
    ).dropna()
    expected_df = zone_df.query("borough_name == 'EWR'")[
        ["borough_name", "zone_name", "service_zone"]
    ]

    query = "SELECT DISTINCT borough_name, zone_name, service_zone FROM taxi_zone_lookup WHERE borough_name = ? ORDER BY borough_name"
    params = ["EWR"]
    actual_df = run_query(query, params)

    pd.testing.assert_frame_equal(
        expected_df.reset_index(drop=True), actual_df.reset_index(drop=True)
    )


########################################################################################
# list_all_boroughs()


def test_list_all_boroughs_valid():
    """working list of all borough names"""

    project_root = Path(__file__).parents[2]
    seed_file = project_root / "taxi_transforms/seeds/taxi_zone_lookup.csv"
    zone_df = pd.read_csv(
        seed_file,
        dtype={"id": str, "borough_name": str, "zone_name": str, "service_zone": str},
    ).dropna()
    expected_lst = zone_df["borough_name"].unique().tolist()
    expected_lst.append("Unknown")
    expected_lst.sort()
    actual_lst = list_all_boroughs()
    assert actual_lst == expected_lst


@patch("data_access.run_query")
def test_list_all_boroughs_empty_df_returned(mock_query):
    """triggering backup list of all borough names"""

    backup_list = [
        "Bronx",
        "Brooklyn",
        "EWR",
        "Manhattan",
        "Queens",
        "Staten Island",
        "Unknown",
    ]

    mock_query.return_value = pd.DataFrame()

    actual_lst = list_all_boroughs()
    assert actual_lst == backup_list


@patch("data_access.run_query")
def test_list_all_boroughs_empty_list(mock_query):
    """triggering backup list of all borough names"""

    backup_list = [
        "Bronx",
        "Brooklyn",
        "EWR",
        "Manhattan",
        "Queens",
        "Staten Island",
        "Unknown",
    ]

    mock_query.return_value = pd.DataFrame({"borough_name": ["N/A", "N/A", "N/A"]})

    actual_lst = list_all_boroughs()
    assert actual_lst == backup_list


########################################################################################
# def get_table_data( start_date, end_date, pick_up_boros, drop_off_boros, agg_level="weekly")


def test_get_table_data_missing_args():

    actual_df = get_table_data(
        date(2023, 1, 6), date(2023, 2, 4), ["EWR"], [], "weekly"
    )

    assert actual_df.empty

    actual_df = get_table_data(
        date(2023, 1, 6), date(2023, 2, 4), [], ["EWR"], "weekly"
    )

    assert actual_df.empty

    actual_df = get_table_data(date(2023, 1, 6), None, ["EWR"], ["EWR"], "weekly")

    assert actual_df.empty

    actual_df = get_table_data(None, "Yellow", ["EWR"], ["EWR"], "weekly")

    assert actual_df.empty


def test_get_table_data_bad_dates():
    """neither test or prod db has data from before 2023"""

    actual_df = get_table_data(
        date(2019, 12, 6), date(2023, 2, 4), ["EWR"], None, "weekly"
    )
    assert actual_df.empty

    actual_df = get_table_data(
        date(2023, 2, 4), date(3012, 12, 6), ["EWR"], None, "weekly"
    )
    assert actual_df.empty

    actual_df = get_table_data(
        date(2023, 2, 4), date(2023, 2, 3), ["EWR"], ["EWR"], "weekly"
    )
    assert actual_df.empty


def test_get_table_data_aggregation():
    """test for non existent agg level and thus no table"""

    actual_df = get_table_data(
        date(2019, 12, 6), date(2023, 2, 4), ["EWR"], ["EWR"], "banana"
    )

    assert actual_df.empty


def test_get_table_data_success():
    """test for non existent agg level and thus no table"""

    actual_df = get_table_data(
        date(2019, 12, 6), date(2023, 2, 4), ["EWR"], ["EWR"], "banana"
    )

    assert actual_df.empty


@patch("data_access.run_query")
def test_get_table_weekly_agg(run_query):
    """valid query for weekly data"""

    expected_df = pd.DataFrame(
        {
            "agg_trip_date": pd.to_datetime(["2023-02-04"]),
            "pick_up_borough": ["EWR"],
            "drop_off_borough": ["EWR"],
            "total_trip_count": [1],
            "total_passenger_count": [1.0],
            "total_trip_distance_miles": [0.0],
            "total_fare_amount": [90.0],
            "total_amount_charged": [91.0],
        }
    )

    run_query.return_value = expected_df

    actual_df = get_table_data(
        date(2023, 1, 6), date(2023, 2, 4), ["EWR"], ["EWR"], "weekly"
    )

    pd.testing.assert_frame_equal(
        expected_df.reset_index(drop=True), actual_df.reset_index(drop=True)
    )


@patch("data_access.run_query")
def test_get_table_monthly_agg(run_query):
    """valid query for weekly data"""

    expected_df = pd.DataFrame(
        {
            "agg_trip_date": pd.to_datetime(["2023-02-04"]),
            "pick_up_borough": ["EWR"],
            "drop_off_borough": ["EWR"],
            "total_passenger_count": [1.0],
            "total_trip_distance_miles": [0.0],
            "total_fare_amount": [90.0],
            "total_amount_charged": [91.0],
        }
    )

    run_query.return_value = expected_df

    actual_df = get_table_data(
        date(2023, 1, 6), date(2023, 2, 4), ["EWR"], ["EWR"], "monthly"
    )

    pd.testing.assert_frame_equal(
        expected_df.reset_index(drop=True), actual_df.reset_index(drop=True)
    )


########################################################################################
# get_dataset_date_bounds()


@patch("data_access.run_query")
def test_get_dataset_date_bounds_success(mock_query):
    """simluating success"""

    mock_query.return_value = pd.DataFrame(
        {
            "max_date": [pd.to_datetime("2026-01-02")],
            "min_date": [pd.to_datetime("2026-01-01")],
        }
    )
    expected_start = date(2026, 1, 1)
    expected_end = date(2026, 1, 2)

    start_date, end_date = get_dataset_date_bounds()

    assert start_date == expected_start
    assert end_date == expected_end


@patch("data_access.run_query")
def test_get_dataset_missing_cols(mock_query):
    """simluating db not returning a col"""

    mock_query.return_value = pd.DataFrame(
        {
            "max_dateS": [pd.to_datetime("2026-01-02")],
            "min_date": [pd.to_datetime("2026-01-01")],
        }
    )

    expected_start = date(2023, 1, 1)
    tz = pytz.timezone("UTC")
    expected_end = datetime.now(tz=tz).date()

    start_date, end_date = get_dataset_date_bounds()

    assert start_date == expected_start
    assert end_date == expected_end


@patch("data_access.run_query")
def test_get_dataset_missing_max_date(mock_query):
    """simluating database not returning a max value"""

    mock_query.return_value = pd.DataFrame(
        {
            "max_date": [None],
            "min_date": [pd.to_datetime("2026-01-01")],
        }
    )

    expected_start = date(2023, 1, 1)
    tz = pytz.timezone("UTC")
    expected_end = datetime.now(tz=tz).date()

    start_date, end_date = get_dataset_date_bounds()

    assert start_date == expected_start
    assert end_date == expected_end


@patch("data_access.run_query")
def test_get_dataset_not_a_date(mock_query):
    """simluating db not returning a date"""

    mock_query.return_value = pd.DataFrame(
        {
            "max_date": [1.0],
            "min_date": [pd.to_datetime("2026-01-01")],
        }
    )

    expected_start = date(2023, 1, 1)
    tz = pytz.timezone("UTC")
    expected_end = datetime.now(tz=tz).date()

    start_date, end_date = get_dataset_date_bounds()

    assert start_date == expected_start
    assert end_date == expected_end


@patch("data_access.run_query")
def test_get_dataset_date_bounds_simulate_dbError(mock_query):
    """simluating DB error"""

    mock_query.side_effect = duckdb.Error("Simulated syntax error")

    start_date, end_date = get_dataset_date_bounds()

    expected_start = date(2023, 1, 1)
    tz = pytz.timezone("UTC")
    expected_end = datetime.now(tz=tz).date()

    assert start_date == expected_start
    assert end_date == expected_end


@patch("data_access.run_query")
def test_get_dataset_date_bounds_simulate_error(mock_query):
    """simluating DB error"""

    mock_query.side_effect = RuntimeError("Simulated error")

    start_date, end_date = get_dataset_date_bounds()

    expected_start = date(2023, 1, 1)
    tz = pytz.timezone("UTC")
    expected_end = datetime.now(tz=tz).date()

    assert start_date == expected_start
    assert end_date == expected_end


@patch("data_access.run_query")
def test_get_dataset_date_bounds_simulate_no_data(mock_query):
    """simluating DB error"""

    mock_query.return_value = pd.DataFrame()

    start_date, end_date = get_dataset_date_bounds()

    expected_start = date(2023, 1, 1)
    tz = pytz.timezone("UTC")
    expected_end = datetime.now(tz=tz).date()

    assert start_date == expected_start
    assert end_date == expected_end
