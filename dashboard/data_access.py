import datetime
import logging
import os
import re

import duckdb
import pandas as pd
import pytz

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    # We are in production. The package isn't installed,
    # and environment variables are already injected by the host.
    pass

logger = logging.getLogger(__name__)


def run_query(sql: str, params: list | tuple | None = None) -> pd.DataFrame:
    """
    Runs SQL query given in input; opening and closing connection as required

    Args:
        sql(str): SQL statement to run
        params: list or tuples of string values that are inserted into the SQL by this function

    Returns:
        Pandas dateframe of results. Empty if no results.

    """

    db_path = os.getenv("DBT_DUCKDB_PATH")

    if not isinstance(sql, str):
        logger.error(f"Fail: Invalid SQL: {sql}")
        raise TypeError(f"Not valid SQL: {sql}")

    tmp_sql = sql.lower()

    tables_found = re.findall(r"from\s+([a-z_]+)", tmp_sql)

    if not tables_found:
        logger.error(f"Fail: Could not identify table name in: {sql}")
        raise duckdb.InvalidInputException(f"Not valid SQL: {sql}")

    for table_name in tables_found:
        # only works as not expecting joins or nested queries
        is_obt = table_name == os.getenv("OBT_TABLE_NAME")
        is_rpt = table_name.startswith("rpt_nyc_taxi__")
        is_boro = table_name.startswith("taxi_zone_lookup")

        if not (is_obt or is_rpt or is_boro):
            logger.error(f"Fail: You cannot query this table: {table_name}")
            raise duckdb.InvalidInputException(f"Invalid table: {table_name}")

    if not os.path.exists(db_path):
        logger.error(f"Fail: Cannot find database: {db_path}")
        raise duckdb.ConnectionException("Database not found")

    with duckdb.connect(database=db_path, read_only=True) as con:
        if params:
            return con.execute(sql, params).fetch_df()
        con.execute(sql)
        return con.fetch_df()


def show_table(resultSet):
    """Displays a given result set"""
    print(resultSet.head())


def list_all_boroughs() -> list[str]:
    """
    Returns list of all boroughs from Seeds table

    Returns:
        List of boroughs alphabetically sorted. If query fails will return:
        ['Bronx', 'Brooklyn', 'EWR', 'Manhattan', 'Queens', 'Staten Island', 'Unknown']
    """

    backup_list = [
        "Bronx",
        "Brooklyn",
        "EWR",
        "Manhattan",
        "Queens",
        "Staten Island",
        "Unknown",
    ]

    query = """
       SELECT DISTINCT borough_name FROM taxi_zone_lookup ORDER BY borough_name
    """

    try:
        df = run_query(query)

        if df.empty:
            return backup_list

        # N/A filtered out in warehouse so filter it out here too
        boro_list = df[df["borough_name"] != "N/A"]["borough_name"].tolist()

        if len(boro_list) == 0:
            return backup_list

        return boro_list

    except duckdb.Error as e:
        logger.error(f"Database error when fetching boroughs: {e}")
        return backup_list
    except Exception as e:  # noqa: BLE001
        logger.error(f"Unexpected error when fetching boroughs: {e}")
        return backup_list


