from datetime import date

import streamlit as st
from data_access import get_table_data, list_all_boroughs


def render(start_date, end_date):
    """
    Tab that displays a line chart. Allows user to select the metric displayed
    then provides a line per pick up borough. Data can be filtered by pick up and
    drop off boroughs

    Args:
        start_date(date): Start of user selected date range
        end_date(date): End of user selected date range
    """

    borough_list = list_all_boroughs()

    with st.popover("⚙️ Filter Line Chart Data and choose the y axis"):
        agg_level = st.selectbox(
            "Aggregation level", options=["Daily", "Weekly", "Monthly"]
        )

        metric_to_plot = st.selectbox(
            "Metric to Plot",
            options=[
                "total_trip_count",
                "total_amount_charged",
                "total_fare_amount",
                "total_trip_distance_miles",
                "total_passenger_count",
            ],
            format_func=lambda x: x.replace("_", " ").title(),
        )

        pu_boroughs = st.multiselect(
            "Pick up boroughs", options=borough_list, default=borough_list
        )

        do_boroughs = st.multiselect(
            "Drop off boroughs", options=borough_list, default=borough_list
        )

    try:
        df = get_table_data(start_date, end_date, pu_boroughs, do_boroughs, agg_level)
    except Exception:  # noqa: BLE001
        st.error("Failed to load data mart. Please verify dbt build status.")
        return

    if df.empty:
        st.info("No trips found for this date range.")
        return

    all_col_names = list(df.columns.values)
    required_cols = [
        "agg_trip_date",
        "pick_up_borough",
        "drop_off_borough",
        metric_to_plot,
    ]

    if not set(required_cols).issubset(all_col_names):
        st.error("Failed to load required data.")
        return

    # regrouping to support desired metric
    chart_df = df.groupby(["agg_trip_date", "pick_up_borough"], as_index=False)[
        metric_to_plot
    ].sum()

    metric_to_plot_fancy = metric_to_plot.replace("_", " ").title()

    # discrete values instead of continuous scale
    chart_df["agg_trip_date"] = chart_df["agg_trip_date"].astype(str)

    chart_df = chart_df.rename(
        columns={
            "pick_up_borough": "Pick up Borough",
            "agg_trip_date": "Trip Date",
            metric_to_plot: metric_to_plot_fancy,
        }
    )

    st.subheader(
        f"{metric_to_plot_fancy} by Trip Date at a {agg_level.lower()} level for each pick up borough"
    )

    st.line_chart(
        chart_df,
        x="Trip Date",
        y=metric_to_plot_fancy,
        color="Pick up Borough",
        x_label="Trip Date",
        y_label=metric_to_plot_fancy,
    )


if __name__ == "__main__":  # pragma: no cover
    render(date(2023, 1, 1), date(2023, 1, 31))
