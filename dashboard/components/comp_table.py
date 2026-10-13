import streamlit as st
from data_access import get_table_data, list_all_boroughs


def render(start_date, end_date):
    """
    Tab that displays a table of metrics. User can choose granularity (day, week, month)
    and can filter by pick up and drop off boroughs.

    Args:
        start_date(date): Start of user selected date range
        end_date(date): End of user selected date range
    """

    borough_list = list_all_boroughs()

    with st.popover("⚙️ Filter Table Data"):
        # Everything inside this block stacks neatly inside the popover menu
        agg_level = st.selectbox(
            "Desired aggregation level?", options=["Daily", "Weekly", "Monthly"]
        )

        pu_boroughs = st.multiselect(
            "Pick up boroughs",
            options=borough_list,
            default=borough_list,
            select_all=True,
        )

        do_boroughs = st.multiselect(
            "Drop off boroughs",
            options=borough_list,
            default=borough_list,
            select_all=True,
        )

    try:
        df = get_table_data(start_date, end_date, pu_boroughs, do_boroughs, agg_level)
    except Exception:  # noqa: BLE001
        st.error("Failed to load data mart. Please verify dbt build status.")
        return

    if df.empty:
        st.info("No trips found for this date range.")
        return

    st.subheader(f"{agg_level} level aggregation data")
    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
        column_config={
            "agg_trip_date": st.column_config.DateColumn(
                label="Trip Date", format="DD/MM/YYYY"
            ),
            "pick_up_borough": st.column_config.TextColumn(label="Pick-up Borough"),
            "drop_off_borough": st.column_config.TextColumn(label="Drop-off Borough"),
            "total_trip_count": st.column_config.NumberColumn(label="Trip Count"),
            "total_passenger_count": st.column_config.NumberColumn(
                label="Passenger Count"
            ),
            "total_trip_distance_miles": st.column_config.NumberColumn(
                label="Total Distance (miles)"
            ),
            "total_fare_amount": st.column_config.NumberColumn(
                label="Total Fare ($)", format="$%.2f"
            ),
            "total_amount_charged": st.column_config.NumberColumn(
                label="Total Charged ($)", format="$%.2f"
            ),
        },
    )


if __name__ == "__main__":  # pragma: no cover
    render("start_date", "end_date")