def get_table_data(
    start_date: datetime.date,
    end_date: datetime.date,
    pick_up_boros: list[str],
    drop_off_boros: list[str],
    agg_level: str = "weekly",
) -> pd.DataFrame:
    """
    Returns the data showning the table tab of the streamlit dashboard

    Args:
        start_date(datetime.date): Starting date for data
        end_date(datetime.date): Ending date for data
        pick_up_boros(list): List of all borough names to be included as a pick up loction
        drop_off_boros(list): List of all borough names to be included as a drop off loction
        agg_level(str): One off ['daily', 'weekly', 'monthly']

    Returns:
        pd.DataFrame of all the data relevant for the above inputs at the requested aggregation level
    """

    if not pick_up_boros or not drop_off_boros or not start_date or not end_date:
        logger.warning(
            f"one of the args in missing: 'start_date': {start_date}, 'end_date': {end_date}, 'pick_up_boros': {pick_up_boros}, 'drop_off_boros': {drop_off_boros}"
        )
        return pd.DataFrame()
    try:
        if start_date > end_date:
            logger.warning(f"{start_date} > {end_date}")
            return pd.DataFrame()

        table_name = "rpt_nyc_taxi__" + agg_level.lower() + "_metrics"

        query = f"""
            SELECT agg_trip_date, pick_up_borough, drop_off_borough, total_trip_count, total_passenger_count, total_trip_distance_miles, total_fare_amount, total_amount_charged        
            FROM {table_name}
            WHERE agg_trip_date >= ?
            AND agg_trip_date <= ?
            AND pick_up_borough IN (SELECT UNNEST(?))
            AND drop_off_borough IN (SELECT UNNEST(?))
            ORDER BY agg_trip_date DESC
            """

        logger.info(
            f"get_table_data query with params: 'start_date': {start_date}, 'end_date': {end_date}, 'pick_up_boros': {pick_up_boros}, 'drop_off_boros': {drop_off_boros}"
        )

        df = run_query(query, [start_date, end_date, pick_up_boros, drop_off_boros])
    except Exception:  # noqa: BLE001
        return pd.DataFrame()

    return df


def get_dataset_date_bounds() -> tuple[datetime.date, datetime.date]:
    """
    Fetches the absolute min and max dates, returning fallbacks if data is invalid.

    Returns:
        tuple[datetime.date, datetime.date]: A tuple containing (start_date, end_date).
    """

    # Define sensible fallbacks to keep the UI alive if the database fails
    fallback_start = datetime.date(2023, 1, 1)  # earliest date in prod
    tz = pytz.timezone("UTC")
    fallback_end = datetime.datetime.now(tz=tz).date()

    try:
        df = run_query(
            f"select max(pick_up_date_time) as max_date, min(pick_up_date_time) as min_date from {os.getenv('OBT_TABLE_NAME')}"
        )

        if df is None or df.empty:
            logger.warning(
                "Date bounds query returned an empty dataframe. Using fallbacks."
            )
            return fallback_start, fallback_end

        if "min_date" not in df.columns or "max_date" not in df.columns:
            logger.warning("Date bounds missing expected columns. Using fallbacks.")
            return fallback_start, fallback_end

        min_val = df["min_date"].iloc[0]
        max_val = df["max_date"].iloc[0]

        if pd.isna(min_val) or pd.isna(max_val):
            logger.warning("Date bounds query returned NULL values. Using fallbacks.")
            return fallback_start, fallback_end

        if not hasattr(min_val, "date") or not hasattr(max_val, "date"):
            logger.warning(
                f"Unexpected data types for dates: {type(min_val)}. Using fallbacks."
            )
            return fallback_start, fallback_end

        return min_val.date(), max_val.date()

    except duckdb.Error as e:
        logger.error(f"Database error when fetching date bounds: {e}")
        return fallback_start, fallback_end
    except Exception as e:  # noqa: BLE001
        logger.error(f"Unexpected error parsing date bounds: {e}")
        return fallback_start, fallback_end


########################################################################################################################

if __name__ == "__main__":  # pragma: no cover
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    queries = [
        "select * from obt_nyc_taxi__tripsB",
        "select * fromobt_nyc_taxi__trips",
        "select * from obt_nyc_taxi__trips",
    ]

    for test_sql in queries:
        try:
            logger.info(f"Testing query: {test_sql}")
            rs = run_query(test_sql)
            nRows = rs.shape[0]
            logger.info(f"Dev test results:  {nRows}")
            if nRows > 0:
                show_table(rs)
        except Exception as e:  # noqa: BLE001
            logger.error(f"Caught expected failure: {type(e).__name__} - {e}")

    get_table_data(
        "2023-01-11", "2023-02-05", pick_up_boros=["EWR"], drop_off_boros=["EWR"]
    )

    # list_all_boroughs()
