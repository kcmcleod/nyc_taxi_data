from datetime import date

import streamlit as st
from data_access import get_table_data, list_all_boroughs


def render(start_date: date, end_date: date, min_date: date, max_date: date):
    """
    Tab displays a bar chart that shows how much data we have for each week or month.
    User can select granularity.

    Args:
        start_date(date): Start of user selected date range
        end_date(date): End of user selected date range
        min_date(date): Start of date range from our entire dataset
        max_date(date): End of date range from our entire dataset
    """

    all_boroughs = list_all_boroughs()

    with st.popover("⚙️ Options"):
        agg_level = st.selectbox(
            "Granularity",
            options=["Monthly", "Weekly"],
        )

        dedsired_time_range = st.selectbox(
            "Data range:",
            options=["From above selection", "Full range (ie all time)"],
        )

    if dedsired_time_range == "From above selection":
        chosen_start_date = start_date
        chosen_end_date = end_date
    else:
        chosen_start_date = min_date
        chosen_end_date = max_date

    try:
        df = get_table_data(
            chosen_start_date, chosen_end_date, all_boroughs, all_boroughs, agg_level
        )
    except Exception:  # noqa: BLE001
        st.error("Failed to load data mart. Please verify dbt build status.")
        return

    if df.empty:
        st.info("No trips found for this date range.")
        return

    all_col_names = list(df.columns.values)
    required_cols = ["agg_trip_date", "total_trip_count"]

    if not set(required_cols).issubset(all_col_names):
        st.error("Failed to load required data.")
        return

    # regrouping to support desired metric
    chart_df = df.groupby(["agg_trip_date"], as_index=False)["total_trip_count"].sum()

    # discrete values instead of continuous scale
    chart_df["agg_trip_date"] = chart_df["agg_trip_date"].astype(str)

    chart_df = chart_df.rename(
        columns={
            "agg_trip_date": "Trip Date",
            "total_trip_count": "Total Number of Trips",
        }
    )

    st.subheader(f"Total Number of Trips by Trip Date at a {agg_level.lower()} level")

    st.bar_chart(
        chart_df,
        x="Trip Date",
        y="Total Number of Trips",
        x_label="Trip Date",
        y_label="Total Number of Trips",
    )


if __name__ == "__main__":  # pragma: no cover
    render(date(2023, 1, 1), date(2023, 1, 31), date(2023, 1, 1), date(2023, 1, 31))
